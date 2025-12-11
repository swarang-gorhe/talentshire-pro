import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, RoleEnum } from '@/types/api';
import { authApi } from '@/services/api';

interface AuthState {
  // State
  user: User | null;
  isAuthenticated: boolean;
  authToken: string | null;
  isLoading: boolean;
  currentError: string | null;

  // Actions
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  loginWithToken: (token: string) => Promise<{ success: boolean; error?: string }>;
  getCurrentUser: () => Promise<void>;
  refreshToken: () => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      authToken: null,
      isLoading: false,
      currentError: null,

      // Actions
      login: async (email: string, password: string) => {
        set({ isLoading: true, currentError: null });
        try {
          const response = await authApi.login(email, password);
          if (response.success && response.data) {
            const { token, user } = response.data;
            localStorage.setItem('auth_token', token);
            set({
              user,
              isAuthenticated: true,
              authToken: token,
            });
            return { success: true };
          }
          return { success: false, error: response.error || 'Login failed' };
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Login failed';
          set({ currentError: errorMsg });
          return { success: false, error: errorMsg };
        } finally {
          set({ isLoading: false });
        }
      },

      loginWithToken: async (token: string) => {
        set({ isLoading: true, currentError: null });
        try {
          const response = await authApi.loginWithToken(token);
          if (response.success && response.data) {
            localStorage.setItem('auth_token', token);
            set({
              user: response.data.user,
              isAuthenticated: true,
              authToken: token,
            });
            return { success: true };
          }
          return { success: false, error: response.error || 'Token login failed' };
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Token login failed';
          set({ currentError: errorMsg });
          return { success: false, error: errorMsg };
        } finally {
          set({ isLoading: false });
        }
      },

      getCurrentUser: async () => {
        set({ isLoading: true, currentError: null });
        try {
          const response = await authApi.getCurrentUser();
          if (response.success && response.data) {
            set({ user: response.data, isAuthenticated: true });
          }
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to get current user';
          set({ currentError: errorMsg });
        } finally {
          set({ isLoading: false });
        }
      },

      refreshToken: async () => {
        try {
          const response = await authApi.refreshToken();
          if (response.success && response.data) {
            const { token } = response.data;
            localStorage.setItem('auth_token', token);
            set({ authToken: token });
          }
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to refresh token';
          set({ currentError: errorMsg });
        }
      },

      logout: () => {
        localStorage.removeItem('auth_token');
        set({
          user: null,
          isAuthenticated: false,
          authToken: null,
          currentError: null,
        });
      },

      clearError: () => {
        set({ currentError: null });
      },
    }),
    {
      name: 'talentshire-auth',
      // Only persist user and token
      partialize: (state) => ({
        user: state.user,
        authToken: state.authToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
