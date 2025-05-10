import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import Navbar from '../Navbar';

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('Navbar', () => {  const renderWithContext = (isAuthenticated = false) => {
    const authContext = {
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
          <Navbar />
        </BrowserRouter>
      </AuthContext.Provider>
    );
  };

  it('renders logo and brand name', () => {
    renderWithContext();
    expect(screen.getByText(/Problem Validation/i)).toBeInTheDocument();
  });

  it('shows login button when not authenticated', () => {
    renderWithContext(false);
    expect(screen.getByText(/Login/i)).toBeInTheDocument();
    expect(screen.queryByText(/Logout/i)).not.toBeInTheDocument();
  });

  it('shows user menu and logout when authenticated', () => {
    renderWithContext(true);
    expect(screen.getByText(/testuser/i)).toBeInTheDocument();
    expect(screen.queryByText(/Login/i)).not.toBeInTheDocument();
  });

  it('navigates to login page when login button clicked', () => {
    renderWithContext(false);
    fireEvent.click(screen.getByText(/Login/i));
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('shows navigation links when authenticated', () => {
    renderWithContext(true);
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/New Problem/i)).toBeInTheDocument();
  });

  it('handles logout correctly', () => {
    const { container } = renderWithContext(true);
    const userMenu = container.querySelector('[aria-label="user menu"]');
    expect(userMenu).toBeInTheDocument();
    
    if (userMenu) {
      fireEvent.click(userMenu);
      const logoutButton = screen.getByText(/Logout/i);
      fireEvent.click(logoutButton);
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    }
  });
});
