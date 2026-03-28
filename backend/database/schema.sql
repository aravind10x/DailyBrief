-- Daily Brief Database Schema for Supabase
-- This schema supports the hybrid operational + memory architecture

-- Create custom types
CREATE TYPE task_status AS ENUM ('parking_lot', 'todo', 'inprogress', 'done');
CREATE TYPE approval_status AS ENUM ('draft', 'approved', 'auto_approved');

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tasks table (Current operational state – Approved only)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    okr_id UUID, -- Will add foreign key constraint after weekly_okrs table is created
    title TEXT NOT NULL,
    status task_status DEFAULT 'todo',
    rank INTEGER DEFAULT 0,
    estimated_duration INTEGER NOT NULL CHECK (estimated_duration > 0),
    due_date DATE,
    memory_id TEXT, -- Reference to OpenMemory for task context
    carried_forward BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Draft tasks table (Staging area for daily task generation)
CREATE TABLE draft_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    okr_id UUID, -- Will add foreign key constraint after weekly_okrs table is created
    title TEXT NOT NULL,
    status task_status DEFAULT 'todo',
    rank INTEGER DEFAULT 0,
    estimated_duration INTEGER NOT NULL CHECK (estimated_duration > 0),
    due_date DATE,
    memory_id TEXT, -- Reference to OpenMemory for task context
    carried_forward BOOLEAN DEFAULT FALSE,
    generation_context JSONB, -- Store AI generation metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Task logs table (Tracking)
CREATE TABLE task_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    previous_status task_status,
    new_status task_status,
    previous_rank INTEGER,
    new_rank INTEGER,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Weekly OKRs table (Current week operational data - approved only)
CREATE TABLE weekly_okrs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    objective_text TEXT NOT NULL,
    key_results TEXT NOT NULL,
    week_start_date DATE NOT NULL,
    approval_status approval_status DEFAULT 'approved',
    approved_at TIMESTAMP WITH TIME ZONE,
    auto_approved BOOLEAN DEFAULT FALSE,
    memory_id TEXT, -- Reference to OpenMemory for objective context
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Draft weekly OKRs table (Staging area for weekly planning)
CREATE TABLE draft_weekly_okrs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    objective_text TEXT NOT NULL,
    key_results TEXT NOT NULL,
    week_start_date DATE NOT NULL,
    generation_context JSONB, -- Store AI generation metadata
    memory_id TEXT, -- Reference to OpenMemory for objective context
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. LLM usage table (Cost monitoring)
CREATE TABLE llm_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    model TEXT NOT NULL,
    cost_estimate DECIMAL(10,4),
    memory_context_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Structured context table (Static context storage)
CREATE TABLE structured_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    context_type TEXT NOT NULL CHECK (context_type IN ('business_overview', 'current_situation', 'strategic_context', 'operational_context')),
    raw_content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_rank ON tasks(rank);

CREATE INDEX idx_draft_tasks_user_id ON draft_tasks(user_id);
CREATE INDEX idx_draft_tasks_due_date ON draft_tasks(due_date);

CREATE INDEX idx_task_logs_user_id ON task_logs(user_id);
CREATE INDEX idx_task_logs_task_id ON task_logs(task_id);
CREATE INDEX idx_task_logs_changed_at ON task_logs(changed_at);

CREATE INDEX idx_weekly_okrs_user_id ON weekly_okrs(user_id);
CREATE INDEX idx_weekly_okrs_week_start_date ON weekly_okrs(week_start_date);
CREATE INDEX idx_weekly_okrs_approval_status ON weekly_okrs(approval_status);

CREATE INDEX idx_draft_weekly_okrs_user_id ON draft_weekly_okrs(user_id);
CREATE INDEX idx_draft_weekly_okrs_week_start_date ON draft_weekly_okrs(week_start_date);

CREATE INDEX idx_llm_usage_user_id ON llm_usage(user_id);
CREATE INDEX idx_llm_usage_created_at ON llm_usage(created_at);

CREATE INDEX idx_structured_context_user_id ON structured_context(user_id);
CREATE INDEX idx_structured_context_type ON structured_context(context_type);
CREATE INDEX idx_structured_context_user_type ON structured_context(user_id, context_type);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add updated_at triggers
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_draft_tasks_updated_at
    BEFORE UPDATE ON draft_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_structured_context_updated_at
    BEFORE UPDATE ON structured_context
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE draft_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_okrs ENABLE ROW LEVEL SECURITY;
ALTER TABLE draft_weekly_okrs ENABLE ROW LEVEL SECURITY;
ALTER TABLE llm_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE structured_context ENABLE ROW LEVEL SECURITY;

-- Add foreign key constraints after tables are created
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_okr_id FOREIGN KEY (okr_id) REFERENCES weekly_okrs(id) ON DELETE SET NULL;
ALTER TABLE draft_tasks ADD CONSTRAINT fk_draft_tasks_okr_id FOREIGN KEY (okr_id) REFERENCES weekly_okrs(id) ON DELETE SET NULL;

-- Create RLS policies
-- Tasks policies
CREATE POLICY "Users can view own tasks" ON tasks
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own tasks" ON tasks
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own tasks" ON tasks
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own tasks" ON tasks
    FOR DELETE USING (auth.uid() = user_id);

-- Draft tasks policies
CREATE POLICY "Users can view own draft tasks" ON draft_tasks
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own draft tasks" ON draft_tasks
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own draft tasks" ON draft_tasks
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own draft tasks" ON draft_tasks
    FOR DELETE USING (auth.uid() = user_id);

-- Task logs policies
CREATE POLICY "Users can view own task logs" ON task_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own task logs" ON task_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Weekly OKRs policies
CREATE POLICY "Users can view own weekly okrs" ON weekly_okrs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own weekly okrs" ON weekly_okrs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own weekly okrs" ON weekly_okrs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own weekly okrs" ON weekly_okrs
    FOR DELETE USING (auth.uid() = user_id);

-- Draft weekly OKRs policies
CREATE POLICY "Users can view own draft weekly okrs" ON draft_weekly_okrs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own draft weekly okrs" ON draft_weekly_okrs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own draft weekly okrs" ON draft_weekly_okrs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own draft weekly okrs" ON draft_weekly_okrs
    FOR DELETE USING (auth.uid() = user_id);

-- LLM usage policies
CREATE POLICY "Users can view own llm usage" ON llm_usage
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own llm usage" ON llm_usage
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Structured context policies
CREATE POLICY "Users can view own structured context" ON structured_context
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own structured context" ON structured_context
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own structured context" ON structured_context
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own structured context" ON structured_context
    FOR DELETE USING (auth.uid() = user_id);

-- Create functions for scheduled jobs
CREATE OR REPLACE FUNCTION get_users_for_daily_brief()
RETURNS TABLE(user_id UUID, timezone TEXT) AS $$
BEGIN
    -- This function would return active users who need daily briefs
    -- For now, return all users with tasks
    RETURN QUERY
    SELECT DISTINCT t.user_id, 'UTC' as timezone
    FROM tasks t
    WHERE t.created_at > NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_draft_okrs_for_auto_approval()
RETURNS TABLE(
    okr_id UUID,
    user_id UUID,
    objective_text TEXT,
    key_results TEXT,
    week_start_date DATE,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    -- Return draft OKRs older than 24 hours for auto-approval
    RETURN QUERY
    SELECT 
        d.id,
        d.user_id,
        d.objective_text,
        d.key_results,
        d.week_start_date,
        d.created_at
    FROM draft_weekly_okrs d
    WHERE d.created_at < NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql;