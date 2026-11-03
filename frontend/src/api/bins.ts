import { apiClient } from './client';
import { Bin, BinCreate, BinQRRead, BinUpdate } from '../types';

export const binsApi = {
  async getBins(params?: {
    location_id?: number;
    waste_type_id?: number;
    status?: string;
    skip?: number;
    limit?: number;
  }): Promise<Bin[]> {
    return apiClient<Bin[]>('/bins', { params });
  },

  async getBinById(binId: string): Promise<Bin> {
    return apiClient<Bin>(`/bins/${binId}`);
  },

  async getBinByQrToken(qrToken: string): Promise<BinQRRead> {
    return apiClient<BinQRRead>(`/bins/qr/${qrToken}`);
  },

  async getPublicBinByQrToken(qrToken: string): Promise<BinQRRead> {
    return apiClient<BinQRRead>(`/bins/public/${qrToken}`);
  },

  async createBin(data: BinCreate): Promise<Bin> {
    return apiClient<Bin>('/bins', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateBin(binId: string, data: BinUpdate): Promise<Bin> {
    return apiClient<Bin>(`/bins/${binId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },
};
