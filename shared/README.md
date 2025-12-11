# Talentshire Shared Models & Database Integration

Complete model integration for the Talentshire technical assessment platform.

## 📁 Files in This Module

```
shared/
├── __init__.py                  # Package initialization and usage guide
├── models.py                    # Pydantic models for APIs (500+ lines)
├── database_models.py           # SQLAlchemy ORM models (600+ lines)
├── model_converters.py          # Conversion functions between formats (400+ lines)
├── MODEL_MAPPING.md             # Complete mapping documentation
├── INTEGRATION_GUIDE.md          # Real-world usage examples
├── schema.sql                   # PostgreSQL DDL schema
└── README.md                    # This file
```

## 🎯 Overview

This module provides **unified data models** for the entire Talentshire platform:

- **Pydantic Models** → Validate API requests/responses
- **SQLAlchemy Models** → Define database schema and relationships
- **Conversion Functions** → Transform between representations
- **Complete Documentation** → How everything connects

### Model Hierarchy

```
API Request (JSON)
        ↓
Pydantic Model (validates)
        ↓
Conversion Function
        ↓
SQLAlchemy Model (database)
        ↓
PostgreSQL
```

## 🚀 Quick Start

### 1. Setup Database

```python
from sqlalchemy import create_engine
from shared.database_models import Base

DATABASE_URL = "postgresql+psycopg://user:password@localhost/talentshire"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
```

### 2. Use Models in API

```python
from fastapi import FastAPI, Depends
from shared.models import TestCreate, Test
from shared.database_models import Test as SQLTest

app = FastAPI()

@app.post("/api/tests")
async def create_test(test: TestCreate):  # Pydantic validates
    # Convert to database model
    db_test = SQLTest(
        test_id=uuid.uuid4(),
        **test.model_dump(exclude_unset=True)
    )
    # Save and return
    db.add(db_test)
    db.commit()
    return db_test
```

### 3. Convert Between Formats

```python
from shared.model_converters import (
    convert_code_submission_to_analysis_request,
    convert_analysis_result_to_test_answer_enrichment
)

# Convert submission for AI analysis
submission_db = db.query(SQLCodeSubmission).first()
gemini_request = convert_code_submission_to_analysis_request(submission_db, problem)

# Enrich with analysis results
analysis = gemini_api.analyze(gemini_request)
test_answer = convert_analysis_result_to_test_answer_enrichment(analysis, test_answer)
```

## 📚 Model Categories

### User Models
- `UserBase` → Basic user info
- `CandidateProfile` → Extended candidate info

### Test Models
- `TestCreate` → Create test request
- `Test` → Complete test with metadata
- `TestAssignmentCreate` → Assign test to candidate
- `TestAssignment` → Tracked assignment with status

### Question Models
- `MCQQuestion` → Multiple choice question
- `CodingProblem` → Coding problem definition
- `TestQuestion` → Question in a test (ordering & marks)

### Answer Models
- `TestAnswer` → Candidate's answer (MCQ or coding)
- `MCQAnswer` → MCQ answer with correctness
- `CodeSubmission` → Code submission with execution results

### Analysis Models
- `Submission` → Input for Gemini API
- `AnalysisResult` → Output from Gemini API
- `CodeReviewResult` → Detailed code review
- `CodeAnalysisStyle`, `CodeComplexityAnalysis`, etc. → Review sections

### Report Models
- `CandidateReportData` → Complete test report
- `MCQReportSection` → MCQ section of report
- `CodingReportSection` → Coding section of report
- `ProctoringData` → Proctoring metrics

### Skill Models
- `SkillExtractionRequest` → JD input for skill extraction
- `SkillExtractionResult` → Extracted skills
- `CandidateSkillMatch` → Skill matching results

## 🔄 Data Flow Examples

### Example 1: Creating and Taking a Test

```
Admin                          Candidate
  │                               │
  ├─ POST /api/tests             │
  │  TestCreate (Pydantic)        │
  │  ↓                            │
  ├─ INSERT tests table           │
  │  Test (SQLAlchemy)            │
  │                               │
  ├─ POST /api/assignments        │
  │  TestAssignmentCreate (Pydantic)
  │  ↓                            │
  ├─ INSERT test_assignments table│
  │  TestAssignment (SQLAlchemy)  │
  │                               │
  │                          ├─ GET /api/assignments/{id}
  │                          │ TestAssignment (Pydantic response)
  │                          │
  │                          ├─ POST /api/answer/mcq
  │                          │ selected_option: "A"
  │                          │ ↓
  │                          ├─ INSERT test_answers table
  │                          │ TestAnswer (SQLAlchemy)
  │                          │
  │                          ├─ POST /api/coding/submit
  │                          │ CodeSubmission (Pydantic)
  │                          │ ↓
  │                          ├─ INSERT code_submissions table
  │                          │ CodeSubmission (SQLAlchemy)
  │                          │
  │                          ├─ POST /api/submit
  │                          │ Generate report
  │                          │ ↓
  │                          ├─ INSERT candidate_reports table
  │                          │ CandidateReport (SQLAlchemy)
  │                          │
  │                          └─ GET /api/reports/{id}
  │                            CandidateReportData (Pydantic response)
```

### Example 2: Code Analysis Pipeline

```
CodeSubmission (DB)
    ↓
convert_code_submission_to_analysis_request()
    ↓
Submission (Pydantic for Gemini API)
    ↓
Gemini API call
    ↓
AnalysisResult (Pydantic from Gemini)
    ↓
convert_analysis_result_to_test_answer_enrichment()
    ↓
TestAnswer.ai_analysis = detailed_analysis
TestAnswer.code_quality_score = total_score
    ↓
UPDATE test_answers table
```

## 📋 Database Tables

### Core Tables (20 total)

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `users` | User accounts | user_id, email, role |
| `candidate_profiles` | Extended candidate info | skills, experience |
| `tests` | Test definitions | test_id, test_name, duration |
| `mcq_questions` | MCQ questions | question_text, options, correct |
| `coding_questions` | Coding problems | title, description, test_cases |
| `test_questions` | Questions in test | test_id, question_id, order |
| `test_assignments` | Test to candidate mapping | assignment_id, status |
| `test_answers` | Candidate answers | answer_id, score, code_output |
| `code_submissions` | Code submissions | submission_id, code, output |
| `code_drafts` | Auto-saved drafts | draft_id, code, cursor_position |
| `candidate_reports` | Generated reports | report_id, percentage, grade |
| `code_analysis_results` | AI analysis | analysis_id, total_score |
| `skill_extractions` | Extracted skills | extraction_id, skills |
| `candidate_skill_matches` | Skill matches | match_id, match_percentage |
| `proctoring_data` | Proctoring metrics | proctoring_id, flagged_faces |
| `proctoring_frame_captures` | Frame data | capture_id, frame_url |
| `audit_logs` | Action log | log_id, action, entity_type |

### Relationships

```
User (1) ──── (N) Test (created_by)
User (1) ──── (N) TestAssignment (candidate)
User (1) ──── (N) TestAnswer (candidate)
User (1) ──── (N) CodeSubmission (candidate)
User (1) ──── (N) CandidateReport (candidate)

Test (1) ──── (N) TestQuestion
Test (1) ──── (N) TestAssignment
Test (1) ──── (N) TestAnswer
Test (1) ──── (N) CandidateReport

TestQuestion ──── MCQQuestion or CodingQuestion

TestAssignment (1) ──── (N) TestAnswer
TestAssignment (1) ──── (1) ProctoringData

MCQQuestion (1) ──── (N) TestQuestion
CodingQuestion (1) ──── (N) TestQuestion
CodingQuestion (1) ──── (N) CodeSubmission

CodeSubmission (1) ──── (1) CodeAnalysisResult
CodeSubmission (1) ──── (1) TestAnswer (code_submission_id)

SkillExtraction (1) ──── (N) CandidateSkillMatch
```

## 📖 Enum Values

All enums are synchronized across Pydantic and SQLAlchemy:

```python
LanguageEnum: python, java, sql, pyspark, javascript, cpp, csharp
DifficultyEnum: easy, medium, hard
TestStatusEnum: active, inactive, completed, draft, published
QuestionTypeEnum: multiple_choice, coding, true_false, unified
AssignmentStatusEnum: pending, scheduled, in_progress, completed, expired
CodeExecutionStatusEnum: pending, success, error, timeout, compilation_error, runtime_error
RoleEnum: admin, candidate, reviewer, super_admin
```

## 🔐 Security Considerations

1. **Field Validation**: Pydantic validates all API inputs
2. **Foreign Keys**: Database enforces referential integrity
3. **Enum Values**: No invalid status values accepted
4. **Timestamps**: All mutations tracked with created_at/updated_at
5. **Audit Logging**: Important actions logged in audit_logs

## ⚡ Performance

### Indexes (15+ indexes)
- User lookups: `idx_users_email`, `idx_users_role`
- Assignment queries: `idx_assignments_candidate_status`
- Test queries: `idx_tests_status`, `idx_tests_created_by`
- Question lookups: `idx_mcq_difficulty`, `idx_coding_language`
- Report queries: `idx_reports_candidate`, `idx_reports_test`

### Optimization Tips
1. Use eager loading for relationships:
   ```python
   from sqlalchemy.orm import joinedload
   test = db.query(SQLTest).options(
       joinedload(SQLTest.questions)
   ).first()
   ```

2. Batch insert operations:
   ```python
   db.bulk_insert_mappings(SQLTestAnswer, answer_list)
   ```

3. Use read replicas for reports

## 🧪 Testing

```python
from unittest.mock import Mock
from shared.models import Test

# Mock Pydantic model
mock_test = Mock(spec=Test)
mock_test.test_id = uuid.uuid4()
mock_test.test_name = "Test Name"

# Mock SQLAlchemy model
mock_db_test = Mock(spec=SQLTest)
mock_db_test.test_id = uuid.uuid4()
```

## 📝 Documentation References

- **MODEL_MAPPING.md** → Complete field mappings and relationships
- **INTEGRATION_GUIDE.md** → Real-world usage examples
- **schema.sql** → PostgreSQL DDL
- **__init__.py** → Module docstring with examples

## 🔧 Common Operations

### Query by ID
```python
user = db.query(SQLUser).filter_by(user_id=user_id).first()
```

### Query with relationships
```python
test = db.query(SQLTest).filter_by(test_id=test_id).first()
questions = test.questions  # Lazy load relationship
```

### Create and save
```python
user = SQLUser(user_id=uuid.uuid4(), email="test@example.com", ...)
db.add(user)
db.commit()
```

### Update
```python
assignment.status = AssignmentStatusEnum.completed
assignment.submitted_at = datetime.utcnow()
db.commit()
```

### Delete
```python
db.delete(test)
db.commit()
```

## 🆘 Troubleshooting

### Foreign Key Violations
```python
# Check referenced record exists
if not db.query(SQLTest).filter_by(test_id=test_id).first():
    raise ValueError("Test not found")
```

### Enum Mismatches
```python
# Use enum, not string
code_status = CodeExecutionStatusEnum.pending  # ✓ Correct
# NOT: code_status = "pending"  # ✗ Wrong
```

### Lazy Loading Issues
```python
# Access relationships within session
test = db.query(SQLTest).first()
questions = test.questions  # Within session ✓

# NOT after session closed
db.close()
questions = test.questions  # Will fail ✗
```

## 📦 Dependencies

```
sqlalchemy>=2.0
pydantic>=2.0
psycopg[binary]>=3.1
python-dotenv
```

## 📄 License

Part of Talentshire Technical Assessment Platform

## 🤝 Contributing

When adding new models:
1. Add to both `models.py` (Pydantic) and `database_models.py` (SQLAlchemy)
2. Update enums in both places
3. Add conversion functions to `model_converters.py`
4. Document in `MODEL_MAPPING.md`
5. Add SQL to `schema.sql`

---

**Last Updated**: December 2025  
**Version**: 1.0  
**Status**: Production Ready
