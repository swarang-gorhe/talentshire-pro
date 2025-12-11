import { create } from 'zustand';
import { MCQQuestion, CodingQuestion } from './testStore';
import { apiPost } from '../lib/api';
import { useAuthStore } from './authStore';

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
  isVisited: boolean;
  isMarkedForReview: boolean;
}

export interface CodingAnswer {
  questionId: string;
  code: string;
  language: string;
  isVisited: boolean;
  isMarkedForReview: boolean;
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
  
  // Mark for review
  toggleMarkForReview: (questionId: string) => void;
  markQuestionVisited: (questionId: string) => void;
  
  // Timer
  decrementTimer: () => void;
  
  // Autosave
  markAutosaved: () => void;
  
  // Recovery
  loadSavedSession: (session: TestSession) => void;
  
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
      isVisited: false,
      isMarkedForReview: false,
    }));
    
    const codingAnswers: CodingAnswer[] = codings.map((q) => ({
      questionId: q.id,
      code: q.starterCode,
      language: q.language,
      isVisited: false,
      isMarkedForReview: false,
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
        remainingTime: duration * 60,
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
      
      // Fire-and-forget: also save MCQ answer to backend
      const auth = useAuthStore.getState();
      const candidateId = auth.user?.id;
      if (candidateId) {
        const assignmentId = prev.session.assignmentId;
        apiPost('/mcq-answer', {
          candidate_id: candidateId,
          assignment_id: assignmentId,
          question_id: questionId,
          selected_option: selectedOption.toString(),
          is_correct: null, // Backend can grade if needed
        }).catch(() => {
          // ignore network errors for MCQ save
        });
      }
      
      return {
        session: {
          ...prev.session,
          mcqAnswers: prev.session.mcqAnswers.map((a) =>
            a.questionId === questionId ? { ...a, selectedOption, isVisited: true } : a
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
            a.questionId === questionId ? { ...a, code, isVisited: true } : a
          ),
        },
      };
    });
  },
  
  toggleMarkForReview: (questionId) => {
    set((prev) => {
      if (!prev.session) return prev;
      
      const mcqAnswer = prev.session.mcqAnswers.find(a => a.questionId === questionId);
      if (mcqAnswer) {
        return {
          session: {
            ...prev.session,
            mcqAnswers: prev.session.mcqAnswers.map((a) =>
              a.questionId === questionId ? { ...a, isMarkedForReview: !a.isMarkedForReview } : a
            ),
          },
        };
      }
      
      return {
        session: {
          ...prev.session,
          codingAnswers: prev.session.codingAnswers.map((a) =>
            a.questionId === questionId ? { ...a, isMarkedForReview: !a.isMarkedForReview } : a
          ),
        },
      };
    });
  },
  
  markQuestionVisited: (questionId) => {
    set((prev) => {
      if (!prev.session) return prev;
      
      const mcqAnswer = prev.session.mcqAnswers.find(a => a.questionId === questionId);
      if (mcqAnswer) {
        return {
          session: {
            ...prev.session,
            mcqAnswers: prev.session.mcqAnswers.map((a) =>
              a.questionId === questionId ? { ...a, isVisited: true } : a
            ),
          },
        };
      }
      
      return {
        session: {
          ...prev.session,
          codingAnswers: prev.session.codingAnswers.map((a) =>
            a.questionId === questionId ? { ...a, isVisited: true } : a
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
    set(async (prev) => {
      if (!prev.session) return prev;

      const auth = useAuthStore.getState();
      const candidateId = auth.user?.id;

      // Fire-and-forget: save coding drafts to /draft for recovery
      try {
        if (candidateId) {
          for (const c of prev.session.codingAnswers) {
            await apiPost('/draft', {
              candidate_id: candidateId,
              problem_id: c.questionId,
              language: c.language,
              code: c.code,
              cursor_position: 0,
            });
          }
        }
      } catch (e) {
        // ignore network errors for autosave
      }

      return {
        session: { ...prev.session, lastAutosave: new Date().toISOString() },
      };
    });
  },
  
  loadSavedSession: (session) => {
    set({ session });
  },
  
  submitTest: () => {
    set(async (prev) => {
      if (!prev.session) return prev;

      const auth = useAuthStore.getState();
      const candidateId = auth.user?.id;

      // Submit coding answers to submission service
      try {
        if (candidateId) {
          const assignmentId = prev.session.assignmentId;
          for (const c of prev.session.codingAnswers) {
            await apiPost('/test-answer', {
              candidate_id: candidateId,
              assignment_id: assignmentId,
              question_id: c.questionId,
              problem_id: c.questionId,
              language: c.language,
              code: c.code,
              stdin: '',
              stdout: '',
              output: '',
              code_status: 'pending',
              code_passed: false,
              time_spent_seconds: 0,
            });
          }
        }
      } catch (e) {
        // If backend fails, still mark as submitted locally
      }

      return {
        session: { ...prev.session, state: 'SUBMITTED' },
      };
    });
  },
  
  resetSession: () => {
    set({ session: null });
  },
}));
