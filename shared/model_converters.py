"""
Model Conversion Utilities
==========================

Functions to convert between:
- Pydantic models (APIs)
- SQLAlchemy models (Database)
- MongoDB documents
- External API formats (Gemini, etc.)

This module provides consistent, tested conversion patterns across the platform.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json

# Import models (these would be actual imports in real code)
# from shared.models import (
#     Submission, AnalysisResult, CodeSubmission, TestAnswer,
#     Test, TestAssignment, MCQQuestion, CodingProblem, etc.
# )
# from shared.database_models import (
#     Test as SQLTest, TestAnswer as SQLTestAnswer,
#     CodeSubmission as SQLCodeSubmission, etc.
# )


# ============================================================================
# CODE SUBMISSION CONVERSIONS
# ============================================================================

def convert_code_submission_to_analysis_request(
    submission: 'CodeSubmission',
    problem: 'CodingQuestion'
) -> 'Submission':
    """
    Convert CodeSubmission (database) to Submission (Gemini API request)
    
    Args:
        submission: Code submission from database
        problem: Associated coding problem
    
    Returns:
        Submission model ready for Gemini API analysis
    
    Example:
        >>> submission = db.query(CodeSubmission).first()
        >>> problem = db.query(CodingQuestion).filter(...).first()
        >>> analysis_request = convert_code_submission_to_analysis_request(submission, problem)
        >>> response = gemini_client.analyze(analysis_request)
    """
    return {
        "candidate_id": str(submission.candidate_id),
        "question": problem.description,
        "expected_output": problem.sample_output or submission.expected_output,
        "candidate_output": submission.output or submission.stdout,
        "candidate_code": submission.code,
        "language": submission.language.value
    }


def convert_analysis_result_to_test_answer_enrichment(
    analysis_result: 'AnalysisResult',
    test_answer: 'SQLTestAnswer'
) -> 'SQLTestAnswer':
    """
    Enrich TestAnswer with AI analysis results
    
    Args:
        analysis_result: Result from Gemini code analysis
        test_answer: TestAnswer to enrich
    
    Returns:
        Updated TestAnswer with analysis data
    
    Example:
        >>> analysis = process_gemini_response(response)
        >>> test_answer = session.query(SQLTestAnswer).first()
        >>> enriched = convert_analysis_result_to_test_answer_enrichment(analysis, test_answer)
        >>> session.commit()
    """
    test_answer.ai_analysis = analysis_result.detailed_analysis
    test_answer.ai_review_notes = analysis_result.improvements_suggested
    test_answer.code_quality_score = analysis_result.total_score
    test_answer.updated_at = datetime.utcnow()
    return test_answer


def convert_code_submission_db_to_pydantic(
    db_submission: 'SQLCodeSubmission'
) -> 'CodeSubmission':
    """
    Convert SQLAlchemy CodeSubmission to Pydantic model for API response
    
    Args:
        db_submission: SQLAlchemy CodeSubmission from database
    
    Returns:
        Pydantic CodeSubmission model
    
    Example:
        >>> db_sub = session.query(SQLCodeSubmission).first()
        >>> pydantic_sub = convert_code_submission_db_to_pydantic(db_sub)
        >>> return pydantic_sub.model_dump()  # For JSON response
    """
    return {
        "submission_id": db_submission.submission_id,
        "candidate_id": db_submission.candidate_id,
        "problem_id": db_submission.problem_id,
        "language": db_submission.language.value,
        "code": db_submission.code,
        "stdin": db_submission.stdin,
        "status": db_submission.status.value,
        "stdout": db_submission.stdout,
        "stderr": db_submission.stderr,
        "output": db_submission.output,
        "expected_output": db_submission.expected_output,
        "is_passed": db_submission.is_passed,
        "passed_test_cases": db_submission.passed_test_cases,
        "total_test_cases": db_submission.total_test_cases,
        "execution_time_ms": db_submission.execution_time_ms,
        "memory_used_mb": db_submission.memory_used_mb,
        "submitted_at": db_submission.submitted_at
    }


def convert_pydantic_code_submission_to_db(
    pydantic_submission: 'CodeSubmission'
) -> 'SQLCodeSubmission':
    """
    Convert Pydantic CodeSubmission (API request) to SQLAlchemy model
    
    Args:
        pydantic_submission: Pydantic model from API request
    
    Returns:
        SQLAlchemy model for database storage
    
    Example:
        >>> api_request = CodeSubmission(...)  # from request body
        >>> db_submission = convert_pydantic_code_submission_to_db(api_request)
        >>> session.add(db_submission)
        >>> session.commit()
    """
    from datetime import datetime
    return {
        "submission_id": uuid.uuid4(),
        "candidate_id": pydantic_submission.candidate_id,
        "problem_id": pydantic_submission.problem_id,
        "language": pydantic_submission.language,
        "code": pydantic_submission.code,
        "stdin": pydantic_submission.stdin,
        "status": "pending",
        "stdout": "",
        "stderr": "",
        "output": "",
        "expected_output": pydantic_submission.expected_output or "",
        "is_passed": False,
        "passed_test_cases": 0,
        "total_test_cases": 0,
        "submitted_at": datetime.utcnow()
    }


# ============================================================================
# TEST ASSIGNMENT CONVERSIONS
# ============================================================================

def convert_test_assignment_create_to_db(
    assignment_create: 'TestAssignmentCreate',
    created_at: datetime = None
) -> 'SQLTestAssignment':
    """
    Convert TestAssignmentCreate (Pydantic) to SQLAlchemy model
    
    Args:
        assignment_create: API request model
        created_at: Optional creation timestamp
    
    Returns:
        SQLAlchemy TestAssignment for database
    
    Example:
        >>> request = TestAssignmentCreate(test_id=test_id, candidate_id=cand_id)
        >>> db_assign = convert_test_assignment_create_to_db(request)
        >>> session.add(db_assign)
        >>> session.commit()
    """
    return {
        "assignment_id": uuid.uuid4(),
        "test_id": assignment_create.test_id,
        "candidate_id": assignment_create.candidate_id,
        "status": "pending",
        "scheduled_start_time": assignment_create.scheduled_start_time,
        "scheduled_end_time": assignment_create.scheduled_end_time,
        "max_attempts": assignment_create.max_attempts,
        "created_at": created_at or datetime.utcnow()
    }


def convert_test_assignment_db_to_pydantic(
    db_assignment: 'SQLTestAssignment'
) -> 'TestAssignment':
    """
    Convert SQLAlchemy TestAssignment to Pydantic model for API
    
    Args:
        db_assignment: SQLAlchemy model from database
    
    Returns:
        Pydantic TestAssignment model
    
    Example:
        >>> db_assign = session.query(SQLTestAssignment).first()
        >>> pydantic_assign = convert_test_assignment_db_to_pydantic(db_assign)
        >>> return pydantic_assign.model_dump()
    """
    return {
        "assignment_id": db_assignment.assignment_id,
        "test_id": db_assignment.test_id,
        "candidate_id": db_assignment.candidate_id,
        "status": db_assignment.status.value,
        "scheduled_start_time": db_assignment.scheduled_start_time,
        "scheduled_end_time": db_assignment.scheduled_end_time,
        "max_attempts": db_assignment.max_attempts,
        "created_at": db_assignment.created_at,
        "started_at": db_assignment.started_at,
        "submitted_at": db_assignment.submitted_at,
        "score": db_assignment.score
    }


# ============================================================================
# TEST ANSWER CONVERSIONS
# ============================================================================

def convert_mcq_answer_to_test_answer(
    question_id: uuid.UUID,
    assignment_id: uuid.UUID,
    test_id: uuid.UUID,
    candidate_id: uuid.UUID,
    selected_option: str,
    correct_answer: str,
    marks: int = 1
) -> Dict[str, Any]:
    """
    Convert MCQ answer input to TestAnswer database model
    
    Args:
        question_id: The MCQ question ID
        assignment_id: Test assignment ID
        test_id: Test ID
        candidate_id: Candidate user ID
        selected_option: A, B, C, or D
        correct_answer: A, B, C, or D
        marks: Maximum marks for question
    
    Returns:
        Dictionary ready for TestAnswer creation
    
    Example:
        >>> answer_data = convert_mcq_answer_to_test_answer(
        ...     question_id=q_id,
        ...     assignment_id=a_id,
        ...     test_id=t_id,
        ...     candidate_id=c_id,
        ...     selected_option='A',
        ...     correct_answer='A',
        ...     marks=2
        ... )
        >>> db_answer = SQLTestAnswer(**answer_data)
        >>> session.add(db_answer)
    """
    is_correct = selected_option == correct_answer
    score = marks if is_correct else 0.0
    
    return {
        "answer_id": uuid.uuid4(),
        "assignment_id": assignment_id,
        "test_id": test_id,
        "question_id": question_id,
        "question_type": "multiple_choice",
        "candidate_id": candidate_id,
        "selected_option": selected_option,
        "is_correct_mcq": is_correct,
        "score": float(score),
        "max_score": float(marks),
        "submitted_at": datetime.utcnow()
    }


def convert_coding_answer_to_test_answer(
    problem_id: uuid.UUID,
    assignment_id: uuid.UUID,
    test_id: uuid.UUID,
    candidate_id: uuid.UUID,
    code_submission_id: uuid.UUID,
    marks: int = 1,
    passed: bool = False
) -> Dict[str, Any]:
    """
    Convert coding submission to TestAnswer database model
    
    Args:
        problem_id: The coding problem ID
        assignment_id: Test assignment ID
        test_id: Test ID
        candidate_id: Candidate user ID
        code_submission_id: Reference to CodeSubmission
        marks: Maximum marks for problem
        passed: Whether code passed all test cases
    
    Returns:
        Dictionary ready for TestAnswer creation
    
    Example:
        >>> answer_data = convert_coding_answer_to_test_answer(
        ...     problem_id=p_id,
        ...     assignment_id=a_id,
        ...     test_id=t_id,
        ...     candidate_id=c_id,
        ...     code_submission_id=sub_id,
        ...     marks=5,
        ...     passed=True
        ... )
    """
    score = float(marks) if passed else 0.0
    
    return {
        "answer_id": uuid.uuid4(),
        "assignment_id": assignment_id,
        "test_id": test_id,
        "question_id": problem_id,
        "question_type": "coding",
        "candidate_id": candidate_id,
        "code_submission_id": code_submission_id,
        "code_status": "pending",  # Will be updated after execution
        "code_passed": passed,
        "score": score,
        "max_score": float(marks),
        "submitted_at": datetime.utcnow()
    }


def convert_test_answer_db_to_pydantic(
    db_answer: 'SQLTestAnswer'
) -> 'TestAnswer':
    """
    Convert SQLAlchemy TestAnswer to Pydantic model for API response
    
    Args:
        db_answer: SQLAlchemy TestAnswer from database
    
    Returns:
        Pydantic TestAnswer model
    
    Example:
        >>> db_answer = session.query(SQLTestAnswer).first()
        >>> pydantic_answer = convert_test_answer_db_to_pydantic(db_answer)
        >>> return pydantic_answer.model_dump()
    """
    return {
        "answer_id": db_answer.answer_id,
        "assignment_id": db_answer.assignment_id,
        "test_id": db_answer.test_id,
        "question_id": db_answer.question_id,
        "question_type": db_answer.question_type.value,
        "selected_option": db_answer.selected_option,
        "is_correct_mcq": db_answer.is_correct_mcq,
        "code_submission_id": db_answer.code_submission_id,
        "code": db_answer.code,
        "language": db_answer.language.value if db_answer.language else None,
        "code_status": db_answer.code_status.value,
        "code_output": db_answer.code_output,
        "code_passed": db_answer.code_passed,
        "score": db_answer.score,
        "max_score": db_answer.max_score,
        "time_spent_seconds": db_answer.time_spent_seconds,
        "ai_analysis": db_answer.ai_analysis,
        "ai_review_notes": db_answer.ai_review_notes,
        "code_quality_score": db_answer.code_quality_score,
        "submitted_at": db_answer.submitted_at
    }


# ============================================================================
# REPORT CONVERSIONS
# ============================================================================

def convert_test_results_to_report(
    assignment: 'SQLTestAssignment',
    test_answers: List['SQLTestAnswer'],
    candidate: 'SQLUser',
    test: 'SQLTest'
) -> 'CandidateReportData':
    """
    Convert test results to complete candidate report
    
    Args:
        assignment: Test assignment
        test_answers: List of all test answers
        candidate: Candidate user
        test: Test definition
    
    Returns:
        Complete candidate report data
    
    Example:
        >>> assignment = session.query(SQLTestAssignment).first()
        >>> test_answers = session.query(SQLTestAnswer).filter(...).all()
        >>> candidate = session.query(SQLUser).first()
        >>> test = session.query(SQLTest).first()
        >>> report = convert_test_results_to_report(assignment, test_answers, candidate, test)
    """
    # Calculate MCQ section
    mcq_answers = [a for a in test_answers if a.question_type == "multiple_choice"]
    mcq_correct = sum(1 for a in mcq_answers if a.is_correct_mcq)
    mcq_wrong = sum(1 for a in mcq_answers if not a.is_correct_mcq and a.selected_option)
    mcq_skipped = sum(1 for a in mcq_answers if not a.selected_option)
    mcq_score = sum(a.score for a in mcq_answers)
    mcq_max = sum(a.max_score for a in mcq_answers)
    
    # Calculate coding section
    coding_answers = [a for a in test_answers if a.question_type == "coding"]
    coding_passed = sum(1 for a in coding_answers if a.code_passed)
    coding_failed = len(coding_answers) - coding_passed
    coding_score = sum(a.score for a in coding_answers)
    coding_max = sum(a.max_score for a in coding_answers)
    
    # Calculate totals
    total_score = mcq_score + coding_score
    total_max = mcq_max + coding_max
    percentage = (total_score / total_max * 100) if total_max > 0 else 0.0
    
    # Determine grade
    grade = _calculate_grade(percentage)
    
    # Calculate duration
    duration_seconds = 0
    if assignment.started_at and assignment.submitted_at:
        duration_seconds = int((assignment.submitted_at - assignment.started_at).total_seconds())
    
    return {
        "report_id": uuid.uuid4(),
        "candidate_id": candidate.user_id,
        "candidate_name": candidate.full_name,
        "candidate_email": candidate.email,
        "test_id": test.test_id,
        "test_name": test.test_name,
        "test_date": assignment.started_at or datetime.utcnow(),
        "duration_minutes": test.duration_minutes,
        "mcq": {
            "max_marks": int(mcq_max),
            "marks_obtained": int(mcq_score),
            "correct": mcq_correct,
            "wrong": mcq_wrong,
            "skipped": mcq_skipped,
            "questions": [_format_mcq_answer(a) for a in mcq_answers]
        },
        "coding": {
            "max_marks": int(coding_max),
            "marks_obtained": int(coding_score),
            "output_ok": all(a.code_passed for a in coding_answers),
            "questions": [_format_coding_answer(a) for a in coding_answers]
        },
        "total_score": total_score,
        "total_max": total_max,
        "percentage": percentage,
        "grade": grade,
        "status": "completed",
        "created_at": datetime.utcnow()
    }


def convert_report_db_to_pydantic(
    db_report: 'SQLCandidateReport'
) -> 'CandidateReportData':
    """
    Convert SQLAlchemy report to Pydantic model for API response
    
    Args:
        db_report: SQLAlchemy CandidateReport from database
    
    Returns:
        Pydantic CandidateReportData model
    
    Example:
        >>> db_report = session.query(SQLCandidateReport).first()
        >>> pydantic_report = convert_report_db_to_pydantic(db_report)
        >>> return pydantic_report.model_dump()
    """
    json_data = db_report.json_data or {}
    
    return {
        "report_id": db_report.report_id,
        "candidate_id": db_report.candidate_id,
        "candidate_name": json_data.get("candidate_name", ""),
        "candidate_email": json_data.get("candidate_email", ""),
        "test_id": db_report.test_id,
        "test_name": json_data.get("test_name", ""),
        "test_date": db_report.test_date,
        "duration_minutes": json_data.get("duration_minutes", 0),
        "mcq": json_data.get("mcq", {}),
        "coding": json_data.get("coding", {}),
        "total_score": db_report.total_score,
        "total_max": db_report.total_max,
        "percentage": db_report.percentage,
        "grade": db_report.grade,
        "status": db_report.status,
        "created_at": db_report.created_at
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _calculate_grade(percentage: float) -> str:
    """
    Calculate letter grade from percentage
    
    Args:
        percentage: Score percentage (0-100)
    
    Returns:
        Letter grade: A, B, C, D, or F
    
    Example:
        >>> grade = _calculate_grade(85.5)
        >>> assert grade == 'A'
    """
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'


def _format_mcq_answer(answer: 'SQLTestAnswer') -> Dict[str, Any]:
    """Format MCQ answer for report"""
    return {
        "question_id": str(answer.question_id),
        "selected_option": answer.selected_option,
        "is_correct": answer.is_correct_mcq,
        "score": answer.score,
        "time_spent_seconds": answer.time_spent_seconds
    }


def _format_coding_answer(answer: 'SQLTestAnswer') -> Dict[str, Any]:
    """Format coding answer for report"""
    return {
        "question_id": str(answer.question_id),
        "language": answer.language.value if answer.language else None,
        "passed": answer.code_passed,
        "score": answer.score,
        "status": answer.code_status.value,
        "time_spent_seconds": answer.time_spent_seconds,
        "ai_score": answer.code_quality_score
    }


# ============================================================================
# MONGODB CONVERSION FUNCTIONS
# ============================================================================

def convert_coding_problem_db_to_mongodb(
    db_problem: 'SQLCodingQuestion'
) -> Dict[str, Any]:
    """
    Convert SQLAlchemy CodingQuestion to MongoDB document format
    
    Args:
        db_problem: SQLAlchemy CodingQuestion from PostgreSQL
    
    Returns:
        Dictionary formatted for MongoDB insertion
    
    Example:
        >>> db_problem = session.query(SQLCodingQuestion).first()
        >>> mongo_doc = convert_coding_problem_db_to_mongodb(db_problem)
        >>> collection.insert_one(mongo_doc)
    """
    return {
        "_id": str(db_problem.question_id),
        "id": str(db_problem.question_id),
        "title": db_problem.title,
        "description": db_problem.description,
        "difficulty": db_problem.difficulty.value,
        "language": db_problem.language.value,
        "sample_input": db_problem.sample_input,
        "sample_output": db_problem.sample_output,
        "constraints": db_problem.constraints,
        "test_cases": db_problem.test_cases,
        "labels": db_problem.labels,
        "time_limit_seconds": db_problem.time_limit_seconds,
        "memory_limit_mb": db_problem.memory_limit_mb,
        "created_at": db_problem.created_at.isoformat(),
        "updated_at": db_problem.updated_at.isoformat()
    }


def convert_code_submission_db_to_mongodb(
    db_submission: 'SQLCodeSubmission'
) -> Dict[str, Any]:
    """
    Convert SQLAlchemy CodeSubmission to MongoDB document format
    
    Args:
        db_submission: SQLAlchemy CodeSubmission from PostgreSQL
    
    Returns:
        Dictionary formatted for MongoDB insertion
    
    Example:
        >>> db_sub = session.query(SQLCodeSubmission).first()
        >>> mongo_doc = convert_code_submission_db_to_mongodb(db_sub)
        >>> collection.insert_one(mongo_doc)
    """
    return {
        "_id": str(db_submission.submission_id),
        "submission_id": str(db_submission.submission_id),
        "candidate_id": str(db_submission.candidate_id),
        "problem_id": str(db_submission.problem_id),
        "language": db_submission.language.value,
        "code": db_submission.code,
        "stdin": db_submission.stdin,
        "status": db_submission.status.value,
        "stdout": db_submission.stdout,
        "stderr": db_submission.stderr,
        "output": db_submission.output,
        "expected_output": db_submission.expected_output,
        "is_passed": db_submission.is_passed,
        "passed_test_cases": db_submission.passed_test_cases,
        "total_test_cases": db_submission.total_test_cases,
        "execution_time_ms": db_submission.execution_time_ms,
        "memory_used_mb": db_submission.memory_used_mb,
        "submitted_at": db_submission.submitted_at.isoformat()
    }


# ============================================================================
# BULK CONVERSION FUNCTIONS
# ============================================================================

def convert_test_answers_to_pydantic_list(
    db_answers: List['SQLTestAnswer']
) -> List['TestAnswer']:
    """
    Bulk convert list of TestAnswers to Pydantic models
    
    Args:
        db_answers: List of SQLAlchemy TestAnswers
    
    Returns:
        List of Pydantic TestAnswer models
    
    Example:
        >>> db_answers = session.query(SQLTestAnswer).filter(...).all()
        >>> pydantic_answers = convert_test_answers_to_pydantic_list(db_answers)
    """
    return [convert_test_answer_db_to_pydantic(answer) for answer in db_answers]


def convert_questions_to_pydantic_list(
    db_questions: List['SQLTestQuestion']
) -> List['TestQuestion']:
    """
    Bulk convert test questions to Pydantic models
    
    Args:
        db_questions: List of SQLAlchemy TestQuestions
    
    Returns:
        List of Pydantic TestQuestion models
    """
    return [_convert_test_question_db_to_pydantic(q) for q in db_questions]


def _convert_test_question_db_to_pydantic(
    db_question: 'SQLTestQuestion'
) -> 'TestQuestion':
    """Convert single test question"""
    return {
        "test_question_id": db_question.test_question_id,
        "test_id": db_question.test_id,
        "question_id": db_question.question_id,
        "question_type": db_question.question_type.value,
        "order_index": db_question.order_index,
        "marks": db_question.marks,
        "time_limit_seconds": db_question.time_limit_seconds
    }
