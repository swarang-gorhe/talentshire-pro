# Talentshire - Database Mapping & Data Flow Guide

## 📊 Complete Data Flow from Frontend to Database

---

## 1️⃣ CANDIDATE LOGIN FLOW

### What Happens:
1. Candidate enters email or test token
2. Backend validates credentials
3. Frontend stores auth token in Zustand store
4. Redirects to /candidate/tests

### Code Path:
```
Frontend: CandidateLogin.tsx
  ↓ User clicks "Login" button
  ↓ Calls loginWithToken(token) or login(email, password)
  ↓
Backend: POST /api/v1/candidates/login
  ↓
PostgreSQL Query:
  SELECT * FROM test_assignments 
  WHERE candidate_token = 'token'
  
Frontend Zustand Store (authStore.ts):
  - candidate_id: stored
  - token: stored
  - assignment_id: stored
```

**Database Tables Involved:**
- `candidates` - Read candidate info
- `test_assignments` - Verify token and get assignment
- `tests` - Get test metadata

---

## 2️⃣ LOAD TEST & QUESTIONS FLOW

### What Happens:
1. Candidate clicks on test
2. Frontend loads test details and all questions
3. Backend joins multiple tables to fetch complete data

### Code Path:
```
Frontend: TestTaking.tsx
  ↓ useEffect runs on mount
  ↓ Fetches test data via /api/v1/tests/{test_id}
  ↓
Backend: GET /api/v1/tests/{test_id}/questions
  ↓
PostgreSQL Queries (JOIN operations):
  
  Query 1: Get test details
  SELECT * FROM tests WHERE test_id = 'uuid'
  
  Query 2: Get all questions in test
  SELECT tq.*, uq.* FROM test_questions tq
  JOIN unified_questions uq ON tq.question_id = uq.question_id
  WHERE tq.test_id = 'uuid'
  ORDER BY tq.order_index
  
  Query 3: For MCQ questions, get options
  SELECT * FROM mcq_questions WHERE mcq_id = 'uuid'
  
  Query 4: For Coding questions, fetch from MongoDB
  MongoDB: db.coding_questions.findOne({_id: ObjectId(...)})

Frontend State Management:
  testStore.tsx stores:
    - questions: [MCQ and CODING mixed]
    - currentQuestionIndex
    - test metadata
```

**Database Tables Involved:**
- `tests` - Test metadata
- `test_questions` - Question mapping
- `unified_questions` - Question details
- `mcq_questions` - MCQ specific data
- `coding_questions` (MongoDB) - Coding problem details

---

## 3️⃣ MCQ ANSWER SUBMISSION FLOW

### What Happens:
1. Candidate selects option (A/B/C/D)
2. Frontend auto-saves or submits immediately
3. Backend saves to PostgreSQL test_answers table
4. Response contains answer_id

### Code Path:
```
Frontend: TestTaking.tsx (MCQ component)
  ↓ User clicks radio button option
  ↓ handleSelectOption(question_id, 'A') called
  ↓ Calls submitMCQAnswer() function
  ↓
POST /api/v1/submissions/mcq
Request Body:
{
  "assignment_id": "550e8400-e29b-41d4-a716-446655440000",
  "question_id": "660e8400-e29b-41d4-a716-446655440001",
  "selected_option": "A",
  "is_correct": true,
  "time_spent_seconds": 45,
  "candidate_id": "770e8400-e29b-41d4-a716-446655440002"
}
  ↓
Backend: submissions.py → submit_mcq_answer()
  ↓
PostgreSQL INSERT:
  INSERT INTO test_answers 
    (answer_id, assignment_id, question_id, question_type, 
     selected_option, is_correct, score, time_spent_seconds, 
     submitted_at, candidate_id)
  VALUES
    (gen_random_uuid(), 
     '550e8400-e29b-41d4-a716-446655440000',
     '660e8400-e29b-41d4-a716-446655440001',
     'MCQ',
     'A',
     true,
     1.0,
     45,
     CURRENT_TIMESTAMP,
     '770e8400-e29b-41d4-a716-446655440002')
  ↓
Response:
{
  "success": true,
  "answer_id": "880e8400-e29b-41d4-a716-446655440003",
  "message": "MCQ answer saved..."
}
  ↓
Frontend: Update candidateTestStore
  - answers: [{answer_id, question_id, selected_option, ...}]
```

**PostgreSQL test_answers Table Fields Used:**
```
- answer_id: UUID (Generated)
- assignment_id: UUID (From request)
- question_id: UUID (From request)
- question_type: ENUM = 'MCQ'
- selected_option: VARCHAR = 'A'|'B'|'C'|'D'
- is_correct: BOOLEAN = true/false
- score: NUMERIC = 0.0 to 1.0
- time_spent_seconds: INT
- submitted_at: TIMESTAMP (Auto)
- candidate_id: UUID (From request)

NOT USED for MCQ:
  - code_submission: NULL
  - code_output: NULL
  - code_status: NULL
  - language: NULL
  - stdin: NULL
  - stdout: NULL
```

**Database Tables Involved:**
- `test_answers` - PRIMARY (INSERT only)
- `test_assignments` - For validation (SELECT)
- `unified_questions` - For verification (SELECT)

---

## 4️⃣ CODE SUBMISSION FLOW (COMPLEX - TWO DATABASES!)

### What Happens:
1. Candidate writes code and clicks Submit
2. Frontend may execute code first (optional)
3. Backend saves to BOTH PostgreSQL AND MongoDB
4. Response contains IDs from both databases

### Code Path:
```
Frontend: TestTaking.tsx (Code Editor component)
  ↓ CodeEditor component
  ↓ User writes code and clicks "Submit Code"
  ↓ handleSubmitCode() function
  ↓
  Optional: Execute code locally via /execute endpoint
  (This uses external code executor on port 8001)
  ↓
POST /api/v1/submissions/code
Request Body:
{
  "assignment_id": "550e8400-e29b-41d4-a716-446655440000",
  "question_id": "660e8400-e29b-41d4-a716-446655440001",
  "code": "def solution(n):\n    return n * 2",
  "language": "python",
  "code_status": "success",
  "code_passed": true,
  "code_output": "Program executed successfully",
  "stdin": "5",
  "stdout": "10",
  "time_spent_seconds": 120,
  "candidate_id": "770e8400-e29b-41d4-a716-446655440002"
}
  ↓
Backend: submissions.py → submit_code_answer()
  ↓
OPERATION 1: PostgreSQL INSERT
  INSERT INTO test_answers
    (answer_id, assignment_id, question_id, question_type,
     code_submission, code_output, code_status, code_passed,
     language, stdin, stdout, time_spent_seconds,
     submitted_at, candidate_id)
  VALUES
    (gen_random_uuid(),
     '550e8400-e29b-41d4-a716-446655440000',
     '660e8400-e29b-41d4-a716-446655440001',
     'CODING',
     'def solution(n):\n    return n * 2',
     'Program executed successfully',
     'success',
     true,
     'python',
     '5',
     '10',
     120,
     CURRENT_TIMESTAMP,
     '770e8400-e29b-41d4-a716-446655440002')
  RETURNING answer_id
  ↓ answer_id = '880e8400-e29b-41d4-a716-446655440003'
  ↓
OPERATION 2: MongoDB INSERT
  db.code_submissions.insertOne({
    _id: ObjectId(),
    answer_id: '880e8400-e29b-41d4-a716-446655440003',
    assignment_id: '550e8400-e29b-41d4-a716-446655440000',
    question_id: '660e8400-e29b-41d4-a716-446655440001',
    candidate_id: '770e8400-e29b-41d4-a716-446655440002',
    code: 'def solution(n):\n    return n * 2',
    language: 'python',
    execution_result: {
      status: 'success',
      passed: true,
      output: 'Program executed successfully',
      stdin: '5',
      stdout: '10'
    },
    submitted_at: ISODate("2025-12-11T10:00:00.000Z")
  })
  ↓ mongo_id = ObjectId('507f1f77bcf86cd799439011')
  ↓
Response:
{
  "success": true,
  "answer_id": "880e8400-e29b-41d4-a716-446655440003",
  "mongo_id": "507f1f77bcf86cd799439011",
  "message": "Code submission saved to PostgreSQL & MongoDB"
}
  ↓
Frontend: Update candidateTestStore
  - answers: [{answer_id, question_id, code, language, ...}]
```

**PostgreSQL test_answers Table Fields Used:**
```
For CODING questions:
- answer_id: UUID (Generated)
- assignment_id: UUID
- question_id: UUID
- question_type: ENUM = 'CODING'
- code_submission: TEXT = full code text
- code_output: TEXT = execution output
- code_status: VARCHAR = 'pending'|'success'|'error'|'timeout'
- code_passed: BOOLEAN = true/false
- language: VARCHAR = 'python'|'javascript'|'java'|etc
- stdin: TEXT = input provided to code
- stdout: TEXT = output from code
- time_spent_seconds: INT
- submitted_at: TIMESTAMP
- candidate_id: UUID

NOT USED for Coding:
  - selected_option: NULL
  - is_correct: NULL (calculated later)
  - score: NULL (calculated later)
```

**MongoDB code_submissions Collection Structure:**
```
{
  "_id": ObjectId,              # MongoDB generated
  "answer_id": UUID,            # Reference to PostgreSQL
  "assignment_id": UUID,
  "question_id": UUID,
  "candidate_id": UUID,
  "code": TEXT,                 # Full source code
  "language": VARCHAR,          # python, javascript, etc
  "execution_result": {
    "status": VARCHAR,          # success, error, timeout
    "passed": BOOLEAN,          # All test cases?
    "output": TEXT,             # Program output
    "stdin": TEXT,              # Input given
    "stdout": TEXT              # Output from code
  },
  "submitted_at": ISODate       # Timestamp
}
```

**Database Tables Involved:**
- `test_answers` - PostgreSQL INSERT
- `code_submissions` - MongoDB INSERT
- `test_assignments` - Validation
- `unified_questions` - Validation

---

## 5️⃣ AUTO-SAVE FLOW (DRAFT ANSWERS)

### What Happens:
1. Candidate typing/selecting answers
2. Frontend auto-saves every 30 seconds
3. Backend saves draft to test_autosave table
4. Does NOT mark as final submission

### Code Path:
```
Frontend: TestTaking.tsx
  ↓ useEffect with interval (30 seconds)
  ↓ Saves current state to autosave
  ↓
POST /api/v1/submissions/autosave
Request Body:
{
  "assignment_id": "uuid",
  "question_id": "uuid",
  "draft_answer": {
    "type": "MCQ",
    "selected_option": "A"
  }
  OR
  {
    "type": "CODING",
    "code": "def solution(): ...",
    "language": "python"
  }
}
  ↓
PostgreSQL INSERT or UPDATE:
  INSERT INTO test_autosave
    (autosave_id, assignment_id, question_id, draft_answer, updated_at)
  VALUES
    (gen_random_uuid(), 'uuid', 'uuid', 
     '{"type":"MCQ","selected_option":"A"}',
     CURRENT_TIMESTAMP)
  ON CONFLICT (assignment_id, question_id) 
  DO UPDATE SET draft_answer = EXCLUDED.draft_answer
```

**Database Table: test_autosave**
```
- autosave_id: UUID (Primary Key)
- assignment_id: UUID
- question_id: UUID
- draft_answer: JSONB = flexible structure
- updated_at: TIMESTAMP
```

---

## 6️⃣ FETCH RESULTS FLOW

### What Happens:
1. Test completed, candidate clicks "View Results"
2. Frontend fetches all answers for assignment
3. Calculates scores and displays

### Code Path:
```
Frontend: TestResults.tsx
  ↓ useEffect on mount
  ↓ Fetch all answers for assignment
  ↓
GET /api/v1/submissions/assignment/{assignment_id}
  ↓
Backend: submissions.py → get_answers_by_assignment()
  ↓
PostgreSQL SELECT:
  SELECT * FROM test_answers 
  WHERE assignment_id = '550e8400-e29b-41d4-a716-446655440000'
  ORDER BY submitted_at
  ↓
Response:
{
  "success": true,
  "assignment_id": "uuid",
  "total_answers": 50,
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
    {
      "answer_id": "uuid",
      "question_id": "uuid",
      "question_type": "CODING",
      "code_submission": "def solution(): ...",
      "code_status": "success",
      "code_passed": true,
      "score": 0.0,
      "submitted_at": "2025-12-11T10:30:00"
    },
    ...
  ]
}
  ↓
Frontend: candidateTestStore
  - Results display with MCQ vs Coding breakdown
```

**Database Query:**
```sql
SELECT answer_id, question_id, question_type, 
       selected_option, code_submission, is_correct, 
       score, code_status, code_passed, submitted_at
FROM test_answers 
WHERE assignment_id = $1
ORDER BY submitted_at ASC
```

---

## 7️⃣ GENERATE TEST REPORT FLOW

### What Happens:
1. Admin or system generates report
2. Aggregates all answers for assignment
3. Calculates total score and section scores
4. Inserts into test_results table

### Code Path:
```
Backend: (New endpoint needed)
POST /api/v1/reports/generate/{assignment_id}
  ↓
PostgreSQL AGGREGATION:
  
  Query 1: Count questions by type
  SELECT question_type, COUNT(*) 
  FROM test_answers 
  WHERE assignment_id = 'uuid'
  GROUP BY question_type
  
  Query 2: Calculate scores
  SELECT 
    question_type,
    SUM(score) as section_score,
    COUNT(*) as total_questions,
    SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
  FROM test_answers 
  WHERE assignment_id = 'uuid'
  GROUP BY question_type
  
  Query 3: Calculate total time
  SELECT SUM(time_spent_seconds) as total_time
  FROM test_answers 
  WHERE assignment_id = 'uuid'
  ↓
PostgreSQL INSERT (test_results):
  INSERT INTO test_results
    (result_id, assignment_id, total_score, 
     section_scores, time_taken_seconds, 
     completion_status, generated_at)
  VALUES
    (gen_random_uuid(), 'uuid', 45.5,
     '{"mcq_score": 30, "coding_score": 15.5}',
     3600,
     'PASSED',
     CURRENT_TIMESTAMP)
  ↓
Response:
{
  "success": true,
  "result_id": "uuid",
  "total_score": 45.5,
  "section_scores": {
    "mcq_score": 30,
    "coding_score": 15.5
  },
  "time_taken_seconds": 3600,
  "completion_status": "PASSED"
}
```

**Database Table: test_results**
```
- result_id: UUID (Primary Key)
- assignment_id: UUID (Unique, FOREIGN KEY)
- total_score: NUMERIC
- section_scores: JSONB = {mcq_score: X, coding_score: Y}
- time_taken_seconds: INT
- completion_status: ENUM = 'PASSED'|'FAILED'|'INCOMPLETE'
- generated_at: TIMESTAMP
```

---

## 🔄 Complete Data Mapping Table

| Frontend Action | API Endpoint | HTTP Method | PostgreSQL Table | MongoDB Collection | Operations |
|---|---|---|---|---|---|
| Select MCQ option | `/submissions/mcq` | POST | test_answers | - | INSERT |
| Submit code | `/submissions/code` | POST | test_answers | code_submissions | INSERT + INSERT |
| Auto-save answer | `/submissions/autosave` | POST | test_autosave | - | INSERT/UPDATE |
| View results | `/submissions/assignment/{id}` | GET | test_answers | - | SELECT |
| Get candidate history | `/submissions/candidate/{id}` | GET | test_answers | - | SELECT |
| Load test | `/tests/{test_id}` | GET | tests, test_questions, unified_questions | - | SELECT (JOIN) |
| Load questions | `/questions/{question_id}` | GET | mcq_questions, unified_questions | coding_questions | SELECT + FIND |
| Login | `/candidates/login` | POST | test_assignments, candidates | - | SELECT |
| Generate report | `/reports/generate/{id}` | POST | test_answers, test_results | - | SELECT + INSERT |

---

## 📍 WHERE TO CHANGE THINGS

### ✅ Add a New Submission Type (e.g., Essay, File Upload)

**Step 1**: Add endpoint in `backend/app/api/v1/endpoints/submissions.py`
```python
@router.post("/essay")
async def submit_essay(data: dict, db: AsyncSession = Depends(get_db)):
    # Similar to MCQ, insert to test_answers with question_type='ESSAY'
    pass
```

**Step 2**: Add column to PostgreSQL (if needed)
```sql
ALTER TABLE test_answers ADD COLUMN essay_submission TEXT;
```

**Step 3**: Update frontend TestTaking.tsx
```tsx
{questionType === 'ESSAY' && (
  <textarea onChange={handleEssayChange} />
)}
```

---

### ✅ Change Which Table Stores Code Output

**Current**: Stores in `test_answers.code_output`
**To change**: Create new table `code_outputs`

**Step 1**: Create table
```sql
CREATE TABLE code_outputs (
    output_id UUID PRIMARY KEY,
    answer_id UUID REFERENCES test_answers(answer_id),
    output TEXT,
    created_at TIMESTAMP
);
```

**Step 2**: Update `backend/app/api/v1/endpoints/submissions.py`
```python
# In submit_code_answer, after saving to test_answers:
insert_output = text("""
    INSERT INTO code_outputs (output_id, answer_id, output, created_at)
    VALUES (gen_random_uuid(), :answer_id, :output, CURRENT_TIMESTAMP)
""")
await db.execute(insert_output, {
    "answer_id": str(answer_id),
    "output": data.get("code_output")
})
```

**Step 3**: Update retrieval query
```python
# When fetching results:
SELECT ta.*, co.output as code_output
FROM test_answers ta
LEFT JOIN code_outputs co ON ta.answer_id = co.answer_id
```

---

### ✅ Add New Database & Change Connection

**Step 1**: Update config
```python
# backend/app/core/config.py
MONGODB_URL = "mongodb://new-host:27017"
POSTGRES_URL = "postgresql+asyncpg://user:pass@new-host/db"
```

**Step 2**: Update connection files
```python
# backend/app/db/postgres.py
engine = create_async_engine(settings.DATABASE_URL)

# backend/app/db/mongodb.py
client = AsyncMongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DB_NAME]
```

**Step 3**: Update frontend
```typescript
// src/lib/api.ts
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://new-host:8000';
```

---

### ✅ Add Scoring/Evaluation Logic

**Step 1**: Create new endpoint
```python
# backend/app/api/v1/endpoints/submissions.py
@router.post("/evaluate/{assignment_id}")
async def evaluate_answers(
    assignment_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Query all answers
    query = text("""
        SELECT answer_id, is_correct, question_type, score
        FROM test_answers
        WHERE assignment_id = :assignment_id
    """)
    result = await db.execute(query, {"assignment_id": assignment_id})
    answers = result.fetchall()
    
    # Calculate scores
    total_score = sum(ans.score for ans in answers)
    
    # Update test_results
    insert_result = text("""
        INSERT INTO test_results 
        (result_id, assignment_id, total_score, ...)
        VALUES (...)
    """)
    await db.execute(insert_result, {...})
    
    return {"total_score": total_score}
```

**Step 2**: Call from frontend or admin panel
```typescript
await fetch(`/api/v1/submissions/evaluate/${assignmentId}`, {
    method: 'POST'
});
```

---

## 🚨 Important Notes

### PostgreSQL test_answers Table
- **NEVER** delete from this table
- Always use soft deletes if needed
- Add `deleted_at` column for archiving
- This is the AUDIT TRAIL

### MongoDB code_submissions
- Can be archived/deleted after 1 year
- Keep for audit purposes
- Indexes on `candidateId`, `assignmentId`

### test_autosave Table
- Can be cleaned up after test submission
- Query: `DELETE FROM test_autosave WHERE assignment_id IN (...)`

### API Response Format
All endpoints should follow:
```json
{
  "success": true/false,
  "data": {...},
  "message": "Description",
  "error": "Error details if failed"
}
```

---

## 📞 Quick Reference: Which Table to Query?

| Need | Query | Table |
|------|-------|-------|
| Candidate's answers | `SELECT * FROM test_answers WHERE candidate_id = ?` | PostgreSQL |
| Test's questions | `SELECT * FROM test_questions WHERE test_id = ?` | PostgreSQL |
| MCQ details | `SELECT * FROM mcq_questions WHERE mcq_id = ?` | PostgreSQL |
| Coding problem | `db.coding_questions.findOne({_id: ObjectId(?)})` | MongoDB |
| Code execution | `db.code_submissions.findOne({answer_id: ?})` | MongoDB |
| Test results | `SELECT * FROM test_results WHERE assignment_id = ?` | PostgreSQL |
| Candidate login | `SELECT * FROM test_assignments WHERE candidate_token = ?` | PostgreSQL |

---

**Document Version**: 1.0  
**Last Updated**: December 11, 2025  
**Status**: Complete ✅
