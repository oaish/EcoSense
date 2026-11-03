import { apiClient } from './client';
import {
  AdminUserCreatePayload,
  AdminUserDetail,
  AdminUserListResponse,
  AdminUserSummary,
  AdminUserUpdatePayload,
  User,
} from '../types';

export const usersApi = {
  async getMe(): Promise<User> {
    return apiClient<User>('/users/me');
  },

  async verifyAdminTest(): Promise<{ message: string; admin_user: string; timestamp: string }> {
    return apiClient<{ message: string; admin_user: string; timestamp: string }>('/users/admin-test');
  },

  async listUsers(params?: {
    search?: string;
    role?: string;
    is_active?: boolean;
    skip?: number;
    limit?: number;
  }): Promise<AdminUserListResponse> {
    return apiClient<AdminUserListResponse>('/users', { params });
  },

  async getUserDetail(userId: string): Promise<AdminUserDetail> {
    return apiClient<AdminUserDetail>(`/users/${userId}/detail`);
  },

  async createAdminUser(data: AdminUserCreatePayload): Promise<AdminUserSummary> {
    return apiClient<AdminUserSummary>('/users', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateAdminUser(userId: string, data: AdminUserUpdatePayload): Promise<AdminUserSummary> {
    return apiClient<AdminUserSummary>(`/users/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async updateUserPhone(userId: string, phoneNumber: string | null): Promise<AdminUserSummary> {
    return apiClient<AdminUserSummary>(`/users/${userId}/phone`, {
      method: 'PATCH',
      body: JSON.stringify({ phone_number: phoneNumber }),
    });
  },
};
