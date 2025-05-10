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
  title: string;
  description: string;
  keywords: string[];
  target_market?: string;
}

export interface ValidationResponse {
  request_id: string;
}

export interface ValidationResult {
  problem_id: string;
  validation_score: number;
  sentiment_summary: {
    overall_sentiment: string;
    positive_ratio: number;
    negative_ratio: number;
    neutral_ratio: number;
    average_score: number;
  };
  engagement_metrics: {
    total_engagement: number;
    avg_score: number;
    avg_comments: number;
  };
  temporal_analysis: {
    earliest_post: string;
    latest_post: string;
    avg_posts_per_day: number;
  };
}

export interface ValidationStatusResponse {
  status: 'processing' | 'completed' | 'failed';
  request_id: string;
  timestamp: string;
  result?: ValidationResult;
}

export const validateProblem = async (problem: ValidationRequest): Promise<ValidationResponse> => {
  const response = await api.post<ValidationResponse>('/validate', problem);
  return response.data;
};

export const getValidationStatus = async (requestId: string): Promise<ValidationStatusResponse> => {
  const response = await api.get<ValidationStatusResponse>(`/validate/${requestId}`);
  return response.data;
};

export const listProblems = async (): Promise<ValidationResult[]> => {
  const response = await api.get<ValidationResult[]>('/problems');
  return response.data;
};

export const deleteProblem = async (problemId: string): Promise<void> => {
  await api.delete(`/problems/${problemId}`);
};
