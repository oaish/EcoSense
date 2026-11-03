import { apiClient } from './client';
import { ProcessingCreate, ProcessingRecord } from '../types';

export const processingApi = {
  async createProcessingRecord(data: ProcessingCreate): Promise<ProcessingRecord> {
    return apiClient<ProcessingRecord>('/processing', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getProcessingRecords(params?: {
    processing_type?: string;
    status?: string;
    collection_id?: number;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<ProcessingRecord[]> {
    return apiClient<ProcessingRecord[]>('/processing', { params });
  },

  async getProcessingRecordById(processingId: number): Promise<ProcessingRecord> {
    return apiClient<ProcessingRecord>(`/processing/${processingId}`);
  },

  async getCollectionProcessingRecords(collectionId: number): Promise<ProcessingRecord[]> {
    return apiClient<ProcessingRecord[]>(`/collections/${collectionId}/processing`);
  },

  async getBinProcessingRecords(binId: string, params?: { skip?: number; limit?: number }): Promise<ProcessingRecord[]> {
    return apiClient<ProcessingRecord[]>(`/bins/${binId}/processing`, { params });
  },
};
