"""
SQLAlchemy ORM Models for Talentshire Database Schema
=====================================================

These models map directly to the PostgreSQL schema shown in the database diagram.
All tables, relationships, and constraints are defined here.
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime,
    ForeignKey, Enum, JSON, UniqueConstraint, Index, CheckConstraint,
    TIMESTAMP
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
import enum

Base = declarative_base()

# ============================================================================
# ENUMS (matching Pydantic enums)
# ============================================================================

class LanguageEnum(str, enum.Enum):
    python = "Python"
    java = "Java"
    sql = "SQL"
    pyspark = "PySpark"
    javascript = "JavaScript"
    cpp = "C++"
    csharp = "C#"


class DifficultyEnum(str, enum.Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"


class TestStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    completed = "completed"
    draft = "draft"
    published = "published"


class QuestionTypeEnum(str, enum.Enum):
    multiple_choice = "multiple_choice"
    coding = "coding"
    true_false = "true_false"
    unified = "unified"


class AssignmentStatusEnum(str, enum.Enum):
    pending = "pending"
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    expired = "expired"


class CodeExecutionStatusEnum(str, enum.Enum):
    pending = "pending"
    success = "success"
    error = "error"
    timeout = "timeout"
    compilation_error = "compilation_error"
    runtime_error = "runtime_error"


class RoleEnum(str, enum.Enum):
    admin = "admin"
    candidate = "candidate"
    reviewer = "reviewer"
    super_admin = "super_admin"


# ============================================================================
# USER MANAGEMENT TABLES
# ============================================================================

class User(Base):
    """Users table - stores all user accounts"""
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.candidate)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tests = relationship("Test", back_populates="creator")
    assignments = relationship("TestAssignment", back_populates="candidate")
    test_answers = relationship("TestAnswer", back_populates="candidate")
    submissions = relationship("CodeSubmission", back_populates="candidate")
    reports = relationship("CandidateReport", back_populates="candidate")


class CandidateProfile(Base):
    """Extended candidate information"""
    __tablename__ = "candidate_profiles"
    
    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    resume_url = Column(String(512), nullable=True)
    skills = Column(ARRAY(String), default=[])
    experience_years = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# TEST & QUESTION TABLES
# ============================================================================

class Test(Base):
    """Tests table - stores test configurations"""
    __tablename__ = "tests"
    
    test_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_name = Column(String(255), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(Enum(TestStatusEnum), default=TestStatusEnum.draft)
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=[])
    total_marks = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_created_by', 'created_by'),
        Index('idx_test_status', 'status'),
    )
    
    # Relationships
    creator = relationship("User", back_populates="tests")
    questions = relationship("TestQuestion", back_populates="test", cascade="all, delete-orphan")
    assignments = relationship("TestAssignment", back_populates="test", cascade="all, delete-orphan")
    answers = relationship("TestAnswer", back_populates="test")
    reports = relationship("CandidateReport", back_populates="test")


class MCQQuestion(Base):
    """MCQ Questions table (from Mukesh's service)"""
    __tablename__ = "mcq_questions"
    
    question_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)  # A, B, C, D
    difficulty = Column(Enum(DifficultyEnum), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    explanation = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=[])
    marks = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_mcq_difficulty', 'difficulty'),
        Index('idx_mcq_language', 'language'),
        CheckConstraint("correct_answer IN ('A', 'B', 'C', 'D')"),
    )
    
    # Relationships
    test_questions = relationship("TestQuestion", back_populates="mcq_question")


class CodingQuestion(Base):
    """Coding Problems table (from Satyam's service)"""
    __tablename__ = "coding_questions"
    
    question_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyEnum), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    sample_input = Column(Text, nullable=True)
    sample_output = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    test_cases = Column(JSON, default=[])  # Array of {input, output, hidden}
    labels = Column(ARRAY(String), default=[])
    time_limit_seconds = Column(Integer, default=5)
    memory_limit_mb = Column(Integer, default=256)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_coding_difficulty', 'difficulty'),
        Index('idx_coding_language', 'language'),
    )
    
    # Relationships
    test_questions = relationship("TestQuestion", back_populates="coding_question")
    submissions = relationship("CodeSubmission", back_populates="problem")


class TestQuestion(Base):
    """Questions in a test (many-to-many with ordering)"""
    __tablename__ = "test_questions"
    
    test_question_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.test_id"), nullable=False)
    question_type = Column(Enum(QuestionTypeEnum), nullable=False)
    question_id = Column(UUID(as_uuid=True), nullable=False)  # Can be MCQ or Coding
    order_index = Column(Integer, nullable=False)
    marks = Column(Integer, default=1)
    time_limit_seconds = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('test_id', 'order_index', name='uq_test_question_order'),
        Index('idx_test_id', 'test_id'),
    )
    
    # Relationships
    test = relationship("Test", back_populates="questions")
    mcq_question = relationship("MCQQuestion", back_populates="test_questions", 
                               foreign_keys=[question_id],
                               primaryjoin="and_(TestQuestion.question_id==MCQQuestion.question_id, "
                                          "TestQuestion.question_type=='multiple_choice')",
                               viewonly=True)
    coding_question = relationship("CodingQuestion", back_populates="test_questions",
                                  foreign_keys=[question_id],
                                  primaryjoin="and_(TestQuestion.question_id==CodingQuestion.question_id, "
                                             "TestQuestion.question_type=='coding')",
                                  viewonly=True)


# ============================================================================
# TEST ASSIGNMENT & ANSWERS TABLES
# ============================================================================

class TestAssignment(Base):
    """Test assignments - maps tests to candidates"""
    __tablename__ = "test_assignments"
    
    assignment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.test_id"), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    status = Column(Enum(AssignmentStatusEnum), default=AssignmentStatusEnum.pending)
    scheduled_start_time = Column(TIMESTAMP, nullable=True)
    scheduled_end_time = Column(TIMESTAMP, nullable=True)
    max_attempts = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    started_at = Column(TIMESTAMP, nullable=True)
    submitted_at = Column(TIMESTAMP, nullable=True)
    score = Column(Float, nullable=True)
    
    __table_args__ = (
        Index('idx_candidate_id', 'candidate_id'),
        Index('idx_assignment_status', 'status'),
        UniqueConstraint('test_id', 'candidate_id', name='uq_test_candidate'),
    )
    
    # Relationships
    test = relationship("Test", back_populates="assignments")
    candidate = relationship("User", back_populates="assignments")
    answers = relationship("TestAnswer", back_populates="assignment", cascade="all, delete-orphan")


class TestAnswer(Base):
    """Candidate answers to test questions"""
    __tablename__ = "test_answers"
    
    answer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("test_assignments.assignment_id"), nullable=False)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.test_id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), nullable=False)  # Can be MCQ or Coding
    question_type = Column(Enum(QuestionTypeEnum), nullable=False)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    
    # MCQ Fields
    selected_option = Column(String(1), nullable=True)  # A, B, C, D
    is_correct_mcq = Column(Boolean, nullable=True)
    
    # Coding Fields
    code_submission_id = Column(UUID(as_uuid=True), ForeignKey("code_submissions.submission_id"), nullable=True)
    code = Column(Text, nullable=True)
    language = Column(Enum(LanguageEnum), nullable=True)
    code_status = Column(Enum(CodeExecutionStatusEnum), default=CodeExecutionStatusEnum.pending)
    code_output = Column(Text, nullable=True)
    code_passed = Column(Boolean, default=False)
    
    # Scoring
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=1.0)
    time_spent_seconds = Column(Integer, default=0)
    
    # AI Analysis (from Anjali's code-analyzer service)
    ai_analysis = Column(Text, nullable=True)
    ai_review_notes = Column(Text, nullable=True)
    code_quality_score = Column(Float, nullable=True)
    
    submitted_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_assignment_id', 'assignment_id'),
        Index('idx_candidate_id', 'candidate_id'),
        Index('idx_answer_status', 'code_status'),
    )
    
    # Relationships
    assignment = relationship("TestAssignment", back_populates="answers")
    test = relationship("Test", back_populates="answers")
    candidate = relationship("User", back_populates="test_answers")
    code_submission = relationship("CodeSubmission", back_populates="test_answer")


# ============================================================================
# CODE SUBMISSION & EXECUTION TABLES (Satyam)
# ============================================================================

class CodeSubmission(Base):
    """Code submissions from candidates"""
    __tablename__ = "code_submissions"
    
    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("coding_questions.question_id"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    code = Column(Text, nullable=False)
    stdin = Column(Text, default="")
    status = Column(Enum(CodeExecutionStatusEnum), default=CodeExecutionStatusEnum.pending)
    stdout = Column(Text, default="")
    stderr = Column(Text, default="")
    output = Column(Text, default="")
    expected_output = Column(Text, default="")
    is_passed = Column(Boolean, default=False)
    passed_test_cases = Column(Integer, default=0)
    total_test_cases = Column(Integer, default=0)
    execution_time_ms = Column(Float, nullable=True)
    memory_used_mb = Column(Float, nullable=True)
    submitted_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_candidate_id', 'candidate_id'),
        Index('idx_problem_id', 'problem_id'),
        Index('idx_submission_status', 'status'),
    )
    
    # Relationships
    candidate = relationship("User", back_populates="submissions")
    problem = relationship("CodingQuestion", back_populates="submissions")
    test_answer = relationship("TestAnswer", back_populates="code_submission")


class CodeDraft(Base):
    """Auto-saved code drafts (session recovery)"""
    __tablename__ = "code_drafts"
    
    draft_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("coding_questions.question_id"), nullable=False)
    language = Column(Enum(LanguageEnum), nullable=False)
    code = Column(Text, nullable=False)
    cursor_position = Column(Integer, default=0)
    session_id = Column(String(255), nullable=True)
    last_saved_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_candidate_session', 'candidate_id', 'session_id'),
    )


# ============================================================================
# REPORT TABLES (Swarang)
# ============================================================================

class CandidateReport(Base):
    """Test reports for candidates"""
    __tablename__ = "candidate_reports"
    
    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.test_id"), nullable=False)
    test_date = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Aggregate scores
    total_score = Column(Float, nullable=False)
    total_max = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    grade = Column(String(1), nullable=True)  # A, B, C, D, F
    
    # Section scores
    mcq_score = Column(Float, default=0.0)
    mcq_max = Column(Float, default=0.0)
    coding_score = Column(Float, default=0.0)
    coding_max = Column(Float, default=0.0)
    
    # Report details
    mcq_correct = Column(Integer, default=0)
    mcq_wrong = Column(Integer, default=0)
    mcq_skipped = Column(Integer, default=0)
    coding_passed = Column(Integer, default=0)
    coding_failed = Column(Integer, default=0)
    
    # Timing
    duration_seconds = Column(Integer, nullable=False)
    status = Column(String(50), default="completed")  # completed, in_progress
    
    # File storage
    pdf_url = Column(String(512), nullable=True)
    json_data = Column(JSON, nullable=True)  # Complete report as JSON
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_candidate_reports', 'candidate_id'),
        Index('idx_test_reports', 'test_id'),
    )
    
    # Relationships
    candidate = relationship("User", back_populates="reports")
    test = relationship("Test", back_populates="reports")


class ProctoringData(Base):
    """Proctoring metrics (optional)"""
    __tablename__ = "proctoring_data"
    
    proctoring_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("test_assignments.assignment_id"), nullable=False)
    flagged_faces = Column(Integer, default=0)
    focus_deviation_percent = Column(Float, default=0.0)
    cheating_events = Column(Integer, default=0)
    unusual_activity = Column(Text, default="None detected")
    frame_captures = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class ProctoringFrameCapture(Base):
    """Individual proctoring frame captures"""
    __tablename__ = "proctoring_frame_captures"
    
    capture_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("test_assignments.assignment_id"), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    frame_url = Column(String(512), nullable=True)
    face_detected = Column(Boolean, default=False)
    faces_count = Column(Integer, default=0)
    suspicious_activity = Column(Boolean, default=False)
    activity_type = Column(String(100), nullable=True)  # eye_movement, face_off_screen, multiple_faces
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# ============================================================================
# AI ANALYSIS TABLES (Anjali)
# ============================================================================

class CodeAnalysisResult(Base):
    """AI code analysis results from Gemini"""
    __tablename__ = "code_analysis_results"
    
    analysis_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("code_submissions.submission_id"), nullable=False, unique=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    
    # Scores
    total_score = Column(Integer, nullable=True)  # 0-100
    style_score = Column(Integer, nullable=True)  # 0-10
    maintainability_score = Column(Integer, nullable=True)  # 0-10
    complexity_score = Column(Integer, nullable=True)  # 0-10
    security_score = Column(Integer, nullable=True)  # 0-10
    
    # Analysis details
    improvements_suggested = Column(Text, nullable=True)
    detailed_analysis = Column(Text, nullable=True)
    code_review = Column(JSON, nullable=True)  # Full review structure
    
    # Complexity analysis
    time_complexity = Column(String(50), nullable=True)
    space_complexity = Column(String(50), nullable=True)
    
    # Error handling
    error = Column(String(255), nullable=True)
    
    analysis_timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_candidate_analysis', 'candidate_id'),
        Index('idx_submission_analysis', 'submission_id'),
    )


# ============================================================================
# SKILL EXTRACTION TABLES (Ishaan - NLP)
# ============================================================================

class SkillExtraction(Base):
    """Extracted skills from job descriptions"""
    __tablename__ = "skill_extractions"
    
    extraction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_description = Column(Text, nullable=False)
    extracted_skills = Column(ARRAY(String), nullable=False)
    skill_scores = Column(ARRAY(Float), nullable=True)
    extracted_at = Column(TIMESTAMP, default=datetime.utcnow)


class CandidateSkillMatch(Base):
    """Skill matching between candidates and jobs"""
    __tablename__ = "candidate_skill_matches"
    
    match_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    extraction_id = Column(UUID(as_uuid=True), ForeignKey("skill_extractions.extraction_id"), nullable=False)
    required_skills = Column(ARRAY(String), nullable=False)
    candidate_skills = Column(ARRAY(String), nullable=False)
    matched_skills = Column(ARRAY(String), nullable=False)
    missing_skills = Column(ARRAY(String), nullable=False)
    match_percentage = Column(Float, nullable=False)
    skill_gap_analysis = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# ============================================================================
# AUDIT & LOGGING TABLES
# ============================================================================

class AuditLog(Base):
    """Audit trail for important actions"""
    __tablename__ = "audit_logs"
    
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    action = Column(String(255), nullable=False)
    entity_type = Column(String(100), nullable=False)  # test, submission, report, etc.
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_user_actions', 'user_id'),
        Index('idx_entity_actions', 'entity_type', 'entity_id'),
    )
