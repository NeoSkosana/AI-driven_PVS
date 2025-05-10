import { renderHook, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AuthProvider, useAuth } from '../../context/AuthContext';
import { getCurrentUser } from '../../services/auth';

// Mock auth service
jest.mock('../../services/auth', () => ({
  getCurrentUser: jest.fn(),
  isAuthenticated: jest.fn()
}));

describe('AuthContext', () => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('provides authentication state and methods', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current).toHaveProperty('isAuthenticated', false);
    expect(result.current).toHaveProperty('user', null);
    expect(result.current).toHaveProperty('isLoading', true);
    expect(typeof result.current.setUser).toBe('function');
  });

  it('updates authentication state when setting user', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    act(() => {
      result.current.setUser({ username: 'testuser' });
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({ username: 'testuser' });
  });

  it('handles initial user loading correctly', async () => {
    const mockUser = { username: 'testuser' };
    (getCurrentUser as jest.Mock).mockResolvedValueOnce(mockUser);

    const { result } = renderHook(() => useAuth(), { wrapper });

    // Initially loading
    expect(result.current.isLoading).toBe(true);

    // Wait for loading to complete
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    // Loading complete, user set
    expect(result.current.isLoading).toBe(false);
    expect(result.current.user).toEqual(mockUser);
  });

  it('handles failed user loading gracefully', async () => {
    (getCurrentUser as jest.Mock).mockRejectedValueOnce(new Error('Failed to load user'));

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('clears user state correctly', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    // Set a user
    act(() => {
      result.current.setUser({ username: 'testuser' });
    });

    // Clear the user
    act(() => {
      result.current.setUser(null);
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
  });

  it('maintains consistent loading state', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    // Should start loading
    expect(result.current.isLoading).toBe(true);

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    // Should finish loading
    expect(result.current.isLoading).toBe(false);
  });
});
