import { apiClient } from './client';
import { FillPrediction, PredictionRequest } from '../types';

export const predictionsApi = {
  async generatePrediction(binId: string, payload?: PredictionRequest): Promise<FillPrediction> {
    return apiClient<FillPrediction>(`/bins/${binId}/predictions`, {
      method: 'POST',
      body: payload ? JSON.stringify(payload) : undefined,
    });
  },

  async getBinPredictions(binId: string, params?: { skip?: number; limit?: number }): Promise<FillPrediction[]> {
    return apiClient<FillPrediction[]>(`/bins/${binId}/predictions`, { params });
  },

  async getPredictionById(predictionId: number): Promise<FillPrediction> {
    return apiClient<FillPrediction>(`/predictions/${predictionId}`);
  },
};
