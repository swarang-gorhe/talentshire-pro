# Talentshire - Integrated Talent Assessment Platform

A full-stack talent assessment platform with integrated test creation, management, and candidate evaluation capabilities.

## 📁 Project Structure

```
talentshire/
├── backend/                 # FastAPI backend (Python)
│   ├── main.py             # Main FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/          # Page components (Admin, Candidate)
│   │   ├── components/     # Reusable UI components
│   │   ├── services/       # API service layer
│   │   ├── store/          # Zustand state management
│   │   ├── types/          # TypeScript type definitions
│   │   └── App.tsx         # Root component
│   ├── package.json        # Node dependencies
│   └── vite.config.ts      # Vite build configuration
├── shared/                 # Shared utilities and models
│   ├── models.py           # Database models
│   ├── database_models.py  # SQLAlchemy models
│   └── schema.sql          # Database schema
├── docker-compose.yml      # Docker orchestration
└── README.md               # This file
```

## 🚀 Quick Start (macOS & Windows)

### Prerequisites
- **Python**: 3.11+ (Download from python.org)
- **Node.js**: 18+ (Download from nodejs.org)
- **Git**: Latest version
- **PostgreSQL**: 15+ (Optional, can use Docker)
- **MongoDB**: 6+ (Optional, for advanced features)

### Option 1: Local Development (Recommended)

#### Step 1: Clone Repository
```bash
git clone https://github.com/swarang-gorhe/talentshire-pro.git
cd talentshire-pro
```

#### Step 2: Backend Setup

**Windows:**
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Start backend server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**macOS:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Start backend server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`

#### Step 3: Frontend Setup

**Windows & macOS (same):**
```bash
# In a new terminal, navigate to project root
cd frontend
npm install

# Start development server
npm run dev -- --host 0.0.0.0 --port 8080
```

Frontend will be available at: `http://localhost:8080`

#### Step 4: Database Setup

**PostgreSQL Connection:**
```
Host: localhost
Port: 5432
Database: talentshire
Username: talentshire
Password: talentshire123
```

Run schema:
```bash
psql -U talentshire -d talentshire -f ../shared/schema.sql
```

### Option 2: Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# Services available at:
# Backend: http://localhost:8000
# Frontend: http://localhost:80 (or 8080 if mapped)
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/token-login` - Login with JWT token
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh token

### Tests
- `GET /api/tests` - List all tests
- `POST /api/tests` - Create new test
- `GET /api/tests/{id}` - Get test details
- `PUT /api/tests/{id}` - Update test
- `PATCH /api/tests/{id}/publish` - Publish test
- `GET /api/tests/{id}/questions` - Get test questions

### Assignments
- `GET /api/assignments/{test_id}` - Get assignments
- `POST /api/assignments` - Create assignment
- `PATCH /api/assignments/{id}/start` - Start assignment
- `PATCH /api/assignments/{id}/end` - End assignment
- `GET /api/assignments/{id}` - Get assignment details

### Answers & Questions
- `POST /api/answers` - Submit answer
- `GET /api/assignments/{id}/answers` - Get answers
- `POST /api/tests/{id}/questions` - Add question to test

### Candidates
- `GET /api/candidates/{id}/assignments` - Get candidate assignments

## 🎨 Frontend Features

### Admin Dashboard
- ✅ Create and manage tests
- ✅ View test library
- ✅ Publish/unpublish tests
- ✅ Assign tests to candidates
- ✅ View test assignments
- ✅ Generate reports

### Candidate Portal
- ✅ View assigned tests
- ✅ Take tests (MCQ + Coding)
- ✅ Submit answers in real-time
- ✅ View test results
- ✅ Download performance reports

## 🗄️ Database Schema

### Core Tables
- `users` - User accounts (admin, candidate)
- `tests` - Test metadata and configuration
- `test_questions` - Questions mapped to tests
- `mcq_questions` - Multiple choice questions
- `coding_questions` - Coding challenge questions
- `test_assignments` - Test assignments to candidates
- `test_answers` - Candidate test answers
- `test_reports` - Test result reports

## 🔄 CORS Configuration

Backend accepts requests from:
```
http://localhost:8080
http://localhost:8081
http://localhost:5173
http://127.0.0.1:8080
http://127.0.0.1:8081
```

## 🛠️ Development

### Backend
- **Framework**: FastAPI
- **Server**: uvicorn (auto-reload enabled)
- **API Docs**: http://localhost:8000/docs
- **Code**: `backend/main.py`

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **UI Library**: shadcn/ui
- **State**: Zustand
- **Styling**: Tailwind CSS
- **Hot Reload**: Enabled by default

### Database
- **Primary**: PostgreSQL 15
- **Optional**: MongoDB 6 (for advanced features)
- **ORM**: psycopg (PostgreSQL) / pymongo (MongoDB)

## 📦 Tech Stack Summary

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.11+ |
| Frontend | React 18, TypeScript, Vite |
| State Management | Zustand |
| Styling | Tailwind CSS, shadcn/ui |
| Database | PostgreSQL, MongoDB |
| Server | uvicorn, Node.js |
| Deployment | Docker, Docker Compose |

## 🤝 Cross-Platform Notes

### Windows-Specific
- Use `python` instead of `python3`
- Use `venv\Scripts\activate` to activate virtualenv
- Use `\` for directory paths in commands
- Use `psql` or GUI tools (pgAdmin) for database

### macOS-Specific
- Use `python3` for Python commands
- Use `source venv/bin/activate` to activate virtualenv
- Use `/` for directory paths
- Use `psql` or Postico for database

### Both Platforms
- All `.env` files use `/` for paths
- Git commands are identical
- npm/Node.js commands are identical
- API endpoints work the same way

## 🚨 Common Issues

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS
lsof -i :8000
kill -9 <PID>
```

### Python Module Not Found
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### npm Modules Issues
```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
# Windows: Check Services or Task Manager
# macOS: Check Activity Monitor

# Verify credentials in backend connection
# Default: talentshire / talentshire123
```

## 📝 Environment Variables

### Backend (.env or system)
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=talentshire
POSTGRES_USER=talentshire
POSTGRES_PASSWORD=talentshire123
JWT_SECRET=talentshire-secret-key-change-in-production
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000/api
```

## 🔗 Useful Links

- FastAPI Docs: http://localhost:8000/docs
- React DevTools Browser Extension
- PostgreSQL Documentation
- Vite Documentation
- Zustand Documentation

## 📧 Support

For issues and questions:
1. Check existing GitHub issues
2. Create new issue with details
3. Include error messages and logs

## 📄 License

Proprietary - All rights reserved

---

**Last Updated**: December 11, 2025
**Platform**: Full-Stack Integrated Assessment System
**Status**: Production Ready
