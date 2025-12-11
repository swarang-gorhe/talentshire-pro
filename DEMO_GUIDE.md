# 🎬 Talentshire Live Demo Guide

Complete guide for deploying and running the integrated Talentshire platform with live demonstrations.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Deployment Methods](#deployment-methods)
4. [Demo Features](#demo-features)
5. [Manual Testing](#manual-testing)
6. [Troubleshooting](#troubleshooting)
7. [Platform Access](#platform-access)

---

## Quick Start

### Option 1: Automated Demo (Recommended)

```bash
cd /Users/swarang.gorhe/Documents/Talentshire-main
chmod +x deploy.sh
./deploy.sh --demo
```

This single command will:
- ✅ Check all prerequisites (Docker, ports, dependencies)
- ✅ Build all Docker images (backend, frontend, database)
- ✅ Start all services (API, Frontend, PostgreSQL, PgAdmin)
- ✅ Run live API demonstrations
- ✅ Show service status and URLs

### Option 2: Manual Steps

```bash
# Step 1: Build images
docker-compose build

# Step 2: Start services
docker-compose up -d

# Step 3: Wait for services (30 seconds)
sleep 30

# Step 4: Run Python demo
python3 demo.py
```

---

## Prerequisites

### Required Software

```bash
# Check if Docker is installed
docker --version
# Expected: Docker version 20.10+

# Check if Docker Compose is installed
docker-compose --version
# Expected: Docker Compose version 1.29+

# Check if Python 3 is installed
python3 --version
# Expected: Python 3.9+

# Check if curl is installed (for API testing)
curl --version
```

### Required Ports

Make sure these ports are available on your machine:

| Port | Service | Purpose |
|------|---------|---------|
| 5432 | PostgreSQL | Database |
| 8000 | FastAPI Backend | REST API |
| 5173 | React Frontend | Web Application |
| 5050 | PgAdmin | Database Management |

**Check port availability:**

```bash
# macOS
lsof -i :8000  # Backend port
lsof -i :5173  # Frontend port
lsof -i :5432  # Database port
lsof -i :5050  # PgAdmin port

# If ports are in use, stop the services:
./deploy.sh --stop
```

### Required Python Packages

For running the Python demo, install:

```bash
pip install requests
```

Or let the deployment script handle it.

---

## Deployment Methods

### Method 1: Full Automated Deployment with Demo

```bash
./deploy.sh --demo
```

**What happens:**
1. Prerequisites check (Docker, ports)
2. Build all Docker images
3. Start containers (PostgreSQL → Backend → Frontend)
4. Wait for services to be healthy (health checks)
5. Run Python demo script with interactive tests
6. Display service URLs and next steps

**Expected time:** 3-5 minutes on first run

### Method 2: Deployment without Demo

```bash
./deploy.sh
```

**What happens:**
1. Prerequisites check
2. Build and start services
3. Show service status
4. **Does not** run the demo

**Use when:** You want to start services manually and access them

### Method 3: Manual Docker Commands

```bash
# Build images
docker-compose build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

### Method 4: Run Demo Only (Services Already Running)

If services are already running, just run the Python demo:

```bash
python3 demo.py
```

---

## Demo Features

### What Gets Demonstrated

The live demo (`demo.py`) shows the following capabilities:

#### 1. **Test Management**
```python
✓ Create new test with specifications
  - Name: "Talentshire Demo Test"
  - Duration: 90 minutes
  - Total Marks: 100
  - Passing Marks: 40

✓ Fetch all available tests
✓ Retrieve specific test details
```

#### 2. **Test Publishing**
```python
✓ Update test status (draft → active)
✓ Publish test for candidates
✓ Manage test lifecycle
```

#### 3. **Test Assignments**
```python
✓ Create assignment for candidate
✓ Set assignment duration (e.g., 2 hours)
✓ Track assignment status
✓ Retrieve candidate assignments
```

#### 4. **API Response Examples**

The demo shows actual responses from your integrated API:

```json
POST /api/tests → 201 Created
{
  "test_id": "123e4567-e89b-12d3-a456-426614174000",
  "test_name": "Talentshire Demo Test",
  "description": "Live demonstration of the integrated platform",
  "duration_minutes": 90,
  "total_marks": 100,
  "passing_marks": 40,
  "status": "draft",
  "created_at": "2024-01-15T10:30:00Z"
}

GET /api/tests → 200 OK
{
  "data": [
    { "test_id": "...", "test_name": "...", ... }
  ],
  "count": 5,
  "page": 1
}
```

### Demo Output

The demo provides color-coded output:

```
✅ API is running and healthy
✓ Test created with ID: 123e4567-...
✓ Retrieved 5 tests
✓ Test details retrieved successfully
✓ Test updated successfully
✓ Test published successfully
✓ Assignment created: abc123-...
✓ Retrieved 2 assignments

🎉 Demo Complete!
✨ Your Talentshire platform is fully integrated and ready!

Available Features Demonstrated:
  ✓ Test Management (Create, Read, Update, Delete)
  ✓ Test Publishing & Status Management
  ✓ Test Assignments to Candidates
  ✓ Unified API Endpoints
  ✓ Complete Type Safety (TypeScript ↔ Python)

Next Steps:
  1. Open http://localhost:5173 in your browser
  2. Review API docs at http://localhost:8000/docs
  3. Manage database via http://localhost:5050
  4. Build your own features using the integrated models
```

---

## Manual Testing

### Test 1: Health Check

```bash
# Check backend health
curl http://localhost:8000/docs

# Check frontend health
curl http://localhost:5173

# Expected: 200 OK
```

### Test 2: Create a Test

```bash
curl -X POST http://localhost:8000/api/tests \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "My Test",
    "description": "Test Description",
    "duration_minutes": 60,
    "total_marks": 100,
    "passing_marks": 40,
    "status": "draft"
  }'

# Expected Response (201 Created):
# {
#   "test_id": "...",
#   "test_name": "My Test",
#   ...
# }
```

### Test 3: Get All Tests

```bash
curl http://localhost:8000/api/tests

# Expected Response (200 OK):
# {
#   "data": [...],
#   "count": 5,
#   "page": 1
# }
```

### Test 4: Update Test

```bash
curl -X PUT http://localhost:8000/api/tests/{test_id} \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "Updated Test Name",
    "status": "active"
  }'
```

### Test 5: Database Check

```bash
# Connect to PostgreSQL
docker exec -it talentshire-postgres psql -U postgres -d talentshire

# Inside PostgreSQL:
\dt                    # List all tables
SELECT * FROM tests;   # View tests table
```

---

## Platform Access

### 🌐 Frontend Application

**URL:** http://localhost:5173

**Features:**
- Test Management Dashboard
- Candidate Test Taking Interface
- Test Reports & Analytics
- Real-time Results

**Login Credentials:**
```
Email: demo@talentshire.com
Password: demo@123
```

### 📚 API Documentation

**URL:** http://localhost:8000/docs

**Interactive Features:**
- Try out any API endpoint
- See request/response examples
- View all available operations
- Download OpenAPI spec

**Quick Endpoints:**
```
GET    /api/tests              - List all tests
POST   /api/tests              - Create test
GET    /api/tests/{id}         - Get test details
PUT    /api/tests/{id}         - Update test
PATCH  /api/tests/{id}/publish - Publish test

POST   /api/assignments        - Create assignment
GET    /api/assignments        - List assignments
GET    /api/candidates/{id}/...  - Candidate data
```

### 🗄️ Database Management

**URL:** http://localhost:5050

**Credentials:**
```
Email: admin@talentshire.com
Password: admin@123
```

**Connection Details:**
```
Server: postgres
Port: 5432
Database: talentshire
Username: postgres
Password: admin@123
```

**Tables (20 total):**
- tests
- questions
- assignments
- candidates
- submissions
- reports
- test_sections
- answer_templates
- rubrics
- evaluations
- ...and more

---

## Troubleshooting

### Issue: Docker not found

```bash
# Install Docker
# macOS: brew install docker

# Verify installation
docker --version

# Start Docker daemon
open /Applications/Docker.app
```

### Issue: Port already in use

```bash
# Check which process is using port 8000
lsof -i :8000

# Stop existing service
kill -9 <PID>

# Or use different port (edit docker-compose.yml)
```

### Issue: Services won't start

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Nuclear option: Clean and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Issue: API returns 500 error

```bash
# Check backend logs
docker-compose logs backend

# Verify database is running
docker-compose logs postgres

# Common issues:
# - Database not initialized (check schema.sql)
# - Environment variables not set (check docker-compose.yml)
# - Port conflict
```

### Issue: Database connection failed

```bash
# Verify PostgreSQL is running
docker ps | grep postgres

# Check database credentials in docker-compose.yml
docker-compose config | grep -A 10 "postgres:"

# Try connecting directly
docker exec -it talentshire-postgres psql -U postgres -d talentshire
```

### Issue: Frontend won't load

```bash
# Check if port 5173 is available
lsof -i :5173

# View frontend logs
docker-compose logs frontend

# Verify frontend build
docker-compose build frontend

# Restart frontend service
docker-compose restart frontend
```

### Issue: Python demo fails

```bash
# Install requests package
pip install requests

# Verify API is accessible
curl http://localhost:8000/docs

# Run with verbose output
python3 -u demo.py

# Check Python version
python3 --version  # Should be 3.9+
```

---

## Service Management

### View Service Status

```bash
# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Stop Services

```bash
# Graceful stop (keeps data)
./deploy.sh --stop
# or
docker-compose down

# Stop with volume cleanup (removes data)
docker-compose down -v
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### View Service Health

```bash
# PostgreSQL health
docker-compose ps postgres

# Backend health
docker exec talentshire-backend curl localhost:8000/docs

# Frontend health
curl http://localhost:5173
```

---

## Advanced Testing

### Load Testing

```bash
# Install Apache Bench (if not installed)
# macOS: brew install httpd

# Test API performance
ab -n 1000 -c 10 http://localhost:8000/api/tests

# Results will show:
# - Requests per second
# - Average response time
# - Min/max response times
```

### Database Performance

```bash
# Connect to database
docker exec -it talentshire-postgres psql -U postgres -d talentshire

# Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname='public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Check slow queries
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
```

### API Profiling

```bash
# Generate API profiling data
curl -X POST http://localhost:8000/api/tests \
  -H "Content-Type: application/json" \
  -d '{...}' \
  -w "@curl-format.txt" \
  -o /dev/null \
  -s

# Time breakdown:
# - DNS lookup time
# - Connect time
# - Time to first byte
# - Total time
```

---

## Next Steps After Demo

### 1. Explore the Code

- **Backend Models:** `shared/models.py`, `shared/database_models.py`
- **Frontend Types:** `frontend/src/types/api.ts`
- **API Service:** `frontend/src/services/api.ts`
- **API Implementation:** `backend/main.py`

### 2. Start Development

```bash
# Frontend development
cd frontend
npm run dev

# Backend development (in another terminal)
cd backend
python -m uvicorn main:app --reload
```

### 3. Add New Features

- Create new endpoints in `backend/main.py`
- Add corresponding types in `frontend/src/types/api.ts`
- Add API calls in `frontend/src/services/api.ts`
- Update stores in `frontend/src/store/`

### 4. Database Modifications

- Edit schema in `shared/schema.sql`
- Create migration in database
- Update models in `shared/database_models.py`

### 5. Deployment to Production

- Update environment variables
- Configure SSL/HTTPS
- Set up persistent volumes
- Configure backup strategies

---

## Documentation Reference

For detailed information, see:

- **`START_HERE.md`** - Quick navigation
- **`COMPLETE_PLATFORM_INTEGRATION.md`** - Full overview
- **`shared/INTEGRATION_GUIDE.md`** - Backend details
- **`frontend/FRONTEND_INTEGRATION.md`** - Frontend details
- **`shared/MODEL_MAPPING.md`** - Database schema (2000+ lines)

---

## Support & Troubleshooting

### Debug Mode

Set debug environment variable:

```bash
export DEBUG=true
./deploy.sh --demo
```

### View All Logs

```bash
# All service logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Common Commands

```bash
# Clean rebuild
docker-compose down -v && docker-compose build --no-cache && docker-compose up -d

# Health check
docker-compose ps

# Database shell
docker exec -it talentshire-postgres psql -U postgres -d talentshire

# Backend shell
docker exec -it talentshire-backend bash

# Frontend shell
docker exec -it talentshire-frontend bash
```

---

## Success Indicators

Your deployment is successful when you see:

✅ All 4 containers running (`docker ps`)
✅ Backend accessible at http://localhost:8000/docs
✅ Frontend accessible at http://localhost:5173
✅ Database responsive via PgAdmin http://localhost:5050
✅ Demo script completes with "🎉 Demo Complete!"
✅ API tests show 200/201 status codes
✅ No error messages in logs

---

## Quick Reference

```bash
# Deploy with demo
./deploy.sh --demo

# Check status
docker ps

# View logs
docker-compose logs -f

# Stop services
./deploy.sh --stop

# Clean reset
docker-compose down -v

# Run demo only
python3 demo.py

# Database access
docker exec -it talentshire-postgres psql -U postgres -d talentshire
```

---

**🎉 Enjoy your integrated Talentshire platform!**
