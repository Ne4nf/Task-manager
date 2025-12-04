-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- =====================================================
-- PROJECTS TABLE
-- =====================================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    domain VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'on-hold', 'completed', 'archived')),
    
    -- Statistics (calculated from modules/tasks)
    module_count INT DEFAULT 0,
    task_count INT DEFAULT 0,
    completed_tasks INT DEFAULT 0,
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_projects_created_by ON projects(created_by);
CREATE INDEX idx_projects_domain ON projects(domain);
CREATE INDEX idx_projects_status ON projects(status);

-- =====================================================
-- PROJECT DOCUMENTS TABLE (for uploaded .md/.docx files)
-- =====================================================
CREATE TABLE project_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL CHECK (file_type IN ('markdown', 'docx', 'pdf')),
    content TEXT NOT NULL,
    file_size INT,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_project_id ON project_documents(project_id);
CREATE INDEX idx_documents_file_type ON project_documents(file_type);

-- =====================================================
-- MODULES TABLE
-- =====================================================
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Comprehensive module fields (matching FE form)
    scope TEXT,
    dependencies TEXT,
    features TEXT,
    requirements TEXT,
    technical_specs TEXT,
    
    progress INT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    task_count INT DEFAULT 0,
    completed_tasks INT DEFAULT 0,
    
    -- AI generation metadata
    generated_by_ai BOOLEAN DEFAULT FALSE,
    generation_metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_modules_project_id ON modules(project_id);
CREATE INDEX idx_modules_progress ON modules(progress);

-- =====================================================
-- TASKS TABLE
-- =====================================================
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    assignee VARCHAR(255),
    status VARCHAR(50) DEFAULT 'todo' CHECK (status IN ('todo', 'in-progress', 'in-review', 'blocked', 'done')),
    priority VARCHAR(50) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),

    -- Performance tracking (matching FE form fields)
    difficulty INT DEFAULT 2 CHECK (difficulty >= 1 AND difficulty <= 5),
    time_estimate DECIMAL(5,2) DEFAULT 0,
    actual_time DECIMAL(5,2) DEFAULT 0,
    quality_score INT DEFAULT 3 CHECK (quality_score >= 1 AND quality_score <= 5),
    autonomy INT DEFAULT 2 CHECK (autonomy >= 1 AND autonomy <= 4),

    due_date DATE,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- AI generation metadata
    generated_by_ai BOOLEAN DEFAULT FALSE,
    generation_metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tasks_module_id ON tasks(module_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_assignee ON tasks(assignee);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- =====================================================
-- PROJECT MEMORIES TABLE (for AI context)
-- =====================================================
CREATE TABLE project_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Vector embeddings for semantic search (1536 dimensions for OpenAI ada-002)
    embedding vector(1536),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_memories_project_id ON project_memories(project_id);
CREATE INDEX idx_memories_type ON project_memories(memory_type);

-- Vector similarity search index (using HNSW algorithm for fast similarity search)
CREATE INDEX idx_memories_embedding ON project_memories
USING hnsw (embedding vector_cosine_ops);

-- =====================================================
-- TEAM MEMBERS TABLE
-- =====================================================
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'Developer',
    joined_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(project_id, user_id)
);

CREATE INDEX idx_team_project_id ON team_members(project_id);
CREATE INDEX idx_team_user_id ON team_members(user_id);

-- =====================================================
-- ACTIVITY LOGS TABLE
-- =====================================================
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_activity_project_id ON activity_logs(project_id);
CREATE INDEX idx_activity_created_at ON activity_logs(created_at DESC);

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_modules_updated_at
    BEFORE UPDATE ON modules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON project_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto-calculate module statistics based on tasks
CREATE OR REPLACE FUNCTION update_module_stats()
RETURNS TRIGGER AS $$
DECLARE
    v_module_id UUID;
BEGIN
    v_module_id := COALESCE(NEW.module_id, OLD.module_id);
    
    UPDATE modules
    SET 
        task_count = (SELECT COUNT(*) FROM tasks WHERE module_id = v_module_id),
        completed_tasks = (SELECT COUNT(*) FROM tasks WHERE module_id = v_module_id AND status = 'done'),
        progress = (
            SELECT CASE
                WHEN COUNT(*) = 0 THEN 0
                ELSE ROUND((COUNT(*) FILTER (WHERE status = 'done')::DECIMAL / COUNT(*)) * 100)
            END
            FROM tasks
            WHERE module_id = v_module_id
        )
    WHERE id = v_module_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER task_stats_change
    AFTER INSERT OR UPDATE OR DELETE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_module_stats();

-- Auto-calculate project statistics based on modules
CREATE OR REPLACE FUNCTION update_project_stats()
RETURNS TRIGGER AS $$
DECLARE
    v_project_id UUID;
BEGIN
    v_project_id := COALESCE(NEW.project_id, OLD.project_id);
    
    UPDATE projects
    SET 
        module_count = (SELECT COUNT(*) FROM modules WHERE project_id = v_project_id),
        task_count = (
            SELECT COUNT(*) 
            FROM tasks t 
            JOIN modules m ON t.module_id = m.id 
            WHERE m.project_id = v_project_id
        ),
        completed_tasks = (
            SELECT COUNT(*) 
            FROM tasks t 
            JOIN modules m ON t.module_id = m.id 
            WHERE m.project_id = v_project_id AND t.status = 'done'
        ),
        progress = (
            SELECT CASE
                WHEN COUNT(*) = 0 THEN 0
                ELSE ROUND((COUNT(*) FILTER (WHERE status = 'done')::DECIMAL / COUNT(*)) * 100)
            END
            FROM tasks t 
            JOIN modules m ON t.module_id = m.id 
            WHERE m.project_id = v_project_id
        )
    WHERE id = v_project_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER module_stats_change
    AFTER INSERT OR UPDATE OR DELETE ON modules
    FOR EACH ROW EXECUTE FUNCTION update_project_stats();

-- Semantic search function for project memories
CREATE OR REPLACE FUNCTION match_project_memories(
    query_embedding vector(1536),
    match_threshold float,
    match_count int,
    filter_project_id uuid DEFAULT NULL,
    filter_memory_type varchar DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    project_id uuid,
    memory_type varchar,
    title varchar,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pm.id,
        pm.project_id,
        pm.memory_type,
        pm.title,
        pm.content,
        pm.metadata,
        1 - (pm.embedding <=> query_embedding) as similarity
    FROM project_memories pm
    WHERE
        (filter_project_id IS NULL OR pm.project_id = filter_project_id)
        AND (filter_memory_type IS NULL OR pm.memory_type = filter_memory_type)
        AND 1 - (pm.embedding <=> query_embedding) > match_threshold
    ORDER BY pm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- Users: Can read their own data
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Projects: Team members can read, creators can update
CREATE POLICY "Team members can read projects" ON projects
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM team_members
            WHERE team_members.project_id = projects.id
            AND team_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Creators can update projects" ON projects
    FOR UPDATE USING (created_by = auth.uid());

CREATE POLICY "Authenticated users can create projects" ON projects
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Modules: Inherit project permissions
CREATE POLICY "Team members can read modules" ON modules
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM team_members
            WHERE team_members.project_id = modules.project_id
            AND team_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Team members can modify modules" ON modules
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM team_members
            WHERE team_members.project_id = modules.project_id
            AND team_members.user_id = auth.uid()
        )
    );

-- Tasks: Inherit module/project permissions
CREATE POLICY "Team members can read tasks" ON tasks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM modules m
            JOIN team_members tm ON tm.project_id = m.project_id
            WHERE m.id = tasks.module_id
            AND tm.user_id = auth.uid()
        )
    );

CREATE POLICY "Team members can modify tasks" ON tasks
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM modules m
            JOIN team_members tm ON tm.project_id = m.project_id
            WHERE m.id = tasks.module_id
            AND tm.user_id = auth.uid()
        )
    );

-- Project Memories: Inherit project permissions
CREATE POLICY "Team members can read memories" ON project_memories
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM team_members
            WHERE team_members.project_id = project_memories.project_id
            AND team_members.user_id = auth.uid()
        )
    );

-- Project Documents: Inherit project permissions
CREATE POLICY "Team members can read documents" ON project_documents
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM team_members
            WHERE team_members.project_id = project_documents.project_id
            AND team_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Team members can upload documents" ON project_documents
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM team_members
            WHERE team_members.project_id = project_documents.project_id
            AND team_members.user_id = auth.uid()
        )
    );

-- Team Members: Can read, project creators can manage
CREATE POLICY "Team members can read team" ON team_members
    FOR SELECT USING (
        user_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = team_members.project_id
            AND projects.created_by = auth.uid()
        )
    );

-- Activity Logs: Read-only for team members
CREATE POLICY "Team members can read activity" ON activity_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM team_members
            WHERE team_members.project_id = activity_logs.project_id
            AND team_members.user_id = auth.uid()
        )
    );

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE projects IS 'Main projects table with statistics calculated from modules and tasks';
COMMENT ON TABLE project_documents IS 'Uploaded project documentation files (.md, .docx) for AI module generation';
COMMENT ON TABLE modules IS 'Modules within projects - large features with comprehensive specifications';
COMMENT ON TABLE tasks IS 'Tasks within modules - actionable work items with performance tracking';
COMMENT ON TABLE project_memories IS 'AI context storage with vector embeddings for semantic search';
COMMENT ON COLUMN project_memories.embedding IS 'OpenAI ada-002 embeddings (1536 dimensions) for semantic similarity search';
COMMENT ON FUNCTION match_project_memories IS 'Semantic search function using cosine similarity on embeddings';
