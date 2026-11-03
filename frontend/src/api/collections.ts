import { apiClient } from './client';
import { Collection, CollectionCreate } from '../types';

export const collectionsApi = {
  async recordCollection(data: CollectionCreate): Promise<Collection> {
    return apiClient<Collection>('/collections', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getCollections(params?: {
    bin_id?: string;
    collector_id?: string;
    start_date?: string;
    end_date?: string;
    skip?: number;
    limit?: number;
  }): Promise<Collection[]> {
    return apiClient<Collection[]>('/collections', { params });
  },

  async getCollectionById(collectionId: number): Promise<Collection> {
    return apiClient<Collection>(`/collections/${collectionId}`);
  },
};
