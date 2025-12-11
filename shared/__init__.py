"""
Talentshire Shared Models & Database Module
============================================

This package provides:
1. Pydantic models for API contracts (shared/models.py)
2. SQLAlchemy ORM models for database (shared/database_models.py)
3. Conversion functions between representations (shared/model_converters.py)
4. Comprehensive mapping documentation (shared/MODEL_MAPPING.md)

All models are integrated across:
- Test Management (Ishaan)
- Code Analysis (Anjali)
- Submissions & Execution (Satyam)
- Reports (Swarang)
- Question Filtering (Mukesh)
- Skill Extraction (Ishaan - NLP)

USAGE
=====

### 1. Pydantic Models (for APIs)
```python
from shared.models import (
    TestCreate, Test,
    CodeSubmission, AnalysisResult,
    CandidateReportData,
    Submission
)

# Create API request model
test_req = TestCreate(
    test_name="Python Fundamentals",
    duration_minutes=60,
    status="active"
)

# Validate and convert to dict for database
test_data = test_req.model_dump()
```

### 2. Database Models (SQLAlchemy)
```python
from shared.database_models import (
    Base, Test as SQLTest,
    TestAssignment, TestAnswer,
    CodeSubmission as SQLCodeSubmission,
    CandidateReport
)

# Create tables
Base.metadata.create_all(engine)

# Query and work with models
test = session.query(SQLTest).filter_by(test_id=test_id).first()
assignments = test.assignments  # Relationships work automatically
```

### 3. Conversion Functions
```python
from shared.model_converters import (
    convert_code_submission_to_analysis_request,
    convert_analysis_result_to_test_answer_enrichment,
    convert_test_results_to_report
)

# Convert CodeSubmission to API format for Gemini
submission_db = session.query(SQLCodeSubmission).first()
problem = session.query(SQLCodingQuestion).first()
gemini_request = convert_code_submission_to_analysis_request(submission_db, problem)

# Enrich test answer with analysis
analysis_result = gemini_api.analyze(gemini_request)
test_answer = convert_analysis_result_to_test_answer_enrichment(analysis_result, test_answer)

# Generate report
report = convert_test_results_to_report(assignment, answers, candidate, test)
```

### 4. Mapping Documentation
See `shared/MODEL_MAPPING.md` for:
- Complete architecture overview
- Field-by-field mappings
- Data flow examples
- Validation rules
- Performance indexes

ENUM VALUES
===========

All enums are defined in both Pydantic and SQLAlchemy:

- LanguageEnum: python, java, sql, pyspark, javascript, cpp, csharp
- DifficultyEnum: easy, medium, hard
- TestStatusEnum: active, inactive, completed, draft, published
- QuestionTypeEnum: multiple_choice, coding, true_false, unified
- AssignmentStatusEnum: pending, scheduled, in_progress, completed, expired
- CodeExecutionStatusEnum: pending, success, error, timeout, compilation_error, runtime_error
- RoleEnum: admin, candidate, reviewer, super_admin

DATABASE SCHEMA
===============

Key tables:
- users: User accounts with roles
- candidate_profiles: Extended candidate info
- tests: Test definitions
- mcq_questions: Multiple choice questions
- coding_questions: Coding problems
- test_questions: Question assignments within tests
- test_assignments: Test assignments to candidates
- test_answers: Candidate answers with scores
- code_submissions: Code submissions with execution results
- code_drafts: Auto-saved code drafts
- candidate_reports: Generated test reports
- code_analysis_results: AI code analysis from Gemini
- skill_extractions: Extracted skills from job descriptions
- candidate_skill_matches: Skill matching results
- proctoring_data: Proctoring metrics
- proctoring_frame_captures: Individual frame data
- audit_logs: Action audit trail

All tables include proper:
- Foreign key relationships
- Indexes for performance
- Timestamps (created_at, updated_at)
- Soft-delete support (where applicable)

INTEGRATION WITH SERVICES
==========================

### Test Management (Ishaan)
Uses: Test, TestQuestion, TestAssignment, TestCreate models
Stores: Creates tests and assigns to candidates

### Code Analysis (Anjali)
Uses: Submission, AnalysisResult, CodeReviewResult models
Stores: CodeAnalysisResult in database
Updates: TestAnswer with AI scores

### Submission Service (Satyam)
Uses: CodeSubmission, CodeDraft models
Stores: Code submissions, auto-saves, execution results
Triggers: Code analysis pipeline

### Report Generation (Swarang)
Uses: CandidateReportData, MCQReportSection, CodingReportSection models
Stores: CandidateReport in database
Creates: PDF files in file system

### Question Filtering (Mukesh)
Uses: FilterRequest, MCQQuestion, CodingProblem models
Queries: MCQs and coding problems by difficulty/language
Returns: Filtered questions

### Skill Extraction (Ishaan - NLP)
Uses: SkillExtractionRequest, SkillExtractionResult, CandidateSkillMatch
Stores: Extracted skills and matches
Pipeline: Job description → FLAN-T5 → BGE-M3 → FAISS → Database

BEST PRACTICES
==============

1. Always use Pydantic models for API endpoints
   ✓ Validates input automatically
   ✓ Consistent JSON serialization
   ✓ OpenAPI documentation generation

2. Always use SQLAlchemy models for database operations
   ✓ Type safety
   ✓ Automatic query building
   ✓ Relationship management

3. Use conversion functions for transformations
   ✓ Tested and documented
   ✓ Handles field mapping
   ✓ Single source of truth

4. Validate before converting
   ✓ Pydantic validation happens automatically
   ✓ Check foreign key references
   ✓ Validate enum values

5. Use database relationships
   ✓ Don't manually build complex queries
   ✓ Use `.relationships` to traverse
   ✓ Lazy loading optimization

PERFORMANCE NOTES
=================

- All high-cardinality fields have indexes
- Use `join()` for eager loading when needed
- Use `select()` for partial column loading
- Batch operations with bulk_insert_mappings
- Cache frequently accessed data (tests, questions)
- Use read replicas for reports

TESTING
=======

Mock models for testing:
```python
from shared.models import Test, CodeSubmission
from unittest.mock import Mock

mock_test = Mock(spec=Test)
mock_test.test_id = uuid.uuid4()
mock_test.test_name = "Test"

mock_submission = Mock(spec=CodeSubmission)
mock_submission.code = "def foo(): pass"
```

DATABASE MIGRATIONS
===================

Initialize schema:
```python
from shared.database_models import Base
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
```

Future migrations (use Alembic):
```bash
alembic init migrations
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

RELATED FILES
=============

- shared/models.py - Pydantic models (APIs)
- shared/database_models.py - SQLAlchemy models (Database)
- shared/model_converters.py - Conversion functions
- shared/MODEL_MAPPING.md - Complete documentation

For integration, see:
- backend/main.py - Monolithic backend using shared models
- Anjali/code-analyzer-service/ - Analyzes code using Submission model
- Satyam/final_codeditor/ - Stores submissions using CodeSubmission model
- swarang/online_test_report_dashboard/ - Generates reports using CandidateReportData model
"""
