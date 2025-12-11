"""
INTEGRATION GUIDE - Complete Model Usage
=========================================

This guide shows how to use shared models across the entire platform
with real-world examples from each service.

TABLE OF CONTENTS
=================
1. Setup & Database
2. Test Management Flow
3. Code Submission & Analysis Flow
4. Report Generation Flow
5. Complete Example: End-to-End Test
6. API Endpoint Examples
7. Troubleshooting
"""

# ===========================================================================
# 1. SETUP & DATABASE INITIALIZATION
# ===========================================================================

"""
Step 1: Import and create database engine
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.database_models import Base

# Database connection
DATABASE_URL = "postgresql+psycopg://user:password@localhost/talentshire"
engine = create_engine(DATABASE_URL, echo=False)

# Create tables
Base.metadata.create_all(engine)

# Session factory
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===========================================================================
# 2. TEST MANAGEMENT FLOW
# ===========================================================================

"""
Flow: Admin creates test → Assigns to candidates → Candidates answer
Models: Test, TestQuestion, MCQQuestion, CodingQuestion, TestAssignment
Database: tests, test_questions, test_assignments
"""

from fastapi import FastAPI, Depends, HTTPException
from shared.models import TestCreate, Test, TestAssignmentCreate, TestAssignment
from shared.database_models import (
    Test as SQLTest, TestQuestion as SQLTestQuestion,
    TestAssignment as SQLTestAssignment, TestAnswer as SQLTestAnswer,
    MCQQuestion as SQLMCQQuestion, CodingQuestion as SQLCodingQuestion
)
from shared.model_converters import (
    convert_test_assignment_create_to_db,
    convert_test_assignment_db_to_pydantic,
    convert_test_answer_db_to_pydantic
)
from typing import List
import uuid
from datetime import datetime

app = FastAPI()


# Endpoint 1: Admin creates a test
@app.post("/api/tests")
async def create_test(
    test_create: TestCreate,
    admin_id: uuid.UUID,
    db = Depends(get_db)
):
    """
    Create a new test with questions
    
    Request:
    {
        "test_name": "Python Fundamentals",
        "duration_minutes": 60,
        "status": "active"
    }
    """
    # Create SQLAlchemy model
    db_test = SQLTest(
        test_id=uuid.uuid4(),
        test_name=test_create.test_name,
        duration_minutes=test_create.duration_minutes,
        status=test_create.status,
        created_by=admin_id
    )
    
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    
    # Convert back to Pydantic for response
    response = Test(
        test_id=db_test.test_id,
        test_name=db_test.test_name,
        duration_minutes=db_test.duration_minutes,
        status=db_test.status,
        created_by=db_test.created_by,
        created_at=db_test.created_at,
        updated_at=db_test.updated_at
    )
    
    return response.model_dump()


# Endpoint 2: Admin adds questions to test
@app.post("/api/tests/{test_id}/questions")
async def add_question_to_test(
    test_id: uuid.UUID,
    question_id: uuid.UUID,
    question_type: str,  # "multiple_choice" or "coding"
    order_index: int,
    marks: int = 1,
    db = Depends(get_db)
):
    """
    Add a question (MCQ or Coding) to a test
    """
    # Verify test exists
    test = db.query(SQLTest).filter(SQLTest.test_id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Verify question exists
    if question_type == "multiple_choice":
        question = db.query(SQLMCQQuestion).filter(
            SQLMCQQuestion.question_id == question_id
        ).first()
    else:  # coding
        question = db.query(SQLCodingQuestion).filter(
            SQLCodingQuestion.question_id == question_id
        ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Create test question
    test_question = SQLTestQuestion(
        test_question_id=uuid.uuid4(),
        test_id=test_id,
        question_id=question_id,
        question_type=question_type,
        order_index=order_index,
        marks=marks
    )
    
    db.add(test_question)
    
    # Update test total marks
    test.total_marks += marks
    
    db.commit()
    db.refresh(test_question)
    
    return {
        "test_question_id": test_question.test_question_id,
        "test_id": test_question.test_id,
        "question_id": test_question.question_id,
        "order_index": test_question.order_index,
        "marks": test_question.marks
    }


# Endpoint 3: Admin assigns test to candidate
@app.post("/api/assignments")
async def assign_test_to_candidate(
    assignment_create: TestAssignmentCreate,
    db = Depends(get_db)
):
    """
    Assign a test to a candidate
    
    Request:
    {
        "test_id": "uuid",
        "candidate_id": "uuid",
        "max_attempts": 1
    }
    """
    # Verify test and candidate exist
    test = db.query(SQLTest).filter(SQLTest.test_id == assignment_create.test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Create assignment using conversion function
    assignment_data = convert_test_assignment_create_to_db(assignment_create)
    db_assignment = SQLTestAssignment(**assignment_data)
    
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    # Convert back to Pydantic
    response = convert_test_assignment_db_to_pydantic(db_assignment)
    return response


# Endpoint 4: Get test details with questions
@app.get("/api/tests/{test_id}")
async def get_test(test_id: uuid.UUID, db = Depends(get_db)):
    """
    Get test with all questions loaded
    """
    test = db.query(SQLTest).filter(SQLTest.test_id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Relationships are lazy-loaded
    questions = test.questions
    
    return {
        "test_id": test.test_id,
        "test_name": test.test_name,
        "duration_minutes": test.duration_minutes,
        "total_marks": test.total_marks,
        "status": test.status.value,
        "questions_count": len(questions)
    }


# ===========================================================================
# 3. CODE SUBMISSION & ANALYSIS FLOW
# ===========================================================================

"""
Flow: Candidate submits code → Execute code → Analyze with Gemini → Store results
Models: CodeSubmission, Submission, AnalysisResult, CodeAnalysisResult, TestAnswer
Database: code_submissions, code_analysis_results, test_answers
"""

from shared.models import CodeSubmission, Submission, AnalysisResult
from shared.database_models import (
    CodeSubmission as SQLCodeSubmission,
    CodeAnalysisResult as SQLCodeAnalysisResult
)
from shared.model_converters import (
    convert_code_submission_to_analysis_request,
    convert_code_submission_db_to_pydantic,
    convert_analysis_result_to_test_answer_enrichment
)


# Endpoint 5: Submit code solution
@app.post("/api/coding/submit")
async def submit_code(
    submission: CodeSubmission,
    assignment_id: uuid.UUID,
    test_id: uuid.UUID,
    db = Depends(get_db)
):
    """
    Candidate submits code for a coding problem
    
    Request:
    {
        "candidate_id": "uuid",
        "problem_id": "uuid",
        "language": "Python",
        "code": "def solution(): ..."
    }
    """
    # Verify problem exists
    problem = db.query(SQLCodingQuestion).filter(
        SQLCodingQuestion.question_id == submission.problem_id
    ).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Create code submission in database
    db_submission = SQLCodeSubmission(
        submission_id=uuid.uuid4(),
        candidate_id=submission.candidate_id,
        problem_id=submission.problem_id,
        language=submission.language,
        code=submission.code,
        stdin=submission.stdin,
        expected_output=problem.sample_output,
        status="pending"
    )
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    # Note: In real implementation, trigger async execution service here
    # execution_service.execute_code.delay(str(db_submission.submission_id))
    
    # Convert to Pydantic for response
    response = convert_code_submission_db_to_pydantic(db_submission)
    return response


# Endpoint 6: Process code execution results and trigger analysis
async def process_code_execution(
    submission_id: uuid.UUID,
    execution_output: dict,  # {status, stdout, stderr, output, passed_tests, total_tests}
    db = Depends(get_db)
):
    """
    Called after code execution completes
    Updates submission and triggers AI analysis
    """
    # Get submission
    db_submission = db.query(SQLCodeSubmission).filter(
        SQLCodeSubmission.submission_id == submission_id
    ).first()
    if not db_submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Update execution results
    db_submission.status = execution_output['status']
    db_submission.stdout = execution_output.get('stdout', '')
    db_submission.stderr = execution_output.get('stderr', '')
    db_submission.output = execution_output.get('output', '')
    db_submission.is_passed = execution_output.get('passed', False)
    db_submission.passed_test_cases = execution_output.get('passed_tests', 0)
    db_submission.total_test_cases = execution_output.get('total_tests', 0)
    db_submission.execution_time_ms = execution_output.get('time_ms')
    
    db.commit()
    db.refresh(db_submission)
    
    # Get problem details
    problem = db.query(SQLCodingQuestion).filter(
        SQLCodingQuestion.question_id == db_submission.problem_id
    ).first()
    
    # Trigger Gemini analysis
    # Convert to Submission model for Gemini API
    analysis_request = convert_code_submission_to_analysis_request(db_submission, problem)
    
    # Call Gemini (pseudo-code)
    # gemini_response = await gemini_client.analyze(analysis_request)
    # analysis_result = AnalysisResult(**gemini_response)
    
    # Store analysis results (pseudo-code)
    # db_analysis = SQLCodeAnalysisResult(
    #     analysis_id=uuid.uuid4(),
    #     submission_id=submission_id,
    #     candidate_id=db_submission.candidate_id,
    #     total_score=analysis_result.total_score,
    #     improvements_suggested=analysis_result.improvements_suggested,
    #     detailed_analysis=analysis_result.detailed_analysis,
    #     code_review=analysis_result.code_review.model_dump() if analysis_result.code_review else None
    # )
    # db.add(db_analysis)
    # db.commit()


# ===========================================================================
# 4. REPORT GENERATION FLOW
# ===========================================================================

"""
Flow: Test submitted → Aggregate scores → Generate report → Store in DB
Models: CandidateReportData, MCQReportSection, CodingReportSection
Database: candidate_reports
"""

from shared.models import CandidateReportData
from shared.database_models import CandidateReport as SQLCandidateReport
from shared.model_converters import convert_test_results_to_report


# Endpoint 7: Submit test and generate report
@app.post("/api/assignments/{assignment_id}/submit")
async def submit_test(
    assignment_id: uuid.UUID,
    db = Depends(get_db)
):
    """
    Candidate submits test - generates report
    """
    # Get assignment with all related data
    assignment = db.query(SQLTestAssignment).filter(
        SQLTestAssignment.assignment_id == assignment_id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Mark as submitted
    assignment.status = "completed"
    assignment.submitted_at = datetime.utcnow()
    
    # Get all answers
    test_answers = db.query(SQLTestAnswer).filter(
        SQLTestAnswer.assignment_id == assignment_id
    ).all()
    
    # Get candidate and test
    candidate = db.query(SQLTest).filter(
        SQLTest.test_id == assignment.test_id
    ).first()
    test = db.query(SQLTest).filter(
        SQLTest.test_id == assignment.test_id
    ).first()
    
    # Generate report using conversion function
    report_data = convert_test_results_to_report(
        assignment, test_answers, candidate, test
    )
    
    # Store report in database
    db_report = SQLCandidateReport(
        report_id=report_data['report_id'],
        candidate_id=report_data['candidate_id'],
        test_id=report_data['test_id'],
        test_date=report_data['test_date'],
        total_score=report_data['total_score'],
        total_max=report_data['total_max'],
        percentage=report_data['percentage'],
        grade=report_data['grade'],
        mcq_score=report_data['mcq']['marks_obtained'],
        mcq_max=report_data['mcq']['max_marks'],
        mcq_correct=report_data['mcq']['correct'],
        mcq_wrong=report_data['mcq']['wrong'],
        mcq_skipped=report_data['mcq']['skipped'],
        coding_score=report_data['coding']['marks_obtained'],
        coding_max=report_data['coding']['max_marks'],
        coding_passed=sum(1 for a in test_answers if a.code_passed),
        coding_failed=sum(1 for a in test_answers if not a.code_passed and a.question_type == 'coding'),
        duration_seconds=int((assignment.submitted_at - assignment.started_at).total_seconds()) if assignment.started_at else 0,
        json_data=report_data
    )
    
    db.add(db_report)
    db.commit()
    
    # Generate PDF (using Swarang's report_generator)
    # pdf_path = generate_pdf_report(report_data)
    # db_report.pdf_url = pdf_path
    # db.commit()
    
    return {
        "report_id": report_data['report_id'],
        "total_score": report_data['total_score'],
        "total_max": report_data['total_max'],
        "percentage": report_data['percentage'],
        "grade": report_data['grade']
    }


# Endpoint 8: Retrieve generated report
@app.get("/api/reports/{report_id}")
async def get_report(report_id: uuid.UUID, db = Depends(get_db)):
    """
    Get saved report
    """
    report = db.query(SQLCandidateReport).filter(
        SQLCandidateReport.report_id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report.json_data


# ===========================================================================
# 5. COMPLETE EXAMPLE: END-TO-END TEST
# ===========================================================================

"""
This example shows the complete flow from test creation to report generation
"""

async def end_to_end_test_flow():
    """
    Complete workflow:
    1. Admin creates test with MCQ and coding questions
    2. Admin assigns to candidate
    3. Candidate answers MCQ questions
    4. Candidate submits code
    5. Code is executed and analyzed
    6. Report is generated
    """
    
    db = SessionLocal()
    
    try:
        # Step 1: Create MCQ question
        mcq = SQLMCQQuestion(
            question_id=uuid.uuid4(),
            question_text="What is the output of print(2 + 2)?",
            option_a="3",
            option_b="4",
            option_c="5",
            option_d="Error",
            correct_answer="B",
            difficulty="easy",
            language="python",
            marks=2
        )
        db.add(mcq)
        
        # Step 2: Create coding question
        coding = SQLCodingQuestion(
            question_id=uuid.uuid4(),
            title="Two Sum",
            description="Given array and target, find two numbers that add to target",
            difficulty="medium",
            language="python",
            sample_input="[1,2,3,4,5] target=7",
            sample_output="[2,5]",
            labels=["arrays", "two-pointers"],
            test_cases=[
                {"input": "[1,2,3] target=5", "output": "[2,3]"}
            ],
            marks=5
        )
        db.add(coding)
        
        # Step 3: Create test
        test = SQLTest(
            test_id=uuid.uuid4(),
            test_name="Python Basics Test",
            duration_minutes=30,
            status="active",
            created_by=uuid.uuid4()  # Admin ID
        )
        db.add(test)
        db.flush()
        
        # Step 4: Add questions to test
        test_mcq = SQLTestQuestion(
            test_question_id=uuid.uuid4(),
            test_id=test.test_id,
            question_id=mcq.question_id,
            question_type="multiple_choice",
            order_index=1,
            marks=2
        )
        test.total_marks += 2
        
        test_coding = SQLTestQuestion(
            test_question_id=uuid.uuid4(),
            test_id=test.test_id,
            question_id=coding.question_id,
            question_type="coding",
            order_index=2,
            marks=5
        )
        test.total_marks += 5
        
        db.add(test_mcq)
        db.add(test_coding)
        
        # Step 5: Create candidate
        candidate_id = uuid.uuid4()
        
        # Step 6: Assign test to candidate
        assignment = SQLTestAssignment(
            assignment_id=uuid.uuid4(),
            test_id=test.test_id,
            candidate_id=candidate_id,
            status="pending",
            max_attempts=1
        )
        db.add(assignment)
        db.flush()
        
        # Step 7: Mark as started
        assignment.status = "in_progress"
        assignment.started_at = datetime.utcnow()
        
        # Step 8: Candidate answers MCQ
        mcq_answer = SQLTestAnswer(
            answer_id=uuid.uuid4(),
            assignment_id=assignment.assignment_id,
            test_id=test.test_id,
            question_id=mcq.question_id,
            question_type="multiple_choice",
            candidate_id=candidate_id,
            selected_option="B",
            is_correct_mcq=True,
            score=2.0,
            max_score=2.0
        )
        db.add(mcq_answer)
        
        # Step 9: Candidate submits code
        submission = SQLCodeSubmission(
            submission_id=uuid.uuid4(),
            candidate_id=candidate_id,
            problem_id=coding.question_id,
            language="python",
            code="def two_sum(arr, target):\n    return sorted([a for a in arr if target-a in arr][:2])",
            expected_output="[2,5]",
            output="[2,5]",
            is_passed=True,
            passed_test_cases=1,
            total_test_cases=1,
            status="success"
        )
        db.add(submission)
        db.flush()
        
        # Step 10: Create test answer for coding
        coding_answer = SQLTestAnswer(
            answer_id=uuid.uuid4(),
            assignment_id=assignment.assignment_id,
            test_id=test.test_id,
            question_id=coding.question_id,
            question_type="coding",
            candidate_id=candidate_id,
            code_submission_id=submission.submission_id,
            code_passed=True,
            score=5.0,
            max_score=5.0
        )
        db.add(coding_answer)
        
        db.commit()
        
        # Step 11: Mark test as submitted
        assignment.status = "completed"
        assignment.submitted_at = datetime.utcnow()
        db.commit()
        
        # Step 12: Generate report
        test_answers = [mcq_answer, coding_answer]
        report_data = convert_test_results_to_report(
            assignment, test_answers, db.query(SQLTest).filter(
                SQLTest.test_id == candidate_id  # Should be user
            ).first(), test
        )
        
        # Step 13: Store report
        report = SQLCandidateReport(
            report_id=uuid.uuid4(),
            candidate_id=candidate_id,
            test_id=test.test_id,
            total_score=7.0,
            total_max=7.0,
            percentage=100.0,
            grade='A',
            duration_seconds=600,
            json_data=report_data
        )
        db.add(report)
        db.commit()
        
        print(f"✓ Test completed successfully!")
        print(f"  Report ID: {report.report_id}")
        print(f"  Score: {report.total_score}/{report.total_max}")
        print(f"  Grade: {report.grade}")
        
    finally:
        db.close()


# ===========================================================================
# 6. API ENDPOINT EXAMPLES
# ===========================================================================

"""
Summary of key endpoints using shared models
"""

"""
POST /api/tests
├─ Input: TestCreate (Pydantic)
├─ Output: Test (Pydantic)
└─ Storage: SQLTest (SQLAlchemy)

POST /api/tests/{test_id}/questions
├─ Input: question_id, question_type, marks
├─ Output: TestQuestion (Pydantic)
└─ Storage: SQLTestQuestion (SQLAlchemy)

POST /api/assignments
├─ Input: TestAssignmentCreate (Pydantic)
├─ Output: TestAssignment (Pydantic)
└─ Storage: SQLTestAssignment (SQLAlchemy)

POST /api/coding/submit
├─ Input: CodeSubmission (Pydantic)
├─ Output: CodeSubmission (Pydantic)
└─ Storage: SQLCodeSubmission (SQLAlchemy)

POST /api/assignments/{id}/answer/mcq
├─ Input: question_id, selected_option
├─ Output: TestAnswer (Pydantic)
└─ Storage: SQLTestAnswer (SQLAlchemy)

POST /api/assignments/{id}/submit
├─ Input: assignment_id
├─ Output: CandidateReportData (Pydantic)
└─ Storage: SQLCandidateReport (SQLAlchemy)

GET /api/reports/{report_id}
├─ Output: CandidateReportData (Pydantic)
└─ Storage: SQLCandidateReport (SQLAlchemy)
"""

# ===========================================================================
# 7. TROUBLESHOOTING
# ===========================================================================

"""
COMMON ISSUES & SOLUTIONS

Issue 1: Foreign key constraint violation
├─ Cause: Referencing non-existent record
├─ Solution: Verify referenced record exists before creation
└─ Example:
   problem = db.query(SQLCodingQuestion).filter(...).first()
   if not problem:
       raise HTTPException(404, "Problem not found")

Issue 2: Enum value mismatch
├─ Cause: Using string instead of Enum
├─ Solution: Use Enum values from models
└─ Example:
   # Wrong: code_status="pending"
   # Right: code_status=CodeExecutionStatusEnum.pending

Issue 3: Lazy loading issues
├─ Cause: Accessing relationships after session closed
├─ Solution: Eager load relationships or access within session
└─ Example:
   test = db.query(SQLTest).filter(...).first()
   questions = test.questions  # Access within session
   # Don't use questions after db.close()

Issue 4: Stale object errors
├─ Cause: Using object after session expired
├─ Solution: Refresh or re-query
└─ Example:
   db.refresh(obj)  # Reload from database
   # Or
   obj = db.query(SQLTest).filter_by(id=obj_id).first()

Issue 5: Circular imports
├─ Cause: Importing models in wrong order
├─ Solution: Use TYPE_CHECKING
└─ Example:
   from typing import TYPE_CHECKING
   if TYPE_CHECKING:
       from shared.models import Test
"""
