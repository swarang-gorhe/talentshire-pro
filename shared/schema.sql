-- ============================================================================
-- Talentshire Complete Database Schema
-- ============================================================================
-- PostgreSQL DDL for all tables with proper constraints, indexes, and relationships
-- Generated from SQLAlchemy models in shared/database_models.py

-- Enable UUID support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE user_role AS ENUM ('admin', 'candidate', 'reviewer', 'super_admin');
CREATE TYPE test_status AS ENUM ('active', 'inactive', 'completed', 'draft', 'published');
CREATE TYPE question_type AS ENUM ('multiple_choice', 'coding', 'true_false', 'unified');
CREATE TYPE assignment_status AS ENUM ('pending', 'scheduled', 'in_progress', 'completed', 'expired');
CREATE TYPE code_execution_status AS ENUM ('pending', 'success', 'error', 'timeout', 'compilation_error', 'runtime_error');
CREATE TYPE language AS ENUM ('Python', 'Java', 'SQL', 'PySpark', 'JavaScript', 'C++', 'C#');
CREATE TYPE difficulty AS ENUM ('Easy', 'Medium', 'Hard');

-- ============================================================================
-- USER MANAGEMENT TABLES
-- ============================================================================

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'candidate',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

CREATE TABLE candidate_profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    phone VARCHAR(20),
    resume_url VARCHAR(512),
    skills TEXT[] DEFAULT '{}',
    experience_years INTEGER,
    bio TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TEST & QUESTION TABLES
-- ============================================================================

CREATE TABLE tests (
    test_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_name VARCHAR(255) NOT NULL,
    created_by UUID NOT NULL REFERENCES users(user_id),
    duration_minutes INTEGER NOT NULL,
    status test_status NOT NULL DEFAULT 'draft',
    description TEXT,
    tags TEXT[] DEFAULT '{}',
    total_marks INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tests_created_by ON tests(created_by);
CREATE INDEX idx_tests_status ON tests(status);

CREATE TABLE mcq_questions (
    question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer VARCHAR(1) NOT NULL CHECK (correct_answer IN ('A', 'B', 'C', 'D')),
    difficulty difficulty NOT NULL,
    language language NOT NULL,
    explanation TEXT,
    tags TEXT[] DEFAULT '{}',
    marks INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mcq_difficulty ON mcq_questions(difficulty);
CREATE INDEX idx_mcq_language ON mcq_questions(language);

CREATE TABLE coding_questions (
    question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    difficulty difficulty NOT NULL,
    language language NOT NULL,
    sample_input TEXT,
    sample_output TEXT,
    constraints TEXT,
    test_cases JSONB DEFAULT '[]'::jsonb,
    labels TEXT[] DEFAULT '{}',
    time_limit_seconds INTEGER DEFAULT 5,
    memory_limit_mb INTEGER DEFAULT 256,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coding_difficulty ON coding_questions(difficulty);
CREATE INDEX idx_coding_language ON coding_questions(language);

CREATE TABLE test_questions (
    test_question_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id UUID NOT NULL REFERENCES tests(test_id) ON DELETE CASCADE,
    question_type question_type NOT NULL,
    question_id UUID NOT NULL,
    order_index INTEGER NOT NULL,
    marks INTEGER DEFAULT 1,
    time_limit_seconds INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_id, order_index)
);

CREATE INDEX idx_test_questions_test_id ON test_questions(test_id);

-- ============================================================================
-- TEST ASSIGNMENT & ANSWERS TABLES
-- ============================================================================

CREATE TABLE test_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id UUID NOT NULL REFERENCES tests(test_id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    status assignment_status NOT NULL DEFAULT 'pending',
    scheduled_start_time TIMESTAMP,
    scheduled_end_time TIMESTAMP,
    max_attempts INTEGER DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    submitted_at TIMESTAMP,
    score FLOAT,
    UNIQUE(test_id, candidate_id)
);

CREATE INDEX idx_assignments_candidate ON test_assignments(candidate_id);
CREATE INDEX idx_assignments_status ON test_assignments(status);
CREATE INDEX idx_assignments_test ON test_assignments(test_id);

CREATE TABLE test_answers (
    answer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES test_assignments(assignment_id) ON DELETE CASCADE,
    test_id UUID NOT NULL REFERENCES tests(test_id) ON DELETE CASCADE,
    question_id UUID NOT NULL,
    question_type question_type NOT NULL,
    candidate_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- MCQ Fields
    selected_option VARCHAR(1) CHECK (selected_option IS NULL OR selected_option IN ('A', 'B', 'C', 'D')),
    is_correct_mcq BOOLEAN,
    
    -- Coding Fields
    code_submission_id UUID,
    code TEXT,
    language language,
    code_status code_execution_status DEFAULT 'pending',
    code_output TEXT,
    code_passed BOOLEAN DEFAULT FALSE,
    
    -- Scoring
    score FLOAT DEFAULT 0.0,
    max_score FLOAT DEFAULT 1.0,
    time_spent_seconds INTEGER DEFAULT 0,
    
    -- AI Analysis
    ai_analysis TEXT,
    ai_review_notes TEXT,
    code_quality_score FLOAT,
    
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_answers_assignment ON test_answers(assignment_id);
CREATE INDEX idx_answers_candidate ON test_answers(candidate_id);
CREATE INDEX idx_answers_status ON test_answers(code_status);

-- ============================================================================
-- CODE SUBMISSION & EXECUTION TABLES
-- ============================================================================

CREATE TABLE code_submissions (
    submission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    problem_id UUID NOT NULL REFERENCES coding_questions(question_id) ON DELETE CASCADE,
    language language NOT NULL,
    code TEXT NOT NULL,
    stdin TEXT DEFAULT '',
    status code_execution_status NOT NULL DEFAULT 'pending',
    stdout TEXT DEFAULT '',
    stderr TEXT DEFAULT '',
    output TEXT DEFAULT '',
    expected_output TEXT DEFAULT '',
    is_passed BOOLEAN DEFAULT FALSE,
    passed_test_cases INTEGER DEFAULT 0,
    total_test_cases INTEGER DEFAULT 0,
    execution_time_ms FLOAT,
    memory_used_mb FLOAT,
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_submissions_candidate ON code_submissions(candidate_id);
CREATE INDEX idx_submissions_problem ON code_submissions(problem_id);
CREATE INDEX idx_submissions_status ON code_submissions(status);

CREATE TABLE code_drafts (
    draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    problem_id UUID NOT NULL REFERENCES coding_questions(question_id) ON DELETE CASCADE,
    language language NOT NULL,
    code TEXT NOT NULL,
    cursor_position INTEGER DEFAULT 0,
    session_id VARCHAR(255),
    last_saved_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_drafts_candidate_session ON code_drafts(candidate_id, session_id);

-- ============================================================================
-- REPORT TABLES
-- ============================================================================

CREATE TABLE candidate_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    test_id UUID NOT NULL REFERENCES tests(test_id) ON DELETE CASCADE,
    test_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Aggregate scores
    total_score FLOAT NOT NULL,
    total_max FLOAT NOT NULL,
    percentage FLOAT NOT NULL,
    grade VARCHAR(1),
    
    -- Section scores
    mcq_score FLOAT DEFAULT 0.0,
    mcq_max FLOAT DEFAULT 0.0,
    coding_score FLOAT DEFAULT 0.0,
    coding_max FLOAT DEFAULT 0.0,
    
    -- Answer counts
    mcq_correct INTEGER DEFAULT 0,
    mcq_wrong INTEGER DEFAULT 0,
    mcq_skipped INTEGER DEFAULT 0,
    coding_passed INTEGER DEFAULT 0,
    coding_failed INTEGER DEFAULT 0,
    
    -- Timing
    duration_seconds INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'completed',
    
    -- File storage
    pdf_url VARCHAR(512),
    json_data JSONB,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_candidate ON candidate_reports(candidate_id);
CREATE INDEX idx_reports_test ON candidate_reports(test_id);

CREATE TABLE proctoring_data (
    proctoring_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES test_assignments(assignment_id) ON DELETE CASCADE,
    flagged_faces INTEGER DEFAULT 0,
    focus_deviation_percent FLOAT DEFAULT 0.0,
    cheating_events INTEGER DEFAULT 0,
    unusual_activity TEXT DEFAULT 'None detected',
    frame_captures INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE proctoring_frame_captures (
    capture_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES test_assignments(assignment_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL,
    frame_url VARCHAR(512),
    face_detected BOOLEAN DEFAULT FALSE,
    faces_count INTEGER DEFAULT 0,
    suspicious_activity BOOLEAN DEFAULT FALSE,
    activity_type VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AI ANALYSIS TABLES
-- ============================================================================

CREATE TABLE code_analysis_results (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID NOT NULL UNIQUE REFERENCES code_submissions(submission_id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Scores
    total_score INTEGER,
    style_score INTEGER,
    maintainability_score INTEGER,
    complexity_score INTEGER,
    security_score INTEGER,
    
    -- Analysis details
    improvements_suggested TEXT,
    detailed_analysis TEXT,
    code_review JSONB,
    
    -- Complexity analysis
    time_complexity VARCHAR(50),
    space_complexity VARCHAR(50),
    
    -- Error handling
    error VARCHAR(255),
    
    analysis_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analysis_candidate ON code_analysis_results(candidate_id);
CREATE INDEX idx_analysis_submission ON code_analysis_results(submission_id);

-- ============================================================================
-- SKILL EXTRACTION TABLES
-- ============================================================================

CREATE TABLE skill_extractions (
    extraction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_description TEXT NOT NULL,
    extracted_skills TEXT[] NOT NULL,
    skill_scores FLOAT[],
    extracted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE candidate_skill_matches (
    match_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    extraction_id UUID NOT NULL REFERENCES skill_extractions(extraction_id) ON DELETE CASCADE,
    required_skills TEXT[] NOT NULL,
    candidate_skills TEXT[] NOT NULL,
    matched_skills TEXT[] NOT NULL,
    missing_skills TEXT[] NOT NULL,
    match_percentage FLOAT NOT NULL,
    skill_gap_analysis TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AUDIT & LOGGING TABLES
-- ============================================================================

CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_user ON audit_logs(user_id);
CREATE INDEX idx_logs_entity ON audit_logs(entity_type, entity_id);

-- ============================================================================
-- FOREIGN KEY CONSTRAINTS FOR test_answers.code_submission_id
-- ============================================================================

ALTER TABLE test_answers
ADD CONSTRAINT fk_answers_submission 
FOREIGN KEY (code_submission_id) 
REFERENCES code_submissions(submission_id) 
ON DELETE SET NULL;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Test performance summary
CREATE VIEW test_performance_summary AS
SELECT 
    t.test_id,
    t.test_name,
    COUNT(DISTINCT ta.candidate_id) as total_candidates,
    AVG(CASE WHEN ta.status = 'completed' THEN ta.score ELSE NULL END) as avg_score,
    COUNT(DISTINCT CASE WHEN ta.status = 'completed' THEN ta.candidate_id END) as completed_count
FROM tests t
LEFT JOIN test_assignments ta ON t.test_id = ta.test_id
GROUP BY t.test_id, t.test_name;

-- View: Candidate assessment summary
CREATE VIEW candidate_assessment_summary AS
SELECT 
    u.user_id,
    u.full_name,
    u.email,
    COUNT(DISTINCT ta.assignment_id) as tests_taken,
    COUNT(DISTINCT CASE WHEN ta.status = 'completed' THEN ta.assignment_id END) as tests_completed,
    AVG(CASE WHEN cr.report_id IS NOT NULL THEN cr.percentage ELSE NULL END) as avg_percentage
FROM users u
LEFT JOIN test_assignments ta ON u.user_id = ta.candidate_id
LEFT JOIN candidate_reports cr ON ta.assignment_id = cr.report_id
WHERE u.role = 'candidate'
GROUP BY u.user_id, u.full_name, u.email;

-- ============================================================================
-- SAMPLE DATA INSERTION (Optional)
-- ============================================================================

-- Create admin user
INSERT INTO users (email, password_hash, full_name, role)
VALUES ('admin@talentshire.com', 'hashed_password_here', 'Admin User', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Create MCQ question
INSERT INTO mcq_questions (
    question_text, option_a, option_b, option_c, option_d,
    correct_answer, difficulty, language, marks
) VALUES (
    'What is 2+2?',
    '3', '4', '5', '6',
    'B', 'Easy', 'Python', 1
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX idx_assignments_candidate_status ON test_assignments(candidate_id, status);
CREATE INDEX idx_answers_assignment_type ON test_answers(assignment_id, question_type);
CREATE INDEX idx_submissions_candidate_status ON code_submissions(candidate_id, status);

-- For pagination and sorting
CREATE INDEX idx_tests_created_at ON tests(created_at DESC);
CREATE INDEX idx_reports_created_at ON candidate_reports(created_at DESC);
CREATE INDEX idx_answers_submitted_at ON test_answers(submitted_at DESC);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
