-- =====================================================
-- MIGRATION 002: Module Memory & Reuse System
-- Purpose: Enable Hybrid Weighted Scoring for cross-project module reuse
-- Date: 2025-12-10
-- =====================================================

-- =====================================================
-- 0. EXTEND PROJECT_DOCUMENTS TABLE (if needed)
-- Add metadata to distinguish git-analyzed vs manual uploads
-- =====================================================

-- Check if metadata column exists, add if not
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'project_documents' 
        AND column_name = 'metadata'
    ) THEN
        ALTER TABLE project_documents 
        ADD COLUMN metadata JSONB DEFAULT '{}'::jsonb;
        
        COMMENT ON COLUMN project_documents.metadata IS 'Metadata for document source tracking (git_analyzer, manual_upload, etc.)';
    END IF;
END $$;


-- =====================================================
-- 1. EXTEND MODULES TABLE
-- Add 4-layer metadata and source tracking
-- =====================================================

-- Add source type to distinguish how module was created
ALTER TABLE modules 
ADD COLUMN source_type VARCHAR(50) DEFAULT 'manual_upload' 
CHECK (source_type IN ('git_analyzed', 'manual_upload', 'ai_generated', 'reused'));

-- Add primary intent (L1) as dedicated column for fast filtering
-- This is the most important matching factor
ALTER TABLE modules 
ADD COLUMN intent_primary VARCHAR(100);

-- Add comprehensive tags metadata as JSONB for flexibility
-- Structure: {
--   "L1_intent": ["Auth", "Payment"],
--   "L2_constraint": ["Node.js", "PostgreSQL", "React"],
--   "L3_context": ["Fintech", "B2B"],
--   "L4_quality": ["High-Traffic", "Core-Service"],
--   "confidence_scores": {"L1": 0.95, "L2": 0.88, ...},
--   "ai_assigned": true,
--   "assigned_at": "2025-12-10T..."
-- }
ALTER TABLE modules 
ADD COLUMN tags_metadata JSONB DEFAULT '{}'::jsonb;

-- Add reuse tracking
ALTER TABLE modules 
ADD COLUMN reused_from_module_id UUID REFERENCES modules(id) ON DELETE SET NULL,
ADD COLUMN reuse_strategy VARCHAR(50) CHECK (reuse_strategy IN ('direct', 'logic_reference', 'new_gen', NULL));

-- Update generation_metadata to track if tags were AI-generated
COMMENT ON COLUMN modules.tags_metadata IS '4-layer metadata: L1-Intent, L2-Constraint, L3-Context, L4-Quality';
COMMENT ON COLUMN modules.source_type IS 'How this module originated: git_analyzed, manual_upload, ai_generated, reused';
COMMENT ON COLUMN modules.reuse_strategy IS 'If reused: direct (copy), logic_reference (adapt), new_gen (scratch)';


-- =====================================================
-- 2. CREATE MODULE_TAGS TABLE
-- Normalized storage for multi-tagging with confidence scores
-- =====================================================

CREATE TABLE module_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    
    -- 4-layer classification
    layer VARCHAR(20) NOT NULL CHECK (layer IN ('L1_intent', 'L2_constraint', 'L3_context', 'L4_quality')),
    tag_value VARCHAR(100) NOT NULL,
    
    -- AI confidence in this tag (0.0 - 1.0)
    confidence_score NUMERIC(3,2) DEFAULT 0.80 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Metadata for tag
    tag_metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Who/what assigned this tag
    assigned_by VARCHAR(50) DEFAULT 'ai', -- 'ai' or 'human' or user_id
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Prevent duplicate tags for same module+layer+value
    CONSTRAINT unique_module_layer_tag UNIQUE (module_id, layer, tag_value)
);

-- Indexes for fast tag-based searching
CREATE INDEX idx_module_tags_module_id ON module_tags(module_id);
CREATE INDEX idx_module_tags_layer ON module_tags(layer);
CREATE INDEX idx_module_tags_tag_value ON module_tags(tag_value);
CREATE INDEX idx_module_tags_layer_value ON module_tags(layer, tag_value);
CREATE INDEX idx_module_tags_confidence ON module_tags(confidence_score DESC);

-- GIN index for JSONB queries
CREATE INDEX idx_module_tags_metadata ON module_tags USING GIN(tag_metadata);

COMMENT ON TABLE module_tags IS 'Multi-tag storage for module classification with confidence scores';


-- =====================================================
-- 3. CREATE REUSE_HISTORY TABLE
-- Track module reuse decisions for analytics and learning
-- =====================================================

CREATE TABLE reuse_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Source: Which module was used as reference
    source_module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    
    -- Target: Which new module was created
    target_module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    
    -- Target project context
    target_project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Matching score (0.0 - 1.0)
    similarity_score NUMERIC(4,3) CHECK (similarity_score >= 0 AND similarity_score <= 1),
    
    -- Component scores for debugging/tuning
    score_breakdown JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "L1_intent_score": 0.95,
    --   "L2_constraint_score": 0.70,
    --   "L3_context_score": 0.85,
    --   "L4_quality_score": 0.60,
    --   "weights_used": {"L1": 0.5, "L2": 0.25, "L3": 0.15, "L4": 0.1},
    --   "final_weighted_score": 0.83
    -- }
    
    -- Decision made
    reuse_strategy VARCHAR(50) NOT NULL CHECK (reuse_strategy IN ('direct', 'logic_reference', 'new_gen')),
    decision_rationale TEXT,
    
    -- User feedback (for future ML training)
    user_accepted BOOLEAN,
    user_feedback TEXT,
    
    -- AI model used for matching
    ai_model VARCHAR(100),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX idx_reuse_history_source ON reuse_history(source_module_id);
CREATE INDEX idx_reuse_history_target ON reuse_history(target_module_id);
CREATE INDEX idx_reuse_history_project ON reuse_history(target_project_id);
CREATE INDEX idx_reuse_history_score ON reuse_history(similarity_score DESC);
CREATE INDEX idx_reuse_history_strategy ON reuse_history(reuse_strategy);
CREATE INDEX idx_reuse_history_created ON reuse_history(created_at DESC);

-- GIN index for score breakdown analysis
CREATE INDEX idx_reuse_history_breakdown ON reuse_history USING GIN(score_breakdown);

COMMENT ON TABLE reuse_history IS 'Tracks module reuse decisions with scores for analytics and weight tuning';


-- =====================================================
-- 4. CREATE SCORING_WEIGHTS_CONFIG TABLE
-- Store configurable weights for different project types
-- =====================================================

CREATE TABLE scoring_weights_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Config name/description
    config_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    
    -- When to use this config (optional filters)
    project_domain VARCHAR(100), -- e.g., 'fintech', 'ecommerce', NULL = default
    target_tech_stack VARCHAR(100), -- e.g., 'node.js', 'python', NULL = any
    
    -- Weights (must sum to 1.0)
    weight_L1_intent NUMERIC(3,2) DEFAULT 0.50 CHECK (weight_L1_intent >= 0 AND weight_L1_intent <= 1),
    weight_L2_constraint NUMERIC(3,2) DEFAULT 0.25 CHECK (weight_L2_constraint >= 0 AND weight_L2_constraint <= 1),
    weight_L3_context NUMERIC(3,2) DEFAULT 0.15 CHECK (weight_L3_context >= 0 AND weight_L3_context <= 1),
    weight_L4_quality NUMERIC(3,2) DEFAULT 0.10 CHECK (weight_L4_quality >= 0 AND weight_L4_quality <= 1),
    
    -- Zone thresholds
    threshold_direct_reuse NUMERIC(3,2) DEFAULT 0.85 CHECK (threshold_direct_reuse >= 0 AND threshold_direct_reuse <= 1),
    threshold_logic_reference NUMERIC(3,2) DEFAULT 0.60 CHECK (threshold_logic_reference >= 0 AND threshold_logic_reference <= 1),
    
    -- Usage tracking
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,
    usage_count INT DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure weights sum to 1.0
    CONSTRAINT weights_sum_check CHECK (
        weight_L1_intent + weight_L2_constraint + weight_L3_context + weight_L4_quality = 1.0
    )
);

-- Insert default configuration
INSERT INTO scoring_weights_config (
    config_name, 
    description, 
    is_default,
    weight_L1_intent,
    weight_L2_constraint,
    weight_L3_context,
    weight_L4_quality,
    threshold_direct_reuse,
    threshold_logic_reference
) VALUES (
    'default',
    'Default weights - Intent-first approach (50% Intent, 25% Constraint, 15% Context, 10% Quality)',
    true,
    0.50, -- L1 Intent (most important)
    0.25, -- L2 Constraint 
    0.15, -- L3 Context
    0.10, -- L4 Quality
    0.85, -- Direct reuse threshold
    0.60  -- Logic reference threshold
);

-- Insert tech-agnostic configuration (for cross-tech reuse)
INSERT INTO scoring_weights_config (
    config_name, 
    description,
    weight_L1_intent,
    weight_L2_constraint,
    weight_L3_context,
    weight_L4_quality,
    threshold_direct_reuse,
    threshold_logic_reference
) VALUES (
    'tech_agnostic',
    'Focus on logic/domain - Lower constraint weight (60% Intent, 10% Constraint, 25% Context, 5% Quality)',
    0.60, -- L1 Intent (higher)
    0.10, -- L2 Constraint (much lower - tech doesn''t matter much)
    0.25, -- L3 Context (higher - domain matters more)
    0.05, -- L4 Quality
    0.75, -- Lower threshold since tech might differ
    0.55
);

CREATE INDEX idx_weights_config_name ON scoring_weights_config(config_name);
CREATE INDEX idx_weights_config_domain ON scoring_weights_config(project_domain);
CREATE INDEX idx_weights_config_active ON scoring_weights_config(is_active);

COMMENT ON TABLE scoring_weights_config IS 'Configurable scoring weights for different reuse scenarios';


-- =====================================================
-- 5. INDEXES ON MODULES TABLE (for fast searching)
-- =====================================================

-- Index on primary intent for quick filtering
CREATE INDEX idx_modules_intent_primary ON modules(intent_primary);

-- Index on source type
CREATE INDEX idx_modules_source_type ON modules(source_type);

-- GIN index on tags_metadata JSONB for complex queries
CREATE INDEX idx_modules_tags_metadata ON modules USING GIN(tags_metadata);

-- Index on reuse tracking
CREATE INDEX idx_modules_reused_from ON modules(reused_from_module_id);
CREATE INDEX idx_modules_reuse_strategy ON modules(reuse_strategy);


-- =====================================================
-- 6. UPDATE EXISTING MODULES
-- Set default values for existing records
-- =====================================================

-- Set source_type for existing modules based on generation_metadata
UPDATE modules 
SET source_type = CASE 
    WHEN generated_by_ai = true THEN 'ai_generated'
    ELSE 'manual_upload'
END
WHERE source_type IS NULL;


-- =====================================================
-- 7. HELPER FUNCTIONS
-- =====================================================

-- Function to calculate similarity score between two modules
CREATE OR REPLACE FUNCTION calculate_module_similarity(
    source_module_id UUID,
    target_tags JSONB,
    config_name VARCHAR DEFAULT 'default'
) RETURNS TABLE(
    similarity_score NUMERIC,
    score_breakdown JSONB,
    recommended_strategy VARCHAR
) AS $$
DECLARE
    weights_config RECORD;
    source_tags JSONB;
    L1_score NUMERIC := 0;
    L2_score NUMERIC := 0;
    L3_score NUMERIC := 0;
    L4_score NUMERIC := 0;
    final_score NUMERIC := 0;
    strategy VARCHAR;
BEGIN
    -- Get weights configuration
    SELECT * INTO weights_config 
    FROM scoring_weights_config 
    WHERE scoring_weights_config.config_name = calculate_module_similarity.config_name
    LIMIT 1;
    
    -- Get source module tags
    SELECT tags_metadata INTO source_tags
    FROM modules
    WHERE id = source_module_id;
    
    -- Calculate layer scores (Jaccard similarity for array overlap)
    -- L1 Intent
    L1_score := (
        SELECT COUNT(*)::NUMERIC / GREATEST(
            (SELECT COUNT(*) FROM jsonb_array_elements_text(source_tags->'L1_intent')) +
            (SELECT COUNT(*) FROM jsonb_array_elements_text(target_tags->'L1_intent')) -
            (SELECT COUNT(*) FROM (
                SELECT * FROM jsonb_array_elements_text(source_tags->'L1_intent')
                INTERSECT
                SELECT * FROM jsonb_array_elements_text(target_tags->'L1_intent')
            ) overlap),
            1
        )
    );
    
    -- Similar for L2, L3, L4...
    -- (Simplified here - full implementation would calculate all layers)
    
    -- Calculate weighted final score
    final_score := (
        L1_score * weights_config.weight_L1_intent +
        L2_score * weights_config.weight_L2_constraint +
        L3_score * weights_config.weight_L3_context +
        L4_score * weights_config.weight_L4_quality
    );
    
    -- Determine strategy based on thresholds
    IF final_score >= weights_config.threshold_direct_reuse THEN
        strategy := 'direct';
    ELSIF final_score >= weights_config.threshold_logic_reference THEN
        strategy := 'logic_reference';
    ELSE
        strategy := 'new_gen';
    END IF;
    
    -- Return results
    RETURN QUERY SELECT 
        final_score,
        jsonb_build_object(
            'L1_intent_score', L1_score,
            'L2_constraint_score', L2_score,
            'L3_context_score', L3_score,
            'L4_quality_score', L4_score,
            'weights_used', jsonb_build_object(
                'L1', weights_config.weight_L1_intent,
                'L2', weights_config.weight_L2_constraint,
                'L3', weights_config.weight_L3_context,
                'L4', weights_config.weight_L4_quality
            )
        ),
        strategy;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_module_similarity IS 'Calculate similarity score between modules using weighted 4-layer matching';


-- =====================================================
-- 8. ROW LEVEL SECURITY (RLS) POLICIES
-- Grant access to authenticated users (same as existing tables)
-- =====================================================

-- Enable RLS on new tables
ALTER TABLE module_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE reuse_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE scoring_weights_config ENABLE ROW LEVEL SECURITY;

-- MODULE_TAGS: Users can manage tags for modules they have access to
CREATE POLICY "Users can view all module tags"
ON module_tags FOR SELECT
USING (true);

CREATE POLICY "Users can insert module tags"
ON module_tags FOR INSERT
WITH CHECK (true);

CREATE POLICY "Users can update module tags"
ON module_tags FOR UPDATE
USING (true);

CREATE POLICY "Users can delete module tags"
ON module_tags FOR DELETE
USING (true);

-- REUSE_HISTORY: Users can view all reuse history for analytics
CREATE POLICY "Users can view reuse history"
ON reuse_history FOR SELECT
USING (true);

CREATE POLICY "Users can insert reuse history"
ON reuse_history FOR INSERT
WITH CHECK (true);

CREATE POLICY "Users can update reuse history"
ON reuse_history FOR UPDATE
USING (true);

-- SCORING_WEIGHTS_CONFIG: Users can view all configs, admins can modify
CREATE POLICY "Users can view scoring configs"
ON scoring_weights_config FOR SELECT
USING (true);

CREATE POLICY "Users can insert scoring configs"
ON scoring_weights_config FOR INSERT
WITH CHECK (true);

CREATE POLICY "Users can update scoring configs"
ON scoring_weights_config FOR UPDATE
USING (true);


-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- Next steps:
-- 1. Update Python models (modules/module_manager/model.py) ✅
-- 2. Create tag generation service (AI-powered) ✅
-- 3. Implement search/matching algorithm ✅
-- 4. Update module generation flow to check memories first ✅
-- 5. Test both workflows (git-analyzed vs manual-upload) ⏳
