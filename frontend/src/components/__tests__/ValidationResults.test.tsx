import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ValidationResults from '../../pages/ValidationResults';
import { AuthContext } from '../../context/AuthContext';
import { getValidationStatus } from '../../services/api';

// Mock the API calls
jest.mock('../../services/api', () => ({
  getValidationStatus: jest.fn()
}));

// Mock react-router-dom's useParams
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({ id: '123-456' })
}));

describe('ValidationResults', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const renderResults = () => {    const authContext = {
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
            <ValidationResults />
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
    renderResults();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows error state when API call fails', async () => {
    (getValidationStatus as jest.Mock).mockRejectedValueOnce(new Error('API Error'));
    renderResults();

    await waitFor(() => {
      expect(screen.getByText(/error loading validation results/i)).toBeInTheDocument();
    });
  });

  it('shows processing state while validation is ongoing', async () => {
    (getValidationStatus as jest.Mock).mockResolvedValueOnce({
      status: 'processing',
      request_id: '123-456',
      created_at: new Date().toISOString()
    });
    renderResults();

    await waitFor(() => {
      expect(screen.getByText(/validating problem/i)).toBeInTheDocument();
    });
  });

  it('shows failed state when validation fails', async () => {
    (getValidationStatus as jest.Mock).mockResolvedValueOnce({
      status: 'failed',
      request_id: '123-456',
      created_at: new Date().toISOString()
    });
    renderResults();

    await waitFor(() => {
      expect(screen.getByText(/validation failed/i)).toBeInTheDocument();
    });
  });

  it('displays validation results when successful', async () => {
    const mockResult = {
      request_id: '123-456',
      status: 'completed',
      created_at: new Date().toISOString(),
      result: {
        validation_score: 0.75,
        sentiment_summary: {
          overall_sentiment: 'Positive',
          positive_ratio: 0.6,
          negative_ratio: 0.2,
          neutral_ratio: 0.2,
          average_score: 0.75
        },
        engagement_metrics: {
          avg_score: 4.2,
          avg_comments: 8,
          total_engagement: 150
        },
        temporal_analysis: {
          earliest_post: new Date().toISOString(),
          latest_post: new Date().toISOString(),
          avg_posts_per_day: 5.5
        }
      }
    };

    (getValidationStatus as jest.Mock).mockResolvedValueOnce(mockResult);
    renderResults();

    // Check for main components
    await waitFor(() => {
      expect(screen.getByText(/validation results/i)).toBeInTheDocument();
      expect(screen.getByText(/75%/)).toBeInTheDocument();
      expect(screen.getByText(/positive/i)).toBeInTheDocument();
      expect(screen.getByText('150')).toBeInTheDocument();
    });

    // Check for detailed metrics
    expect(screen.getByText(/engagement metrics/i)).toBeInTheDocument();
    expect(screen.getByText('4.2')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();

    // Check for sentiment breakdown
    expect(screen.getByText(/sentiment analysis/i)).toBeInTheDocument();
  });
});
