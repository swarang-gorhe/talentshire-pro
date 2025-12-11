"""
Monolithic Talent Assessment Backend
====================================

This FastAPI app consolidates all services into a single monolithic backend.

Services included:

1. Test Storage Service - Working code intact
2. Admin Panel Service - test_assignments endpoints
3. Test–Candidate Mapping Service 
4. Question Fetching Service (MCQ + Coding + Unified)
5. Candidate Answers Storage Service
6. MCQ Filtering Service - Fetch MCQs by language and difficulty
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
import logging
import psycopg
import uuid
from datetime import datetime, timedelta
import hashlib
import os

try:
    import jwt
except ImportError:
    # Fallback: simple token handling without JWT
    jwt = None

# ---------- Logging ----------
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- FastAPI App ----------
app = FastAPI()

# ---------- CORS Configuration ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8081", "http://localhost:5173", "http://127.0.0.1:8080", "http://127.0.0.1:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "talentshire-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

# ---------- PostgreSQL Connection ----------
def get_db_connection():
    try:
        import os
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        conn = psycopg.connect(
            dbname=os.getenv("POSTGRES_DB", "talentshire"),
            user=os.getenv("POSTGRES_USER", "talentshire"),
            password=os.getenv("POSTGRES_PASSWORD", "talentshire123"),
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# ---------- Enums ----------
class LanguageEnum(str, Enum):
    python = "Python"
    java = "Java"
    sql = "SQL"

class DifficultyEnum(str, Enum):
    easy = "Easy"
    medium = "Medium"
    hard = "Hard"

class TestStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    completed = "completed"

class QuestionTypeEnum(str, Enum):
    multiple_choice = "multiple_choice"
    coding = "coding"
    unified = "unified"

class AssignmentStatusEnum(str, Enum):
    assigned = "ASSIGNED"
    started = "STARTED"
    completed = "COMPLETED"
    expired = "EXPIRED"

# ---------- Pydantic Models ----------
class FilterRequest(BaseModel):
    language: LanguageEnum
    difficulty_level: DifficultyEnum

class TestCreate(BaseModel):
    test_name: str
    description: str = ""
    duration_minutes: int
    status: str = "draft"
    total_marks: int = 100
    passing_marks: int = 50

class TestQuestionCreate(BaseModel):
    question_id: uuid.UUID
    question_type: QuestionTypeEnum
    order_index: int

class TestAssignmentCreate(BaseModel):
    test_id: uuid.UUID
    candidate_id: uuid.UUID
    scheduled_start_time: datetime = None
    scheduled_end_time: datetime = None

class TestAnswerCreate(BaseModel):
    assignment_id: uuid.UUID
    question_id: uuid.UUID
    question_type: QuestionTypeEnum
    selected_option: str = None
    code_submission: str = None
    code_output: str = None
    is_correct: bool = None
    score: float = None
    time_spent_seconds: int = None
    code_analysis: str = None
    ai_review_notes: str = None
    language: str = None
    stdin: str = ""
    stdout: str = ""
    code_status: str = "pending"
    code_passed: bool = False

# ---------- Auth Models ----------
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenLoginRequest(BaseModel):
    token: str

class User(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str = "candidate"

class LoginResponse(BaseModel):
    token: str
    user: User

# ---------- Auth Service Functions ----------
def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_jwt_token(user_id: str, email: str) -> str:
    """Generate JWT token for user or simple token string"""
    if jwt:
        payload = {
            "user_id": str(user_id),
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token
    else:
        # Simple fallback token
        import base64
        return base64.b64encode(f"{user_id}:{email}:{int(datetime.utcnow().timestamp())}".encode()).decode()

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token"""
    if jwt:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
    else:
        # Simple fallback verification
        try:
            import base64
            decoded = base64.b64decode(token).decode()
            parts = decoded.split(':')
            if len(parts) >= 2:
                return {"user_id": parts[0], "email": parts[1]}
        except:
            pass
        raise HTTPException(status_code=401, detail="Invalid token")

def get_or_create_user(db_conn, email: str, name: str = None) -> tuple[uuid.UUID, str]:
    """Get or create a user in the database"""
    try:
        cur = db_conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE email = %s;", (email,))
        row = cur.fetchone()
        if row:
            cur.close()
            return row[0], email
        
        # Create new user
        user_id = uuid.uuid4()
        cur.execute(
            "INSERT INTO users (user_id, full_name, email) VALUES (%s, %s, %s) RETURNING user_id;",
            (user_id, name or email.split('@')[0], email)
        )
        created_id = cur.fetchone()[0]
        db_conn.commit()
        cur.close()
        return created_id, email
    except Exception as e:
        logger.error(f"Error getting/creating user: {e}")
        raise HTTPException(status_code=500, detail="Error managing user account")

# ---------- Service Functions ----------
# ---- Test Storage Service (Ishaan) ----
def create_test(db_conn, test: TestCreate, created_by: uuid.UUID):
    try:
        cur = db_conn.cursor()
        # Ensure status is lowercase for the enum
        status = (test.status or "draft").lower()
        test_id = uuid.uuid4()
        cur.execute("""
            INSERT INTO tests (test_id, test_name, description, created_by, duration_minutes, total_marks, passing_marks, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING test_id, test_name, description, duration_minutes, total_marks, passing_marks, status;
        """, (test_id, test.test_name, test.description, created_by, test.duration_minutes, test.total_marks, test.passing_marks, status))
        row = cur.fetchone()
        db_conn.commit()
        cur.close()
        return {
            "test_id": str(row[0]),
            "test_name": row[1],
            "description": row[2],
            "duration_minutes": row[3],
            "total_marks": row[4],
            "passing_marks": row[5],
            "status": row[6],
            "created_by": str(created_by)
        }
    except Exception as e:
        logger.error(f"Error creating test: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating test: {str(e)}")

def create_test_question(db_conn, test_id: uuid.UUID, test_question: TestQuestionCreate):
    try:
        cur = db_conn.cursor()
        cur.execute("""
            INSERT INTO test_questions (id, test_id, question_id, question_type, order_index)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (uuid.uuid4(), test_id, test_question.question_id, test_question.question_type.value, test_question.order_index))
        question_id = cur.fetchone()[0]
        db_conn.commit()
        cur.close()
        return {"id": question_id, "test_id": test_id}
    except Exception as e:
        logger.error(f"Error creating test question: {e}")
        raise HTTPException(status_code=500, detail="Error creating test question")

# ---- Admin Panel + Mapping Service (Swarang + Harsh P) ----
def assign_test_to_candidate(db_conn, assignment: TestAssignmentCreate):
    try:
        cur = db_conn.cursor()
        # Ensure candidate exists; create if needed
        cur.execute("SELECT candidate_id FROM candidates WHERE candidate_id = %s;", (assignment.candidate_id,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO candidates (candidate_id, email) VALUES (%s, %s);",
                (assignment.candidate_id, f"candidate-{assignment.candidate_id}@local")
            )
        
        cur.execute("""
            INSERT INTO test_assignments (assignment_id, test_id, candidate_id, status, assigned_at, scheduled_start_time, scheduled_end_time)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s)
            RETURNING assignment_id;
        """, (uuid.uuid4(), assignment.test_id, assignment.candidate_id, "ASSIGNED", assignment.scheduled_start_time, assignment.scheduled_end_time))
        assignment_id = cur.fetchone()[0]
        db_conn.commit()
        cur.close()
        return {"assignment_id": assignment_id}
    except Exception as e:
        logger.error(f"Error assigning test: {e}")
        raise HTTPException(status_code=500, detail="Error assigning test")

def get_assignments_for_test(db_conn, test_id: uuid.UUID):
    try:
        cur = db_conn.cursor()
        cur.execute("""
            SELECT assignment_id, candidate_id, status, scheduled_start_time, scheduled_end_time
            FROM test_assignments
            WHERE test_id = %s;
        """, (test_id,))
        rows = cur.fetchall()
        cur.close()
        return [{"assignment_id": r[0], "candidate_id": r[1], "status": r[2],
                 "scheduled_start_time": r[3], "scheduled_end_time": r[4]} for r in rows]
    except Exception as e:
        logger.error(f"Error fetching assignments: {e}")
        raise HTTPException(status_code=500, detail="Error fetching assignments")

# ---- Candidate Answer Service (Mukesh) ----
def submit_test_answer(db_conn, answer: TestAnswerCreate):
    try:
        cur = db_conn.cursor()
        cur.execute("""
            INSERT INTO test_answers (
                answer_id, assignment_id, question_id, question_type, selected_option,
                code_submission, code_output, is_correct, score, time_spent_seconds,
                code_analysis, ai_review_notes, language, stdin, stdout, code_status, code_passed
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING answer_id;
        """, (
            uuid.uuid4(), answer.assignment_id, answer.question_id, answer.question_type.value,
            answer.selected_option, answer.code_submission, answer.code_output, answer.is_correct,
            answer.score, answer.time_spent_seconds, answer.code_analysis, answer.ai_review_notes,
            answer.language, answer.stdin, answer.stdout, answer.code_status, answer.code_passed
        ))
        answer_id = cur.fetchone()[0]
        db_conn.commit()
        cur.close()
        return {"answer_id": answer_id}
    except Exception as e:
        logger.error(f"Error submitting test answer: {e}")
        raise HTTPException(status_code=500, detail="Error submitting test answer")

# ---- MCQ Filter Service ----
def fetch_mcqs(language: str, difficulty: str):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT mcq_id, question_text, option_a, option_b, option_c, option_d, correct_answer
            FROM mcq_questions
            WHERE language = %s AND difficulty_level = %s
            ORDER BY mcq_id;
        """, (language, difficulty))
        rows = cur.fetchall()
        mcqs = [{"mcq_id": r[0], "question_text": r[1], "option_a": r[2], "option_b": r[3], "option_c": r[4], "option_d": r[5], "correct_answer": r[6]} for r in rows]
        cur.close()
        conn.close()
        return mcqs
    except Exception as e:
        logger.error(f"Error fetching MCQs: {e}")
        raise HTTPException(status_code=500, detail="Error fetching MCQs")

# ---------- FastAPI Endpoints ----------

# ---- Health Check ----
@app.get("/health")
def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "service": "talentshire-backend"}

# ---- Auth Endpoints ----
@app.post("/api/auth/login", status_code=200)
def login_endpoint(request: LoginRequest):
    """Simple login endpoint - accepts demo credentials and creates JWT token"""
    conn = get_db_connection()
    try:
        # Get or create user
        user_id, email = get_or_create_user(conn, request.email, request.email.split('@')[0])
        
        # Generate JWT token
        token = generate_jwt_token(user_id, request.email)
        
        # Return wrapped response matching ApiResponse<T> format
        return {
            "success": True,
            "data": {
                "token": token,
                "user": {
                    "user_id": str(user_id),
                    "email": request.email,
                    "full_name": request.email.split('@')[0],
                    "role": "admin" if "admin" in request.email else "candidate"
                }
            }
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        return {"success": False, "error": "Login failed"}
    finally:
        conn.close()

@app.post("/api/auth/token-login", status_code=200)
def token_login_endpoint(request: TokenLoginRequest):
    """Token-based login for candidates with shared token"""
    try:
        payload = verify_jwt_token(request.token)
        user_id = payload.get("user_id")
        email = payload.get("email")
        
        return {
            "success": True,
            "data": {
                "user": {
                    "user_id": user_id,
                    "email": email,
                    "full_name": email.split('@')[0] if email else "Candidate",
                    "role": "candidate"
                }
            }
        }
    except Exception as e:
        logger.error(f"Token login error: {e}")
        return {"success": False, "error": "Invalid token"}

@app.post("/api/auth/logout", status_code=200)
def logout_endpoint():
    """Logout endpoint (primarily client-side token removal)"""
    return {"success": True, "message": "Logged out successfully"}

@app.get("/api/auth/me")
def get_current_user_endpoint():
    """Get current authenticated user - requires Bearer token in Authorization header"""
    return {
        "success": True,
        "data": {
            "user_id": "demo-user",
            "email": "demo@talentshire.com",
            "full_name": "Demo User",
            "role": "admin"
        }
    }

@app.post("/api/auth/refresh", status_code=200)
def refresh_token_endpoint():
    """Refresh auth token - for demo purposes, just returns a new token"""
    token = generate_jwt_token("demo-user", "demo@talentshire.com")
    return {"success": True, "data": {"token": token}}

@app.post("/tests/", status_code=201)
def create_test_endpoint(test: TestCreate):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Try to use an existing user as the creator; if none, create a system user
        cur.execute("SELECT user_id FROM users LIMIT 1;")
        row = cur.fetchone()
        if row:
            created_by = row[0]
        else:
            # Insert a lightweight system user so FK constraints succeed
            system_id = uuid.uuid4()
            cur.execute(
                "INSERT INTO users (user_id, full_name, email) VALUES (%s, %s, %s) RETURNING user_id;",
                (system_id, 'System User', 'system@local')
            )
            created_by = cur.fetchone()[0]
            conn.commit()
        cur.close()
    except Exception as e:
        logger.error(f"Error ensuring creator user: {e}")
        raise HTTPException(status_code=500, detail="Error preparing creator user")

    result = create_test(conn, test, created_by=created_by)
    return {"success": True, "data": result}


@app.get("/tests")
def list_tests_endpoint():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT test_id, test_name, duration_minutes, status, created_at FROM tests ORDER BY created_at DESC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        data = [{"test_id": str(r[0]), "test_name": r[1], "duration_minutes": r[2], "status": r[3], "created_at": r[4].isoformat() if r[4] else None} for r in rows]
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error listing tests: {e}")
        return {"success": False, "error": "Error listing tests"}


@app.get("/tests/{test_id}")
def get_test_endpoint(test_id: uuid.UUID):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT test_id, test_name, duration_minutes, status, created_at FROM tests WHERE test_id = %s", (test_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return {"success": False, "error": "Test not found"}
        return {"success": True, "data": {"test_id": str(row[0]), "test_name": row[1], "duration_minutes": row[2], "status": row[3], "created_at": row[4].isoformat() if row[4] else None}}
    except Exception as e:
        logger.error(f"Error fetching test: {e}")
        return {"success": False, "error": "Error fetching test"}


@app.put("/tests/{test_id}")
def update_test_endpoint(test_id: uuid.UUID, test: TestCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE tests SET test_name = %s, duration_minutes = %s, status = %s WHERE test_id = %s RETURNING test_id, test_name, duration_minutes, status",
                (test.test_name, test.duration_minutes, (test.status or "DRAFT").upper(), test_id))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Test not found for update")
        return {"test_id": row[0], "test_name": row[1], "duration_minutes": row[2], "status": row[3]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating test: {e}")
        raise HTTPException(status_code=500, detail="Error updating test")


@app.patch("/tests/{test_id}/publish")
def publish_test_endpoint(test_id: uuid.UUID):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE tests SET status = 'active' WHERE test_id = %s RETURNING test_id, status", (test_id,))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Test not found to publish")
        return {"success": True, "data": {"test_id": str(row[0]), "status": row[1]}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing test: {e}")
        raise HTTPException(status_code=500, detail="Error publishing test")


@app.get("/candidates/{candidate_id}/assignments")
def get_assignments_for_candidate(candidate_id: uuid.UUID):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT assignment_id, test_id, status, scheduled_start_time, scheduled_end_time FROM test_assignments WHERE candidate_id = %s ORDER BY assigned_at DESC", (candidate_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        data = [{"assignment_id": r[0], "test_id": r[1], "status": r[2], "scheduled_start_time": r[3].isoformat() if r[3] else None, "scheduled_end_time": r[4].isoformat() if r[4] else None} for r in rows]
        return {"data": data}
    except Exception as e:
        logger.error(f"Error fetching assignments for candidate: {e}")
        raise HTTPException(status_code=500, detail="Error fetching assignments")

@app.post("/tests/{test_id}/questions/")
def create_test_question_endpoint(test_id: uuid.UUID, question: TestQuestionCreate):
    conn = get_db_connection()
    return create_test_question(conn, test_id, question)

@app.post("/assignments/", status_code=201)
def assign_test_endpoint(assignment: TestAssignmentCreate):
    conn = get_db_connection()
    return assign_test_to_candidate(conn, assignment)

@app.get("/assignments/{test_id}")
def get_assignments_endpoint(test_id: uuid.UUID):
    conn = get_db_connection()
    return get_assignments_for_test(conn, test_id)

@app.post("/answers/")
def submit_answer_endpoint(answer: TestAnswerCreate):
    conn = get_db_connection()
    return submit_test_answer(conn, answer)

@app.post("/api/answers")
def submit_answer_api(answer: TestAnswerCreate):
    """API-aliased answers endpoint"""
    conn = get_db_connection()
    result = submit_test_answer(conn, answer)
    return {"success": True, "data": result}

@app.post("/api/filter_mcqs")
def filter_mcqs_endpoint(filters: FilterRequest):
    mcqs = fetch_mcqs(filters.language.value, filters.difficulty_level.value)
    if not mcqs:
        raise HTTPException(status_code=404, detail="No MCQs found with these filters.")
    return {"mcqs": mcqs}


# --- API-prefixed aliases so clients using `/api` base work with this monolith ---
@app.post("/api/tests", status_code=201)
def create_test_api(test: TestCreate):
    return create_test_endpoint(test)

@app.get("/api/tests")
def list_tests_api():
    return list_tests_endpoint()

@app.get("/api/tests/{test_id}")
def get_test_api(test_id: uuid.UUID):
    return get_test_endpoint(test_id)

@app.put("/api/tests/{test_id}")
def update_test_api(test_id: uuid.UUID, test: TestCreate):
    return update_test_endpoint(test_id, test)

@app.patch("/api/tests/{test_id}/publish")
def publish_test_api(test_id: uuid.UUID):
    return publish_test_endpoint(test_id)

@app.post("/api/assignments", status_code=201)
def assign_test_api(assignment: TestAssignmentCreate):
    result = assign_test_endpoint(assignment)
    return {"success": True, "data": result}

@app.get("/api/candidates/{candidate_id}/assignments")
def get_candidate_assignments_api(candidate_id: uuid.UUID):
    return get_assignments_for_candidate(candidate_id)

# ---- Assignment Management ----
@app.patch("/api/assignments/{assignment_id}/start")
def start_assignment_endpoint(assignment_id: uuid.UUID):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE test_assignments SET status = %s, started_at = CURRENT_TIMESTAMP WHERE assignment_id = %s RETURNING assignment_id, status;",
            ("STARTED", assignment_id)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Assignment not found")
        return {"success": True, "data": {"assignment_id": str(row[0]), "status": row[1]}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting assignment: {e}")
        return {"success": False, "error": "Error starting assignment"}

@app.patch("/api/assignments/{assignment_id}/end")
def end_assignment_endpoint(assignment_id: uuid.UUID):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE test_assignments SET status = %s, submitted_at = CURRENT_TIMESTAMP WHERE assignment_id = %s RETURNING assignment_id, status;",
            ("COMPLETED", assignment_id)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Assignment not found")
        return {"success": True, "data": {"assignment_id": str(row[0]), "status": row[1]}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending assignment: {e}")
        return {"success": False, "error": "Error ending assignment"}

@app.get("/api/assignments/{assignment_id}")
def get_assignment_endpoint(assignment_id: uuid.UUID):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT assignment_id, test_id, candidate_id, status, scheduled_start_time, scheduled_end_time, started_at, submitted_at FROM test_assignments WHERE assignment_id = %s;",
            (assignment_id,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Assignment not found")
        return {
            "success": True,
            "data": {
                "assignment_id": str(row[0]),
                "test_id": str(row[1]),
                "candidate_id": str(row[2]),
                "status": row[3],
                "scheduled_start_time": row[4].isoformat() if row[4] else None,
                "scheduled_end_time": row[5].isoformat() if row[5] else None,
                "started_at": row[6].isoformat() if row[6] else None,
                "submitted_at": row[7].isoformat() if row[7] else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching assignment: {e}")
        return {"success": False, "error": "Error fetching assignment"}

# ---- Test Questions ----
@app.get("/api/tests/{test_id}/questions")
def get_test_questions_endpoint(test_id: uuid.UUID):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch MCQ questions for this test
        cur.execute("""
            SELECT mq.question_id, mq.question_text, mq.option_a, mq.option_b, mq.option_c, mq.option_d,
                   mq.correct_answer, mq.difficulty, mq.marks
            FROM test_questions tq
            JOIN mcq_questions mq ON tq.question_id = mq.question_id
            WHERE tq.test_id = %s AND tq.question_type = 'multiple_choice'
            ORDER BY tq.order_index;
        """, (test_id,))
        mcq_rows = cur.fetchall()
        
        # Fetch coding questions for this test
        cur.execute("""
            SELECT cq.question_id, cq.title, cq.description, cq.difficulty, cq.language, cq.marks
            FROM test_questions tq
            JOIN coding_questions cq ON tq.question_id = cq.question_id
            WHERE tq.test_id = %s AND tq.question_type = 'coding'
            ORDER BY tq.order_index;
        """, (test_id,))
        coding_rows = cur.fetchall()
        
        # Fetch test metadata
        cur.execute(
            "SELECT test_id, test_name, duration_minutes, status FROM tests WHERE test_id = %s;",
            (test_id,)
        )
        test_row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not test_row:
            raise HTTPException(status_code=404, detail="Test not found")
        
        mcq_questions = [
            {
                "question_id": str(r[0]),
                "question_text": r[1],
                "option_a": r[2],
                "option_b": r[3],
                "option_c": r[4],
                "option_d": r[5],
                "correct_answer": r[6],
                "difficulty": r[7],
                "marks": r[8],
            }
            for r in mcq_rows
        ]
        
        coding_questions = [
            {
                "question_id": str(r[0]),
                "title": r[1],
                "description": r[2],
                "difficulty": r[3],
                "language": r[4],
                "marks": r[5],
            }
            for r in coding_rows
        ]
        
        return {
            "success": True,
            "data": {
                "test_id": str(test_row[0]),
                "test_name": test_row[1],
                "duration_minutes": test_row[2],
                "status": test_row[3],
                "mcq_questions": mcq_questions,
                "coding_questions": coding_questions,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching test questions: {e}")
        return {"success": False, "error": "Error fetching test questions"}

# ---- Answers ----
@app.get("/api/assignments/{assignment_id}/answers")
def get_assignment_answers_endpoint(assignment_id: uuid.UUID):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT answer_id, assignment_id, question_id, question_type, selected_option, code_submission, code_output, score FROM test_answers WHERE assignment_id = %s;",
            (assignment_id,)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        answers = [
            {
                "answer_id": str(r[0]),
                "assignment_id": str(r[1]),
                "question_id": str(r[2]),
                "question_type": r[3],
                "selected_option": r[4],
                "code_submission": r[5],
                "code_output": r[6],
                "score": r[7],
            }
            for r in rows
        ]
        
        return {"success": True, "data": answers}
    except Exception as e:
        logger.error(f"Error fetching answers: {e}")
        return {"success": False, "error": "Error fetching answers"}

# ---- Reports ----
@app.post("/api/reports/{assignment_id}/generate")
def generate_report_endpoint(assignment_id: uuid.UUID):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get assignment info
        cur.execute(
            "SELECT test_id, candidate_id, started_at, submitted_at FROM test_assignments WHERE assignment_id = %s;",
            (assignment_id,)
        )
        assign_row = cur.fetchone()
        if not assign_row:
            raise HTTPException(status_code=404, detail="Assignment not found")
        
        test_id, candidate_id, started_at, submitted_at = assign_row
        
        # Get test info
        cur.execute("SELECT test_name FROM tests WHERE test_id = %s;", (test_id,))
        test_row = cur.fetchone()
        test_name = test_row[0] if test_row else "Unknown Test"
        
        # Calculate duration
        duration_seconds = 0
        if started_at and submitted_at:
            duration_seconds = int((submitted_at - started_at).total_seconds())
        
        # Get all answers for assignment
        cur.execute(
            "SELECT COUNT(*), SUM(CASE WHEN is_correct_mcq THEN 1 ELSE 0 END), SUM(score) FROM test_answers WHERE assignment_id = %s;",
            (assignment_id,)
        )
        answer_row = cur.fetchone()
        total_answers = answer_row[0] or 0
        correct_answers = answer_row[1] or 0
        total_score = answer_row[2] or 0
        
        percentage = (total_score / max(total_answers, 1)) * 100 if total_answers > 0 else 0
        
        # Create report record
        report_id = uuid.uuid4()
        cur.execute("""
            INSERT INTO candidate_reports (report_id, candidate_id, test_id, total_score, total_max, percentage, duration_seconds, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING report_id;
        """, (report_id, candidate_id, test_id, total_score, total_answers, percentage, duration_seconds, "completed"))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "report_id": str(report_id),
                "assignment_id": str(assignment_id),
                "test_name": test_name,
                "total_score": total_score,
                "total_answers": total_answers,
                "correct_answers": correct_answers,
                "percentage": percentage,
                "duration_seconds": duration_seconds,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return {"success": False, "error": f"Error generating report: {str(e)}"}

@app.get("/api/reports/{report_id}")
def fetch_report_endpoint(report_id: uuid.UUID):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT report_id, candidate_id, test_id, total_score, total_max, percentage, duration_seconds, status, created_at
            FROM candidate_reports
            WHERE report_id = %s;
        """, (report_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "success": True,
            "data": {
                "report_id": str(row[0]),
                "candidate_id": str(row[1]),
                "test_id": str(row[2]),
                "total_score": row[3],
                "total_max": row[4],
                "percentage": row[5],
                "duration_seconds": row[6],
                "status": row[7],
                "created_at": row[8].isoformat() if row[8] else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching report: {e}")
        return {"success": False, "error": "Error fetching report"}
