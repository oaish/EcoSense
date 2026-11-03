import { apiClient } from './client';

export interface DeviceTokenResponse {
  token_id: number;
  device_name?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationPreferences {
  push_notifications_enabled: boolean;
  active_device_count: number;
}

export interface NotificationHistoryItem {
  notification_id: number;
  task_id?: number | null;
  report_id?: number | null;
  recipient_user_id: string;
  channel: string;
  notification_type?: string | null;
  title?: string | null;
  body?: string | null;
  status: string;
  created_at: string;
}

export interface PushTestResult {
  status: string;
  devices_targeted: number;
  success_count: number;
  failure_count: number;
  message: string;
}

export const notificationsApi = {
  registerDeviceToken: (fcm_token: string, device_name?: string): Promise<DeviceTokenResponse> => {
    return apiClient<DeviceTokenResponse>('/notifications/tokens', {
      method: 'POST',
      body: JSON.stringify({ fcm_token, device_name }),
    });
  },

  unregisterDeviceToken: (fcm_token: string): Promise<{ success: boolean; message: string }> => {
    return apiClient<{ success: boolean; message: string }>('/notifications/tokens', {
      method: 'DELETE',
      body: JSON.stringify({ fcm_token }),
    });
  },

  getPreferences: (): Promise<NotificationPreferences> => {
    return apiClient<NotificationPreferences>('/notifications/preferences', {
      method: 'GET',
    });
  },

  updatePreferences: (push_notifications_enabled: boolean): Promise<NotificationPreferences> => {
    return apiClient<NotificationPreferences>('/notifications/preferences', {
      method: 'PUT',
      body: JSON.stringify({ push_notifications_enabled }),
    });
  },

  sendTestPush: (payload?: { title?: string; body?: string; target_url?: string }): Promise<PushTestResult> => {
    return apiClient<PushTestResult>('/notifications/test', {
      method: 'POST',
      body: JSON.stringify(payload || {}),
    });
  },

  getHistory: (skip = 0, limit = 50): Promise<NotificationHistoryItem[]> => {
    return apiClient<NotificationHistoryItem[]>('/notifications/history', {
      method: 'GET',
      params: { skip, limit },
    });
  },
};
