"""
Unified Data Models for Talentshire Platform
============================================

This module consolidates all Pydantic models and database schemas across:
- Code Analyzer Service (Anjali)
- Submission Service (Satyam)
- Test Management Service (Ishaan)
- Report Dashboard (Swarang)
- Filter Service (Mukesh)

All models are interconnected with proper relationships and mappings.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid

# ============================================================================
# SHARED ENUMS (Single Source of Truth)
# ============================================================================

class LanguageEnum(str, Enum):
    """Programming languages supported across platform"""
    python = "Python"
    java = "Java"
    sql = "SQL"
    pyspark = "PySpark"
    javascript = "JavaScript"
    cpp = "C++"
    csharp = "C#"


class DifficultyEnum(str, Enum):
    """Question difficulty levels"""
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"


class TestStatusEnum(str, Enum):
    """Test lifecycle statuses"""
    active = "active"
    inactive = "inactive"
    completed = "completed"
    draft = "draft"
    published = "published"


class QuestionTypeEnum(str, Enum):
    """Types of questions in a test"""
    multiple_choice = "multiple_choice"
    coding = "coding"
    true_false = "true_false"
    unified = "unified"  # MCQ + Coding combined


class AssignmentStatusEnum(str, Enum):
    """Test assignment statuses"""
    pending = "pending"
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    expired = "expired"


class CodeExecutionStatusEnum(str, Enum):
    """Code execution result statuses"""
    pending = "pending"
    success = "success"
    error = "error"
    timeout = "timeout"
    compilation_error = "compilation_error"
    runtime_error = "runtime_error"


# ============================================================================
# USER & CANDIDATE MODELS
# ============================================================================

class UserBase(BaseModel):
    """Base user information"""
    user_id: uuid.UUID
    email: str
    full_name: str
    role: str  # admin, candidate, reviewer


class CandidateProfile(UserBase):
    """Candidate-specific profile"""
    candidate_id: uuid.UUID = Field(alias="user_id")
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    skills: List[str] = []
    experience_years: Optional[int] = None
    
    class Config:
        orm_mode = True


# ============================================================================
# TEST & QUESTION MODELS (Test Management - Ishaan)
# ============================================================================

class MCQOption(BaseModel):
    """Single MCQ option"""
    option_id: uuid.UUID
    option_text: str
    option_key: str  # A, B, C, D
    is_correct: bool


class MCQQuestion(BaseModel):
    """Multiple Choice Question from Mukesh's service"""
    question_id: uuid.UUID
    question_text: str
    options: List[MCQOption]
    difficulty: DifficultyEnum
    language: LanguageEnum
    correct_answer: str  # A, B, C, D
    explanation: Optional[str] = None
    tags: List[str] = []
    marks: int = 1
    
    class Config:
        orm_mode = True


class CodingProblem(BaseModel):
    """Coding problem definition (from Satyam's service)"""
    problem_id: uuid.UUID
    title: str
    description: str
    difficulty: DifficultyEnum
    language: LanguageEnum
    sample_input: str
    sample_output: str
    constraints: str
    test_cases: List[dict] = []  # [{"input": "", "output": "", "hidden": bool}]
    labels: List[str] = []
    time_limit_seconds: int = 5
    memory_limit_mb: int = 256
    
    class Config:
        orm_mode = True


class TestQuestion(BaseModel):
    """Question within a test"""
    test_question_id: uuid.UUID
    test_id: uuid.UUID
    question_id: uuid.UUID
    question_type: QuestionTypeEnum
    order_index: int
    marks: int = 1
    time_limit_seconds: Optional[int] = None
    
    class Config:
        orm_mode = True


class TestBase(BaseModel):
    """Base test information"""
    test_name: str
    duration_minutes: int
    status: TestStatusEnum
    description: Optional[str] = None
    tags: List[str] = []


class TestCreate(TestBase):
    """Create test request"""
    pass


class Test(TestBase):
    """Test entity with metadata"""
    test_id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    questions: List[TestQuestion] = []
    total_marks: int = 0
    
    class Config:
        orm_mode = True


# ============================================================================
# TEST ASSIGNMENT & CANDIDATE ANSWER MODELS
# ============================================================================

class TestAssignmentCreate(BaseModel):
    """Assign test to candidate"""
    test_id: uuid.UUID
    candidate_id: uuid.UUID
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    max_attempts: int = 1


class TestAssignment(TestAssignmentCreate):
    """Test assignment tracking"""
    assignment_id: uuid.UUID
    status: AssignmentStatusEnum
    created_at: datetime
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    score: Optional[float] = None
    
    class Config:
        orm_mode = True


class MCQAnswer(BaseModel):
    """Candidate's answer to an MCQ"""
    mcq_answer_id: uuid.UUID
    question_id: uuid.UUID
    selected_option: str  # A, B, C, D
    is_correct: bool
    score: float = 0.0
    time_spent_seconds: int = 0


class CodeSubmission(BaseModel):
    """Code submission (from Satyam's service)"""
    submission_id: uuid.UUID
    candidate_id: uuid.UUID
    problem_id: uuid.UUID
    language: LanguageEnum
    code: str
    stdin: str = ""
    status: CodeExecutionStatusEnum
    stdout: str = ""
    stderr: str = ""
    output: str = ""
    expected_output: str = ""
    is_passed: bool = False
    passed_test_cases: int = 0
    total_test_cases: int = 0
    execution_time_ms: Optional[float] = None
    memory_used_mb: Optional[float] = None
    submitted_at: datetime
    
    class Config:
        orm_mode = True


class TestAnswer(BaseModel):
    """Candidate's answer to a test question"""
    answer_id: uuid.UUID
    assignment_id: uuid.UUID
    test_id: uuid.UUID
    question_id: uuid.UUID
    question_type: QuestionTypeEnum
    
    # MCQ fields
    selected_option: Optional[str] = None
    is_correct_mcq: Optional[bool] = None
    
    # Coding fields
    code_submission_id: Optional[uuid.UUID] = None
    code: Optional[str] = None
    language: Optional[LanguageEnum] = None
    code_status: CodeExecutionStatusEnum = CodeExecutionStatusEnum.pending
    code_output: Optional[str] = None
    code_passed: bool = False
    
    # Scoring
    score: float = 0.0
    max_score: float = 1.0
    time_spent_seconds: int = 0
    
    # AI Analysis (from Anjali)
    ai_analysis: Optional[str] = None
    ai_review_notes: Optional[str] = None
    code_quality_score: Optional[float] = None
    
    submitted_at: datetime
    
    class Config:
        orm_mode = True


class TestResult(BaseModel):
    """Aggregated test results for candidate"""
    assignment_id: uuid.UUID
    test_id: uuid.UUID
    candidate_id: uuid.UUID
    total_score: float
    max_score: float
    percentage: float
    mcq_score: float
    mcq_max: float
    coding_score: float
    coding_max: float
    answers: List[TestAnswer]
    completed_at: datetime
    duration_seconds: int
    
    class Config:
        orm_mode = True


# ============================================================================
# CODE ANALYSIS MODELS (Anjali)
# ============================================================================

class CodeAnalysisStyle(BaseModel):
    """Style and readability analysis"""
    score: int  # 0-10
    findings: str
    suggestions: List[str] = []


class CodeAnalysisMaintainability(BaseModel):
    """Maintainability assessment"""
    score: int  # 0-10
    findings: str
    suggestions: List[str] = []


class CodeComplexityAnalysis(BaseModel):
    """Algorithm complexity analysis"""
    time_complexity: str  # e.g., "O(n)"
    space_complexity: str  # e.g., "O(1)"
    assessment: str


class CodeSecurityReview(BaseModel):
    """Security analysis"""
    vulnerabilities: str  # empty if none
    recommendations: str


class RefactoringSuggestion(BaseModel):
    """Single refactoring suggestion"""
    refactor_title: str
    reason: str
    example: str  # code example


class CodeReviewResult(BaseModel):
    """Comprehensive code review from AI"""
    style_and_readability: CodeAnalysisStyle
    maintainability: CodeAnalysisMaintainability
    complexity_analysis: CodeComplexityAnalysis
    security_review: CodeSecurityReview
    suggested_refactors: List[RefactoringSuggestion] = []


class Submission(BaseModel):
    """Input for code analysis (from Anjali)"""
    candidate_id: str
    question: str
    expected_output: str
    candidate_output: str
    candidate_code: str
    language: LanguageEnum = LanguageEnum.python
    
    class Config:
        json_schema_extra = {
            "examples": [{
                "candidate_id": "CAND_001",
                "question": "Sum integers from 1 to n",
                "expected_output": "55",
                "candidate_output": "55",
                "candidate_code": "def sum_n(n):\n    return sum(range(1, n+1))",
                "language": "Python"
            }]
        }


class AnalysisResult(BaseModel):
    """Output from code analysis (from Anjali)"""
    candidate_id: str
    submission_id: Optional[uuid.UUID] = None
    total_score: Optional[int] = None  # 0-100
    improvements_suggested: str
    detailed_analysis: str
    code_review: Optional[CodeReviewResult] = None
    error: Optional[str] = None
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True


# ============================================================================
# REPORT MODELS (Swarang)
# ============================================================================

class MCQReportSection(BaseModel):
    """MCQ section of test report"""
    max_marks: int
    marks_obtained: int
    correct: int
    wrong: int
    skipped: int
    questions: List[dict] = []  # Question details with answers


class CodingReportSection(BaseModel):
    """Coding section of test report"""
    max_marks: int
    marks_obtained: int
    output_ok: bool
    questions: List[dict] = []  # Problem details with results


class ProctoringData(BaseModel):
    """Proctoring metrics"""
    flagged_faces: int = 0
    focus_deviation_percent: float = 0.0
    cheating_events: int = 0
    unusual_activity: str = "None detected"


class CandidateReportData(BaseModel):
    """Complete test report for candidate"""
    report_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    candidate_id: uuid.UUID
    candidate_name: str
    candidate_email: str
    test_id: uuid.UUID
    test_name: str
    test_date: datetime
    duration_minutes: int
    
    # Sections
    mcq: MCQReportSection
    coding: CodingReportSection
    proctoring: Optional[ProctoringData] = None
    
    # Aggregate
    total_score: float
    total_max: float
    percentage: float
    grade: Optional[str] = None  # A, B, C, etc.
    status: str = "completed"  # completed, in_progress
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True


# ============================================================================
# FILTER & SEARCH MODELS (Mukesh)
# ============================================================================

class FilterRequest(BaseModel):
    """Filter MCQs by language and difficulty"""
    language: LanguageEnum
    difficulty: DifficultyEnum


class CodingFilterRequest(BaseModel):
    """Filter coding problems"""
    title: Optional[str] = None
    labels: Optional[List[str]] = None
    difficulty: Optional[DifficultyEnum] = None
    language: Optional[LanguageEnum] = None
    limit: int = 10
    offset: int = 0


class QuestionSearchRequest(BaseModel):
    """Search MCQ and coding questions"""
    query: str
    languages: List[LanguageEnum] = []
    difficulties: List[DifficultyEnum] = []
    question_types: List[QuestionTypeEnum] = []
    limit: int = 10
    offset: int = 0


class QuestionSearchResult(BaseModel):
    """Search result containing both MCQ and coding questions"""
    mcq_results: List[MCQQuestion]
    coding_results: List[CodingProblem]
    total_mcq: int
    total_coding: int


# ============================================================================
# SKILL EXTRACTION MODELS (Ishaan - NLP)
# ============================================================================

class SkillExtractionRequest(BaseModel):
    """Extract skills from job description"""
    job_description: str
    top_k: int = 10


class SkillExtractionResult(BaseModel):
    """Extracted skills with relevance"""
    skills: List[str]
    relevance_scores: List[float]
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class CandidateSkillMatch(BaseModel):
    """Skill match between candidate and job"""
    candidate_id: uuid.UUID
    required_skills: List[str]
    candidate_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    match_percentage: float
    skill_gap_analysis: str = ""


# ============================================================================
# DRAFT & SESSION MODELS (Satyam)
# ============================================================================

class CodeDraft(BaseModel):
    """Auto-saved code draft"""
    draft_id: uuid.UUID
    candidate_id: uuid.UUID
    problem_id: uuid.UUID
    language: LanguageEnum
    code: str
    cursor_position: int = 0
    last_saved_at: datetime
    session_id: str = ""
    
    class Config:
        orm_mode = True


class ProctoringFrameCapture(BaseModel):
    """Proctoring frame data"""
    capture_id: uuid.UUID
    assignment_id: uuid.UUID
    timestamp: datetime
    frame_url: Optional[str] = None
    face_detected: bool
    faces_count: int = 0
    suspicious_activity: bool = False
    activity_type: Optional[str] = None


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[dict] = None


class PaginatedResponse(BaseModel):
    """Paginated list response"""
    items: List[dict]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# UTILITY FUNCTIONS FOR MODEL CONVERSION
# ============================================================================

def convert_submission_to_test_answer(
    submission: Submission,
    assignment_id: uuid.UUID,
    test_id: uuid.UUID,
    problem_id: uuid.UUID
) -> TestAnswer:
    """Convert CodeSubmission to TestAnswer for storage"""
    return TestAnswer(
        answer_id=uuid.uuid4(),
        assignment_id=assignment_id,
        test_id=test_id,
        question_id=problem_id,
        question_type=QuestionTypeEnum.coding,
        code=submission.candidate_code,
        language=submission.language,
        code_status=CodeExecutionStatusEnum.pending,
        submitted_at=datetime.utcnow()
    )


def convert_analysis_to_test_answer_score(
    analysis: AnalysisResult,
    test_answer: TestAnswer
) -> TestAnswer:
    """Enrich TestAnswer with analysis results"""
    test_answer.ai_analysis = analysis.detailed_analysis
    test_answer.ai_review_notes = analysis.improvements_suggested
    test_answer.code_quality_score = analysis.total_score
    return test_answer


def convert_code_submission_to_model(
    submission: CodeSubmission,
    assignment_id: uuid.UUID,
    test_id: uuid.UUID
) -> TestAnswer:
    """Convert CodeSubmission to TestAnswer"""
    return TestAnswer(
        answer_id=uuid.uuid4(),
        assignment_id=assignment_id,
        test_id=test_id,
        question_id=submission.problem_id,
        question_type=QuestionTypeEnum.coding,
        code_submission_id=submission.submission_id,
        code=submission.code,
        language=submission.language,
        code_status=submission.status,
        code_output=submission.output,
        code_passed=submission.is_passed,
        score=submission.passed_test_cases * (1.0 / submission.total_test_cases) if submission.total_test_cases > 0 else 0,
        submitted_at=submission.submitted_at
    )
