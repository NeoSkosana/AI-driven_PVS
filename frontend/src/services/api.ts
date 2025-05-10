import axios from 'axios';
import { ValidationResult, ValidationStatusResponse } from '../types/validation';

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

export interface ValidationRequest {
  title: string;
  description: string;
  keywords: string[];
  target_market?: string;
}

export interface ValidationResponse {
  request_id: string;
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
