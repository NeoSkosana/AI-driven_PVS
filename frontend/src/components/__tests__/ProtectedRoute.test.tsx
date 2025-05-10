import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import ProtectedRoute from '../ProtectedRoute';

describe('ProtectedRoute', () => {
  const MockComponent = () => <div>Protected Content</div>;
  
  const renderWithAuth = (isAuthenticated = false) => {    const authContext = {
      isAuthenticated,
      user: isAuthenticated ? { username: 'testuser' } : null,
      isLoading: false,
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
  });

  it('preserves the route state when redirecting', () => {
    const { container } = renderWithAuth(false);
    const location = container.querySelector('div')?.baseURI;
    expect(location).toContain('/login');
  });
});
