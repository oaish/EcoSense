import { apiClient } from './client';
import { Reward, RewardCreate, RewardRedemption, RewardUpdate } from '../types';

export const rewardsApi = {
  async getRewards(params?: { skip?: number; limit?: number }): Promise<Reward[]> {
    return apiClient<Reward[]>('/rewards', { params });
  },

  async getRewardById(rewardId: number): Promise<Reward> {
    return apiClient<Reward>(`/rewards/${rewardId}`);
  },

  async createReward(data: RewardCreate): Promise<Reward> {
    return apiClient<Reward>('/rewards', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateReward(rewardId: number, data: RewardUpdate): Promise<Reward> {
    return apiClient<Reward>(`/rewards/${rewardId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  async redeemReward(rewardId: number): Promise<RewardRedemption> {
    return apiClient<RewardRedemption>(`/rewards/${rewardId}/redeem`, {
      method: 'POST',
    });
  },

  async getMyRedemptions(params?: { skip?: number; limit?: number }): Promise<RewardRedemption[]> {
    return apiClient<RewardRedemption[]>('/gamification/me/redemptions', { params });
  },

  async getAllRedemptions(params?: { skip?: number; limit?: number }): Promise<RewardRedemption[]> {
    return apiClient<RewardRedemption[]>('/gamification/redemptions', { params });
  },
};
