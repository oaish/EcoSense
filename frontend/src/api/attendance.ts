import { apiClient } from './client';
import { AttendanceRecord, AdminAttendanceOverview } from '../types';

export const attendanceApi = {
  async checkIn(notes?: string): Promise<AttendanceRecord> {
    return apiClient<AttendanceRecord>('/attendance/check-in', {
      method: 'POST',
      body: JSON.stringify(notes ? { notes } : {}),
    });
  },

  async checkOut(notes?: string): Promise<AttendanceRecord> {
    return apiClient<AttendanceRecord>('/attendance/check-out', {
      method: 'POST',
      body: JSON.stringify(notes ? { notes } : {}),
    });
  },

  async getMyActiveShift(): Promise<AttendanceRecord | null> {
    return apiClient<AttendanceRecord | null>('/attendance/me');
  },

  async getMyHistory(): Promise<AttendanceRecord[]> {
    return apiClient<AttendanceRecord[]>('/attendance/me/history');
  },

  async getAdminOverview(targetDate?: string): Promise<AdminAttendanceOverview> {
    return apiClient<AdminAttendanceOverview>('/attendance/admin/overview', {
      params: targetDate ? { target_date: targetDate } : undefined,
    });
  },

  async getCollectorHistory(collectorId: string): Promise<AttendanceRecord[]> {
    return apiClient<AttendanceRecord[]>(`/attendance/admin/collector/${collectorId}`);
  },

  async updateCollectorPhone(collectorId: string, phoneNumber: string | null): Promise<void> {
    return apiClient<void>(`/users/${collectorId}/phone`, {
      method: 'PATCH',
      body: JSON.stringify({ phone_number: phoneNumber }),
    });
  },
};
