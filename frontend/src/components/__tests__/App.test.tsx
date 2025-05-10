import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../../App';

describe('App', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const renderApp = () => {
    return render(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <App />
        </QueryClientProvider>
      </BrowserRouter>
    );
  };

  beforeEach(() => {
    queryClient.clear();
    localStorage.clear();
  });

  it('renders navigation and main content', () => {
    renderApp();
    expect(screen.getByText(/problem validation/i)).toBeInTheDocument();
  });

  it('shows login page for unauthenticated users', () => {
    renderApp();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('renders with the correct theme', () => {
    const { container } = renderApp();
    // Check if MUI theme is applied
    const mainContent = container.querySelector('main');
    expect(mainContent).toHaveStyle({ padding: '24px' }); // MUI default spacing of 3 = 24px
  });

  it('includes AuthProvider for authentication context', () => {
    renderApp();
    // Verify that AuthProvider is working by checking for auth-related UI
    expect(screen.getByText(/login/i)).toBeInTheDocument();
  });

  it('has protected routes set up correctly', async () => {
    renderApp();
    // Attempt to access a protected route
    window.history.pushState({}, 'Dashboard', '/');
    // Should be redirected to login
    expect(window.location.pathname).toBe('/login');
  });
});
