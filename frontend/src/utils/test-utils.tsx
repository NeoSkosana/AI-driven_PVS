import { ReactElement, ReactNode, FC } from 'react';
import { render as rtlRender, RenderResult, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { AuthContext, AuthContextType } from '../context/AuthContext';

interface WrapperProps {
  children: ReactNode;
  authContext?: Partial<AuthContextType>;
}

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  authContext?: Partial<AuthContextType>;
  route?: string;
}

// Default auth context for testing
const defaultAuthContext: AuthContextType = {
  isAuthenticated: false,
  user: null,
  isLoading: false,
  setUser: () => {},
};

const TestWrapper: FC<WrapperProps> = ({ children, authContext = {} }) => {
  const mergedContext = { ...defaultAuthContext, ...authContext };
  return (
    <AuthContext.Provider value={mergedContext}>
      <BrowserRouter>{children}</BrowserRouter>
    </AuthContext.Provider>
  );
};

export function render(
  ui: ReactElement,
  {
    authContext = {},
    route = '/',
    ...renderOptions
  }: CustomRenderOptions = {}
): RenderResult {
  // Update window location if route is provided
  if (route) {
    window.history.pushState({}, 'Test page', route);
  }

  return rtlRender(ui, {
    wrapper: ({ children }) => (
      <TestWrapper authContext={authContext}>{children}</TestWrapper>
    ),
    ...renderOptions,
  });
}

// Mock response generators
export const mockValidationResponse = (status = 'processing') => ({
  requestId: '123-456',
  status,
  timestamp: new Date().toISOString(),
});

export * from '@testing-library/react';

// Test data generators
export const mockValidationResult = {
  id: '123-456',
  sentiment_score: 0.75,
  market_validation: {
    score: 0.8,
    discussions_analyzed: 100,
    positive_mentions: 75,
    negative_mentions: 25,
  },
  recommendations: [
    'Consider expanding target audience',
    'Focus on mobile-first approach',
  ],
  created_at: new Date().toISOString(),
};

export const mockProblemData = {
  title: 'AI-Powered Personal Finance App',
  description: 'A mobile application that uses artificial intelligence to help users manage their personal finances better through automated analysis and recommendations.',
  keywords: 'AI, finance, personal finance, money management',
  targetAudience: 'Young professionals',
  industry: 'Fintech',
};
