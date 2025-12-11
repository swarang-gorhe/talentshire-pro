/**
 * Frontend Type Definitions - Mirroring Backend Shared Models
 * 
 * These types correspond to the shared models in backend/shared/models.py
 * They provide type safety and autocomplete for all API calls
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum LanguageEnum {
  PYTHON = 'python',
  JAVASCRIPT = 'javascript',
  JAVA = 'java',
  CPLUS = 'cpp',
  CSHARP = 'csharp',
  GOLANG = 'golang',
  RUST = 'rust',
  SQL = 'sql',
}

export enum DifficultyEnum {
  EASY = 'easy',
  MEDIUM = 'medium',
  HARD = 'hard',
}

export enum TestStatusEnum {
  DRAFT = 'draft',
  ACTIVE = 'active',
  ARCHIVED = 'archived',
}

export enum QuestionTypeEnum {
  MCQ = 'mcq',
  CODING = 'coding',
}

export enum AssignmentStatusEnum {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  EXPIRED = 'expired',
}

export enum CodeExecutionStatusEnum {
  PENDING = 'pending',
  RUNNING = 'running',
  SUCCESS = 'success',
  FAILED = 'failed',
  TIMEOUT = 'timeout',
  ERROR = 'error',
}

export enum RoleEnum {
  ADMIN = 'admin',
  TEST_SETTER = 'test_setter',
  CANDIDATE = 'candidate',
}

// ============================================================================
// USER MODELS
// ============================================================================

export interface CandidateProfile {
  candidate_id: string;
  full_name: string;
  email: string;
  phone?: string;
  resume_url?: string;
  college_name?: string;
  graduation_year?: number;
  skills: string[];
  experience_years: number;
  linkedin_url?: string;
}

export interface User {
  user_id: string;
  email: string;
  full_name: string;
  password_hash?: string;
  role: RoleEnum;
  is_active: boolean;
  created_at: string;
  candidate_profile?: CandidateProfile;
}

// ============================================================================
// TEST MODELS
// ============================================================================

export interface MCQQuestion {
  question_id: string;
  test_id: string;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  correct_answer: 'A' | 'B' | 'C' | 'D';
  marks: number;
  difficulty: DifficultyEnum;
  tags: string[];
  explanation?: string;
  created_at: string;
}

export interface CodingQuestion {
  question_id: string;
  test_id: string;
  title: string;
  description: string;
  starter_code: string;
  language: LanguageEnum;
  marks: number;
  difficulty: DifficultyEnum;
  tags: string[];
  test_cases: TestCase[];
  time_limit_seconds: number;
  memory_limit_mb: number;
  created_at: string;
}

export interface TestCase {
  test_case_id: string;
  question_id: string;
  input_data: string;
  expected_output: string;
  is_visible: boolean;
}

export interface Test {
  test_id: string;
  test_name: string;
  description: string;
  duration_minutes: number;
  status: TestStatusEnum;
  total_marks: number;
  passing_marks: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  mcq_questions?: MCQQuestion[];
  coding_questions?: CodingQuestion[];
}

export interface TestCreate {
  test_name: string;
  description: string;
  duration_minutes: number;
  status?: TestStatusEnum;
  total_marks?: number;
  passing_marks?: number;
}

// ============================================================================
// ASSIGNMENT MODELS
// ============================================================================

export interface TestAssignment {
  assignment_id: string;
  test_id: string;
  candidate_id: string;
  assigned_date: string;
  start_time: string;
  end_time: string;
  status: AssignmentStatusEnum;
  started_at?: string;
  completed_at?: string;
  score?: number;
  percentage?: number;
  passed: boolean;
  candidate_name?: string;
  candidate_email?: string;
  test_name?: string;
}

export interface TestAssignmentCreate {
  test_id: string;
  candidate_id: string;
  start_time: string;
  end_time: string;
}

// ============================================================================
// TEST ANSWER MODELS
// ============================================================================

export interface MCQAnswer {
  answer_id: string;
  assignment_id: string;
  question_id: string;
  selected_option?: 'A' | 'B' | 'C' | 'D';
  is_correct?: boolean;
  marks_obtained?: number;
  answered_at: string;
}

export interface CodingAnswer {
  answer_id: string;
  assignment_id: string;
  question_id: string;
  submitted_code: string;
  language: LanguageEnum;
  execution_status: CodeExecutionStatusEnum;
  test_cases_passed?: number;
  test_cases_total?: number;
  marks_obtained?: number;
  submitted_at: string;
}

export interface TestAnswer {
  answer_id: string;
  assignment_id: string;
  question_id: string;
  question_type: QuestionTypeEnum;
  mcq_answer?: MCQAnswer;
  coding_answer?: CodingAnswer;
  analysis_result?: AnalysisResult;
  marks_obtained?: number;
  submitted_at: string;
}

// ============================================================================
// CODE SUBMISSION & ANALYSIS MODELS
// ============================================================================

export interface CodeSubmission {
  submission_id: string;
  assignment_id: string;
  question_id: string;
  code: string;
  language: LanguageEnum;
  submitted_at: string;
  execution_status: CodeExecutionStatusEnum;
  stdout?: string;
  stderr?: string;
  execution_time_ms?: number;
  memory_used_mb?: number;
}

export interface CodeDraft {
  draft_id: string;
  assignment_id: string;
  question_id: string;
  code: string;
  language: LanguageEnum;
  saved_at: string;
  is_auto_saved: boolean;
}

export interface Submission {
  submission_id: string;
  code: string;
  language: LanguageEnum;
  problem_title: string;
  problem_description: string;
}

export interface AnalysisResult {
  analysis_id: string;
  submission_id: string;
  code_quality_score: number;
  efficiency_score: number;
  readability_score: number;
  security_issues: SecurityIssue[];
  optimization_suggestions: string[];
  code_review: CodeReviewResult;
  time_complexity?: string;
  space_complexity?: string;
  analyzed_at: string;
}

export interface SecurityIssue {
  issue_type: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
  line_number?: number;
  suggestion: string;
}

export interface CodeReviewResult {
  overall_feedback: string;
  strengths: string[];
  improvements: string[];
  best_practices_followed: boolean;
  code_style_score: number;
}

// ============================================================================
// REPORT MODELS
// ============================================================================

export interface MCQReportSection {
  total_questions: number;
  correct_answers: number;
  incorrect_answers: number;
  unanswered: number;
  accuracy_percentage: number;
  total_marks: number;
  marks_obtained: number;
}

export interface CodingReportSection {
  total_questions: number;
  fully_solved: number;
  partially_solved: number;
  unsolved: number;
  success_rate_percentage: number;
  total_marks: number;
  marks_obtained: number;
  average_efficiency_score: number;
}

export interface CandidateReport {
  report_id: string;
  assignment_id: string;
  candidate_id: string;
  test_id: string;
  total_marks: number;
  marks_obtained: number;
  percentage: number;
  passed: boolean;
  time_taken_minutes: number;
  started_at: string;
  completed_at: string;
  mcq_section?: MCQReportSection;
  coding_section?: CodingReportSection;
  generated_at: string;
}

// ============================================================================
// SKILL EXTRACTION MODELS
// ============================================================================

export interface SkillExtractionRequest {
  submission_id: string;
  code: string;
  language: LanguageEnum;
  problem_context: string;
}

export interface SkillExtractionResult {
  extraction_id: string;
  submission_id: string;
  identified_skills: IdentifiedSkill[];
  proficiency_level: 'beginner' | 'intermediate' | 'advanced';
  extracted_at: string;
}

export interface IdentifiedSkill {
  skill_name: string;
  confidence_score: number;
  evidence: string[];
}

export interface CandidateSkillMatch {
  match_id: string;
  candidate_id: string;
  skill_extraction_id: string;
  skill_name: string;
  proficiency_level: string;
  matched_at: string;
}

// ============================================================================
// PROCTORING MODELS
// ============================================================================

export interface ProctoringData {
  proctoring_id: string;
  assignment_id: string;
  start_time: string;
  end_time: string;
  flag_suspicious_activity: boolean;
  violations_count: number;
  camera_detected: boolean;
  multiple_faces_detected: number;
}

export interface ProctoringFrameCapture {
  frame_id: string;
  proctoring_id: string;
  timestamp: string;
  image_url: string;
  is_suspicious: boolean;
  violation_type?: string;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}
