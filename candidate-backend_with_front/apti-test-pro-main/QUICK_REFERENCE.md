# Talentshire - Quick Reference Card

## 🚀 START THE PROJECT

### Option 1: Batch File (Windows CMD)
```bash
Double-click: START_ALL.bat
```

### Option 2: PowerShell
```bash
powershell -ExecutionPolicy Bypass -File START_ALL.ps1
```

### Option 3: Manual Start (Separate Terminals)

**Terminal 1 - Frontend:**
```bash
cd C:\Users\MSI\new_project\apti-test-pro-main\apti-test-pro-main
npm run dev
# Frontend: http://localhost:8080/
```

**Terminal 2 - Backend:**
```bash
cd C:\Users\MSI\new_project\apti-test-pro-main\apti-test-pro-main\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Backend: http://localhost:8000/
# API Docs: http://localhost:8000/docs
```

---

## 🔐 DEFAULT CREDENTIALS

```
Email:    test@example.com
Password: test123456
Token:    test_token_123
```

---

## 🌐 IMPORTANT URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:8080/ | Candidate Portal |
| Backend | http://localhost:8000/ | API Server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Server Status |

---

## 💾 DATABASE CREDENTIALS

### PostgreSQL
```
Host:     127.0.0.1
Port:     5432
User:     postgres
Password: Admin@123
Database: talentshire
```

**Connection String:**
```
postgresql+asyncpg://postgres:Admin%40123@127.0.0.1:5432/talentshire
```

### MongoDB
```
URL:      mongodb://127.0.0.1:27017
Database: talentshire
```

---

## 📁 KEY FILES TO MODIFY

| Task | File | Location |
|------|------|----------|
| Add API endpoint | `submissions.py` | `backend/app/api/v1/endpoints/` |
| Change routes | `router.py` | `backend/app/api/v1/` |
| Modify UI | `TestTaking.tsx` | `src/pages/candidate/` |
| Change API base URL | `api.ts` | `src/lib/` |
| Update database URL | `config.py` | `backend/app/core/` |
| Edit test data | `test_schemas.py` | `backend/app/schemas/` |

---

## 🔌 API ENDPOINTS (SUBMISSION)

### MCQ Answer
```
POST /api/v1/submissions/mcq

{
  "assignment_id": "uuid",
  "question_id": "uuid",
  "selected_option": "A",
  "is_correct": true,
  "time_spent_seconds": 30,
  "candidate_id": "uuid"
}

Response: {success: true, answer_id: "uuid"}
```

### Code Submission
```
POST /api/v1/submissions/code

{
  "assignment_id": "uuid",
  "question_id": "uuid",
  "code": "def solution(): ...",
  "language": "python",
  "code_status": "success",
  "code_passed": true,
  "code_output": "output",
  "stdin": "",
  "stdout": "result",
  "time_spent_seconds": 60,
  "candidate_id": "uuid"
}

Response: {success: true, answer_id: "uuid", mongo_id: "uuid"}
```

### Get Assignment Answers
```
GET /api/v1/submissions/assignment/{assignment_id}

Response: {success: true, answers: [{...}, {...}]}
```

### Get Candidate History
```
GET /api/v1/submissions/candidate/{candidate_id}

Response: {success: true, submissions: [{...}, {...}]}
```

---

## 📊 DATABASE TABLES

### Main Tables

| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `users` | Admin/Recruiter accounts | user_id, email, password_hash |
| `candidates` | Candidate profiles | candidate_id, email, name |
| `tests` | Test/Assessment definitions | test_id, test_name, duration_minutes |
| `test_questions` | Question mapping | test_id, question_id, order_index |
| `mcq_questions` | MCQ questions | mcq_id, question_text, options, correct_answer |
| `unified_questions` | All question types | question_id, type, difficulty_level |
| `test_assignments` | Test assignments | assignment_id, test_id, candidate_id, candidate_token |
| **test_answers** ⭐ | **Candidate answers** | **answer_id, selected_option, code_submission, is_correct, score** |
| `test_results` | Test results/scores | result_id, assignment_id, total_score |
| `test_autosave` | Draft answers | autosave_id, assignment_id, question_id, draft_answer |

### MongoDB Collections

| Collection | Purpose | Key Fields |
|-----------|---------|-----------|
| `coding_questions` | Coding problems | _id, title, description, test_cases |
| **code_submissions** ⭐ | **Code execution results** | **_id, answer_id, code, language, execution_result** |

---

## 🔄 DATA FLOW SUMMARY

```
1. Candidate Login
   → test_assignments (SELECT)
   → candidates (SELECT)
   
2. Load Test & Questions
   → tests (SELECT)
   → test_questions (SELECT - JOIN)
   → unified_questions (SELECT - JOIN)
   → mcq_questions (SELECT)
   → coding_questions (FIND)
   
3. Submit MCQ
   → test_answers (INSERT)
   
4. Submit Code
   → test_answers (INSERT)
   → code_submissions (INSERT)
   
5. View Results
   → test_answers (SELECT WHERE assignment_id)
   → code_submissions (FIND)
   
6. Generate Report
   → test_answers (SELECT - AGGREGATE)
   → test_results (INSERT)
```

---

## 🔧 COMMON CHANGES

### Change PostgreSQL Credentials
**File**: `backend/app/core/config.py`
```python
DATABASE_URL = "postgresql+asyncpg://user:password@host:port/database"
```

### Change MongoDB URL
**File**: `backend/app/core/config.py`
```python
MONGODB_URL = "mongodb://host:port"
MONGODB_DB_NAME = "database_name"
```

### Add New Endpoint
**File**: `backend/app/api/v1/endpoints/submissions.py`
```python
@router.post("/new-endpoint")
async def new_endpoint(data: dict, db: AsyncSession = Depends(get_db)):
    # Your code here
    pass
```

### Change Frontend API Base URL
**File**: `src/lib/api.ts`
```typescript
const API_BASE = 'http://your-backend-url:8000';
```

### Modify Test Taking UI
**File**: `src/pages/candidate/TestTaking.tsx`
- Change styling
- Add new question types
- Modify submission logic

---

## 🆘 TROUBLESHOOTING

### Frontend won't start
```bash
# Clear cache and reinstall
rm -r node_modules package-lock.json
npm install
npm run dev
```

### Backend won't start
```bash
# Check if Python packages are installed
pip install -r requirements.txt

# Check if ports are in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux
```

### PostgreSQL connection error
```bash
# Check if running
tasklist | findstr postgres  # Windows

# Try different host
# Change localhost to 127.0.0.1 in config.py
```

### MongoDB connection error
```bash
# Check if running
tasklist | findstr mongod  # Windows

# Verify connection string format
mongodb://127.0.0.1:27017
```

---

## 📚 DOCUMENTATION FILES

| File | Purpose |
|------|---------|
| `SETUP_AND_DOCUMENTATION.md` | Complete architecture & setup guide |
| `DATABASE_MAPPING.md` | Detailed data flow & database mapping |
| `Quick_Reference.md` | This file - quick lookup |
| `START_ALL.bat` | Batch script to start all services |
| `START_ALL.ps1` | PowerShell script to start all services |

---

## 🎯 FREQUENTLY NEEDED

### Check if databases are running
```bash
# PostgreSQL
psql -h 127.0.0.1 -U postgres -c "SELECT 1"

# MongoDB
mongosh mongodb://127.0.0.1:27017/talentshire
```

### View PostgreSQL logs
```bash
# Windows: Check Event Viewer
# Linux/Mac: tail /var/log/postgresql/postgresql.log
```

### View backend logs
```bash
# Check the backend terminal window for logs
# Or redirect to file: python -m uvicorn ... > backend.log
```

### Test API endpoint
```bash
# Using curl
curl -X GET http://localhost:8000/health

# Or use Postman
# Or visit http://localhost:8000/docs for Swagger UI
```

---

## 💡 QUICK TIPS

1. **Always use 127.0.0.1 instead of localhost** for databases (works better on all systems)

2. **URL encode special characters** in connection strings:
   - `@` → `%40`
   - `:` → `%3A`
   - `/` → `%2F`

3. **Restart backend after any code change** (Uvicorn won't auto-reload all changes)

4. **Check API docs** at http://localhost:8000/docs for live testing

5. **Use Chrome DevTools** (F12) to debug frontend issues

6. **Always save drafts** before submitting tests (auto-save every 30 sec)

---

**Version**: 1.0  
**Last Updated**: December 11, 2025  
**Status**: Ready to Use ✅
