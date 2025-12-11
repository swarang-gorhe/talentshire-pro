"""
TALENTSHIRE - COMPLETE MODEL INTEGRATION ARCHITECTURE
=====================================================

ASCII Diagrams and Visual Representations
"""

# ============================================================================
# 1. SYSTEM ARCHITECTURE
# ============================================================================

SYSTEM_OVERVIEW = """
┌────────────────────────────────────────────────────────────────────────┐
│                     TALENTSHIRE PLATFORM                              │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                 │
│  │   FRONTEND   │  │   BACKEND    │  │  SERVICES    │                 │
│  │   (React)    │  │  (FastAPI)   │  │  (Microsvcs) │                 │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                 │
│         │                  │                 │                         │
│         └──────────────────┼─────────────────┘                         │
│                            │                                           │
│                   ┌────────▼────────┐                                  │
│                   │  SHARED MODELS  │◄──────┐                          │
│                   ├─────────────────┤       │                          │
│                   │ • models.py     │       │                          │
│                   │ • db_models.py  │       │                          │
│                   │ • converters.py │       │                          │
│                   │ • documentation │       │                          │
│                   └────────┬────────┘       │                          │
│                            │                │                          │
│         ┌──────────────────┼────────────────┘                          │
│         │                  │                                           │
│    ┌────▼────┐        ┌────▼─────┐                                     │
│    │ Pydantic│        │ SQLAlchemy                                     │
│    │ (APIs)  │        │ (Database)│                                    │
│    └────┬────┘        └────┬─────┘                                     │
│         │                  │                                           │
│         └──────────┬───────┘                                           │
│                    │                                                   │
│              ┌─────▼─────┐                                             │
│              │ PostgreSQL │                                            │
│              │  Database  │                                            │
│              │ (20 tables)│                                            │
│              └────────────┘                                            │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# 2. MODEL RELATIONSHIPS DIAGRAM
# ============================================================================

MODEL_RELATIONSHIPS = """
                                    ┌──────────────────┐
                                    │      User        │
                                    │ (admin/candidate)│
                                    └────────┬─────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
            ┌──────────────┐         ┌────────────────┐      ┌──────────────┐
            │    Test      │         │ TestAssignment │      │ CandidateProf│
            │ - test_id    │         │ - assignment_id│      │ - skills     │
            │ - test_name  │         │ - status       │      │ - experience │
            │ - total_marks│         │ - score        │      └──────────────┘
            └────────┬─────┘         └────────┬───────┘
                     │                        │
        ┌────────────┴────────────┐           │
        │                         │           │
        ▼                         ▼           │
   ┌─────────────┐      ┌──────────────┐     │
   │ TestQuestion│      │  TestAnswer  │◄────┘
   │ - marks     │      │ - score      │
   │ - order_idx │      │ - code_status│
   └─────┬───────┘      │ - ai_analysis│
         │              └──────┬───────┘
    ┌────┴─────────────────────┤
    │                          │
    ▼                          ▼
┌─────────────────┐    ┌──────────────────┐
│  MCQQuestion    │    │ CodeSubmission   │
│ - options       │    │ - code           │
│ - correct_answer│    │ - output         │
│ - difficulty    │    │ - passed_tests   │
└─────────────────┘    └────────┬─────────┘
                                │
                                ▼
                      ┌──────────────────────┐
                      │ CodeAnalysisResult   │
                      │ (from Gemini API)    │
                      │ - total_score        │
                      │ - code_review        │
                      └──────────────────────┘
"""

# ============================================================================
# 3. DATA FLOW DIAGRAM
# ============================================================================

DATA_FLOW = """
CANDIDATE SUBMISSION FLOW
════════════════════════════════════════════════════════════════════

Step 1: SUBMIT MCQ ANSWER
├─ Request: POST /api/answer/mcq
│          {"question_id": "...", "selected_option": "A"}
│
├─ Pydantic: Validate input
│
├─ Conversion: MCQ answer → TestAnswer (model)
│
├─ Database: INSERT test_answers
│            MCQQuestion checked for correct answer
│            TestAnswer.is_correct_mcq = true/false
│            TestAnswer.score = calculated
│
└─ Response: TestAnswer (Pydantic - JSON)


Step 2: SUBMIT CODE SOLUTION
├─ Request: POST /api/coding/submit
│          {"code": "...", "language": "Python", ...}
│
├─ Pydantic: Validate CodeSubmission
│
├─ Conversion: CodeSubmission → CodeSubmission (SQLAlchemy)
│
├─ Database: INSERT code_submissions (status=pending)
│
├─ Async: Trigger execution service
│          execute_code(submission_id)
│
├─ Execution: Run code against test cases
│             Update CodeSubmission (output, passed_tests, status)
│
├─ Analysis: Convert to Submission (Pydantic for Gemini API)
│            Call Gemini API for code analysis
│            Receive AnalysisResult
│
├─ Storage: INSERT code_analysis_results
│           UPDATE test_answers with ai_analysis
│           UPDATE test_answers with code_quality_score
│
└─ Response: CodeSubmission (Pydantic with execution details)


Step 3: SUBMIT TEST
├─ Request: POST /api/assignments/{id}/submit
│
├─ Database: Load TestAssignment + all TestAnswers
│            Calculate MCQ: correct/wrong/skipped
│            Calculate Coding: passed/failed
│
├─ Aggregation: Sum scores for MCQ and Coding sections
│              Calculate total percentage
│              Determine grade (A-F)
│
├─ Conversion: Results → CandidateReportData
│             (using convert_test_results_to_report)
│
├─ Generation: Create PDF report
│             (using Swarang's report_generator)
│
├─ Storage: INSERT candidate_reports
│          Store PDF file
│          Store JSON for retrieval
│
└─ Response: Report ID + basic stats
"""

# ============================================================================
# 4. SERVICE INTEGRATION MAP
# ============================================================================

SERVICE_INTEGRATION = """
SERVICE INTEGRATION WITH SHARED MODELS
════════════════════════════════════════════════════════════════════

ISHAAN - Test Management
├─ Models Used: TestCreate, Test, TestQuestion, TestAssignment
├─ Database: tests, test_questions, test_assignments
├─ Endpoints:
│  ├─ POST /api/tests (TestCreate → Test)
│  ├─ POST /api/tests/{id}/questions
│  ├─ POST /api/assignments
│  └─ GET /api/assignments/{id}
└─ Converters: convert_test_assignment_*

ANJALI - Code Analysis
├─ Models Used: Submission, AnalysisResult, CodeReviewResult
├─ Database: code_analysis_results
├─ Flow: CodeSubmission → Submission → Gemini API → AnalysisResult
├─ Integration: Enriches TestAnswer with ai_analysis, code_quality_score
└─ Converters: convert_code_submission_to_analysis_request
                convert_analysis_result_to_test_answer_enrichment

SATYAM - Code Execution & Submission
├─ Models Used: CodeSubmission, CodeDraft
├─ Database: code_submissions, code_drafts
├─ Endpoints:
│  ├─ POST /api/coding/submit (CodeSubmission)
│  ├─ POST /api/coding/save-draft (CodeDraft)
│  └─ GET /api/submissions/{id}
└─ Converters: convert_code_submission_db_to_pydantic
                convert_pydantic_code_submission_to_db

SWARANG - Report Generation
├─ Models Used: CandidateReportData, MCQReportSection, CodingReportSection
├─ Database: candidate_reports
├─ Endpoints:
│  ├─ POST /api/assignments/{id}/submit (generates report)
│  ├─ GET /api/reports/{id}
│  └─ GET /api/reports/candidate/{email}
└─ Converters: convert_test_results_to_report
                convert_report_db_to_pydantic

MUKESH - Question Filtering
├─ Models Used: FilterRequest, MCQQuestion, CodingProblem
├─ Database: mcq_questions, coding_questions
├─ Endpoints:
│  ├─ POST /api/mcq/filter (FilterRequest)
│  ├─ POST /api/coding/filter (CodingFilterRequest)
│  └─ GET /api/questions/search
└─ No converters (direct queries)

ISHAAN - Skill Extraction
├─ Models Used: SkillExtractionRequest, SkillExtractionResult, CandidateSkillMatch
├─ Database: skill_extractions, candidate_skill_matches
├─ Pipeline: JD → FLAN-T5 → BGE-M3 → FAISS → Database
└─ Converters: Convert to/from SkillExtraction (SQLAlchemy)
"""

# ============================================================================
# 5. ENUM UNIFICATION
# ============================================================================

ENUM_UNIFICATION = """
ENUM VALUES (Unified Across Pydantic & SQLAlchemy)
════════════════════════════════════════════════════════════════════

LanguageEnum
├─ Python
├─ Java
├─ SQL
├─ PySpark
├─ JavaScript
├─ C++
└─ C#

DifficultyEnum
├─ Easy      (for questions)
├─ Medium
└─ Hard

TestStatusEnum
├─ active
├─ inactive
├─ completed
├─ draft
└─ published

QuestionTypeEnum
├─ multiple_choice
├─ coding
├─ true_false
└─ unified    (MCQ + Coding in one)

AssignmentStatusEnum
├─ pending
├─ scheduled
├─ in_progress
├─ completed
└─ expired

CodeExecutionStatusEnum
├─ pending
├─ success
├─ error
├─ timeout
├─ compilation_error
└─ runtime_error

RoleEnum
├─ admin
├─ candidate
├─ reviewer
└─ super_admin
"""

# ============================================================================
# 6. DATABASE TABLE STRUCTURE
# ============================================================================

TABLE_STRUCTURE = """
DATABASE TABLES (20 Total)
════════════════════════════════════════════════════════════════════

User Management (2)
├─ users (17 columns)
│  └─ user_id (PK), email (unique), role, created_at, updated_at
└─ candidate_profiles (8 columns)
   └─ user_id (FK), skills, experience_years

Tests & Questions (4)
├─ tests (10 columns)
│  └─ test_id (PK), created_by (FK), status, total_marks
├─ mcq_questions (12 columns)
│  └─ correct_answer, difficulty, language
├─ coding_questions (11 columns)
│  └─ test_cases (JSON), difficulty, language
└─ test_questions (7 columns)
   └─ test_id (FK), question_id, order_index (unique per test)

Test Execution (4)
├─ test_assignments (11 columns)
│  └─ test_id (FK), candidate_id (FK), status, score
├─ test_answers (21 columns)
│  └─ assignment_id (FK), code_submission_id (FK), score, ai_analysis
├─ code_submissions (17 columns)
│  └─ problem_id (FK), code, output, is_passed, passed_test_cases
└─ code_drafts (8 columns)
   └─ problem_id (FK), code, cursor_position

Reports (3)
├─ candidate_reports (17 columns)
│  └─ candidate_id (FK), percentage, grade, pdf_url, json_data
├─ proctoring_data (7 columns)
│  └─ assignment_id (FK), flagged_faces, cheating_events
└─ proctoring_frame_captures (8 columns)
   └─ assignment_id (FK), face_detected, suspicious_activity

AI Analysis (1)
└─ code_analysis_results (13 columns)
   └─ submission_id (FK), total_score, code_review (JSON)

Skills (2)
├─ skill_extractions (4 columns)
│  └─ extracted_skills (array), skill_scores (array)
└─ candidate_skill_matches (8 columns)
   └─ candidate_id (FK), match_percentage

Audit (1)
└─ audit_logs (7 columns)
   └─ user_id (FK), entity_id, action, details (JSON)
"""

# ============================================================================
# 7. CONVERSION PIPELINE
# ============================================================================

CONVERSION_PIPELINE = """
MODEL CONVERSION PIPELINE
════════════════════════════════════════════════════════════════════

API Request (JSON)
       ↓
Pydantic Validation
├─ Type checking
├─ Field validation
├─ Enum verification
└─ Required fields check
       ↓
Conversion Function
├─ Map fields
├─ Generate IDs
├─ Set defaults
└─ Add timestamps
       ↓
SQLAlchemy Model
├─ Set all columns
├─ Add relationships
└─ Enforce constraints
       ↓
Database Insertion
├─ Foreign key checks
├─ Constraint validation
└─ Transaction commit
       ↓
Result Conversion
├─ SQLAlchemy → Pydantic
├─ Serialize relationships
└─ Format for JSON
       ↓
API Response (JSON)

Example: Code Submission
─────────────────────────────
CodeSubmission (JSON) ←─ request body
        ↓
Pydantic CodeSubmission ←─ validate
        ↓
convert_pydantic_code_submission_to_db() ←─ transform
        ↓
SQLAlchemy CodeSubmission ←─ model
        ↓
INSERT into code_submissions ←─ database
        ↓
convert_code_submission_db_to_pydantic() ←─ transform back
        ↓
CodeSubmission (JSON) ←─ response body
"""

# ============================================================================
# 8. RELATIONSHIPS MATRIX
# ============================================================================

RELATIONSHIPS_MATRIX = """
RELATIONSHIP MATRIX
════════════════════════════════════════════════════════════════════

                  users  tests  questions  assignments  answers  submissions
users              |      -        -           -           -          -
├─ creates tests   |      1        -           -           -          -
├─ takes assign    |      -        -           -           N          -
├─ submits code    |      -        -           -           -          -          N

tests              |      -        -           -           -           -
├─ has questions   |      -        -           N           -           -
├─ has assign      |      -        -           -           N           -
└─ has answers     |      -        -           -           -           N

questions          |      -        -           -           -           -
├─ MCQ questions   |      -        -           -           -           -
│  └─ in tests     |      -        -           -           -           -
└─ Coding ques     |      -        -           -           -           -
   └─ in tests     |      -        -           -           -           -
   └─ submissions  |      -        -           -           -           -          N

assignments        |      -        -           -           -           -
├─ has answers     |      -        -           -           -           N
└─ has proctoring  |      -        -           -           -           -

answers            |      -        -           -           -           -
└─ from submission |      -        -           -           -           -          1

submissions        |      -        -           -           -           -
├─ has analysis    |      -        -           -           -           -          1
└─ linked in tests |      -        -           -           -           1

reports            |      -        -           -           -           -
├─ from candidate  |      1        -           -           -           -
└─ from test       |      -        1           -           -           -
"""

# ============================================================================
# 9. PERFORMANCE INDEX STRATEGY
# ============================================================================

PERFORMANCE_INDEXES = """
PERFORMANCE INDEX STRATEGY
════════════════════════════════════════════════════════════════════

PRIMARY INDEXES (Single column)
├─ users: idx_users_email (unique lookup)
├─ users: idx_users_role (filter by role)
├─ tests: idx_tests_status (filter by status)
├─ tests: idx_tests_created_by (user's tests)
├─ mcq_questions: idx_mcq_difficulty (filter)
├─ mcq_questions: idx_mcq_language (filter)
├─ coding_questions: idx_coding_difficulty
├─ coding_questions: idx_coding_language
├─ test_assignments: idx_assignments_candidate (get assignments)
├─ test_assignments: idx_assignments_status (filter by status)
├─ test_answers: idx_answers_assignment (get answers for test)
├─ test_answers: idx_answers_candidate (candidate answers)
├─ test_answers: idx_answers_status (filter by execution status)
├─ code_submissions: idx_submissions_candidate
├─ code_submissions: idx_submissions_problem
├─ code_submissions: idx_submissions_status
├─ candidate_reports: idx_reports_candidate
└─ candidate_reports: idx_reports_test

COMPOSITE INDEXES (Multiple columns)
├─ test_assignments: idx_assignments_candidate_status
│  └─ Get pending/in_progress assignments for candidate
├─ test_answers: idx_answers_assignment_type
│  └─ Get MCQ vs coding answers for assignment
├─ code_submissions: idx_submissions_candidate_status
│  └─ Get submission status by candidate
├─ tests: idx_tests_created_at (for pagination)
├─ candidate_reports: idx_reports_created_at (for pagination)
└─ test_answers: idx_answers_submitted_at (for sorting)

QUERY OPTIMIZATION TIPS
├─ Use eager loading for related data
├─ Use composite indexes for WHERE + ORDER BY
├─ Batch insert with bulk_insert_mappings
├─ Cache test questions (rarely change)
├─ Use read replica for reports
└─ Archive old submissions to separate table
"""

# ============================================================================
# 10. ERROR HANDLING FLOW
# ============================================================================

ERROR_HANDLING = """
ERROR HANDLING FLOW
════════════════════════════════════════════════════════════════════

Validation Errors
├─ Pydantic catches type mismatches
│  Example: "code": 123 (should be string)
│  Response: 422 Unprocessable Entity
│
├─ Enum validation catches invalid values
│  Example: status = "invalid"
│  Response: 422 Unprocessable Entity
│
└─ Required fields check
   Example: missing test_name
   Response: 422 Unprocessable Entity


Database Errors
├─ Foreign key violation
│  Example: test_id doesn't exist
│  Response: 400 Bad Request / 404 Not Found
│
├─ Unique constraint violation
│  Example: duplicate test_id + candidate_id
│  Response: 409 Conflict
│
├─ NOT NULL constraint
│  Example: missing required field
│  Response: 400 Bad Request
│
└─ Check constraint
   Example: correct_answer = 'Z' (not A-D)
   Response: 400 Bad Request


Business Logic Errors
├─ Test not found
│  Response: 404 Not Found
│
├─ Candidate not found
│  Response: 404 Not Found
│
├─ Already submitted
│  Response: 409 Conflict
│
├─ Assignment expired
│  Response: 403 Forbidden
│
└─ Invalid state transition
   Example: marking complete if pending
   Response: 400 Bad Request


Conversion Errors
├─ Missing required field in conversion
│  Solution: Check for None values
│
├─ Type mismatch during conversion
│  Solution: Use model_validate()
│
└─ Relationship not loaded
   Solution: Use eager loading
"""

# ============================================================================
# Print all diagrams
# ============================================================================

if __name__ == "__main__":
    print(SYSTEM_OVERVIEW)
    print("\n" + "="*80 + "\n")
    print(MODEL_RELATIONSHIPS)
    print("\n" + "="*80 + "\n")
    print(DATA_FLOW)
    print("\n" + "="*80 + "\n")
    print(SERVICE_INTEGRATION)
    print("\n" + "="*80 + "\n")
    print(ENUM_UNIFICATION)
    print("\n" + "="*80 + "\n")
    print(TABLE_STRUCTURE)
    print("\n" + "="*80 + "\n")
    print(CONVERSION_PIPELINE)
    print("\n" + "="*80 + "\n")
    print(RELATIONSHIPS_MATRIX)
    print("\n" + "="*80 + "\n")
    print(PERFORMANCE_INDEXES)
    print("\n" + "="*80 + "\n")
    print(ERROR_HANDLING)
