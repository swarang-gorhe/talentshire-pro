"""
Model Mapping Document - Talentshire Integration
===============================================

This document defines how all models across the platform map to each other
and to the database schema. It serves as a single source of truth for
understanding data flow and transformations.

ARCHITECTURE OVERVIEW
====================

┌─────────────────────────────────────────────────────────────────┐
│                   Pydantic Models (APIs)                        │
│                   (shared/models.py)                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                 Data Conversion Layer                           │
│            (shared/model_converters.py)                        │
│  - Convert between Pydantic ↔ SQLAlchemy ↔ MongoDB             │
│  - Validation and enrichment                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────────┐
│               SQLAlchemy ORM Models (DB)                        │
│              (shared/database_models.py)                       │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────────────┐
│             PostgreSQL + MongoDB Schema                         │
│    (See database diagram schema image)                          │
└─────────────────────────────────────────────────────────────────┘


DETAILED MAPPINGS BY SERVICE
=============================

1. TEST MANAGEMENT (Ishaan - backend/ishaan/test-info.py)
   ─────────────────────────────────────────────────────

   Pydantic Models:
   - TestCreate → Test (Pydantic) → Test (SQLAlchemy)
   - TestQuestionCreate → TestQuestion (Pydantic) → TestQuestion (SQLAlchemy)

   Database Tables:
   - tests
   - test_questions
   - test_assignments
   - test_answers

   Key Relationships:
   Test (1) ──── (N) TestQuestion
                  │
                  └─→ MCQQuestion or CodingQuestion
   
   Test (1) ──── (N) TestAssignment
                  │
                  └─→ Candidate (User)


2. QUESTION MANAGEMENT (Mukesh - mukesh/filterservice.py)
   ──────────────────────────────────────────────────────

   Pydantic Models:
   - FilterRequest → Filters MCQ questions
   - CodingFilterRequest → Filters coding problems
   - MCQQuestion (Pydantic)
   - CodingProblem (Pydantic)

   Database Tables:
   - mcq_questions
   - coding_questions

   Key Relationships:
   MCQQuestion ──── (N) TestQuestion
   CodingQuestion ──── (N) TestQuestion


3. SUBMISSION & EXECUTION (Satyam - Satyam/final_codeditor)
   ────────────────────────────────────────────────────────

   Pydantic Models:
   - CodeSubmission (submitted code)
   - CodeExecutionStatusEnum (status tracking)

   Database Tables:
   - code_submissions
   - code_drafts
   - test_answers (links submissions to tests)

   Key Relationships:
   CodeSubmission ──── (1) CodingQuestion
                       ─── (1) TestAnswer
   CodeDraft ──── (1) Candidate
              ──── (1) CodingQuestion


4. CODE ANALYSIS (Anjali - Anjali/code-analyzer-service)
   ────────────────────────────────────────────────────

   Pydantic Models:
   - Submission (input for analysis)
   - AnalysisResult (output of analysis)
   - CodeReviewResult (detailed review)

   Database Tables:
   - code_analysis_results
   - test_answers (stores ai_analysis, ai_review_notes)

   Conversion Flow:
   CodeSubmission
      ↓
   Submission (Pydantic - for Gemini API)
      ↓
   AnalysisResult (from Gemini)
      ↓
   CodeAnalysisResult (stored in DB)
      ↓
   TestAnswer enrichment (ai_analysis, code_quality_score)


5. REPORT GENERATION (Swarang - swarang/online_test_report_dashboard)
   ──────────────────────────────────────────────────────────────

   Pydantic Models:
   - CandidateReportData (complete report)
   - MCQReportSection (MCQ section)
   - CodingReportSection (Coding section)
   - ProctoringData (proctoring metrics)

   Database Tables:
   - candidate_reports
   - proctoring_data
   - proctoring_frame_captures

   Conversion Flow:
   TestAssignment + TestAnswers
      ↓
   Aggregate scores and sections
      ↓
   CandidateReportData (Pydantic)
      ↓
   CandidateReport (SQLAlchemy)
      ↓
   PostgreSQL + PDF file


6. SKILL EXTRACTION (Ishaan - ishaan/app.py)
   ─────────────────────────────────────────

   Pydantic Models:
   - SkillExtractionRequest
   - SkillExtractionResult
   - CandidateSkillMatch

   Database Tables:
   - skill_extractions
   - candidate_skill_matches

   NLP Pipeline:
   Job Description
      ↓
   Keyword extraction (FLAN-T5)
      ↓
   Skill embedding (BGE-M3)
      ↓
   FAISS vector search
      ↓
   SkillExtractionResult → SkillExtraction (DB)


KEY MODEL CONVERSION PATTERNS
=============================

Pattern 1: API Request → Database Storage
──────────────────────────────────────────
POST /api/test/assign
  ├─ Input: TestAssignmentCreate (Pydantic)
  ├─ Convert: TestAssignmentCreate → TestAssignment (SQLAlchemy)
  ├─ Validate: Check test exists, candidate exists
  ├─ Store: session.add(test_assignment)
  └─ Return: TestAssignment (Pydantic response)


Pattern 2: Database Query → API Response
─────────────────────────────────────────
GET /api/test/{test_id}/questions
  ├─ Query: Test.questions (SQLAlchemy)
  ├─ Load relations: TestQuestion → MCQQuestion/CodingQuestion
  ├─ Convert: SQLAlchemy objects → Pydantic models
  ├─ Serialize: Pydantic.model_dump()
  └─ Return: List[TestQuestion] (JSON response)


Pattern 3: External Service Integration → Database
───────────────────────────────────────────────────
CodeSubmission → Gemini API → Database
  ├─ Load: CodeSubmission from DB
  ├─ Convert: CodeSubmission → Submission (Pydantic for API)
  ├─ Call: Gemini /analyze endpoint
  ├─ Receive: AnalysisResult (Pydantic)
  ├─ Convert: AnalysisResult → CodeAnalysisResult (SQLAlchemy)
  ├─ Store: session.add(code_analysis_result)
  ├─ Enrich: TestAnswer.ai_analysis, code_quality_score
  └─ Update: session.commit()


FIELD MAPPINGS BY TABLE
=======================

USERS TABLE
───────────
Pydantic UserBase → SQLAlchemy User
- user_id: UUID ↔ user_id: UUID (PK)
- email: str ↔ email: str (unique)
- full_name: str ↔ full_name: str
- role: str ↔ role: Enum(RoleEnum)

Related Models:
- UserBase (minimal)
- CandidateProfile (extends user)


TESTS TABLE
───────────
Pydantic TestCreate/Test → SQLAlchemy Test
- test_name: str ↔ test_name: str
- duration_minutes: int ↔ duration_minutes: int
- status: TestStatusEnum ↔ status: Enum(TestStatusEnum)
- description: Optional[str] ↔ description: Text
- tags: List[str] ↔ tags: ARRAY(String)
- total_marks: int ↔ total_marks: int
- created_by: UUID ↔ created_by: UUID (FK)
- created_at: datetime ↔ created_at: TIMESTAMP

Relationships:
- creator (User)
- questions (TestQuestion[])
- assignments (TestAssignment[])
- answers (TestAnswer[])


TEST_QUESTIONS TABLE
─────────────────────
Pydantic TestQuestion → SQLAlchemy TestQuestion
- test_question_id: UUID ↔ test_question_id: UUID (PK)
- test_id: UUID ↔ test_id: UUID (FK)
- question_id: UUID ↔ question_id: UUID
- question_type: QuestionTypeEnum ↔ question_type: Enum(QuestionTypeEnum)
- order_index: int ↔ order_index: int
- marks: int ↔ marks: int
- time_limit_seconds: Optional[int] ↔ time_limit_seconds: int

Note: question_id can reference MCQQuestion or CodingQuestion based on question_type


MCQ_QUESTIONS TABLE
────────────────────
Pydantic MCQQuestion → SQLAlchemy MCQQuestion
- question_id: UUID ↔ question_id: UUID (PK)
- question_text: str ↔ question_text: Text
- option_a/b/c/d: str ↔ option_a/b/c/d: Text
- correct_answer: str ↔ correct_answer: String(1) with CHECK
- difficulty: DifficultyEnum ↔ difficulty: Enum(DifficultyEnum)
- language: LanguageEnum ↔ language: Enum(LanguageEnum)
- explanation: Optional[str] ↔ explanation: Text
- tags: List[str] ↔ tags: ARRAY(String)
- marks: int ↔ marks: int


CODING_QUESTIONS TABLE
───────────────────────
Pydantic CodingProblem → SQLAlchemy CodingQuestion
- question_id: UUID ↔ question_id: UUID (PK)
- title: str ↔ title: str
- description: str ↔ description: Text
- difficulty: DifficultyEnum ↔ difficulty: Enum(DifficultyEnum)
- language: LanguageEnum ↔ language: Enum(LanguageEnum)
- sample_input: str ↔ sample_input: Text
- sample_output: str ↔ sample_output: Text
- constraints: str ↔ constraints: Text
- test_cases: List[dict] ↔ test_cases: JSON
- labels: List[str] ↔ labels: ARRAY(String)
- time_limit_seconds: int ↔ time_limit_seconds: int
- memory_limit_mb: int ↔ memory_limit_mb: int


TEST_ANSWERS TABLE
───────────────────
Pydantic TestAnswer → SQLAlchemy TestAnswer
- answer_id: UUID ↔ answer_id: UUID (PK)
- assignment_id: UUID ↔ assignment_id: UUID (FK)
- test_id: UUID ↔ test_id: UUID (FK)
- question_id: UUID ↔ question_id: UUID
- question_type: QuestionTypeEnum ↔ question_type: Enum(QuestionTypeEnum)
- candidate_id: UUID ↔ candidate_id: UUID (FK)

MCQ Fields:
- selected_option: Optional[str] ↔ selected_option: String(1)
- is_correct_mcq: Optional[bool] ↔ is_correct_mcq: Boolean

Coding Fields:
- code: Optional[str] ↔ code: Text
- language: Optional[LanguageEnum] ↔ language: Enum(LanguageEnum)
- code_status: CodeExecutionStatusEnum ↔ code_status: Enum(CodeExecutionStatusEnum)
- code_output: Optional[str] ↔ code_output: Text
- code_passed: bool ↔ code_passed: Boolean

Scoring & Analysis:
- score: float ↔ score: Float
- max_score: float ↔ max_score: Float
- time_spent_seconds: int ↔ time_spent_seconds: int
- ai_analysis: Optional[str] ↔ ai_analysis: Text
- ai_review_notes: Optional[str] ↔ ai_review_notes: Text
- code_quality_score: Optional[float] ↔ code_quality_score: Float


CODE_SUBMISSIONS TABLE
───────────────────────
Pydantic CodeSubmission → SQLAlchemy CodeSubmission
- submission_id: UUID ↔ submission_id: UUID (PK)
- candidate_id: UUID ↔ candidate_id: UUID (FK)
- problem_id: UUID ↔ problem_id: UUID (FK)
- language: LanguageEnum ↔ language: Enum(LanguageEnum)
- code: str ↔ code: Text
- stdin: str ↔ stdin: Text
- status: CodeExecutionStatusEnum ↔ status: Enum(CodeExecutionStatusEnum)
- stdout: str ↔ stdout: Text
- stderr: str ↔ stderr: Text
- output: str ↔ output: Text
- expected_output: str ↔ expected_output: Text
- is_passed: bool ↔ is_passed: Boolean
- passed_test_cases: int ↔ passed_test_cases: int
- total_test_cases: int ↔ total_test_cases: int
- execution_time_ms: Optional[float] ↔ execution_time_ms: Float
- memory_used_mb: Optional[float] ↔ memory_used_mb: Float
- submitted_at: datetime ↔ submitted_at: TIMESTAMP


CODE_ANALYSIS_RESULTS TABLE
────────────────────────────
Pydantic AnalysisResult → SQLAlchemy CodeAnalysisResult
- analysis_id: UUID ↔ analysis_id: UUID (PK)
- submission_id: UUID ↔ submission_id: UUID (FK, unique)
- candidate_id: UUID ↔ candidate_id: UUID (FK)
- total_score: Optional[int] ↔ total_score: Integer
- improvements_suggested: str ↔ improvements_suggested: Text
- detailed_analysis: str ↔ detailed_analysis: Text
- code_review: Optional[CodeReviewResult] ↔ code_review: JSON
- error: Optional[str] ↔ error: String


CANDIDATE_REPORTS TABLE
────────────────────────
Pydantic CandidateReportData → SQLAlchemy CandidateReport
- report_id: UUID ↔ report_id: UUID (PK)
- candidate_id: UUID ↔ candidate_id: UUID (FK)
- test_id: UUID ↔ test_id: UUID (FK)
- test_date: datetime ↔ test_date: TIMESTAMP
- total_score: float ↔ total_score: Float
- total_max: float ↔ total_max: Float
- percentage: float ↔ percentage: Float
- grade: Optional[str] ↔ grade: String(1)

Section Scores:
- mcq: MCQReportSection ↔ mcq_score, mcq_max, mcq_correct, mcq_wrong, mcq_skipped
- coding: CodingReportSection ↔ coding_score, coding_max, coding_passed, coding_failed

Additional Fields:
- duration_seconds: int ↔ duration_seconds: int
- status: str ↔ status: String
- pdf_url: Optional[str] ↔ pdf_url: String
- json_data: dict ↔ json_data: JSON


TEST_ASSIGNMENTS TABLE
───────────────────────
Pydantic TestAssignmentCreate/TestAssignment → SQLAlchemy TestAssignment
- assignment_id: UUID ↔ assignment_id: UUID (PK)
- test_id: UUID ↔ test_id: UUID (FK)
- candidate_id: UUID ↔ candidate_id: UUID (FK)
- status: AssignmentStatusEnum ↔ status: Enum(AssignmentStatusEnum)
- scheduled_start_time: Optional[datetime] ↔ scheduled_start_time: TIMESTAMP
- scheduled_end_time: Optional[datetime] ↔ scheduled_end_time: TIMESTAMP
- max_attempts: int ↔ max_attempts: int
- score: Optional[float] ↔ score: Float


DATA FLOW EXAMPLES
===================

Example 1: Creating and Assigning a Test
─────────────────────────────────────────
1. Admin calls: POST /api/tests
   {
     "test_name": "Python Fundamentals",
     "duration_minutes": 60,
     "status": "active"
   }

2. Controller receives TestCreate (Pydantic)

3. Service converts:
   TestCreate → Test (Pydantic with UUID) → Test (SQLAlchemy)

4. Database INSERT into tests table

5. Response: Test (Pydantic with test_id)


Example 2: Candidate Takes Test
────────────────────────────────
1. Candidate starts test assignment
   → TestAssignment status = "in_progress"
   → started_at = now

2. Candidate submits MCQ answer
   POST /api/test/{assignment_id}/answer/mcq
   {
     "question_id": "uuid",
     "selected_option": "A"
   }
   
3. Controller creates TestAnswer (Pydantic)

4. Service:
   - Validate question exists
   - Check if option is correct
   - Calculate score
   - Convert to TestAnswer (SQLAlchemy)
   - INSERT into test_answers

5. Response: TestAnswer (Pydantic)


Example 3: Code Submission & Analysis
──────────────────────────────────────
1. Candidate submits code
   POST /api/coding/submit
   {
     "problem_id": "uuid",
     "language": "Python",
     "code": "def solve(): ..."
   }

2. Controller receives CodeSubmission (Pydantic)

3. Service flow:
   a) Save to code_submissions table
   b) Execute code (async)
      → CodeSubmission.status = "success"/"error"
      → CodeSubmission.output = execution result
      → CodeSubmission.is_passed = check test cases
   
   c) Trigger code analysis
      → Convert CodeSubmission → Submission (Pydantic for Gemini)
      → Call Gemini API
      → Receive AnalysisResult (Pydantic)
      → Convert to CodeAnalysisResult (SQLAlchemy)
      → INSERT into code_analysis_results
   
   d) Update TestAnswer
      → TestAnswer.code_submission_id = submission_id
      → TestAnswer.ai_analysis = analysis.detailed_analysis
      → TestAnswer.code_quality_score = analysis.total_score
      → TestAnswer.code_passed = submission.is_passed

4. Response: CodeSubmission (Pydantic with results)


Example 4: Generate Test Report
────────────────────────────────
1. Test submission complete
   PATCH /api/assignments/{assignment_id}/submit

2. Service:
   a) Load TestAssignment with all TestAnswers
   b) Aggregate scores:
      - MCQ: count correct, calculate score
      - Coding: sum passed test cases
   c) Calculate percentage and grade
   d) Create CandidateReportData (Pydantic)
   
3. Report generation:
   a) Generate PDF from report data
   b) Convert to CandidateReport (SQLAlchemy)
   c) Store json_data for later retrieval
   d) Save to PostgreSQL
   e) Store PDF in file system
   
4. Return: CandidateReportData (Pydantic)


MONGODB INTEGRATION
===================

While PostgreSQL is primary storage, MongoDB is used for:

1. Coding Problems (Backup)
   - Collection: coding_questions
   - Schema mirrors CodingQuestion model

2. Code Submissions (Session backup)
   - Collection: code_submissions
   - Useful for session recovery

3. Job Descriptions (For skill extraction)
   - Collection: job_descriptions
   - Used by NLP pipeline

Sync Strategy:
- PostgreSQL is source of truth
- MongoDB used for denormalization and search
- Keep in sync with triggers or async workers


ENUM REFERENCE
==============

LanguageEnum: python, java, sql, pyspark, javascript, cpp, csharp
DifficultyEnum: easy, medium, hard
TestStatusEnum: active, inactive, completed, draft, published
QuestionTypeEnum: multiple_choice, coding, true_false, unified
AssignmentStatusEnum: pending, scheduled, in_progress, completed, expired
CodeExecutionStatusEnum: pending, success, error, timeout, compilation_error, runtime_error
RoleEnum: admin, candidate, reviewer, super_admin


VALIDATION RULES
=================

1. Test Creation
   - duration_minutes > 0
   - at least 1 question

2. Test Question Assignment
   - question_id exists
   - order_index unique per test
   - marks >= 0

3. Code Submission
   - candidate_id exists
   - problem_id exists
   - language supported
   - code not empty

4. Test Answer
   - assignment_id exists
   - test_id matches assignment
   - question_id exists
   - score <= max_score

5. Report Generation
   - all answers submitted
   - assignment status = "completed"


INDEXES FOR PERFORMANCE
=======================

High-priority indexes:
- tests(created_by)
- tests(status)
- test_answers(assignment_id)
- test_answers(candidate_id)
- code_submissions(candidate_id)
- code_submissions(problem_id)
- code_submissions(status)
- candidate_reports(candidate_id)
- mcq_questions(difficulty, language)
- coding_questions(difficulty, language)
"""
