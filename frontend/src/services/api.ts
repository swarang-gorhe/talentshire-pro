/**
 * API Service Layer for Frontend
 * 
 * Handles all communication with backend API
 * Uses shared type definitions from @/types/api
 * Implements standardized error handling and request/response patterns
 */

import {
  User,
  Test,
  TestCreate,
  TestAssignment,
  TestAssignmentCreate,
  TestAnswer,
  CodeSubmission,
  CodeDraft,
  CandidateReport,
  AnalysisResult,
  ApiResponse,
  PaginatedResponse,
  LanguageEnum,
  AssignmentStatusEnum,
  CodeExecutionStatusEnum,
} from '@/types/api';

// ============================================================================
// API CLIENT CONFIGURATION
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const API_TIMEOUT = 30000; // 30 seconds

// ============================================================================
// ERROR HANDLING
// ============================================================================

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public errorData?: any,
    message?: string
  ) {
    super(message || `API Error: ${statusCode}`);
    this.name = 'ApiError';
  }
}

// ============================================================================
// HTTP METHODS
// ============================================================================

async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add auth token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(response.status, errorData, errorData.message || response.statusText);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, error, error instanceof Error ? error.message : 'Unknown error');
  }
}

function get<T>(endpoint: string): Promise<T> {
  return apiCall<T>(endpoint, { method: 'GET' });
}

function post<T>(endpoint: string, data: any): Promise<T> {
  return apiCall<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

function put<T>(endpoint: string, data: any): Promise<T> {
  return apiCall<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

function patch<T>(endpoint: string, data: any): Promise<T> {
  return apiCall<T>(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

function deleteRequest<T>(endpoint: string): Promise<T> {
  return apiCall<T>(endpoint, { method: 'DELETE' });
}

// ============================================================================
// AUTH API
// ============================================================================

export const authApi = {
  login: async (email: string, password: string): Promise<ApiResponse<{ token: string; user: User }>> => {
    return post('/auth/login', { email, password });
  },

  loginWithToken: async (token: string): Promise<ApiResponse<{ user: User }>> => {
    return post('/auth/token-login', { token });
  },

  logout: async (): Promise<ApiResponse<void>> => {
    return post('/auth/logout', {});
  },

  getCurrentUser: async (): Promise<ApiResponse<User>> => {
    return get('/auth/me');
  },

  refreshToken: async (): Promise<ApiResponse<{ token: string }>> => {
    return post('/auth/refresh', {});
  },
};

// ============================================================================
// TEST API
// ============================================================================

export const testApi = {
  // Get all tests
  getAllTests: async (page = 1, limit = 10): Promise<ApiResponse<Test[]>> => {
    return get(`/tests`);
  },

  // Get single test
  getTest: async (testId: string): Promise<ApiResponse<Test>> => {
    return get(`/tests/${testId}`);
  },

  // Create test
  createTest: async (data: TestCreate): Promise<ApiResponse<Test>> => {
    return post('/tests', data);
  },

  // Update test
  updateTest: async (testId: string, data: Partial<TestCreate>): Promise<ApiResponse<Test>> => {
    return put(`/tests/${testId}`, data);
  },

  // Delete test
  deleteTest: async (testId: string): Promise<ApiResponse<void>> => {
    return deleteRequest(`/tests/${testId}`);
  },

  // Publish test
  publishTest: async (testId: string): Promise<ApiResponse<Test>> => {
    return patch(`/tests/${testId}/publish`, {});
  },

  // Get test with all questions
  getTestWithQuestions: async (testId: string): Promise<ApiResponse<Test>> => {
    return get(`/tests/${testId}/questions`);
  },

  // Search tests
  searchTests: async (query: string): Promise<ApiResponse<Test[]>> => {
    return get(`/tests/search?q=${encodeURIComponent(query)}`);
  },
};

// ============================================================================
// TEST ASSIGNMENT API
// ============================================================================

export const assignmentApi = {
  // Get all assignments for a candidate
  getCandidateAssignments: async (candidateId: string): Promise<PaginatedResponse<TestAssignment>> => {
    return get(`/candidates/${candidateId}/assignments`);
  },

  // Get single assignment
  getAssignment: async (assignmentId: string): Promise<ApiResponse<TestAssignment>> => {
    return get(`/assignments/${assignmentId}`);
  },

  // Create assignment
  createAssignment: async (data: TestAssignmentCreate): Promise<ApiResponse<TestAssignment>> => {
    return post('/assignments', data);
  },

  // Start assignment (begin test)
  startAssignment: async (assignmentId: string): Promise<ApiResponse<TestAssignment>> => {
    return patch(`/assignments/${assignmentId}/start`, {});
  },

  // End assignment (submit test)
  endAssignment: async (assignmentId: string): Promise<ApiResponse<TestAssignment>> => {
    return patch(`/assignments/${assignmentId}/end`, {});
  },

  // Get remaining time for assignment
  getRemainingTime: async (assignmentId: string): Promise<ApiResponse<{ remaining_seconds: number }>> => {
    return get(`/assignments/${assignmentId}/remaining-time`);
  },

  // Bulk create assignments
  bulkCreateAssignments: async (assignments: TestAssignmentCreate[]): Promise<ApiResponse<TestAssignment[]>> => {
    return post('/assignments/bulk', { assignments });
  },
};

// ============================================================================
// TEST ANSWERS API
// ============================================================================

export const answerApi = {
  // Submit MCQ answer
  submitMCQAnswer: async (
    assignmentId: string,
    questionId: string,
    selectedOption: 'A' | 'B' | 'C' | 'D'
  ): Promise<ApiResponse<TestAnswer>> => {
    return post(`/answers`, {
      assignment_id: assignmentId,
      question_id: questionId,
      question_type: 'mcq',
      selected_option: selectedOption,
    });
  },

  // Submit coding answer
  submitCodingAnswer: async (
    assignmentId: string,
    questionId: string,
    code: string,
    language: LanguageEnum
  ): Promise<ApiResponse<TestAnswer>> => {
    return post(`/answers`, {
      assignment_id: assignmentId,
      question_id: questionId,
      question_type: 'coding',
      code,
      language,
    });
  },

  // Get all answers for assignment
  getAssignmentAnswers: async (assignmentId: string): Promise<ApiResponse<TestAnswer[]>> => {
    return get(`/assignments/${assignmentId}/answers`);
  },

  // Get single answer
  getAnswer: async (answerId: string): Promise<ApiResponse<TestAnswer>> => {
    return get(`/answers/${answerId}`);
  },

  // Update answer (for saving drafts)
  updateAnswer: async (answerId: string, data: Partial<any>): Promise<ApiResponse<TestAnswer>> => {
    return patch(`/answers/${answerId}`, data);
  },
};

// ============================================================================
// CODE SUBMISSION & ANALYSIS API
// ============================================================================

export const codeApi = {
  // Submit code for execution
  submitCode: async (
    assignmentId: string,
    questionId: string,
    code: string,
    language: LanguageEnum
  ): Promise<ApiResponse<CodeSubmission>> => {
    return post(`/assignments/${assignmentId}/code/submit`, {
      question_id: questionId,
      code,
      language,
    });
  },

  // Save code draft
  saveDraft: async (
    assignmentId: string,
    questionId: string,
    code: string,
    language: LanguageEnum
  ): Promise<ApiResponse<CodeDraft>> => {
    return post(`/assignments/${assignmentId}/code/draft`, {
      question_id: questionId,
      code,
      language,
    });
  },

  // Get code submission
  getSubmission: async (submissionId: string): Promise<ApiResponse<CodeSubmission>> => {
    return get(`/submissions/${submissionId}`);
  },

  // Get analysis result
  getAnalysis: async (submissionId: string): Promise<ApiResponse<AnalysisResult>> => {
    return get(`/submissions/${submissionId}/analysis`);
  },

  // Poll analysis status
  pollAnalysisStatus: async (
    submissionId: string
  ): Promise<ApiResponse<{ status: CodeExecutionStatusEnum; analysis?: AnalysisResult }>> => {
    return get(`/submissions/${submissionId}/analysis-status`);
  },

  // Get submission history
  getSubmissionHistory: async (
    assignmentId: string,
    questionId: string
  ): Promise<ApiResponse<CodeSubmission[]>> => {
    return get(`/assignments/${assignmentId}/code/history?question_id=${questionId}`);
  },
};

// ============================================================================
// REPORT API
// ============================================================================

export const reportApi = {
  // Get candidate report
  getReport: async (assignmentId: string): Promise<ApiResponse<CandidateReport>> => {
    return get(`/reports/${assignmentId}`);
  },

  // Generate report (after test submission)
  generateReport: async (assignmentId: string): Promise<ApiResponse<CandidateReport>> => {
    return post(`/reports/${assignmentId}/generate`, {});
  },

  // Get all reports for candidate
  getCandidateReports: async (candidateId: string): Promise<PaginatedResponse<CandidateReport>> => {
    return get(`/candidates/${candidateId}/reports`);
  },

  // Export report as PDF
  exportReportPDF: async (reportId: string): Promise<Blob> => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE_URL}/reports/${reportId}/export/pdf`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!response.ok) {
      throw new ApiError(response.status, {}, 'Failed to export report');
    }
    return response.blob();
  },

  // Share report
  shareReport: async (reportId: string, emails: string[]): Promise<ApiResponse<void>> => {
    return post(`/reports/${reportId}/share`, { emails });
  },
};

// ============================================================================
// CANDIDATE API
// ============================================================================

export const candidateApi = {
  // Get candidate profile
  getProfile: async (candidateId: string) => {
    return get(`/candidates/${candidateId}`);
  },

  // Update candidate profile
  updateProfile: async (candidateId: string, data: any) => {
    return put(`/candidates/${candidateId}`, data);
  },

  // Get candidate statistics
  getStatistics: async (candidateId: string): Promise<ApiResponse<any>> => {
    return get(`/candidates/${candidateId}/statistics`);
  },

  // Get candidate skills
  getSkills: async (candidateId: string): Promise<ApiResponse<any[]>> => {
    return get(`/candidates/${candidateId}/skills`);
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Create an API service instance with error handling and retry logic
 */
export const createApiService = () => {
  return {
    auth: authApi,
    tests: testApi,
    assignments: assignmentApi,
    answers: answerApi,
    code: codeApi,
    reports: reportApi,
    candidates: candidateApi,
  };
};

export default createApiService();
