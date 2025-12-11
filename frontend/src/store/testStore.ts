import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
  Test,
  TestCreate,
  TestAssignment,
  TestAssignmentCreate,
  TestAnswer,
  CodeDraft,
  MCQQuestion,
  CodingQuestion,
  AssignmentStatusEnum,
  LanguageEnum,
} from '@/types/api';
import { testApi, assignmentApi, answerApi, codeApi } from '@/services/api';

interface TestState {
  // Data
  tests: Test[];
  currentTest: Test | null;
  assignments: TestAssignment[];
  currentAssignment: TestAssignment | null;
  answers: Map<string, TestAnswer>; // question_id -> TestAnswer
  drafts: Map<string, CodeDraft>; // question_id -> CodeDraft

  // Loading states
  isLoading: boolean;
  isLoadingTest: boolean;
  isLoadingAssignments: boolean;
  currentError: string | null;

  // Test Creation (for test setters)
  testCreation: {
    step: number;
    basicInfo: {
      name: string;
      duration: number;
      description: string;
      tags: string[];
    };
    selectedMCQs: any[];
    selectedCoding: any[];
    assignments: any[];
  };

  // Test Taking (for candidates)
  testTaking: {
    startTime: number | null;
    endTime: number | null;
    isExpired: boolean;
    currentQuestionIndex: number;
  };
  
  // Actions - Test Management
  fetchTests: () => Promise<void>;
  fetchTest: (testId: string) => Promise<void>;
  createTest: (data: TestCreate) => Promise<Test>;
  updateTest: (testId: string, data: Partial<TestCreate>) => Promise<void>;
  deleteTest: (testId: string) => Promise<void>;
  publishTest: (testId: string) => Promise<void>;

  // Actions - Test Assignment
  fetchCandidateAssignments: (candidateId: string) => Promise<void>;
  fetchAssignment: (assignmentId: string) => Promise<void>;
  createAssignment: (data: TestAssignmentCreate) => Promise<void>;
  startAssignment: (assignmentId: string) => Promise<void>;
  endAssignment: (assignmentId: string) => Promise<void>;

  // Actions - Test Taking
  setCurrentQuestion: (index: number) => void;
  submitMCQAnswer: (assignmentId: string, questionId: string, option: 'A' | 'B' | 'C' | 'D') => Promise<void>;
  submitCodingAnswer: (assignmentId: string, questionId: string, code: string, language: LanguageEnum) => Promise<void>;
  saveDraft: (assignmentId: string, questionId: string, code: string, language: LanguageEnum) => Promise<void>;
  fetchAnswers: (assignmentId: string) => Promise<void>;

  // Actions - Test Creation Wizard
  setCreationStep: (step: number) => void;
  updateTestData: (data: Partial<TestCreate>) => void;
  updateBasicInfo: (data: any) => void;
  addMCQQuestion: (questionId: string) => void;
  addCodingQuestion: (questionId: string) => void;
  removeMCQQuestion: (questionId: string) => void;
  removeCodingQuestion: (questionId: string) => void;
  resetTestCreation: () => void;

  // Utility
  clearError: () => void;
  reset: () => void;
}

const initialCreationState: TestCreationState = {
  step: 1,
  basicInfo: {
    name: '',
    duration: 60,
    description: '',
    tags: [],
  },
  selectedMCQs: [],
  selectedCoding: [],
  assignments: [],
};

// Mock data
const mockMCQs: MCQQuestion[] = [
  {
    id: 'mcq-1',
    question: 'What is the time complexity of binary search?',
    options: ['O(n)', 'O(log n)', 'O(n²)', 'O(1)'],
    correctAnswer: 1,
    difficulty: 'easy',
    tags: ['algorithms', 'searching'],
    points: 10,
  },
  {
    id: 'mcq-2',
    question: 'Which data structure uses LIFO principle?',
    options: ['Queue', 'Stack', 'Array', 'Linked List'],
    correctAnswer: 1,
    difficulty: 'easy',
    tags: ['data structures'],
    points: 10,
  },
  {
    id: 'mcq-3',
    question: 'What is the worst-case time complexity of QuickSort?',
    options: ['O(n log n)', 'O(n)', 'O(n²)', 'O(log n)'],
    correctAnswer: 2,
    difficulty: 'medium',
    tags: ['algorithms', 'sorting'],
    points: 15,
  },
  {
    id: 'mcq-4',
    question: 'Which of the following is NOT a JavaScript primitive type?',
    options: ['String', 'Number', 'Array', 'Boolean'],
    correctAnswer: 2,
    difficulty: 'easy',
    tags: ['javascript', 'basics'],
    points: 10,
  },
  {
    id: 'mcq-5',
    question: 'What does SQL stand for?',
    options: ['Structured Query Language', 'Simple Query Language', 'Standard Query Language', 'Server Query Language'],
    correctAnswer: 0,
    difficulty: 'easy',
    tags: ['database', 'sql'],
    points: 10,
  },
];

const mockCodingQuestions: CodingQuestion[] = [
  {
    id: 'code-1',
    title: 'Two Sum',
    description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.',
    starterCode: 'function twoSum(nums, target) {\n  // Your code here\n}',
    testCases: [
      { input: '[2,7,11,15], 9', expectedOutput: '[0,1]' },
      { input: '[3,2,4], 6', expectedOutput: '[1,2]' },
    ],
    difficulty: 'easy',
    tags: ['arrays', 'hash-table'],
    points: 25,
    language: 'javascript',
  },
  {
    id: 'code-2',
    title: 'Reverse String',
    description: 'Write a function that reverses a string. The input string is given as an array of characters s.\n\nYou must do this by modifying the input array in-place with O(1) extra memory.',
    starterCode: 'function reverseString(s) {\n  // Your code here\n}',
    testCases: [
      { input: '["h","e","l","l","o"]', expectedOutput: '["o","l","l","e","h"]' },
      { input: '["H","a","n","n","a","h"]', expectedOutput: '["h","a","n","n","a","H"]' },
    ],
    difficulty: 'easy',
    tags: ['strings', 'two-pointers'],
    points: 20,
    language: 'javascript',
  },
  {
    id: 'code-3',
    title: 'Valid Parentheses',
    description: 'Given a string s containing just the characters \'(\', \')\', \'{\', \'}\', \'[\' and \']\', determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.',
    starterCode: 'function isValid(s) {\n  // Your code here\n}',
    testCases: [
      { input: '"()"', expectedOutput: 'true' },
      { input: '"()[]{}"', expectedOutput: 'true' },
      { input: '"(]"', expectedOutput: 'false' },
    ],
    difficulty: 'medium',
    tags: ['stack', 'strings'],
    points: 30,
    language: 'javascript',
  },
];

const mockTests: Test[] = [
  {
    id: 'test-1',
    name: 'JavaScript Fundamentals',
    description: 'A comprehensive test covering JavaScript basics including data types, functions, and DOM manipulation.',
    duration: 60,
    tags: ['javascript', 'frontend'],
    status: 'published',
    mcqQuestions: [mockMCQs[3], mockMCQs[4]],
    codingQuestions: [mockCodingQuestions[0], mockCodingQuestions[1]],
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
    createdBy: '1',
  },
  {
    id: 'test-2',
    name: 'Data Structures & Algorithms',
    description: 'Test your knowledge of common data structures and algorithmic problem-solving.',
    duration: 90,
    tags: ['algorithms', 'data-structures'],
    status: 'published',
    mcqQuestions: [mockMCQs[0], mockMCQs[1], mockMCQs[2]],
    codingQuestions: [mockCodingQuestions[2]],
    createdAt: '2024-01-20T14:00:00Z',
    updatedAt: '2024-01-20T14:00:00Z',
    createdBy: '1',
  },
  {
    id: 'test-3',
    name: 'Full Stack Assessment',
    description: 'Comprehensive assessment for full-stack developer candidates.',
    duration: 120,
    tags: ['fullstack', 'javascript', 'database'],
    status: 'draft',
    mcqQuestions: mockMCQs,
    codingQuestions: mockCodingQuestions,
    createdAt: '2024-02-01T09:00:00Z',
    updatedAt: '2024-02-01T09:00:00Z',
    createdBy: '2',
  },
];

const mockAssignments: Assignment[] = [
  {
    id: 'assign-1',
    testId: 'test-1',
    candidateId: '3',
    candidateName: 'John Candidate',
    candidateEmail: 'candidate@example.com',
    scheduledStartTime: '2024-12-01T09:00:00Z',
    scheduledEndTime: '2024-12-05T18:00:00Z',
    status: 'pending',
  },
  {
    id: 'assign-2',
    testId: 'test-2',
    candidateId: '3',
    candidateName: 'John Candidate',
    candidateEmail: 'candidate@example.com',
    scheduledStartTime: '2024-11-01T09:00:00Z',
    scheduledEndTime: '2024-11-30T18:00:00Z',
    status: 'completed',
    startedAt: '2024-11-15T10:00:00Z',
    completedAt: '2024-11-15T11:30:00Z',
    score: 85,
  },
];

// ============================================================================
// STORE IMPLEMENTATION
// ============================================================================

export const useTestStore = create<TestState>()(
  persist(
    (set, get) => ({
      // Initial state
      tests: [],
      currentTest: null,
      assignments: [],
      currentAssignment: null,
      answers: new Map(),
      drafts: new Map(),
      isLoading: false,
      isLoadingTest: false,
      isLoadingAssignments: false,
      currentError: null,

      testCreation: {
        step: 1,
        basicInfo: {
          name: '',
          duration: 60,
          description: '',
          tags: [],
        },
        selectedMCQs: [],
        selectedCoding: [],
        assignments: [],
      },

      testTaking: {
        startTime: null,
        endTime: null,
        isExpired: false,
        currentQuestionIndex: 0,
      },

      // ===== Test Management Actions =====

      fetchTests: async () => {
        set({ isLoading: true, currentError: null });
        try {
          const resp = await testApi.getAllTests();
          // Backend returns { success: true, data: Test[] }
          const testsArray = resp.data || [];
          set({ tests: testsArray });
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to fetch tests';
          set({ currentError: errorMsg });
          console.error('fetchTests error:', error);
        } finally {
          set({ isLoading: false });
        }
      },

      fetchTest: async (testId: string) => {
        set({ isLoadingTest: true, currentError: null });
        try {
          const resp = await testApi.getTest(testId);
          set({ currentTest: resp.data || null });
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to fetch test';
          set({ currentError: errorMsg });
        } finally {
          set({ isLoadingTest: false });
        }
      },

      createTest: async (data: TestCreate) => {
        set({ isLoading: true, currentError: null });
        try {
          const resp = await testApi.createTest(data);
          const newTest = resp.data as Test;
          if (newTest) {
            set((state) => ({ tests: [...state.tests, newTest] }));
            return newTest;
          }
          throw new Error(resp.error || 'Failed to create test');
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to create test';
          set({ currentError: errorMsg });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      updateTest: async (testId: string, data: Partial<TestCreate>) => {
        set({ isLoading: true, currentError: null });
        try {
          // API call placeholder
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to update test';
          set({ currentError: errorMsg });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      deleteTest: async (testId: string) => {
        set({ isLoading: true, currentError: null });
        try {
          set((state) => ({
            tests: state.tests.filter((t) => t.test_id !== testId),
          }));
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to delete test';
          set({ currentError: errorMsg });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      publishTest: async (testId: string) => {
        set({ isLoading: true, currentError: null });
        try {
          const resp = await testApi.publishTest(testId);
          const updated = resp.data as Test;
          if (updated) {
            set((state) => ({ tests: state.tests.map((t) => (t.test_id === updated.test_id ? updated : t)) }));
            return;
          }
          throw new Error(resp.error || 'Failed to publish test');
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to publish test';
          set({ currentError: errorMsg });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      // ===== Test Assignment Actions =====

      fetchCandidateAssignments: async (candidateId: string) => {
        set({ isLoadingAssignments: true, currentError: null });
        try {
          const resp = await assignmentApi.getCandidateAssignments(candidateId);
          set({ assignments: resp.data || [] });
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to fetch assignments';
          set({ currentError: errorMsg });
        } finally {
          set({ isLoadingAssignments: false });
        }
      },

      fetchAssignment: async (assignmentId: string) => {
        set({ isLoadingTest: true, currentError: null });
        try {
          const resp = await assignmentApi.getAssignment(assignmentId);
          set({ currentAssignment: resp.data || null });
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to fetch assignment';
          set({ currentError: errorMsg });
        } finally {
          set({ isLoadingTest: false });
        }
      },

      createAssignment: async (data: TestAssignmentCreate) => {
        set({ isLoading: true, currentError: null });
        try {
          const resp = await assignmentApi.createAssignment(data);
          const created = resp.data as TestAssignment;
          if (created) {
            set((state) => ({ assignments: [...state.assignments, created] }));
            return;
          }
          throw new Error(resp.error || 'Failed to create assignment');
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to create assignment';
          set({ currentError: errorMsg });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      startAssignment: async (assignmentId: string) => {
        set({ isLoading: true, currentError: null });
        try {
          const resp = await assignmentApi.startAssignment(assignmentId);
          const updated = resp.data as TestAssignment;
          if (updated) {
            set((state) => ({ assignments: state.assignments.map((a) => (a.assignment_id === updated.assignment_id ? updated : a)) }));
            return;
          }
          throw new Error(resp.error || 'Failed to start assignment');
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to start assignment';
          set({ currentError: errorMsg });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      endAssignment: async (assignmentId: string) => {
        set({ isLoading: true, currentError: null });
        try {
          const resp = await assignmentApi.endAssignment(assignmentId);
          const updated = resp.data as TestAssignment;
          if (updated) {
            set((state) => ({ assignments: state.assignments.map((a) => (a.assignment_id === updated.assignment_id ? updated : a)) }));
            return;
          }
          throw new Error(resp.error || 'Failed to end assignment');
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to end assignment';
          set({ currentError: errorMsg });
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      // ===== Test Taking Actions =====

      setCurrentQuestion: (index: number) => {
        set((state) => ({
          testTaking: {
            ...state.testTaking,
            currentQuestionIndex: index,
          },
        }));
      },

      submitMCQAnswer: async (assignmentId: string, questionId: string, option: 'A' | 'B' | 'C' | 'D') => {
        set({ currentError: null });
        try {
          const resp = await answerApi.submitMCQAnswer(assignmentId, questionId, option);
          const ans = resp.data as TestAnswer;
          if (ans) {
            set((state) => {
              const m = new Map(state.answers);
              m.set(questionId, ans);
              return { answers: m };
            });
            return;
          }
          throw new Error(resp.error || 'Failed to submit MCQ answer');
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to submit MCQ answer';
          set({ currentError: errorMsg });
          throw error;
        }
      },

      submitCodingAnswer: async (assignmentId: string, questionId: string, code: string, language: LanguageEnum) => {
        set({ currentError: null });
        try {
          const resp = await answerApi.submitCodingAnswer(assignmentId, questionId, code, language);
          const ans = resp.data as TestAnswer;
          if (ans) {
            set((state) => {
              const m = new Map(state.answers);
              m.set(questionId, ans);
              return { answers: m };
            });
            return;
          }
          throw new Error(resp.error || 'Failed to submit coding answer');
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to submit code';
          set({ currentError: errorMsg });
          throw error;
        }
      },

      saveDraft: async (assignmentId: string, questionId: string, code: string, language: LanguageEnum) => {
        set({ currentError: null });
        try {
          const resp = await codeApi.saveDraft(assignmentId, questionId, code, language);
          const draft = resp.data as CodeDraft;
          if (draft) {
            set((state) => {
              const d = new Map(state.drafts);
              d.set(questionId, draft);
              return { drafts: d };
            });
            return;
          }
          throw new Error(resp.error || 'Failed to save draft');
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to save draft';
          set({ currentError: errorMsg });
          throw error;
        }
      },

      fetchAnswers: async (assignmentId: string) => {
        set({ isLoading: true, currentError: null });
        try {
          const resp = await answerApi.getAssignmentAnswers(assignmentId);
          const arr = resp.data || [];
          const m = new Map<string, TestAnswer>();
          arr.forEach((a) => {
            if (a.question_id) m.set(a.question_id, a);
          });
          set({ answers: m });
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to fetch answers';
          set({ currentError: errorMsg });
        } finally {
          set({ isLoading: false });
        }
      },

      // ===== Test Creation Wizard Actions =====

      setCreationStep: (step: number) => {
        set((state) => ({
          testCreation: {
            ...state.testCreation,
            step,
          },
        }));
      },

      updateTestData: (data: Partial<TestCreate>) => {
        set((state) => ({
          testCreation: {
            ...state.testCreation,
            testData: {
              ...state.testCreation.testData,
              ...data,
            },
          },
        }));
      },

      updateBasicInfo: (data: any) => {
        set((state) => ({
          testCreation: {
            ...state.testCreation,
            basicInfo: {
              ...state.testCreation.basicInfo,
              ...data,
            },
          },
        }));
      },

      addMCQQuestion: (questionId: string) => {
        set((state) => ({
          testCreation: {
            ...state.testCreation,
            mcqQuestionIds: [...state.testCreation.mcqQuestionIds, questionId],
          },
        }));
      },

      addCodingQuestion: (questionId: string) => {
        set((state) => ({
          testCreation: {
            ...state.testCreation,
            codingQuestionIds: [...state.testCreation.codingQuestionIds, questionId],
          },
        }));
      },

      removeMCQQuestion: (questionId: string) => {
        set((state) => ({
          testCreation: {
            ...state.testCreation,
            mcqQuestionIds: state.testCreation.mcqQuestionIds.filter((id) => id !== questionId),
          },
        }));
      },

      removeCodingQuestion: (questionId: string) => {
        set((state) => ({
          testCreation: {
            ...state.testCreation,
            codingQuestionIds: state.testCreation.codingQuestionIds.filter((id) => id !== questionId),
          },
        }));
      },

      resetTestCreation: () => {
        set((state) => ({
          testCreation: {
            step: 0,
            testData: {},
            mcqQuestionIds: [],
            codingQuestionIds: [],
          },
        }));
      },

      // ===== Utility Actions =====

      clearError: () => {
        set({ currentError: null });
      },

      reset: () => {
        set({
          tests: [],
          currentTest: null,
          assignments: [],
          currentAssignment: null,
          answers: new Map(),
          drafts: new Map(),
          isLoading: false,
          isLoadingTest: false,
          isLoadingAssignments: false,
          currentError: null,
          testCreation: {
            step: 0,
            testData: {},
            mcqQuestionIds: [],
            codingQuestionIds: [],
          },
          testTaking: {
            startTime: null,
            endTime: null,
            isExpired: false,
            currentQuestionIndex: 0,
          },
        });
      },
    }),
    {
      name: 'talentshire-test-store',
      // Only persist non-sensitive data
      partialize: (state) => ({
        tests: state.tests,
        testCreation: state.testCreation,
      }),
    }
  )
);

// ============================================================================
// Mock Question Data - For Demo and Testing
// ============================================================================

export const availableMCQs: MCQQuestion[] = [
  {
    id: '1',
    question_text: 'What is the output of print(2 ** 3) in Python?',
    language: LanguageEnum.python,
    difficulty_level: 'Easy',
    option_a: '6',
    option_b: '8',
    option_c: '9',
    option_d: '23',
    correct_answer: 'B',
  },
  {
    id: '2',
    question_text: 'Which of the following is NOT a primitive data type in Java?',
    language: LanguageEnum.java,
    difficulty_level: 'Medium',
    option_a: 'int',
    option_b: 'String',
    option_c: 'boolean',
    option_d: 'float',
    correct_answer: 'B',
  },
  {
    id: '3',
    question_text: 'What is the correct syntax for an INNER JOIN in SQL?',
    language: LanguageEnum.sql,
    difficulty_level: 'Medium',
    option_a: 'SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.id',
    option_b: 'SELECT * FROM table1 JOIN table2 USING (id)',
    option_c: 'Both A and B are correct',
    option_d: 'Neither A nor B',
    correct_answer: 'C',
  },
];

export const availableCodingQuestions: CodingQuestion[] = [
  {
    id: 'c1',
    problem_statement: 'Write a function that returns the sum of all numbers in a list.',
    language: LanguageEnum.python,
    difficulty_level: 'Easy',
    test_cases: [
      { input: '[1, 2, 3, 4, 5]', expected_output: '15' },
      { input: '[10, 20, 30]', expected_output: '60' },
    ],
  },
  {
    id: 'c2',
    problem_statement: 'Write a function that checks if a string is a palindrome.',
    language: LanguageEnum.java,
    difficulty_level: 'Medium',
    test_cases: [
      { input: 'racecar', expected_output: 'true' },
      { input: 'hello', expected_output: 'false' },
    ],
  },
  {
    id: 'c3',
    problem_statement: 'Write an SQL query to find the second highest salary from an employees table.',
    language: LanguageEnum.sql,
    difficulty_level: 'Hard',
    test_cases: [
      { input: 'employees table with salaries', expected_output: '50000' },
    ],
  },
];

// Export types that were imported
export type { MCQQuestion, CodingQuestion };
