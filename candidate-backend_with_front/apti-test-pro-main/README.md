# 🎯 Talentshire - Technical Assessment Platform

Welcome to Talentshire! A complete technical assessment platform with candidate testing, MCQ questions, live coding challenges, and real-time evaluation.

---

## 📖 Quick Navigation

- **New to the project?** → Start with [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- **Want detailed setup?** → Read [SETUP_AND_DOCUMENTATION.md](./SETUP_AND_DOCUMENTATION.md)
- **Need database details?** → Check [DATABASE_MAPPING.md](./DATABASE_MAPPING.md)
- **Ready to run?** → Use [START_ALL.bat](#-quick-start) or [START_ALL.ps1](#-quick-start)

---

## 🚀 Quick Start

### Prerequisites
- PostgreSQL 15+ running on localhost:5432
- MongoDB running on localhost:27017
- Node.js installed
- Python 3.11+ installed

### Option 1: One-Click Start (Recommended)
```bash
# Just double-click this file
START_ALL.bat
```

### Option 2: PowerShell
```bash
powershell -ExecutionPolicy Bypass -File START_ALL.ps1
```

### Option 3: Manual Start
```bash
# Terminal 1: Frontend
cd C:\Users\MSI\new_project\apti-test-pro-main\apti-test-pro-main
npm run dev

# Terminal 2: Backend
cd C:\Users\MSI\new_project\apti-test-pro-main\apti-test-pro-main\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Then visit:**
- Frontend: http://localhost:8080/
- Backend: http://localhost:8000/
- API Docs: http://localhost:8000/docs

---

## 🏗️ Architecture at a Glance

```
Frontend (React + TypeScript)  ←→  Backend (FastAPI + Python)
   http://localhost:8080/              http://localhost:8000/
   
   ↓                                     ↓
   
┌─────────────────────────────────────────────────┐
│         PostgreSQL (talentshire)                 │
│  - Tests, Questions, Answers, Results            │
│  - Host: 127.0.0.1:5432                         │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│         MongoDB (talentshire)                    │
│  - Coding Problems, Execution Results            │
│  - Host: 127.0.0.1:27017                        │
└─────────────────────────────────────────────────┘
```

---

## 📊 What Does This Do?

### For Candidates
- ✅ Login with email or token
- ✅ Take tests with MCQ questions
- ✅ Write and execute code solutions
- ✅ Auto-save test progress
- ✅ View results and scores

### For Recruiters/Admins
- ✅ Create tests with custom questions
- ✅ Assign tests to candidates
- ✅ Review candidate responses
- ✅ Generate test reports and analytics
- ✅ Manage question banks

---

## 🗂️ Project Structure

```
apti-test-pro-main/
├── frontend (React + TypeScript)
│   ├── src/
│   │   ├── pages/          ← Page components
│   │   ├── components/     ← Reusable UI components
│   │   ├── lib/            ← API client & utilities
│   │   ├── store/          ← State management (Zustand)
│   │   └── App.tsx         ← Main app component
│   ├── package.json        ← Frontend dependencies
│   └── vite.config.ts      ← Vite configuration
│
├── backend (FastAPI + Python)
│   ├── app/
│   │   ├── api/            ← REST API endpoints
│   │   ├── db/             ← Database connections
│   │   ├── models/         ← SQLAlchemy models
│   │   ├── schemas/        ← Pydantic validation
│   │   ├── services/       ← Business logic
│   │   ├── core/           ← Configuration
│   │   └── main.py         ← App entry point
│   ├── requirements.txt    ← Python dependencies
│   └── README.md           ← Backend documentation
│
├── SETUP_AND_DOCUMENTATION.md  ← Complete guide
├── DATABASE_MAPPING.md         ← Data flow details
├── QUICK_REFERENCE.md          ← Quick lookup
├── START_ALL.bat               ← Windows startup script
└── START_ALL.ps1               ← PowerShell startup script
```

---

## 🔐 Default Credentials

```
Email:    test@example.com
Password: test123456
Token:    test_token_123
```

---

## 💾 Database Connections

### PostgreSQL
```
Host:     127.0.0.1
Port:     5432
User:     postgres
Password: Admin@123
Database: talentshire
```

### MongoDB
```
URL:      mongodb://127.0.0.1:27017
Database: talentshire
```

---

## 🎯 Key Features

### 📝 MCQ Questions
- Multiple choice with 4 options
- Auto-grading
- Difficulty levels
- Tags/Categories

### 💻 Coding Challenges
- Support for Python, JavaScript, Java, etc.
- Real-time code execution
- Test cases validation
- Code quality analysis

### ⏱️ Test Management
- Timed assessments
- Progress tracking
- Auto-save functionality
- Test results & scoring

### 📊 Analytics & Reporting
- Candidate performance metrics
- Test completion rates
- Score distributions
- Time spent analysis

---

## 🔌 API Endpoints (Main)

### Submissions (Answer Storage)
```
POST   /api/v1/submissions/mcq              - Save MCQ answer
POST   /api/v1/submissions/code             - Save code submission
GET    /api/v1/submissions/assignment/{id}  - Get assignment answers
GET    /api/v1/submissions/candidate/{id}   - Get candidate history
```

### Tests & Questions
```
GET    /api/v1/tests                        - List all tests
POST   /api/v1/tests                        - Create test
GET    /api/v1/tests/{test_id}              - Get test details
GET    /api/v1/questions/mcq/{id}           - Get MCQ question
GET    /api/v1/questions/coding/{id}        - Get coding question
```

### Health & Status
```
GET    /health                              - Server health check
GET    /docs                                - API documentation (Swagger)
```

---

## 📝 Database Schema Highlights

### ⭐ test_answers Table (Critical)
Where all candidate answers are stored:
```
- answer_id: UUID
- assignment_id: UUID
- question_id: UUID
- selected_option: VARCHAR (for MCQ: A/B/C/D)
- code_submission: TEXT (for Coding)
- is_correct: BOOLEAN
- score: NUMERIC
- submitted_at: TIMESTAMP
- candidate_id: UUID
```

### ⭐ code_submissions Collection (MongoDB)
Detailed code execution results:
```
{
  "_id": ObjectId,
  "answer_id": UUID,
  "code": "def solution(): ...",
  "language": "python",
  "execution_result": {...},
  "submitted_at": ISODate
}
```

---

## 🔄 Data Flow Summary

```
1. Candidate logs in
   ↓ (uses candidate_token from test_assignments)
   
2. Frontend loads available tests
   ↓ (fetches from tests, test_questions, unified_questions)
   
3. Candidate takes test
   ↓ (answers auto-saved to test_autosave)
   
4. Candidate submits answer
   ├─ MCQ: Saves to test_answers table
   └─ Code: Saves to test_answers table + code_submissions collection
   
5. Candidate views results
   ↓ (reads from test_answers)
   
6. Admin generates report
   ↓ (aggregates from test_answers to test_results)
```

---

## 🛠️ Common Tasks

### Add a New Question Type
See [DATABASE_MAPPING.md - Section 1](./DATABASE_MAPPING.md#1-add-a-new-question-type)

### Change Database Credentials
See [SETUP_AND_DOCUMENTATION.md - Section 6](./SETUP_AND_DOCUMENTATION.md#2-change-database-credentials)

### Create New API Endpoint
See [SETUP_AND_DOCUMENTATION.md - Section 6](./SETUP_AND_DOCUMENTATION.md#3-add-new-api-endpoint)

### Modify Test Taking UI
**File**: `src/pages/candidate/TestTaking.tsx`
- Adjust styling
- Add new question rendering
- Modify submission logic

### Debug Issues
**File**: [SETUP_AND_DOCUMENTATION.md - Troubleshooting](./SETUP_AND_DOCUMENTATION.md#-troubleshooting)

---

## 📦 Technology Stack

### Frontend
- React 18
- TypeScript
- Vite (Build Tool)
- TailwindCSS + ShadcnUI
- Zustand (State Management)
- React Query (API Caching)
- React Router (Navigation)

### Backend
- FastAPI
- Python 3.11+
- SQLAlchemy 2.0 (ORM)
- AsyncPG (PostgreSQL Driver)
- Motor (MongoDB Async Driver)
- Uvicorn (ASGI Server)

### Databases
- PostgreSQL 15+
- MongoDB 5+

---

## 📚 Documentation Files

| File | Purpose | For Whom |
|------|---------|----------|
| [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) | Quick lookup for common tasks | Everyone |
| [SETUP_AND_DOCUMENTATION.md](./SETUP_AND_DOCUMENTATION.md) | Complete architecture guide | Developers |
| [DATABASE_MAPPING.md](./DATABASE_MAPPING.md) | Data flow & database details | Developers, Database Admins |
| [README.md](./README.md) | This file - Project overview | Everyone |

---

## 🆘 Troubleshooting

### Services won't start?
1. Check PostgreSQL is running (Services → PostgreSQL → Start)
2. Check MongoDB is running (Services → MongoDB → Start)
3. Check ports aren't in use: `netstat -ano | findstr :8000`

### API returns 404?
1. Check endpoint is registered in `backend/app/api/v1/router.py`
2. Verify URL spelling matches exactly
3. Restart backend server

### Frontend blank page?
1. Check browser console (F12) for errors
2. Verify API base URL in `src/lib/api.ts`
3. Check backend is running and healthy

### Database connection errors?
1. Verify credentials in `backend/app/core/config.py`
2. Check database URLs use `127.0.0.1` not `localhost`
3. Verify special characters are URL encoded

---

## 🚀 Next Steps

1. **Run the project**
   ```bash
   START_ALL.bat
   ```

2. **Visit the frontend**
   ```
   http://localhost:8080/
   ```

3. **Login with test credentials**
   ```
   Email: test@example.com
   Password: test123456
   ```

4. **Explore the API docs**
   ```
   http://localhost:8000/docs
   ```

5. **Read the full documentation**
   ```
   Start with QUICK_REFERENCE.md
   ```

---

## 📞 Support

- **Quick answers**: Check [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- **How-to guides**: See [SETUP_AND_DOCUMENTATION.md](./SETUP_AND_DOCUMENTATION.md)
- **Data details**: Read [DATABASE_MAPPING.md](./DATABASE_MAPPING.md)
- **API testing**: Visit http://localhost:8000/docs

---

## 📝 License

Proprietary - Talentshire

---

## 👥 Contributors

- Development Team
- Last Updated: December 11, 2025

---

## ✅ Checklist Before Deployment

- [ ] Change PostgreSQL password
- [ ] Change MongoDB authentication
- [ ] Update CORS origins in backend
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Load test the application
- [ ] Set up monitoring alerts

---

**Ready to get started?** → Run `START_ALL.bat` now!

🎉 **Happy Testing!**
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/e3f1a93e-5779-4f99-9b28-29335c882e6e) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
