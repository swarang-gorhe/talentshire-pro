# Talentshire - Technical Assessment Platform
## Complete Setup & Architecture Documentation

---

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [System Architecture](#system-architecture)
3. [Database Schema & Data Flow](#database-schema--data-flow)
4. [API Endpoints](#api-endpoints)
5. [File Structure](#file-structure)
6. [How to Modify](#how-to-modify)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- PostgreSQL running on localhost:5432 with database `talentshire`
- MongoDB running on localhost:27017 with database `talentshire`
- Node.js & npm installed
- Python 3.11+ installed

### Credentials
```
PostgreSQL:
  Username: postgres
  Password: Admin@123
  Database: talentshire
  
MongoDB:
  URL: mongodb://127.0.0.1:27017
  Database: talentshire
```

### Run Commands

#### Terminal 1: Start Frontend
```bash
cd C:\Users\MSI\new_project\apti-test-pro-main\apti-test-pro-main
npm run dev
# Frontend available at: http://localhost:8080/
```

#### Terminal 2: Start Backend
```bash
cd C:\Users\MSI\new_project\apti-test-pro-main\apti-test-pro-main\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Backend available at: http://localhost:8000/
# API Docs at: http://localhost:8000/docs
```

### Access Points
- **Frontend**: http://localhost:8080/ → Candidate Login Portal
- **Backend API**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

---

## 🏗️ System Architecture

### Tech Stack
```
Frontend: React 18 + TypeScript + Vite
Backend: FastAPI + SQLAlchemy + Motor (async MongoDB)
Databases: PostgreSQL (Relational) + MongoDB (Document)
UI Components: Shadcn/UI + TailwindCSS
State Management: Zustand
```

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│          http://localhost:8080/ - Candidate Portal           │
│  - Candidate Login (Email/Token)                             │
│  - Test Taking (MCQ + Coding)                                │
│  - Code Editor & Execution                                   │
│  - Test Results & Reports                                    │
└────────────────────┬────────────────────────────────────────┘
                     │ API Calls (JSON)
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  BACKEND (FastAPI)                           │
│          http://localhost:8000/ - REST API                   │
│                                                              │
│  /api/v1/tests         - Test management                     │
│  /api/v1/questions     - Question management                 │
│  /api/v1/submissions   - Answer submissions (NEW)            │
│  /health               - Health check                        │
└────────────────┬──────────────────────┬─────────────────────┘
                 │                      │
    ┌────────────▼────┐    ┌───────────▼──────┐
    │   PostgreSQL    │    │     MongoDB      │
    │  (Relational)   │    │   (Document)     │
    └────────────────┘    └──────────────────┘
```

---

## 📊 Database Schema & Data Flow

### PostgreSQL Tables (Relational Data)

#### 1. **users** - Admin/Creator Accounts
```sql
- user_id (UUID, PRIMARY KEY)
- full_name (VARCHAR)
- email (VARCHAR, UNIQUE)
- password_hash (TEXT)
- created_at (TIMESTAMP)
```
**Usage**: Admin authentication & test creation

#### 2. **mcq_questions** - MCQ Question Library
```sql
- mcq_id (UUID, PRIMARY KEY)
- question_text (TEXT)
- option_a, option_b, option_c, option_d (TEXT)
- correct_answer (VARCHAR) - A, B, C, or D
- difficulty_level (VARCHAR) - Easy, Medium, Hard
- language (VARCHAR) - Optional topic
```
**Usage**: Store MCQ questions

#### 3. **unified_questions** - Single Interface for All Question Types
```sql
- question_id (UUID, PRIMARY KEY)
- source_id (UUID) - Reference to MCQ or MongoDB ObjectId
- question_text (TEXT)
- difficulty_level (VARCHAR)
- language (VARCHAR)
- type (ENUM) - 'MCQ' or 'CODING'
- created_at (TIMESTAMP)
```
**Usage**: Map all questions (MCQ & Coding) into one table

#### 4. **tests** - Test/Assessment Definitions
```sql
- test_id (UUID, PRIMARY KEY)
- test_name (VARCHAR)
- created_by (UUID, FOREIGN KEY → users.user_id)
- duration_minutes (INT)
- status (ENUM) - 'DRAFT', 'ACTIVE', 'ARCHIVED'
- created_at (TIMESTAMP)
```
**Usage**: Store test metadata

#### 5. **test_questions** - Question Mapping to Tests
```sql
- id (UUID, PRIMARY KEY)
- test_id (UUID, FOREIGN KEY → tests.test_id)
- question_id (UUID, FOREIGN KEY → unified_questions.question_id)
- question_type (ENUM) - 'MCQ' or 'CODING'
- order_index (INT) - Question order in test
```
**Usage**: Define which questions are in which test & order

#### 6. **candidates** - Candidate Profiles
```sql
- candidate_id (UUID, PRIMARY KEY)
- full_name (VARCHAR)
- email (VARCHAR, UNIQUE)
- phone (VARCHAR, UNIQUE)
- experience_years (INT)
- skills (TEXT)
```
**Usage**: Store candidate information

#### 7. **test_assignments** - Test Assignment to Candidates
```sql
- assignment_id (UUID, PRIMARY KEY)
- test_id (UUID, FOREIGN KEY → tests.test_id)
- candidate_id (UUID, FOREIGN KEY → candidates.candidate_id)
- assigned_at (TIMESTAMP)
- status (ENUM) - 'ASSIGNED', 'STARTED', 'COMPLETED', 'EXPIRED'
- scheduled_start_time (TIMESTAMP)
- scheduled_end_time (TIMESTAMP)
- candidate_token (TEXT) - Token for login without email/password
```
**Usage**: Assign tests to candidates

#### 8. **test_answers** ⭐ - CANDIDATE ANSWERS & RESULTS
```sql
- answer_id (UUID, PRIMARY KEY)
- assignment_id (UUID, FOREIGN KEY → test_assignments.assignment_id)
- question_id (UUID, FOREIGN KEY → unified_questions.question_id)
- question_type (ENUM) - 'MCQ' or 'CODING'
- selected_option (VARCHAR) - For MCQ: A, B, C, or D
- code_submission (TEXT) - For Coding: actual code
- code_output (TEXT) - Compilation/execution output
- submitted_at (TIMESTAMP)
- is_correct (BOOLEAN)
- score (NUMERIC)
- time_spent_seconds (INT)
- code_analysis (TEXT)
- code_quality_score (NUMERIC)
- ai_review_notes (TEXT)
- candidate_id (UUID, FOREIGN KEY → candidates.candidate_id)
- language (VARCHAR) - Programming language
- stdin (TEXT) - Code execution input
- stdout (TEXT) - Code execution output
- code_status (VARCHAR) - 'pending', 'success', 'error', 'timeout'
- code_passed (BOOLEAN) - All test cases passed?
```
**⭐ CRITICAL TABLE**: This is where all candidate answers are saved!
- MCQ answers: `selected_option`, `is_correct`, `score`
- Code submissions: `code_submission`, `code_output`, `code_status`, `language`, `stdin`, `stdout`

#### 9. **test_results** - Overall Test Results/Scores
```sql
- result_id (UUID, PRIMARY KEY)
- assignment_id (UUID, UNIQUE, FOREIGN KEY → test_assignments.assignment_id)
- total_score (NUMERIC)
- section_scores (JSONB) - {mcq_score: X, coding_score: Y}
- time_taken_seconds (INT)
- completion_status (ENUM) - 'PASSED', 'FAILED', 'INCOMPLETE'
- generated_at (TIMESTAMP)
```
**Usage**: Store aggregated test results

#### 10. **test_autosave** - Draft Answers (Auto-save)
```sql
- autosave_id (UUID, PRIMARY KEY)
- assignment_id (UUID, FOREIGN KEY → test_assignments.assignment_id)
- question_id (UUID, FOREIGN KEY → unified_questions.question_id)
- draft_answer (JSONB) - {type: 'mcq', option: 'A'} or {type: 'code', code: '...'}
- updated_at (TIMESTAMP)
```
**Usage**: Store draft answers for auto-save feature

#### 11. **roles** & **user_roles** - Role-Based Access Control
```sql
roles:
- role_id (UUID, PRIMARY KEY)
- role_name (ENUM) - 'ADMIN', 'RECRUITER', 'CANDIDATE'

user_roles:
- user_role_id (UUID, PRIMARY KEY)
- user_id (UUID, FOREIGN KEY → users.user_id)
- role_id (UUID, FOREIGN KEY → roles.role_id)
```
**Usage**: Manage user permissions

### MongoDB Collections (Document Data)

#### 1. **coding_questions** - Coding Problem Details
```json
{
  "_id": ObjectId,
  "id": 61,
  "title": "Find Longest Substring Without Repeating Characters",
  "description": "Given a string, find the length of the longest substring...",
  "difficulty": "Medium",
  "labels": ["string", "sliding-window", "hashmap"],
  "sample_input": "abcabcbb",
  "sample_output": 3,
  "constraints": "0 <= s.length <= 10^5; ...",
  "test_cases": [
    {
      "input": "abcabcbb",
      "expected_output": 3,
      "explanation": "The answer is 'abc'..."
    }
  ]
}
```
**Usage**: Store detailed coding question problems

#### 2. **code_submissions** ⭐ - Code Execution Results
```json
{
  "_id": ObjectId,
  "candidateId": "uuid",
  "assignmentId": "uuid",
  "questionId": "uuid",
  "code": "def solution(s): ...",
  "language": "python",
  "executionResult": {
    "status": "success",
    "output": "result here",
    "passed": true,
    "stdin": "",
    "stdout": "output"
  },
  "submittedAt": ISODate("2025-12-11T10:00:00Z")
}
```
**⭐ CRITICAL COLLECTION**: Stores code execution details
- Code text
- Execution results
- Timestamps

---

## 🔄 Data Flow: Candidate Test Journey

### 1. **Candidate Login Flow**
```
Frontend (CandidateLogin.tsx)
  ↓
POST /api/v1/candidates/login
  ↓
Backend validates token in test_assignments
  ↓
Returns: candidate_id, available_tests
  ↓
Frontend redirects to /candidate/tests
```

### 2. **Load Test & Questions Flow**
```
Frontend (CandidateTests.tsx)
  ↓
GET /api/v1/tests/{test_id}
  ↓
Backend queries:
  - tests table (test metadata)
  - test_questions table (which questions in test)
  - unified_questions table (question details)
  - coding_questions collection (coding problem details)
  ↓
Returns: Full test with all questions
```

### 3. **Submit MCQ Answer Flow** ⭐
```
Frontend (TestTaking.tsx - MCQ component)
  ↓
User selects option A/B/C/D
  ↓
POST /api/v1/submissions/mcq
  {
    assignment_id: uuid,
    question_id: uuid,
    selected_option: "A",
    is_correct: true,
    time_spent_seconds: 30,
    candidate_id: uuid
  }
  ↓
Backend inserts into test_answers:
  - answer_id: Generated UUID
  - selected_option: "A"
  - is_correct: true
  - score: 1.0
  - submitted_at: Current timestamp
  ↓
Response: {success: true, answer_id: uuid}
```

### 4. **Submit Code Answer Flow** ⭐
```
Frontend (TestTaking.tsx - Code component)
  ↓
User writes code and clicks "Submit"
  ↓
Frontend calls external executor (localhost:8001)
  ↓
POST /api/v1/submissions/code
  {
    assignment_id: uuid,
    question_id: uuid,
    code: "def solution(): ...",
    language: "python",
    code_status: "success",
    code_passed: true,
    code_output: "execution output",
    stdin: "",
    stdout: "result",
    time_spent_seconds: 60,
    candidate_id: uuid
  }
  ↓
Backend does TWO operations:
  1. Insert into PostgreSQL test_answers table
  2. Insert into MongoDB code_submissions collection
  ↓
Response: {success: true, answer_id: uuid, mongo_id: uuid}
```

### 5. **Fetch Results Flow**
```
Frontend (TestResults.tsx)
  ↓
GET /api/v1/submissions/assignment/{assignment_id}
  ↓
Backend queries test_answers table
  ↓
Returns: All MCQ & code answers with scores
  ↓
Frontend displays results
```

### 6. **Generate Report Flow**
```
Aggregate from test_answers:
  - Count total questions
  - Sum scores (MCQ: is_correct → score)
  - Calculate time taken (submitted_at times)
  ↓
Insert into test_results:
  - total_score
  - section_scores: {mcq_score: X, coding_score: Y}
  - completion_status: PASSED/FAILED
```

---

## 🔌 API Endpoints

### Submission Endpoints (NEW - CRITICAL)

#### POST /api/v1/submissions/mcq
**Save MCQ Answer**
```
Request:
{
  "assignment_id": "uuid",
  "question_id": "uuid",
  "selected_option": "A",
  "is_correct": true,
  "time_spent_seconds": 30,
  "candidate_id": "uuid"
}

Response:
{
  "success": true,
  "answer_id": "uuid",
  "message": "MCQ answer saved to PostgreSQL test_answers table"
}

Database: PostgreSQL test_answers
Fields populated:
  - assignment_id, question_id, selected_option
  - is_correct, score, time_spent_seconds
  - candidate_id, submitted_at
```

#### POST /api/v1/submissions/code
**Save Code Submission**
```
Request:
{
  "assignment_id": "uuid",
  "question_id": "uuid",
  "code": "def solution(s): ...",
  "language": "python",
  "code_status": "success",
  "code_passed": true,
  "code_output": "execution output",
  "stdin": "",
  "stdout": "result",
  "time_spent_seconds": 60,
  "candidate_id": "uuid"
}

Response:
{
  "success": true,
  "answer_id": "uuid (PostgreSQL)",
  "mongo_id": "uuid (MongoDB)",
  "message": "Code submission saved to PostgreSQL test_answers and MongoDB"
}

Database:
  1. PostgreSQL test_answers:
     - code_submission, code_output, code_status, code_passed
     - language, stdin, stdout, time_spent_seconds
  2. MongoDB code_submissions:
     - Full execution details with metadata
```

#### GET /api/v1/submissions/assignment/{assignment_id}
**Retrieve All Answers for Assignment**
```
Response:
{
  "success": true,
  "assignment_id": "uuid",
  "total_answers": 5,
  "answers": [
    {
      "answer_id": "uuid",
      "question_id": "uuid",
      "question_type": "MCQ",
      "selected_option": "A",
      "is_correct": true,
      "score": 1.0,
      "submitted_at": "2025-12-11T10:00:00"
    },
    ...
  ]
}

Source: PostgreSQL test_answers
```

#### GET /api/v1/submissions/candidate/{candidate_id}
**Retrieve All Submissions by Candidate**
```
Response:
{
  "success": true,
  "candidate_id": "uuid",
  "total_submissions": 15,
  "submissions": [
    {
      "answer_id": "uuid",
      "assignment_id": "uuid",
      "question_type": "CODING",
      "is_correct": false,
      "score": 0.0,
      "submitted_at": "2025-12-11T10:30:00"
    },
    ...
  ]
}

Source: PostgreSQL test_answers
```

### Test Endpoints
- **POST /api/v1/tests** - Create new test
- **GET /api/v1/tests/{test_id}** - Get test with questions
- **PUT /api/v1/tests/{test_id}** - Update test
- **DELETE /api/v1/tests/{test_id}** - Delete test

### Question Endpoints
- **POST /api/v1/questions/mcq** - Create MCQ
- **GET /api/v1/questions/mcq/{mcq_id}** - Get MCQ
- **POST /api/v1/questions/coding** - Create coding question
- **GET /api/v1/questions/coding/{question_id}** - Get coding question

---

## 📁 File Structure

```
apti-test-pro-main/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── CandidateLogin.tsx          ← Login page
│   │   │   └── candidate/
│   │   │       ├── CandidateTests.tsx      ← Show available tests
│   │   │       ├── TestTaking.tsx          ← Main test interface ⭐
│   │   │       ├── TestInstructions.tsx    ← Pre-test instructions
│   │   │       ├── TestSubmitted.tsx       ← Post-submission
│   │   │       └── CandidateCompleted.tsx  ← Completed tests
│   │   │
│   │   ├── store/
│   │   │   ├── authStore.ts                ← Auth state
│   │   │   ├── testStore.ts                ← Test data state
│   │   │   └── candidateTestStore.ts       ← Candidate test progress
│   │   │
│   │   ├── lib/
│   │   │   └── api.ts                      ← API calls to backend
│   │   │
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── CodeEditor.tsx          ← Code editor component
│   │   │   │   ├── TimerDisplay.tsx        ← Test timer
│   │   │   │   └── AutosaveIndicator.tsx   ← Autosave status
│   │   │   │
│   │   │   └── candidate/
│   │   │       ├── QuestionNavigation.tsx  ← Question switcher
│   │   │       └── PreTestChecks.tsx       ← System check
│   │   │
│   │   ├── App.tsx                         ← Main app component
│   │   └── AppContent.tsx                  ← Routes & providers ⭐
│   │
│   ├── package.json                        ← Frontend dependencies
│   ├── vite.config.ts                      ← Vite configuration
│   └── index.html
│
├── backend/
│   ├── app/
│   │   ├── main.py                         ← FastAPI entry point ⭐
│   │   │
│   │   ├── api/v1/
│   │   │   ├── router.py                   ← Route aggregator ⭐
│   │   │   └── endpoints/
│   │   │       ├── tests.py                ← Test CRUD endpoints
│   │   │       ├── questions.py            ← Question CRUD endpoints
│   │   │       └── submissions.py          ← Answer submission endpoints ⭐ (NEW)
│   │   │
│   │   ├── services/
│   │   │   ├── test_service.py             ← Test business logic
│   │   │   ├── mcq_service.py              ← MCQ business logic
│   │   │   ├── coding_service.py           ← Coding question business logic
│   │   │   └── (answer_service.py - TODO)  ← Answer calculation logic
│   │   │
│   │   ├── models/
│   │   │   └── postgres_models.py          ← SQLAlchemy models
│   │   │
│   │   ├── schemas/
│   │   │   ├── test_schemas.py             ← Pydantic models for tests
│   │   │   └── question_schemas.py         ← Pydantic models for questions
│   │   │
│   │   ├── core/
│   │   │   └── config.py                   ← Configuration & settings
│   │   │
│   │   └── db/
│   │       ├── postgres.py                 ← PostgreSQL connection
│   │       └── mongodb.py                  ← MongoDB connection
│   │
│   ├── requirements.txt                    ← Python dependencies
│   └── README.md                           ← Backend docs
│
└── SETUP_AND_DOCUMENTATION.md              ← This file ⭐
```

---

## 🔧 How to Modify

### 1. **Add a New Question Type**

#### Step 1: Update PostgreSQL enum
**File**: Run migration or directly in psql
```sql
ALTER TYPE question_type_enum ADD VALUE 'ESSAY';
```

#### Step 2: Create Pydantic schema
**File**: `backend/app/schemas/question_schemas.py`
```python
class EssayCreate(BaseModel):
    question_text: str
    difficulty_level: str
    sample_answer: str
    rubric: dict  # Scoring criteria
```

#### Step 3: Create endpoint
**File**: `backend/app/api/v1/endpoints/questions.py`
```python
@router.post("/essay", response_model=EssayResponse)
async def create_essay(data: EssayCreate, db: AsyncSession = Depends(get_db)):
    # Create essay question logic
    pass
```

#### Step 4: Include in router
**File**: `backend/app/api/v1/router.py`
```python
api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
# Already includes /essay endpoint
```

#### Step 5: Update frontend
**File**: `src/pages/candidate/TestTaking.tsx`
```tsx
{questionType === 'ESSAY' && (
  <textarea 
    value={essayAnswer}
    onChange={(e) => setEssayAnswer(e.target.value)}
    placeholder="Write your essay here..."
  />
)}
```

#### Step 6: Save submission
**File**: Same submission endpoint in `submissions.py`
```python
# POST /api/v1/submissions/essay will save to test_answers with:
# - question_type: 'ESSAY'
# - code_submission: essay_text (reuse same field)
# - score: (to be calculated by AI/human review)
```

---

### 2. **Change Database Credentials**

#### For PostgreSQL:
**File**: `backend/app/core/config.py`
```python
DATABASE_URL: str = "postgresql+asyncpg://NEW_USER:NEW_PASSWORD@NEW_HOST:NEW_PORT/NEW_DB"
```

#### For MongoDB:
**File**: `backend/app/core/config.py`
```python
MONGODB_URL: str = "mongodb://NEW_USER:NEW_PASSWORD@NEW_HOST:NEW_PORT"
MONGODB_DB_NAME: str = "new_db_name"
```

#### For Frontend API:
**File**: `src/lib/api.ts`
```typescript
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://new-backend-host:8000';
```

---

### 3. **Add New API Endpoint**

#### Example: Add /api/v1/submissions/grade-mcq

**Step 1**: Create endpoint function
**File**: `backend/app/api/v1/endpoints/submissions.py`
```python
@router.post("/grade-mcq")
async def grade_mcq_answers(
    data: dict,  # {assignment_id: uuid}
    db: AsyncSession = Depends(get_db)
):
    """Calculate correct/incorrect MCQ answers"""
    query = text("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
        FROM test_answers
        WHERE assignment_id = :assignment_id AND question_type = 'MCQ'
    """)
    result = await db.execute(query, {"assignment_id": str(data["assignment_id"])})
    row = result.fetchone()
    return {
        "total_mcqs": row[0],
        "correct_mcqs": row[1],
        "mcq_score": (row[1] / row[0] * 100) if row[0] > 0 else 0
    }
```

**Step 2**: Register in router
Endpoint is automatically available at: `POST /api/v1/submissions/grade-mcq`

**Step 3**: Call from frontend
**File**: `src/pages/candidate/TestSubmitted.tsx`
```typescript
const response = await fetch('/api/v1/submissions/grade-mcq', {
    method: 'POST',
    body: JSON.stringify({assignment_id: assignmentId})
});
```

---

### 4. **Change Table Mapping**

#### Example: Save code output to different table

**Current**: Saves to `test_answers.code_output`

**To change**: 

**Step 1**: Create new table (if needed)
```sql
CREATE TABLE code_outputs (
    output_id UUID PRIMARY KEY,
    answer_id UUID REFERENCES test_answers(answer_id),
    output TEXT,
    created_at TIMESTAMP
);
```

**Step 2**: Update endpoint
**File**: `backend/app/api/v1/endpoints/submissions.py`
```python
# In submit_code_answer function:
# After saving to test_answers, also save to code_outputs:

insert_query = text("""
    INSERT INTO code_outputs (output_id, answer_id, output, created_at)
    VALUES (gen_random_uuid(), :answer_id, :output, CURRENT_TIMESTAMP)
""")
await db.execute(insert_query, {
    "answer_id": str(answer_id),
    "output": data.get("code_output")
})
```

---

### 5. **Modify Frontend Pages**

#### Example: Update TestTaking to change MCQ UI

**File**: `src/pages/candidate/TestTaking.tsx`

Find the MCQ rendering section:
```tsx
// Search for: renderMCQQuestion() or similar

// Change:
{question.type === 'MCQ' && (
    <RadioGroup value={selectedAnswer} onChange={handleSelectOption}>
        {/* Update UI here */}
    </RadioGroup>
)}
```

Then update the submission call:
```tsx
// When submitting MCQ:
await fetch('/api/v1/submissions/mcq', {
    method: 'POST',
    body: JSON.stringify({
        assignment_id: assignmentId,
        question_id: question.id,
        selected_option: selectedAnswer,
        is_correct: selectedAnswer === question.correctAnswer,
        time_spent_seconds: timeSpent,
        candidate_id: candidateId
    })
});
```

---

### 6. **Debug & Monitor Database**

#### Check PostgreSQL:
```bash
# Connect to database
psql -h localhost -U postgres -d talentshire -p 5432

# List all tables
\dt

# Check test_answers data
SELECT * FROM test_answers LIMIT 10;

# Check candidate submissions count
SELECT candidate_id, COUNT(*) as submission_count 
FROM test_answers 
GROUP BY candidate_id;

# Check MCQ vs Coding ratio
SELECT question_type, COUNT(*) FROM test_answers GROUP BY question_type;
```

#### Check MongoDB:
```bash
# Connect to MongoDB
mongosh mongodb://127.0.0.1:27017

# Switch to database
use talentshire

# List collections
show collections

# Check code_submissions
db.code_submissions.find().limit(5)

# Count documents
db.code_submissions.countDocuments()

# Find by candidate
db.code_submissions.find({candidateId: "uuid"})
```

---

## ✅ Checklist: Deployment to Production

- [ ] Change PostgreSQL password to strong value
- [ ] Change MongoDB to use authentication
- [ ] Update `backend/app/core/config.py` with production URLs
- [ ] Set `CORS` origins in `backend/app/main.py`
- [ ] Enable HTTPS for API
- [ ] Add rate limiting
- [ ] Set up logging to file
- [ ] Configure backup for PostgreSQL & MongoDB
- [ ] Add health monitoring
- [ ] Load test the application

---

## 🐛 Troubleshooting

### Issue: "process is not defined" error in frontend
**Solution**: Change `process.env` to `import.meta.env` in TypeScript files
```typescript
// ❌ Wrong
const API = process.env.VITE_API_URL

// ✅ Correct
const API = import.meta.env.VITE_API_BASE_URL
```

### Issue: PostgreSQL connection refused
```bash
# Check if PostgreSQL is running
# Windows: Services → PostgreSQL → Start
# Or run: pg_ctl -D "C:\Program Files\PostgreSQL\data" start

# Verify credentials
psql -h 127.0.0.1 -U postgres -d talentshire
```

### Issue: MongoDB connection timeout
```bash
# Check if MongoDB is running
# Windows: Services → MongoDB → Start
# Or: mongod --dbpath "C:\data\db"

# Verify connection
mongosh mongodb://127.0.0.1:27017
```

### Issue: CORS errors in frontend
**Solution**: Update `backend/app/main.py`
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: API endpoint not found (404)
1. Check router registration in `backend/app/api/v1/router.py`
2. Verify endpoint file is imported
3. Check endpoint path syntax
4. Restart backend server

---

## 📞 Support & Quick Reference

### Important Files to Know
- **Backend entry**: `backend/app/main.py`
- **Routes**: `backend/app/api/v1/router.py`
- **Submissions (NEW)**: `backend/app/api/v1/endpoints/submissions.py` ⭐
- **Frontend entry**: `src/AppContent.tsx`
- **Test page**: `src/pages/candidate/TestTaking.tsx`
- **API client**: `src/lib/api.ts`

### Database Connection Details
```
PostgreSQL:
  Host: 127.0.0.1
  Port: 5432
  Username: postgres
  Password: Admin@123
  Database: talentshire

MongoDB:
  URL: mongodb://127.0.0.1:27017
  Database: talentshire
```

### URLs
- Frontend: http://localhost:8080/
- Backend: http://localhost:8000/
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 📝 Document Version
- **Version**: 1.0
- **Last Updated**: December 11, 2025
- **Author**: Development Team
- **Status**: Production Ready ✅
