import { create } from 'zustand';
import { MCQQuestion, CodingQuestion } from './testStore';
import { assignmentApi, testApi } from '@/services/api';

export type TestSessionState = 
  | 'IDLE' 
  | 'INSTRUCTIONS' 
  | 'ACTIVE' 
  | 'SUBMIT_CONFIRM' 
  | 'SUBMITTED' 
  | 'REPORT_VIEW';

export interface MCQAnswer {
  questionId: string;
  selectedOption: number | null;
}

export interface CodingAnswer {
  questionId: string;
  code: string;
  language: string;
}

export interface TestSession {
  assignmentId: string;
  testId: string;
  state: TestSessionState;
  currentQuestionIndex: number;
  mcqAnswers: MCQAnswer[];
  codingAnswers: CodingAnswer[];
  startedAt: string | null;
  remainingTime: number; // in seconds
  lastAutosave: string | null;
}

interface CandidateTestState {
  session: TestSession | null;
  
  // Session management
  initSession: (assignmentId: string, testId: string, duration: number, mcqs: MCQQuestion[], codings: CodingQuestion[]) => void;
  setState: (state: TestSessionState) => void;
  
  // Navigation
  setCurrentQuestion: (index: number) => void;
  nextQuestion: () => void;
  prevQuestion: () => void;
  
  // Answers
  saveMCQAnswer: (questionId: string, selectedOption: number) => void;
  saveCodingAnswer: (questionId: string, code: string) => void;
  
  // Timer
  decrementTimer: () => void;
  
  // Autosave
  markAutosaved: () => void;
  
  // Recovery
  loadSavedSession: (session: TestSession) => void;
  // Load assignment+test from backend and initialize session
  loadAssignmentAndInit: (assignmentId: string) => Promise<void>;
  
  // Submit
  submitTest: () => void;
  
  // Reset
  resetSession: () => void;
}

export const useCandidateTestStore = create<CandidateTestState>((set, get) => ({
  session: null,
  
  initSession: (assignmentId, testId, duration, mcqs, codings) => {
    const mcqAnswers: MCQAnswer[] = mcqs.map((q) => ({
      questionId: q.id,
      selectedOption: null,
    }));
    
    const codingAnswers: CodingAnswer[] = codings.map((q) => ({
      questionId: q.id,
      code: q.starterCode,
      language: q.language,
    }));
    
    set({
      session: {
        assignmentId,
        testId,
        state: 'INSTRUCTIONS',
        currentQuestionIndex: 0,
        mcqAnswers,
        codingAnswers,
        startedAt: null,
        remainingTime: duration * 60, // Convert to seconds
        lastAutosave: null,
      },
    });
  },
  
  setState: (state) => {
    set((prev) => {
      if (!prev.session) return prev;
      
      const updates: Partial<TestSession> = { state };
      
      if (state === 'ACTIVE' && !prev.session.startedAt) {
        updates.startedAt = new Date().toISOString();
      }
      
      return {
        session: { ...prev.session, ...updates },
      };
    });
  },
  
  setCurrentQuestion: (index) => {
    set((prev) => {
      if (!prev.session) return prev;
      return {
        session: { ...prev.session, currentQuestionIndex: index },
      };
    });
  },
  
  nextQuestion: () => {
    const { session } = get();
    if (!session) return;
    
    const totalQuestions = session.mcqAnswers.length + session.codingAnswers.length;
    if (session.currentQuestionIndex < totalQuestions - 1) {
      set({
        session: { ...session, currentQuestionIndex: session.currentQuestionIndex + 1 },
      });
    }
  },
  
  prevQuestion: () => {
    const { session } = get();
    if (!session) return;
    
    if (session.currentQuestionIndex > 0) {
      set({
        session: { ...session, currentQuestionIndex: session.currentQuestionIndex - 1 },
      });
    }
  },
  
  saveMCQAnswer: (questionId, selectedOption) => {
    set((prev) => {
      if (!prev.session) return prev;
      return {
        session: {
          ...prev.session,
          mcqAnswers: prev.session.mcqAnswers.map((a) =>
            a.questionId === questionId ? { ...a, selectedOption } : a
          ),
        },
      };
    });
  },
  
  saveCodingAnswer: (questionId, code) => {
    set((prev) => {
      if (!prev.session) return prev;
      return {
        session: {
          ...prev.session,
          codingAnswers: prev.session.codingAnswers.map((a) =>
            a.questionId === questionId ? { ...a, code } : a
          ),
        },
      };
    });
  },
  
  decrementTimer: () => {
    set((prev) => {
      if (!prev.session || prev.session.remainingTime <= 0) return prev;
      return {
        session: { ...prev.session, remainingTime: prev.session.remainingTime - 1 },
      };
    });
  },
  
  markAutosaved: () => {
    set((prev) => {
      if (!prev.session) return prev;
      return {
        session: { ...prev.session, lastAutosave: new Date().toISOString() },
      };
    });
  },
  
  loadSavedSession: (session) => {
    set({ session });
  },

  // Fetch assignment + test from backend and initialize session
  loadAssignmentAndInit: async (assignmentId: string) => {
    try {
      const assignmentResp = await assignmentApi.getAssignment(assignmentId);
      const assignment = assignmentResp.data;
      if (!assignment) throw new Error(assignmentResp.error || 'Assignment not found');

      const testId = assignment.test_id;
      const testResp = await testApi.getTestWithQuestions(testId);
      const test = testResp.data;
      if (!test) throw new Error(testResp.error || 'Test not found');

      // Prepare MCQ and coding question arrays in the shape expected by initSession
      const mcqs: MCQQuestion[] = (test.mcq_questions || []).map((q: any) => ({
        id: q.question_id,
        question: q.question_text || q.question,
        options: [q.option_a, q.option_b, q.option_c, q.option_d].filter(Boolean),
        correctAnswer: q.correct_answer as any,
        difficulty: q.difficulty,
        tags: q.tags || [],
        points: q.marks || 0,
      }));

      const codings: CodingQuestion[] = (test.coding_questions || []).map((q: any) => ({
        id: q.question_id,
        title: q.title,
        description: q.description,
        starterCode: q.starter_code || q.starterCode || '',
        testCases: q.test_cases || [],
        difficulty: q.difficulty,
        tags: q.tags || [],
        points: q.marks || 0,
        language: q.language,
      }));

      // Initialize session via existing initSession helper
      const duration = test.duration_minutes || 60;
      // @ts-ignore - call initSession from store
      (get() as any).initSession(assignment.assignment_id, test.test_id, duration, mcqs, codings);
    } catch (err) {
      // Store-level error handling could be added; for now console.warn
      // eslint-disable-next-line no-console
      console.warn('Failed to load assignment and init session', err);
    }
  },
  
  submitTest: () => {
    set((prev) => {
      if (!prev.session) return prev;
      return {
        session: { ...prev.session, state: 'SUBMITTED' },
      };
    });
  },
  
  resetSession: () => {
    set({ session: null });
  },
}));
