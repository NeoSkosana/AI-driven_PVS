import axios from 'axios';

interface LoginCredentials {
  username: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
}

interface User {
  username: string;
  email?: string;
  full_name?: string;
}

const authApi = axios.create({
  baseURL: '/auth',
  headers: {
    'Content-Type': 'application/json'
  }
});

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  const response = await authApi.post<AuthResponse>('/token', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
  
  // Store the token
  localStorage.setItem('token', response.data.access_token);
  
  return response.data;
};

export const logout = (): void => {
  localStorage.removeItem('token');
};

export const getCurrentUser = async (): Promise<User> => {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('No authentication token found');
  }

  const response = await authApi.get<User>('/users/me', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  
  return response.data;
};

export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('token');
};
