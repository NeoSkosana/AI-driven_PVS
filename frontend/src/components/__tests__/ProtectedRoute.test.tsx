import { render, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter, Routes, Route, MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import ProtectedRoute from '../ProtectedRoute';

describe('ProtectedRoute', () => {
  const MockComponent = () => <div>Protected Content</div>;
  
  const renderWithAuth = (isAuthenticated = false, isLoading = false) => {
    const authContext = {
      isAuthenticated,
      user: isAuthenticated ? { username: 'testuser' } : null,
      isLoading,
      setUser: jest.fn(),
      login: jest.fn(),
      logout: jest.fn(),
    };

    return render(
      <AuthContext.Provider value={authContext}>
        <BrowserRouter>
          <Routes>
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <MockComponent />
                </ProtectedRoute>
              } 
            />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </BrowserRouter>
      </AuthContext.Provider>
    );
  };

  it('renders children when authenticated', () => {
    renderWithAuth(true);
    expect(screen.getByText(/Protected Content/i)).toBeInTheDocument();
    expect(screen.queryByText(/Login Page/i)).not.toBeInTheDocument();
  });

  it('redirects to login when not authenticated', () => {
    renderWithAuth(false);
    expect(screen.queryByText(/Protected Content/i)).not.toBeInTheDocument();
    expect(screen.getByText(/Login Page/i)).toBeInTheDocument();
  });  it('preserves the route state when redirecting', () => {
    window.history.pushState({}, 'Protected Page', '/protected');
    renderWithAuth(false);
    
    // Check that we're redirected to login
    expect(window.location.pathname).toBe('/login');
    
    // Check that the state contains the original location
    const navigate = screen.getByText('Login Page');
    const state = navigate.getAttribute('state');
    expect(state).toBeDefined();
    const fromPath = JSON.parse(state || '{}').from?.pathname;
    expect(fromPath).toBe('/protected');
  });

  it('shows loading spinner when authentication is being checked', () => {
    renderWithAuth(false, true);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(screen.queryByText(/Protected Content/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Login Page/i)).not.toBeInTheDocument();
  });
  it('properly centers the loading spinner', () => {
    const { container } = renderWithAuth(false, true);
    const loadingBox = container.querySelector('.MuiBox-root');
    expect(loadingBox).toHaveStyle({
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh'
    });
  });  it('handles dynamic authentication state changes', () => {
    const { rerender } = renderWithAuth(false);
    expect(screen.getByText(/Login Page/i)).toBeInTheDocument();

    // Change to loading state
    rerender(
      <BrowserRouter>
        <AuthContext.Provider value={{ isAuthenticated: false, isLoading: true, user: null, setUser: jest.fn() }}>
          <Routes>
            <Route path="/" element={<ProtectedRoute><MockComponent /></ProtectedRoute>} />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </AuthContext.Provider>
      </BrowserRouter>
    );
    expect(screen.getByRole('progressbar')).toBeInTheDocument();

    // Change to authenticated state
    rerender(
      <BrowserRouter>
        <AuthContext.Provider value={{ isAuthenticated: true, isLoading: false, user: { username: 'testuser' }, setUser: jest.fn() }}>
          <Routes>
            <Route path="/" element={<ProtectedRoute><MockComponent /></ProtectedRoute>} />
            <Route path="/login" element={<div>Login Page</div>} />
          </Routes>
        </AuthContext.Provider>
      </BrowserRouter>
    );
    expect(screen.getByText(/Protected Content/i)).toBeInTheDocument();
  });

  it('renders loading state consistently', () => {
    const { container } = renderWithAuth(false, true);
    expect(container).toMatchSnapshot();
  });
  it('handles navigation after successful login', () => {
    // Start at /dashboard which should redirect to /login
    window.history.pushState({}, '', '/dashboard');

    const { rerender } = renderWithAuth(false);
    expect(window.location.pathname).toBe('/login');
    expect(window.history.state?.usr?.from?.pathname).toBe('/dashboard');

    // Simulate successful login
    rerender(
      <BrowserRouter>
        <AuthContext.Provider value={{ isAuthenticated: true, isLoading: false, user: { username: 'testuser' }, setUser: jest.fn() }}>
          <Routes>
            <Route path="/" element={<ProtectedRoute><MockComponent /></ProtectedRoute>} />
            <Route path="/login" element={<div>Login Page</div>} />
            <Route path="/dashboard" element={<ProtectedRoute><div>Dashboard</div></ProtectedRoute>} />
          </Routes>
        </AuthContext.Provider>
      </BrowserRouter>
    );

    // Should be back at the original route
    expect(window.location.pathname).toBe('/dashboard');
    expect(screen.queryByText(/Login Page/i)).not.toBeInTheDocument();
  });
});
