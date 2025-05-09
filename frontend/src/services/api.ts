import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

export interface ProblemStatement {
  title: string;
  description: string;
  keywords: string[];
  target_market?: string;
}

export interface ValidationResult {
  problem_id: string;
  timestamp: string;
  sentiment_summary: {
    overall_sentiment: string;
    positive_ratio: number;
    negative_ratio: number;
    neutral_ratio: number;
    average_score: number;
  };
  engagement_metrics: {
    avg_score: number;
    avg_comments: number;
    total_engagement: number;
  };
  temporal_analysis: {
    earliest_post: string;
    latest_post: string;
    avg_posts_per_day: number;
  };
  validation_score: number;
  relevant_posts: any[];
}

export interface ValidationRequest {
  request_id: string;
  status: string;
  created_at: string;
  completed_at?: string;
  result?: ValidationResult;
}

export const validateProblem = async (problem: ProblemStatement): Promise<ValidationRequest> => {
  const response = await api.post<ValidationRequest>('/validate', problem);
  return response.data;
};

export const getValidationStatus = async (problemId: string): Promise<ValidationRequest> => {
  const response = await api.get<ValidationRequest>(`/validate/${problemId}`);
  return response.data;
};

export const listProblems = async (): Promise<ValidationResult[]> => {
  const response = await api.get<ValidationResult[]>('/problems');
  return response.data;
};

export const deleteProblem = async (problemId: string): Promise<void> => {
  await api.delete(`/problems/${problemId}`);
};
