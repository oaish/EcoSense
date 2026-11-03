import { apiClient, setStoredToken } from './client';
import { AuthResponse, User } from '../types';

export interface LoginCredentials {
  email: string;
  password: string;
}

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
      skipAuth: true,
    });
    if (response.access_token) {
      setStoredToken(response.access_token);
    }
    return response;
  },

  async getMe(): Promise<User> {
    return apiClient<User>('/auth/me');
  },

  logout(): void {
    setStoredToken(null);
  },
};
