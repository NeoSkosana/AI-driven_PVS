import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import ProblemForm from '../../pages/ProblemForm';
import { AuthContext } from '../../context/AuthContext';
import { validateProblem } from '../../services/api';

// Mock react-router-dom's useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

// Mock the API service
jest.mock('../../services/api', () => ({
  validateProblem: jest.fn()
}));

describe('ProblemForm', () => {
  const renderForm = () => {
    const authContext = {
      isAuthenticated: true,
      user: { username: 'testuser' },
      isLoading: false,
      setUser: jest.fn(),
      login: jest.fn(),
      logout: jest.fn()
    };

    return render(
      <AuthContext.Provider value={authContext}>
        <BrowserRouter>
          <ProblemForm />
        </BrowserRouter>
      </AuthContext.Provider>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all form fields', () => {
    renderForm();
    
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/keywords/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/target audience/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/industry/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    renderForm();
    const submitButton = screen.getByRole('button', { name: /submit/i });
    
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      expect(screen.getByText(/description is required/i)).toBeInTheDocument();
      expect(screen.getByText(/keywords are required/i)).toBeInTheDocument();
      expect(screen.getByText(/target audience is required/i)).toBeInTheDocument();
      expect(screen.getByText(/industry is required/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data and navigates to results', async () => {
    renderForm();
    const mockResponse = { request_id: '123-456', status: 'processing' };
    (validateProblem as jest.Mock).mockResolvedValue(mockResponse);

    await userEvent.type(screen.getByLabelText(/problem title/i), 'Test Problem');
    await userEvent.type(screen.getByLabelText(/problem description/i), 'This is a test problem description that needs validation and is long enough to be valid.');
    
    // Add keywords
    await userEvent.type(screen.getByLabelText(/add keyword/i), 'test');
    fireEvent.click(screen.getByRole('button', { name: /add/i }));
    await userEvent.type(screen.getByLabelText(/add keyword/i), 'validation');
    fireEvent.click(screen.getByRole('button', { name: /add/i }));

    // Add target market
    await userEvent.type(screen.getByLabelText(/target market/i), 'Software Developers');

    fireEvent.click(screen.getByRole('button', { name: /validate problem/i }));

    await waitFor(() => {
      expect(validateProblem).toHaveBeenCalledWith({
        title: 'Test Problem',
        description: 'This is a test problem description that needs validation and is long enough to be valid.',
        keywords: ['test', 'validation'],
        target_market: 'Software Developers'
      });
    });

    // Verify navigation
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/results/123-456');
    });

    // Should show success message
    await waitFor(() => {
      expect(screen.getByText(/problem submitted successfully/i)).toBeInTheDocument();
    });
  });

  it('handles API errors and shows error message', async () => {
    renderForm();
    const errorMessage = 'API Error';
    (validateProblem as jest.Mock).mockRejectedValue(new Error(errorMessage));

    await userEvent.type(screen.getByLabelText(/problem title/i), 'Test Problem');
    await userEvent.type(screen.getByLabelText(/problem description/i), 'This is a test problem description that needs validation and is long enough to be valid.');
    
    // Add keyword
    await userEvent.type(screen.getByLabelText(/add keyword/i), 'test');
    fireEvent.click(screen.getByRole('button', { name: /add/i }));
    
    // Add target market
    await userEvent.type(screen.getByLabelText(/target market/i), 'Software Developers');

    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/error validating problem/i)).toBeInTheDocument();
    });
  });

  it('validates description length', async () => {
    renderForm();
    const shortDescription = 'Too short';
    
    await userEvent.type(screen.getByLabelText(/problem description/i), shortDescription);
    fireEvent.blur(screen.getByLabelText(/problem description/i));

    await waitFor(() => {
      expect(screen.getByText(/description must be at least 50 characters/i)).toBeInTheDocument();
    });
  });

  it('manages keywords correctly', async () => {
    renderForm();

    // Add a keyword
    await userEvent.type(screen.getByLabelText(/add keyword/i), 'test-keyword');
    fireEvent.click(screen.getByRole('button', { name: /add/i }));
    expect(screen.getByText('test-keyword')).toBeInTheDocument();

    // Try to add duplicate keyword
    await userEvent.type(screen.getByLabelText(/add keyword/i), 'test-keyword');
    fireEvent.click(screen.getByRole('button', { name: /add/i }));
    expect(screen.getAllByText('test-keyword')).toHaveLength(1);

    // Remove keyword
    const chip = screen.getByText('test-keyword');
    const deleteButton = chip.parentElement?.querySelector('[aria-label="delete"]');
    if (deleteButton) {
      fireEvent.click(deleteButton);
    }
    expect(screen.queryByText('test-keyword')).not.toBeInTheDocument();
  });

  it('disables submit button when form is invalid', () => {
    renderForm();
    const submitButton = screen.getByRole('button', { name: /validate problem/i });
    expect(submitButton).toBeDisabled();

    // Fill only title
    userEvent.type(screen.getByLabelText(/problem title/i), 'Test Title');
    expect(submitButton).toBeDisabled();

    // Add description
    userEvent.type(screen.getByLabelText(/problem description/i), 'Test description that is long enough to be valid in our validation system');
    expect(submitButton).toBeDisabled();

    // Add keyword
    userEvent.type(screen.getByLabelText(/add keyword/i), 'test');
    fireEvent.click(screen.getByRole('button', { name: /add/i }));
    
    // Now the form should be valid
    expect(submitButton).not.toBeDisabled();
  });

  it('handles Enter key in keyword input', async () => {
    renderForm();
    const keywordInput = screen.getByLabelText(/add keyword/i);

    await userEvent.type(keywordInput, 'test-keyword{enter}');
    expect(screen.getByText('test-keyword')).toBeInTheDocument();
    expect(keywordInput).toHaveValue('');
  });

  it('allows form reset', async () => {
    renderForm();
    
    // Fill in form data
    await userEvent.type(screen.getByLabelText(/problem title/i), 'Test Title');
    await userEvent.type(screen.getByLabelText(/problem description/i), 'Test Description');
    await userEvent.type(screen.getByLabelText(/add keyword/i), 'test');
    fireEvent.click(screen.getByRole('button', { name: /add/i }));
    await userEvent.type(screen.getByLabelText(/target market/i), 'Test Market');
    
    // Reset form
    const resetButton = screen.getByRole('button', { name: /reset/i });
    fireEvent.click(resetButton);

    // Verify all fields are reset
    expect(screen.getByLabelText(/problem title/i)).toHaveValue('');
    expect(screen.getByLabelText(/problem description/i)).toHaveValue('');
    expect(screen.getByLabelText(/add keyword/i)).toHaveValue('');
    expect(screen.queryByText('test')).not.toBeInTheDocument();
    expect(screen.getByLabelText(/target market/i)).toHaveValue('');
  });
});
