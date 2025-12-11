-- Migration 003: Single Tag Per Layer + Enhanced Metadata
-- Changes:
-- 1. Enforce single tag per layer per module (unique constraint)
-- 2. Enhance tag_metadata to store detailed reasoning
-- 3. Remove L4_quality layer (MVP simplification)
-- 4. Add index for faster tag lookups

-- Drop existing unique constraint if exists (from previous migrations)
ALTER TABLE module_tags DROP CONSTRAINT IF EXISTS module_tags_module_layer_tag_unique;

-- =====================================================
-- CLEAN UP DUPLICATES FIRST (before adding constraint)
-- =====================================================

-- Step 1: Identify and report duplicate tags
DO $$
DECLARE
    duplicate_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO duplicate_count
    FROM (
        SELECT module_id, layer, COUNT(*) as tag_count
        FROM module_tags
        GROUP BY module_id, layer
        HAVING COUNT(*) > 1
    ) duplicates;
    
    IF duplicate_count > 0 THEN
        RAISE NOTICE 'Found % modules with duplicate tags per layer', duplicate_count;
        RAISE NOTICE 'Cleaning up: Keeping highest confidence tag per layer...';
    ELSE
        RAISE NOTICE 'No duplicate tags found. Database is clean.';
    END IF;
END $$;

-- Step 2: Delete duplicate tags (keep only highest confidence per layer)
DELETE FROM module_tags mt1
WHERE EXISTS (
    SELECT 1
    FROM module_tags mt2
    WHERE mt1.module_id = mt2.module_id
    AND mt1.layer = mt2.layer
    AND (
        mt1.confidence_score < mt2.confidence_score
        OR (mt1.confidence_score = mt2.confidence_score AND mt1.created_at < mt2.created_at)
    )
);

-- Step 3: Verify cleanup
DO $$
DECLARE
    remaining_duplicates INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO remaining_duplicates
    FROM (
        SELECT module_id, layer, COUNT(*) as tag_count
        FROM module_tags
        GROUP BY module_id, layer
        HAVING COUNT(*) > 1
    ) duplicates;
    
    IF remaining_duplicates > 0 THEN
        RAISE EXCEPTION 'Still have % duplicate tags! Cannot proceed with constraint.', remaining_duplicates;
    ELSE
        RAISE NOTICE '✅ All duplicates cleaned up successfully';
    END IF;
END $$;

-- Step 4: NOW add unique constraint (after cleanup)
ALTER TABLE module_tags ADD CONSTRAINT module_tags_module_layer_unique 
    UNIQUE (module_id, layer);

-- Create index for faster tag-based queries
CREATE INDEX IF NOT EXISTS idx_module_tags_tag_value ON module_tags(tag_value);
CREATE INDEX IF NOT EXISTS idx_module_tags_layer ON module_tags(layer);

-- Update tag_metadata column comment to reflect new structure
COMMENT ON COLUMN module_tags.tag_metadata IS 
'Detailed metadata for tag: {"reasoning": "Why this tag was chosen and what secondary aspects exist"}';

-- Clean up any L4_quality tags (we removed this layer)
DO $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM module_tags WHERE layer = 'L4_quality';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RAISE NOTICE '✅ Removed % L4_quality tags', deleted_count;
END $$;

-- Update modules.tags_metadata structure
-- Note: This is just documentation - JSONB allows any structure
-- New structure: {
--   "L1_intent": {"tag": "auth", "confidence": 0.95, "reasoning": "..."},
--   "L2_constraint": {"tag": "nodejs", "confidence": 0.90, "reasoning": "..."},
--   "L3_context": {"tag": "saas", "confidence": 0.85, "reasoning": "..."}
-- }
COMMENT ON COLUMN modules.tags_metadata IS 
'Single tag per layer with reasoning: {"L1_intent": {"tag": "auth", "confidence": 0.95, "reasoning": "..."}, ...}';

-- =====================================================
-- FINAL VERIFICATION
-- =====================================================

-- Verify data integrity one more time
DO $$
DECLARE
    final_duplicate_count INTEGER;
    total_tags INTEGER;
    modules_with_tags INTEGER;
BEGIN
    -- Count remaining tags
    SELECT COUNT(*) INTO total_tags FROM module_tags;
    
    -- Count modules with tags
    SELECT COUNT(DISTINCT module_id) INTO modules_with_tags FROM module_tags;
    
    -- Check for any remaining duplicates (should be 0)
    SELECT COUNT(*)
    INTO final_duplicate_count
    FROM (
        SELECT module_id, layer, COUNT(*) as tag_count
        FROM module_tags
        GROUP BY module_id, layer
        HAVING COUNT(*) > 1
    ) duplicates;
    
    RAISE NOTICE '==================================================';
    RAISE NOTICE '📊 FINAL STATISTICS:';
    RAISE NOTICE '   Total tags: %', total_tags;
    RAISE NOTICE '   Modules with tags: %', modules_with_tags;
    RAISE NOTICE '   Duplicate tags: % (should be 0)', final_duplicate_count;
    RAISE NOTICE '==================================================';
    
    IF final_duplicate_count = 0 THEN
        RAISE NOTICE '✅ Database integrity verified';
    ELSE
        RAISE EXCEPTION '❌ Still have duplicates! Migration failed.';
    END IF;
END $$;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 003 completed successfully';
    RAISE NOTICE '   - Single tag per layer constraint added';
    RAISE NOTICE '   - L4_quality layer removed';
    RAISE NOTICE '   - Indexes created for performance';
    RAISE NOTICE '   - Duplicate tags cleaned up';
END $$;
