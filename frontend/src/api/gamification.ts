import { apiClient } from './client';
import { EcoStage, LeaderboardResponse, PointAdjustmentCreate, PointBalanceRead, PointTransaction } from '../types';

export const gamificationApi = {
  async getMyPoints(): Promise<PointBalanceRead> {
    return apiClient<PointBalanceRead>('/gamification/me');
  },

  async getMyStage(): Promise<EcoStage> {
    return apiClient<EcoStage>('/gamification/me/stage');
  },

  async getLeaderboard(period: string = 'all-time', limit: number = 50): Promise<LeaderboardResponse> {
    return apiClient<LeaderboardResponse>('/gamification/leaderboard', {
      params: { period, limit },
    });
  },

  async getMyTransactions(params?: {
    transaction_type?: string;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<PointTransaction[]> {
    return apiClient<PointTransaction[]>('/gamification/me/transactions', { params });
  },

  async getUserPoints(userId: string): Promise<PointBalanceRead> {
    return apiClient<PointBalanceRead>(`/gamification/users/${userId}`);
  },

  async getUserTransactions(userId: string, params?: {
    transaction_type?: string;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<PointTransaction[]> {
    return apiClient<PointTransaction[]>(`/gamification/users/${userId}/transactions`, { params });
  },

  async adjustUserPoints(userId: string, data: PointAdjustmentCreate): Promise<PointTransaction> {
    return apiClient<PointTransaction>(`/gamification/users/${userId}/adjust`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
