import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import {
  isPushNotificationSupported,
  isFirebaseConfigured,
  requestFcmToken,
  onForegroundMessage,
} from '../utils/firebase';
import { notificationsApi, NotificationPreferences } from '../api/notifications';

export interface ForegroundNotificationData {
  title: string;
  body: string;
  target_url?: string;
  timestamp: number;
}

interface NotificationContextType {
  isSupported: boolean;
  isConfigured: boolean;
  permission: NotificationPermission | 'unsupported';
  token: string | null;
  preferences: NotificationPreferences | null;
  loading: boolean;
  error: string | null;
  foregroundAlert: ForegroundNotificationData | null;
  enableNotifications: () => Promise<boolean>;
  disableNotifications: () => Promise<boolean>;
  sendTestPush: () => Promise<{ success: boolean; message: string }>;
  clearForegroundAlert: () => void;
  refreshPreferences: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

const TOKEN_STORAGE_KEY = 'ecosense_fcm_token';

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [isSupported] = useState<boolean>(() => isPushNotificationSupported());
  const [isConfigured] = useState<boolean>(() => isFirebaseConfigured());

  const [permission, setPermission] = useState<NotificationPermission | 'unsupported'>(() => {
    if (typeof window === 'undefined' || !('Notification' in window)) return 'unsupported';
    return Notification.permission;
  });

  const [token, setToken] = useState<string | null>(() => {
    try {
      return localStorage.getItem(TOKEN_STORAGE_KEY);
    } catch {
      return null;
    }
  });

  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [foregroundAlert, setForegroundAlert] = useState<ForegroundNotificationData | null>(null);

  const clearForegroundAlert = useCallback(() => {
    setForegroundAlert(null);
  }, []);

  const refreshPreferences = useCallback(async () => {
    if (!user) {
      setPreferences(null);
      return;
    }
    try {
      const prefs = await notificationsApi.getPreferences();
      setPreferences(prefs);
    } catch (err) {
      // Backend may not have tokens endpoint configured yet or network error
    }
  }, [user]);

  // Synchronize on user login / logout
  useEffect(() => {
    if (user) {
      refreshPreferences();
    } else {
      // Disassociate token on logout
      const currentToken = localStorage.getItem(TOKEN_STORAGE_KEY);
      if (currentToken) {
        notificationsApi.unregisterDeviceToken(currentToken).catch(() => {});
        try {
          localStorage.removeItem(TOKEN_STORAGE_KEY);
        } catch {}
      }
      setToken(null);
      setPreferences(null);
    }
  }, [user, refreshPreferences]);

  // Setup foreground listener
  useEffect(() => {
    if (!isConfigured || !isSupported) return;

    const unsubscribe = onForegroundMessage((payload) => {
      const title = payload.notification?.title || payload.data?.title || 'EcoSense Update';
      const body = payload.notification?.body || payload.data?.body || 'New operational update.';
      const target_url = payload.data?.target_url || payload.fcmOptions?.link || '/';

      setForegroundAlert({
        title,
        body,
        target_url,
        timestamp: Date.now(),
      });
    });

    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, [isConfigured, isSupported]);

  const enableNotifications = async (): Promise<boolean> => {
    setError(null);
    setLoading(true);

    try {
      if (!isSupported) {
        throw new Error('Push notifications are not supported in this browser.');
      }

      if (!isFirebaseConfigured()) {
        throw new Error('Firebase web push configuration is not set up in environment variables.');
      }

      const fcmToken = await requestFcmToken();
      if (!fcmToken) {
        const currentPerm = typeof window !== 'undefined' && 'Notification' in window
          ? Notification.permission
          : 'denied';
        setPermission(currentPerm);
        if (currentPerm === 'denied') {
          setError('Notification permission was blocked in browser settings. Please enable notifications in your browser address bar.');
        }
        return false;
      }

      setPermission('granted');
      setToken(fcmToken);
      try {
        localStorage.setItem(TOKEN_STORAGE_KEY, fcmToken);
      } catch {}

      // Register with FastAPI backend
      const deviceName = `${navigator.userAgent.includes('Mobile') ? 'Mobile' : 'Desktop'} Browser`;
      await notificationsApi.registerDeviceToken(fcmToken, deviceName);
      await notificationsApi.updatePreferences(true);
      await refreshPreferences();

      return true;
    } catch (err: any) {
      console.error('Failed to enable notifications:', err);
      setError(err?.message || 'Failed to activate web push notifications.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const disableNotifications = async (): Promise<boolean> => {
    setError(null);
    setLoading(true);

    try {
      const currentToken = token || localStorage.getItem(TOKEN_STORAGE_KEY);
      if (currentToken) {
        await notificationsApi.unregisterDeviceToken(currentToken).catch(() => {});
        try {
          localStorage.removeItem(TOKEN_STORAGE_KEY);
        } catch {}
        setToken(null);
      }

      await notificationsApi.updatePreferences(false);
      await refreshPreferences();
      return true;
    } catch (err: any) {
      console.error('Failed to disable notifications:', err);
      setError(err?.message || 'Failed to disable notifications.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const sendTestPush = async (): Promise<{ success: boolean; message: string }> => {
    setError(null);
    setLoading(true);
    try {
      const res = await notificationsApi.sendTestPush({
        title: 'EcoSense Push Verification',
        body: 'Push notifications are working smoothly on DBIT EcoSense!',
      });
      return {
        success: res.status === 'SENT_OR_ACCEPTED',
        message: res.message || 'Test push notification dispatched.',
      };
    } catch (err: any) {
      const msg = err?.message || 'Failed to dispatch test notification.';
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  };

  return (
    <NotificationContext.Provider
      value={{
        isSupported,
        isConfigured,
        permission,
        token,
        preferences,
        loading,
        error,
        foregroundAlert,
        enableNotifications,
        disableNotifications,
        sendTestPush,
        clearForegroundAlert,
        refreshPreferences,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const usePushNotifications = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('usePushNotifications must be used within a NotificationProvider');
  }
  return context;
};
