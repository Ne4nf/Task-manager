-- =====================================================
-- ROLLBACK PARTIAL MIGRATION 002 & CLEAN RERUN
-- =====================================================

-- Step 1: Drop unrestricted tables
DROP TABLE IF EXISTS module_tags CASCADE;
DROP TABLE IF EXISTS reuse_history CASCADE;
DROP TABLE IF EXISTS scoring_weights_config CASCADE;

-- Step 2: Drop function if exists
DROP FUNCTION IF EXISTS calculate_module_similarity(UUID, JSONB, VARCHAR);

-- Step 3: Remove columns added to modules table (rollback ALTER TABLE)
DO $$ 
BEGIN
    -- Remove source_type
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'modules' AND column_name = 'source_type'
    ) THEN
        ALTER TABLE modules DROP COLUMN source_type;
    END IF;

    -- Remove intent_primary
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'modules' AND column_name = 'intent_primary'
    ) THEN
        ALTER TABLE modules DROP COLUMN intent_primary;
    END IF;

    -- Remove tags_metadata
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'modules' AND column_name = 'tags_metadata'
    ) THEN
        ALTER TABLE modules DROP COLUMN tags_metadata;
    END IF;

    -- Remove reused_from_module_id
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'modules' AND column_name = 'reused_from_module_id'
    ) THEN
        ALTER TABLE modules DROP COLUMN reused_from_module_id;
    END IF;

    -- Remove reuse_strategy
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'modules' AND column_name = 'reuse_strategy'
    ) THEN
        ALTER TABLE modules DROP COLUMN reuse_strategy;
    END IF;
END $$;

-- Step 4: Drop indexes on modules if exist
DROP INDEX IF EXISTS idx_modules_intent_primary;
DROP INDEX IF EXISTS idx_modules_source_type;
DROP INDEX IF EXISTS idx_modules_tags_metadata;
DROP INDEX IF EXISTS idx_modules_reused_from;
DROP INDEX IF EXISTS idx_modules_reuse_strategy;

-- Step 5: Remove metadata column from project_documents if added
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'project_documents' AND column_name = 'metadata'
    ) THEN
        ALTER TABLE project_documents DROP COLUMN metadata;
    END IF;
END $$;

-- =====================================================
-- ROLLBACK COMPLETE - NOW READY FOR CLEAN 002 RUN
-- =====================================================
