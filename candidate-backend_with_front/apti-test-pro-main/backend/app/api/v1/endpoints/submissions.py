from uuid import UUID
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from app.db.postgres import get_db
from app.db.mongodb import get_mongo_db

router = APIRouter()


@router.post("/mcq", status_code=201)
async def submit_mcq_answer(
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Save MCQ answer to test_answers table in PostgreSQL.
    
    Request body:
    {
        "assignment_id": "uuid",
        "question_id": "uuid",
        "selected_option": "A/B/C/D",
        "is_correct": true/false,
        "time_spent_seconds": 30,
        "candidate_id": "uuid"
    }
    """
    try:
        # Insert into test_answers table
        query = text("""
            INSERT INTO test_answers (
                assignment_id, 
                question_id, 
                question_type, 
                selected_option, 
                is_correct, 
                score,
                time_spent_seconds,
                candidate_id,
                submitted_at
            ) VALUES (
                :assignment_id,
                :question_id,
                'MCQ',
                :selected_option,
                :is_correct,
                :score,
                :time_spent_seconds,
                :candidate_id,
                CURRENT_TIMESTAMP
            ) RETURNING answer_id;
        """)
        
        result = await db.execute(
            query,
            {
                "assignment_id": str(data.get("assignment_id")),
                "question_id": str(data.get("question_id")),
                "selected_option": data.get("selected_option", "").upper(),
                "is_correct": data.get("is_correct", False),
                "score": 1.0 if data.get("is_correct") else 0.0,
                "time_spent_seconds": data.get("time_spent_seconds", 0),
                "candidate_id": str(data.get("candidate_id"))
            }
        )
        
        answer_id = result.scalar()
        await db.commit()
        
        return {
            "success": True,
            "answer_id": str(answer_id),
            "message": "MCQ answer saved to PostgreSQL test_answers table"
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving MCQ answer: {str(e)}")


@router.post("/code", status_code=201)
async def submit_code_answer(
    data: dict,
    db: AsyncSession = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """
    Save code submission to both PostgreSQL and MongoDB.
    
    PostgreSQL (test_answers table):
    - code_submission, code_output, code_status, code_passed, language, stdin, stdout
    
    MongoDB (code_submissions collection):
    - Full execution details and analysis
    
    Request body:
    {
        "assignment_id": "uuid",
        "question_id": "uuid",
        "code": "python code here",
        "language": "python",
        "code_status": "success/error/timeout",
        "code_passed": true/false,
        "code_output": "execution output",
        "stdin": "",
        "stdout": "result",
        "time_spent_seconds": 60,
        "candidate_id": "uuid"
    }
    """
    try:
        # Save to PostgreSQL test_answers
        query = text("""
            INSERT INTO test_answers (
                assignment_id,
                question_id,
                question_type,
                code_submission,
                code_output,
                code_status,
                code_passed,
                language,
                stdin,
                stdout,
                time_spent_seconds,
                candidate_id,
                submitted_at
            ) VALUES (
                :assignment_id,
                :question_id,
                'CODING',
                :code_submission,
                :code_output,
                :code_status,
                :code_passed,
                :language,
                :stdin,
                :stdout,
                :time_spent_seconds,
                :candidate_id,
                CURRENT_TIMESTAMP
            ) RETURNING answer_id;
        """)
        
        result = await db.execute(
            query,
            {
                "assignment_id": str(data.get("assignment_id")),
                "question_id": str(data.get("question_id")),
                "code_submission": data.get("code", ""),
                "code_output": data.get("code_output", ""),
                "code_status": data.get("code_status", "pending"),
                "code_passed": data.get("code_passed", False),
                "language": data.get("language", "python"),
                "stdin": data.get("stdin", ""),
                "stdout": data.get("stdout", ""),
                "time_spent_seconds": data.get("time_spent_seconds", 0),
                "candidate_id": str(data.get("candidate_id"))
            }
        )
        
        answer_id = result.scalar()
        await db.commit()
        
        # Also save to MongoDB for extended analysis
        mongo_collection = mongo_db["code_submissions"]
        mongo_doc = {
            "candidateId": str(data.get("candidate_id")),
            "assignmentId": str(data.get("assignment_id")),
            "questionId": str(data.get("question_id")),
            "code": data.get("code", ""),
            "language": data.get("language", "python"),
            "executionResult": {
                "status": data.get("code_status", "pending"),
                "output": data.get("code_output", ""),
                "passed": data.get("code_passed", False),
                "stdin": data.get("stdin", ""),
                "stdout": data.get("stdout", "")
            },
            "submittedAt": datetime.utcnow()
        }
        
        mongo_result = await mongo_collection.insert_one(mongo_doc)
        
        return {
            "success": True,
            "answer_id": str(answer_id),
            "mongo_id": str(mongo_result.inserted_id),
            "message": "Code submission saved to PostgreSQL test_answers and MongoDB"
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving code submission: {str(e)}")


@router.get("/assignment/{assignment_id}", status_code=200)
async def get_assignment_answers(
    assignment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all answers submitted for a test assignment from PostgreSQL.
    """
    try:
        query = text("""
            SELECT 
                answer_id, question_id, question_type, selected_option,
                code_submission, is_correct, score, code_status, code_passed,
                submitted_at
            FROM test_answers
            WHERE assignment_id = :assignment_id
            ORDER BY submitted_at DESC;
        """)
        
        result = await db.execute(query, {"assignment_id": assignment_id})
        rows = result.fetchall()
        
        answers = [
            {
                "answer_id": str(row[0]),
                "question_id": str(row[1]),
                "question_type": row[2],
                "selected_option": row[3],
                "code_submission": row[4],
                "is_correct": row[5],
                "score": float(row[6]) if row[6] else 0,
                "code_status": row[7],
                "code_passed": row[8],
                "submitted_at": row[9].isoformat() if row[9] else None
            }
            for row in rows
        ]
        
        return {
            "success": True,
            "assignment_id": assignment_id,
            "total_answers": len(answers),
            "answers": answers
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching answers: {str(e)}")


@router.get("/candidate/{candidate_id}", status_code=200)
async def get_candidate_submissions(
    candidate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all submissions from a candidate across all tests from PostgreSQL.
    """
    try:
        query = text("""
            SELECT 
                answer_id, assignment_id, question_type, is_correct,
                score, submitted_at
            FROM test_answers
            WHERE candidate_id = :candidate_id
            ORDER BY submitted_at DESC;
        """)
        
        result = await db.execute(query, {"candidate_id": candidate_id})
        rows = result.fetchall()
        
        submissions = [
            {
                "answer_id": str(row[0]),
                "assignment_id": str(row[1]),
                "question_type": row[2],
                "is_correct": row[3],
                "score": float(row[4]) if row[4] else 0,
                "submitted_at": row[5].isoformat() if row[5] else None
            }
            for row in rows
        ]
        
        return {
            "success": True,
            "candidate_id": candidate_id,
            "total_submissions": len(submissions),
            "submissions": submissions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching submissions: {str(e)}")
