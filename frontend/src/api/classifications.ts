import { apiClient } from './client';
import { ClassificationCreate, WasteClassification } from '../types';

export const classificationApi = {
  async classifyWaste(data: ClassificationCreate): Promise<WasteClassification> {
    return apiClient<WasteClassification>('/classification', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async classifyWasteUpload(file: File | Blob, disposalId?: number): Promise<WasteClassification> {
    const formData = new FormData();
    formData.append('file', file, file instanceof File ? file.name : 'camera_capture.jpg');
    if (disposalId) {
      formData.append('disposal_id', String(disposalId));
    }
    return apiClient<WasteClassification>('/classification/upload', {
      method: 'POST',
      body: formData,
    });
  },

  async getClassificationById(classificationId: number): Promise<WasteClassification> {
    return apiClient<WasteClassification>(`/classification/${classificationId}`);
  },

  async getClassifications(params?: { skip?: number; limit?: number }): Promise<WasteClassification[]> {
    return apiClient<WasteClassification[]>('/classification', { params });
  },
};
