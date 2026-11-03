import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { NotificationProvider, usePushNotifications } from '../context/NotificationContext';
import { NotificationSettingsModal } from '../components/common/NotificationSettingsModal';
import { ForegroundNotificationBanner } from '../components/common/ForegroundNotificationBanner';
import { notificationsApi } from '../api/notifications';
import * as firebaseUtils from '../utils/firebase';

// Mock AuthContext
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: {
      user_id: 'user_123',
      name: 'Test Student',
      email: 'student@dbit.in',
      role: 'STUDENT',
    },
    logout: vi.fn(),
  }),
}));

// Mock notificationsApi
vi.mock('../api/notifications', () => ({
  notificationsApi: {
    getPreferences: vi.fn().mockResolvedValue({
      push_notifications_enabled: true,
      active_device_count: 1,
    }),
    registerDeviceToken: vi.fn().mockResolvedValue({
      token_id: 1,
      device_name: 'Desktop Browser',
      is_active: true,
      created_at: '2026-10-13T00:00:00Z',
      updated_at: '2026-10-13T00:00:00Z',
    }),
    unregisterDeviceToken: vi.fn().mockResolvedValue({
      success: true,
      message: 'Disassociated',
    }),
    updatePreferences: vi.fn().mockResolvedValue({
      push_notifications_enabled: true,
      active_device_count: 1,
    }),
    sendTestPush: vi.fn().mockResolvedValue({
      status: 'SENT_OR_ACCEPTED',
      devices_targeted: 1,
      success_count: 1,
      failure_count: 0,
      message: 'Test notification delivered successfully.',
    }),
  },
}));

describe('Firebase Web Push Frontend Components & Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('renders NotificationSettingsModal with permission and token status', async () => {
    render(
      <BrowserRouter>
        <NotificationProvider>
          <NotificationSettingsModal isOpen={true} onClose={vi.fn()} />
        </NotificationProvider>
      </BrowserRouter>
    );

    expect(screen.getByText('Notification Settings')).toBeDefined();
    expect(screen.getByText(/Manage operational push alerts on this device/i)).toBeDefined();
    expect(screen.getByText(/Browser Permission/i)).toBeDefined();
    expect(screen.getByText(/FCM Device Token/i)).toBeDefined();
  });

  it('handles enable push notifications and registers token with backend', async () => {
    vi.spyOn(firebaseUtils, 'isPushNotificationSupported').mockReturnValue(true);
    vi.spyOn(firebaseUtils, 'isFirebaseConfigured').mockReturnValue(true);
    vi.spyOn(firebaseUtils, 'requestFcmToken').mockResolvedValue('mock_fcm_token_xyz_123');

    render(
      <BrowserRouter>
        <NotificationProvider>
          <NotificationSettingsModal isOpen={true} onClose={vi.fn()} />
        </NotificationProvider>
      </BrowserRouter>
    );

    const enableBtn = screen.getByRole('button', { name: /Enable Push/i });
    fireEvent.click(enableBtn);

    await waitFor(() => {
      expect(notificationsApi.registerDeviceToken).toHaveBeenCalledWith(
        'mock_fcm_token_xyz_123',
        expect.stringContaining('Browser')
      );
      expect(notificationsApi.updatePreferences).toHaveBeenCalledWith(true);
    });
  });

  it('disables notifications and unregisters device token', async () => {
    localStorage.setItem('ecosense_fcm_token', 'active_fcm_token_abc');
    vi.spyOn(firebaseUtils, 'isPushNotificationSupported').mockReturnValue(true);
    vi.spyOn(firebaseUtils, 'isFirebaseConfigured').mockReturnValue(true);

    render(
      <BrowserRouter>
        <NotificationProvider>
          <NotificationSettingsModal isOpen={true} onClose={vi.fn()} />
        </NotificationProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      const disableBtn = screen.getByRole('button', { name: /Disable/i });
      expect(disableBtn).toBeDefined();
      fireEvent.click(disableBtn);
    });

    await waitFor(() => {
      expect(notificationsApi.unregisterDeviceToken).toHaveBeenCalledWith('active_fcm_token_abc');
      expect(notificationsApi.updatePreferences).toHaveBeenCalledWith(false);
    });
  });

  it('sends test push notification and displays outcome feedback', async () => {
    localStorage.setItem('ecosense_fcm_token', 'active_fcm_token_abc');

    render(
      <BrowserRouter>
        <NotificationProvider>
          <NotificationSettingsModal isOpen={true} onClose={vi.fn()} />
        </NotificationProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      const testBtn = screen.getByRole('button', { name: /Send Test Alert/i });
      expect(testBtn).toBeDefined();
      fireEvent.click(testBtn);
    });

    await waitFor(() => {
      expect(notificationsApi.sendTestPush).toHaveBeenCalled();
      expect(screen.getByText(/Test notification delivered successfully/i)).toBeDefined();
    });
  });
});
