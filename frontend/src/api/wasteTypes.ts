import { apiClient } from './client';
import { WasteType, WasteTypeCreate, WasteTypeUpdate } from '../types';

export const wasteTypesApi = {
  async getWasteTypes(params?: { is_active?: boolean; skip?: number; limit?: number }): Promise<WasteType[]> {
    return apiClient<WasteType[]>('/waste-types', { params });
  },

  async createWasteType(data: WasteTypeCreate): Promise<WasteType> {
    return apiClient<WasteType>('/waste-types', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateWasteType(wasteTypeId: number, data: WasteTypeUpdate): Promise<WasteType> {
    return apiClient<WasteType>(`/waste-types/${wasteTypeId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },
};
