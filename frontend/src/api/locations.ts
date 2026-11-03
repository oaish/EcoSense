import { apiClient } from './client';
import { Location, LocationCreate, LocationUpdate } from '../types';

export const locationsApi = {
  async getLocations(params?: { is_active?: boolean; skip?: number; limit?: number }): Promise<Location[]> {
    return apiClient<Location[]>('/locations', { params });
  },

  async getLocationById(locationId: number): Promise<Location> {
    return apiClient<Location>(`/locations/${locationId}`);
  },

  async createLocation(data: LocationCreate): Promise<Location> {
    return apiClient<Location>('/locations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateLocation(locationId: number, data: LocationUpdate): Promise<Location> {
    return apiClient<Location>(`/locations/${locationId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },
};
