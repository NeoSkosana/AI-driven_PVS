import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from '../../pages/Dashboard';
import { AuthContext } from '../../context/AuthContext';
import { listProblems } from '../../services/api';

// Mock the API calls
jest.mock('../../services/api', () => ({
  listProblems: jest.fn()
}));

// Mock react-router-dom's useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

describe('Dashboard', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const renderDashboard = () => {    const authContext = {
      isAuthenticated: true,
      user: { username: 'testuser' },
      isLoading: false,
      setUser: jest.fn(),
      login: jest.fn(),
      logout: jest.fn(),
    };

    return render(
      <AuthContext.Provider value={authContext}>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <Dashboard />
          </BrowserRouter>
        </QueryClientProvider>
      </AuthContext.Provider>
    );
  };

  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
  });

  it('shows loading state initially', () => {
    renderDashboard();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows error state when API call fails', async () => {
    (listProblems as jest.Mock).mockRejectedValueOnce(new Error('API Error'));
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/error loading problems/i)).toBeInTheDocument();
    });
  });

  it('displays validation history when data is loaded', async () => {
    const mockProblems = [
      {
        problem_id: '123',
        validation_score: 0.75,
        sentiment_summary: {
          overall_sentiment: 'Positive',
          positive_ratio: 0.6,
          negative_ratio: 0.2,
          neutral_ratio: 0.2
        },
        engagement_metrics: {
          total_engagement: 150
        }
      },
      {
        problem_id: '456',
        validation_score: 0.85,
        sentiment_summary: {
          overall_sentiment: 'Very Positive',
          positive_ratio: 0.8,
          negative_ratio: 0.1,
          neutral_ratio: 0.1
        },
        engagement_metrics: {
          total_engagement: 200
        }
      }
    ];

    (listProblems as jest.Mock).mockResolvedValueOnce(mockProblems);
    renderDashboard();

    // Check for problem cards
    await waitFor(() => {
      expect(screen.getByText('75%')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument();
    });

    // Check for sentiment info
    expect(screen.getByText('Positive')).toBeInTheDocument();
    expect(screen.getByText('Very Positive')).toBeInTheDocument();

    // Check for engagement metrics
    expect(screen.getByText('150')).toBeInTheDocument();
    expect(screen.getByText('200')).toBeInTheDocument();
  });

  it('navigates to validation form when new validation button is clicked', () => {
    renderDashboard();
    fireEvent.click(screen.getByText(/validate new problem/i));
    expect(mockNavigate).toHaveBeenCalledWith('/validate');
  });

  it('navigates to result details when View Details is clicked', async () => {
    const mockProblems = [
      {
        problem_id: '123',
        validation_score: 0.75,
        sentiment_summary: {
          overall_sentiment: 'Positive',
          positive_ratio: 0.6,
          negative_ratio: 0.2,
          neutral_ratio: 0.2
        },
        engagement_metrics: {
          total_engagement: 150
        }
      }
    ];

    (listProblems as jest.Mock).mockResolvedValueOnce(mockProblems);
    renderDashboard();

    await waitFor(() => {
      fireEvent.click(screen.getByText(/view details/i));
    });

    expect(mockNavigate).toHaveBeenCalledWith('/results/123');
  });

  it('displays empty state when no problems exist', async () => {
    (listProblems as jest.Mock).mockResolvedValueOnce([]);
    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/no validated problems yet/i)).toBeInTheDocument();
      expect(screen.getByText(/validate new problem/i)).toBeInTheDocument();
    });
  });
});
