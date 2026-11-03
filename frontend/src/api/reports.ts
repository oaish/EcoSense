import { apiClient } from './client';
import { ReportCreate, ReportUpdate, WasteReport } from '../types';

export const reportsApi = {
  async submitReport(data: ReportCreate): Promise<WasteReport> {
    return apiClient<WasteReport>('/reports', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getReports(params?: {
    status?: string;
    report_type?: string;
    bin_id?: string;
    user_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<WasteReport[]> {
    return apiClient<WasteReport[]>('/reports', { params });
  },

  async getReportById(reportId: number): Promise<WasteReport> {
    return apiClient<WasteReport>(`/reports/${reportId}`);
  },

  async updateReport(reportId: number, data: ReportUpdate): Promise<WasteReport> {
    return apiClient<WasteReport>(`/reports/${reportId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },
};
