# 🗺️ Talentshire - Visual Architecture & Flow Guide

## 🏗️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    TALENTSHIRE SYSTEM                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                                   │
│                    React 18 + TypeScript + Vite                          │
│                    http://localhost:8080/                                │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────┐            │
│  │  CandidateLogin.tsx                                     │            │
│  │  - Email login                                          │            │
│  │  - Token login                                          │            │
│  │  - Auth store update                                    │            │
│  └─────────┬───────────────────────────────────────────────┘            │
│            │                                                             │
│  ┌─────────▼───────────────────────────────────────────────────┐        │
│  │  CandidateTests.tsx                                         │        │
│  │  - Show available tests                                     │        │
│  │  - Navigate to test                                         │        │
│  └─────────┬───────────────────────────────────────────────────┘        │
│            │                                                             │
│  ┌─────────▼───────────────────────────────────────────────────┐        │
│  │  TestTaking.tsx ⭐ (CRITICAL)                              │        │
│  │  - Display questions (MCQ + Code)                          │        │
│  │  - Submit MCQ answers                                      │        │
│  │  - Submit code solutions                                   │        │
│  │  - Auto-save progress                                      │        │
│  └─────────┬───────────────────────────────────────────────────┘        │
│            │                                                             │
│  ┌─────────▼───────────────────────────────────────────────────┐        │
│  │  TestResults.tsx                                            │        │
│  │  - Display final scores                                     │        │
│  │  - Show answer details                                      │        │
│  │  - Generate report                                          │        │
│  └────────────────────────────────────────────────────────────┘        │
│                                                                          │
│  State Management: Zustand                                              │
│  - authStore: User login, token                                         │
│  - testStore: Test data, questions                                      │
│  - candidateTestStore: Progress, answers                                │
│                                                                          │
│  API Client: lib/api.ts                                                 │
│  BASE_URL: http://localhost:8000/api/v1                               │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │ HTTP/JSON API │               │
                    ↓               │               ↓

┌──────────────────────────────────────────────────────────────────────────┐
│                         BACKEND LAYER                                    │
│                    FastAPI + Python + SQLAlchemy                         │
│                    http://localhost:8000/                                │
│                                                                          │
│  ┌────────────────────────────────────────────────────────┐             │
│  │  app/main.py (Entry Point)                             │             │
│  │  - FastAPI app initialization                          │             │
│  │  - Database connections                                │             │
│  │  - CORS & middleware setup                             │             │
│  └────────┬───────────────────────────────────────────────┘             │
│           │                                                              │
│  ┌────────▼────────────────────────────────────────────────┐            │
│  │  api/v1/router.py (Route Aggregator)                    │            │
│  │  - /tests → endpoints/tests.py                          │            │
│  │  - /questions → endpoints/questions.py                  │            │
│  │  - /submissions → endpoints/submissions.py ⭐           │            │
│  └────────┬────────────────────────────────────────────────┘            │
│           │                                                              │
│  ┌────────▼──────────────────────────────────────────────────────────┐  │
│  │  api/v1/endpoints/ (Endpoint Implementations)                    │  │
│  │                                                                   │  │
│  │  ┌──────────────────────────────────────┐                        │  │
│  │  │ submissions.py ⭐ (NEW - CRITICAL)   │                        │  │
│  │  │                                      │                        │  │
│  │  │ POST /mcq                            │                        │  │
│  │  │ → Saves to test_answers              │                        │  │
│  │  │                                      │                        │  │
│  │  │ POST /code                           │                        │  │
│  │  │ → Saves to test_answers + MongoDB    │                        │  │
│  │  │                                      │                        │  │
│  │  │ GET /assignment/{id}                 │                        │  │
│  │  │ → Fetches all answers                │                        │  │
│  │  │                                      │                        │  │
│  │  │ GET /candidate/{id}                  │                        │  │
│  │  │ → Fetches candidate history          │                        │  │
│  │  └──────────────────────────────────────┘                        │  │
│  │                                                                   │  │
│  │  ┌──────────────────────────────────────┐                        │  │
│  │  │ tests.py                             │                        │  │
│  │  │ - GET /tests                         │                        │  │
│  │  │ - GET /tests/{id}                    │                        │  │
│  │  │ - POST /tests (create)               │                        │  │
│  │  └──────────────────────────────────────┘                        │  │
│  │                                                                   │  │
│  │  ┌──────────────────────────────────────┐                        │  │
│  │  │ questions.py                         │                        │  │
│  │  │ - GET /questions/mcq/{id}            │                        │  │
│  │  │ - GET /questions/coding/{id}         │                        │  │
│  │  │ - POST /questions (create)           │                        │  │
│  │  └──────────────────────────────────────┘                        │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│           │                                                              │
│  ┌────────▼──────────────────────────────────────────┐                  │
│  │  Database Connections                             │                  │
│  │                                                   │                  │
│  │  ┌────────────────────────────────────────┐      │                  │
│  │  │ db/postgres.py                         │      │                  │
│  │  │ - SQLAlchemy AsyncEngine               │      │                  │
│  │  │ - Connection pooling                   │      │                  │
│  │  │ - Async session management             │      │                  │
│  │  └────────────────────────────────────────┘      │                  │
│  │                                                   │                  │
│  │  ┌────────────────────────────────────────┐      │                  │
│  │  │ db/mongodb.py                          │      │                  │
│  │  │ - Motor AsyncMongoClient                │      │                  │
│  │  │ - Database & collection access         │      │                  │
│  │  │ - Async operations                     │      │                  │
│  │  └────────────────────────────────────────┘      │                  │
│  │                                                   │                  │
│  └───────────────────────────────────────────────────┘                  │
└──────────────────────────────────────────────────────────────────────────┘
            │                               │
            ↓                               ↓
        PostgreSQL                      MongoDB
      (Relational)                    (Document)
    Port: 5432                       Port: 27017
  Database: talentshire            Database: talentshire
```

---

## 📊 Data Flow Diagram

### MCQ Answer Flow
```
┌──────────────────┐
│  Candidate Login │
│  View Test       │
│  See Questions   │
└────────┬─────────┘
         │
         ↓
┌──────────────────────────┐
│  User Selects Option     │
│  (A, B, C, or D)         │
└────────┬─────────────────┘
         │
         ↓
┌──────────────────────────────────────────┐
│ POST /api/v1/submissions/mcq             │
│ {                                        │
│   assignment_id: uuid,                   │
│   question_id: uuid,                     │
│   selected_option: "A",                  │
│   is_correct: true,                      │
│   time_spent_seconds: 30,                │
│   candidate_id: uuid                     │
│ }                                        │
└────────┬─────────────────────────────────┘
         │
         ↓
    ┌────────────────────────────┐
    │  PostgreSQL: test_answers  │
    │                            │
    │  INSERT:                   │
    │  - answer_id (UUID)        │
    │  - selected_option: "A"    │
    │  - is_correct: true        │
    │  - score: 1.0              │
    │  - submitted_at: now       │
    │                            │
    └────────┬───────────────────┘
             │
             ↓
    ┌──────────────────────────┐
    │ Response:                │
    │ {                        │
    │  success: true,          │
    │  answer_id: "uuid"       │
    │ }                        │
    └──────────────────────────┘
```

### Code Submission Flow
```
┌──────────────────┐
│  User Writes     │
│  Code Solution   │
└────────┬─────────┘
         │
         ↓
┌────────────────────────────┐
│  User Clicks "Submit"      │
│  (Optional: Execute first) │
└────────┬───────────────────┘
         │
         ↓
┌──────────────────────────────────────────┐
│ POST /api/v1/submissions/code            │
│ {                                        │
│   assignment_id: uuid,                   │
│   question_id: uuid,                     │
│   code: "def solution(): ...",           │
│   language: "python",                    │
│   code_status: "success",                │
│   code_passed: true,                     │
│   code_output: "output",                 │
│   time_spent_seconds: 120,               │
│   candidate_id: uuid                     │
│ }                                        │
└────────┬─────────────────────────────────┘
         │
         ├─────────────────────────┬──────────────────────────┐
         │                         │                          │
         ↓                         ↓                          ↓
    PostgreSQL              MongoDB              PostgreSQL
    test_answers         code_submissions        test_answers
    
    INSERT:                 INSERT:           (Also INSERT:)
    - answer_id             - _id
    - code_submission       - answer_id       - answer_id
    - code_status           - code            - assignment_id
    - language              - language        - question_id
    - code_output           - exec_result     - code_submission
    - submitted_at          - submitted_at    - code_status
                                              - language
                                              - code_output
         │                         │                          │
         └─────────────────────────┴──────────────────────────┘
                        │
                        ↓
                  Response:
                  {
                    success: true,
                    answer_id: "uuid",
                    mongo_id: "uuid"
                  }
```

---

## 🗄️ Database Tables Relationship

```
┌─────────────┐         ┌──────────────────┐
│   users     │         │    candidates    │
├─────────────┤         ├──────────────────┤
│ user_id (PK)│         │ candidate_id(PK) │
│ email       │         │ email            │
│ password    │         │ name             │
└──────┬──────┘         └────────┬─────────┘
       │                         │
       │                         │
       ├────────────┬────────────┤
       │            │            │
       ↓            ↓            ↓
    ┌────────────────────────┐
    │ test_assignments ⭐     │
    ├────────────────────────┤
    │ assignment_id (PK)     │
    │ test_id (FK→tests)     │
    │ candidate_id (FK)      │
    │ candidate_token        │
    │ status                 │
    └────────┬───────────────┘
             │
             ↓
    ┌──────────────────────────┐
    │ test_answers ⭐⭐ (CRITICAL)
    ├──────────────────────────┤
    │ answer_id (PK)           │
    │ assignment_id (FK)       │
    │ question_id (FK)         │
    │ selected_option (MCQ)    │
    │ code_submission (CODE)   │
    │ is_correct               │
    │ score                    │
    │ submitted_at             │
    └──────────────────────────┘
             │
             ↓
    ┌──────────────────────────┐
    │ test_results             │
    ├──────────────────────────┤
    │ result_id (PK)           │
    │ assignment_id (FK)       │
    │ total_score              │
    │ section_scores           │
    │ completion_status        │
    └──────────────────────────┘

┌─────────────────────────────┐
│ tests                       │
├─────────────────────────────┤
│ test_id (PK)                │
│ test_name                   │
│ created_by (FK→users)       │
│ duration_minutes            │
└─────────┬───────────────────┘
          │
          ↓
┌──────────────────────────┐        ┌──────────────────────────────┐
│ test_questions           │        │ unified_questions ⭐         │
├──────────────────────────┤        ├──────────────────────────────┤
│ id (PK)                  │        │ question_id (PK)             │
│ test_id (FK)             │        │ type (MCQ or CODING)         │
│ question_id (FK)    ─────┼───────→│ question_text                │
│ question_type            │        │ difficulty_level             │
│ order_index              │        └──────────────┬───────────────┘
└──────────────────────────┘                       │
                                 ┌─────────────────┴──────────────┐
                                 │                                │
                                 ↓                                ↓
                        ┌──────────────────┐        ┌──────────────────┐
                        │ mcq_questions    │        │ MongoDB:         │
                        ├──────────────────┤        │ coding_questions │
                        │ mcq_id (PK)      │        ├──────────────────┤
                        │ question_text    │        │ _id              │
                        │ option_a,b,c,d   │        │ title            │
                        │ correct_answer   │        │ description      │
                        │ difficulty       │        │ test_cases       │
                        └──────────────────┘        └──────────────────┘
```

---

## 🔄 Complete Submission Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   CANDIDATE TEST JOURNEY                        │
└─────────────────────────────────────────────────────────────────┘

Step 1: LOGIN
========================================
  Candidate enters email/token
    ↓
  POST /api/v1/candidates/login
    ↓
  Check test_assignments table
    ↓
  Return candidate_id & test_id
    ↓
  Store in authStore (Zustand)

Step 2: LOAD TEST
========================================
  Frontend requests test details
    ↓
  GET /api/v1/tests/{test_id}
    ↓
  Backend queries:
    - tests table
    - test_questions table
    - unified_questions table
    - mcq_questions (for MCQ details)
    - MongoDB coding_questions (for code details)
    ↓
  Return all questions
    ↓
  Store in testStore & candidateTestStore

Step 3: TAKE TEST (Repeat for each question)
========================================
  
  3a. FOR MCQ QUESTIONS:
      Candidate reads question & options
        ↓
      Candidate selects A/B/C/D
        ↓
      Auto-save to test_autosave table
        ↓
      Optional: User clicks "Submit Answer"
        ↓
      POST /api/v1/submissions/mcq
        ↓
      Backend saves to test_answers table:
        - selected_option: "A"
        - is_correct: (calculated or provided)
        - score: (calculated)
        ↓
      Update candidateTestStore with answer
  
  3b. FOR CODE QUESTIONS:
      Candidate reads problem description
        ↓
      Candidate writes code in editor
        ↓
      Auto-save to test_autosave table
        ↓
      Optional: User clicks "Execute" (runs on external service)
        ↓
      User clicks "Submit Code"
        ↓
      POST /api/v1/submissions/code
        ↓
      Backend saves to TWO databases:
        1. PostgreSQL test_answers table:
           - code_submission: full code
           - code_status: success/error
           - language: python/javascript/etc
           - code_output: execution output
           - code_passed: true/false
        
        2. MongoDB code_submissions collection:
           - Full execution details
           - Test case results
           - Code analysis
        ↓
      Update candidateTestStore with answer

Step 4: VIEW RESULTS
========================================
  Candidate completes test
    ↓
  Redirects to results page
    ↓
  GET /api/v1/submissions/assignment/{assignment_id}
    ↓
  Backend queries test_answers table:
    SELECT * FROM test_answers 
    WHERE assignment_id = ?
    ↓
  Return all MCQ & code answers
    ↓
  Frontend calculates:
    - Total MCQ score
    - Total code score
    - Time spent
    - Pass/Fail status
    ↓
  Display results to candidate

Step 5: GENERATE REPORT (Admin/System)
========================================
  POST /api/v1/reports/generate/{assignment_id}
    ↓
  Backend aggregates from test_answers:
    - Count questions
    - Sum scores by type
    - Calculate percentages
    - Determine pass/fail
    ↓
  Inserts into test_results table:
    - total_score
    - section_scores (MCQ + Coding)
    - completion_status
    ↓
  Report ready for viewing
```

---

## 📱 Frontend Component Hierarchy

```
App.tsx
  ↓
AppContent.tsx
  ├─ QueryClientProvider
  ├─ TooltipProvider
  └─ BrowserRouter
      └─ Routes
         ├─ /candidate/login
         │  └─ CandidateLogin.tsx ⭐
         │     ├─ Email Login Form
         │     ├─ Token Login Form
         │     └─ Demo Credentials
         │
         ├─ /candidate/tests
         │  └─ CandidateTests.tsx
         │     ├─ Test List
         │     └─ Start Test Button
         │
         ├─ /candidate/test/:assignmentId
         │  └─ TestTaking.tsx ⭐⭐ (CRITICAL)
         │     ├─ QuestionNavigation
         │     ├─ Question Display
         │     │  ├─ MCQ Component
         │     │  │  ├─ Radio Options
         │     │  │  └─ Submit Button
         │     │  └─ Code Component
         │     │     ├─ CodeEditor
         │     │     ├─ Execute Button
         │     │     └─ Submit Button
         │     ├─ TimerDisplay
         │     ├─ AutosaveIndicator
         │     └─ Submit Test Button
         │
         ├─ /candidate/test/:assignmentId/instructions
         │  └─ TestInstructions.tsx
         │
         ├─ /candidate/test/:assignmentId/results
         │  └─ TestResults.tsx
         │     ├─ Score Summary
         │     ├─ MCQ Results
         │     ├─ Code Results
         │     └─ Download Report
         │
         └─ /candidate/completed
            └─ CandidateCompleted.tsx
               └─ Completed Tests List

State Management (Zustand):
  ├─ authStore
  │  ├─ candidate_id
  │  ├─ token
  │  ├─ assignment_id
  │  └─ login(), loginWithToken()
  │
  ├─ testStore
  │  ├─ tests[]
  │  ├─ currentTest
  │  ├─ questions[]
  │  └─ fetchTests(), getTestById()
  │
  └─ candidateTestStore
     ├─ answers{}
     ├─ currentQuestionIndex
     ├─ testProgress
     ├─ submitAnswer()
     └─ getResults()
```

---

## 🔌 API Endpoint Structure

```
http://localhost:8000/api/v1/
├─ /submissions
│  ├─ POST /mcq                      ← Save MCQ answer ⭐
│  │  Headers: {Content-Type: application/json}
│  │  Body: {assignment_id, question_id, selected_option, ...}
│  │  Returns: {success, answer_id}
│  │
│  ├─ POST /code                     ← Save code submission ⭐
│  │  Headers: {Content-Type: application/json}
│  │  Body: {assignment_id, question_id, code, language, ...}
│  │  Returns: {success, answer_id, mongo_id}
│  │
│  ├─ GET /assignment/{assignment_id} ← Get test answers
│  │  Returns: {success, answers[]}
│  │
│  └─ GET /candidate/{candidate_id}   ← Get candidate history
│     Returns: {success, submissions[]}
│
├─ /tests
│  ├─ GET /                          ← List all tests
│  ├─ POST /                         ← Create test
│  ├─ GET /{test_id}                 ← Get test details
│  ├─ PUT /{test_id}                 ← Update test
│  └─ DELETE /{test_id}              ← Delete test
│
├─ /questions
│  ├─ POST /mcq                      ← Create MCQ
│  ├─ GET /mcq/{mcq_id}              ← Get MCQ
│  ├─ POST /coding                   ← Create coding question
│  └─ GET /coding/{question_id}      ← Get coding question
│
└─ /health                           ← Health check
   Returns: {status: "healthy"}
```

---

## 📊 Data Storage Matrix

| Data Type | Quantity | Primary Storage | Secondary Storage | Frequency |
|-----------|----------|-----------------|-------------------|-----------|
| MCQ Answers | ~1000s | test_answers (PostgreSQL) | - | Per question |
| Code Submissions | ~100s | test_answers (PostgreSQL) | code_submissions (MongoDB) | Per question |
| Test Metadata | ~10s | tests (PostgreSQL) | - | Once per test |
| Questions | ~100s | unified_questions (PostgreSQL) | coding_questions (MongoDB) | Once |
| Candidates | ~1000s | candidates (PostgreSQL) | - | One per candidate |
| Results | ~1000s | test_results (PostgreSQL) | - | Once per test |
| Auto-saves | ~10000s | test_autosave (PostgreSQL) | - | Every 30 sec |

---

**Version**: 1.0  
**Last Updated**: December 11, 2025  
**Status**: Complete ✅

This visual guide complements the text documentation!
