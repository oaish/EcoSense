import { apiClient } from './client';
import {
  AlertItem,
  AnalyticsSummary,
  BinFillAnalytics,
  ClassificationAnalytics,
  CollectionAnalytics,
  GamificationAnalytics,
  LocationMetric,
  ParticipationAnalytics,
  PredictionAnalytics,
  ProcessingAnalytics,
  ReportAnalytics,
  TrendAnalytics,
  WasteTypeMetric,
} from '../types';

export const analyticsApi = {
  async getSummary(params?: { start_date?: string; end_date?: string }): Promise<AnalyticsSummary> {
    return apiClient<AnalyticsSummary>('/analytics/summary', { params });
  },

  async getWasteTypes(params?: { start_date?: string; end_date?: string; location_id?: number }): Promise<WasteTypeMetric[]> {
    return apiClient<WasteTypeMetric[]>('/analytics/waste-types', { params });
  },

  async getLocations(params?: { start_date?: string; end_date?: string }): Promise<LocationMetric[]> {
    return apiClient<LocationMetric[]>('/analytics/locations', { params });
  },

  async getTrends(params?: { start_date?: string; end_date?: string; granularity?: 'day' | 'week' | 'month' }): Promise<TrendAnalytics> {
    return apiClient<TrendAnalytics>('/analytics/trends', { params });
  },

  async getCollections(params?: { start_date?: string; end_date?: string; location_id?: number; bin_id?: string }): Promise<CollectionAnalytics> {
    return apiClient<CollectionAnalytics>('/analytics/collections', { params });
  },

  async getBinFill(params?: { start_date?: string; end_date?: string; location_id?: number; waste_type_id?: number; bin_id?: string; threshold?: number }): Promise<BinFillAnalytics> {
    return apiClient<BinFillAnalytics>('/analytics/bin-fill', { params });
  },

  async getAlerts(params?: { threshold?: number }): Promise<AlertItem[]> {
    return apiClient<AlertItem[]>('/analytics/alerts', { params });
  },

  async getReports(params?: { start_date?: string; end_date?: string; location_id?: number }): Promise<ReportAnalytics> {
    return apiClient<ReportAnalytics>('/analytics/reports', { params });
  },

  async getProcessing(params?: { start_date?: string; end_date?: string; processing_type?: 'RECYCLING' | 'COMPOSTING'; location_id?: number; waste_type_id?: number }): Promise<ProcessingAnalytics> {
    return apiClient<ProcessingAnalytics>('/analytics/processing', { params });
  },

  async getParticipation(params?: { start_date?: string; end_date?: string }): Promise<ParticipationAnalytics> {
    return apiClient<ParticipationAnalytics>('/analytics/participation', { params });
  },

  async getGamification(params?: { start_date?: string; end_date?: string }): Promise<GamificationAnalytics> {
    return apiClient<GamificationAnalytics>('/analytics/gamification', { params });
  },

  async getPredictions(params?: { start_date?: string; end_date?: string; bin_id?: string }): Promise<PredictionAnalytics> {
    return apiClient<PredictionAnalytics>('/analytics/predictions', { params });
  },

  async getClassifications(params?: { start_date?: string; end_date?: string }): Promise<ClassificationAnalytics> {
    return apiClient<ClassificationAnalytics>('/analytics/classifications', { params });
  },
};
