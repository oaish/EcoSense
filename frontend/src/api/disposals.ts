import { apiClient } from './client';
import { Disposal, DisposalCreate } from '../types';

export const disposalsApi = {
  async recordDisposal(data: DisposalCreate): Promise<Disposal> {
    return apiClient<Disposal>('/disposals', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getDisposals(params?: {
    bin_id?: string;
    user_id?: string;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<Disposal[]> {
    return apiClient<Disposal[]>('/disposals', { params });
  },

  async getDisposalById(disposalId: number): Promise<Disposal> {
    return apiClient<Disposal>(`/disposals/${disposalId}`);
  },
};
