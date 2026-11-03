import { apiClient } from './client';
import { FillReading, FillReadingCreate } from '../types';

export const fillReadingsApi = {
  async recordFillReading(binId: string, data: FillReadingCreate): Promise<FillReading> {
    return apiClient<FillReading>(`/bins/${binId}/fill-readings`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getBinFillReadings(binId: string, params?: { skip?: number; limit?: number }): Promise<FillReading[]> {
    return apiClient<FillReading[]>(`/bins/${binId}/fill-readings`, { params });
  },

  async getFillReadingById(readingId: number): Promise<FillReading> {
    return apiClient<FillReading>(`/fill-readings/${readingId}`);
  },
};
