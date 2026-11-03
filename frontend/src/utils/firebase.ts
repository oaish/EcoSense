// Firebase Web Client Configuration & Push Notification Utilities

import { initializeApp, getApps, FirebaseApp } from 'firebase/app';
import { getMessaging, getToken, onMessage, Messaging } from 'firebase/messaging';

// Public Firebase Web App Configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || 'AIzaSyDh9gifE03OIwUoKP1ARwvdLEoaNneBMao',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'ecosense-98229.firebaseapp.com',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || 'ecosense-98229',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 'ecosense-98229.firebasestorage.app',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '237010630633',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '1:237010630633:web:6919b6bc7af6e869933d78',
};

export const VAPID_KEY = import.meta.env.VITE_FIREBASE_VAPID_KEY;

export function isFirebaseConfigured(): boolean {
  return Boolean(
    firebaseConfig.apiKey &&
    firebaseConfig.projectId &&
    firebaseConfig.messagingSenderId &&
    firebaseConfig.appId
  );
}

let appInstance: FirebaseApp | null = null;
let messagingInstance: Messaging | null = null;

export function getFirebaseApp(): FirebaseApp | null {
  if (!isFirebaseConfigured()) {
    return null;
  }
  if (!appInstance) {
    const existing = getApps();
    if (existing.length > 0) {
      appInstance = existing[0];
    } else {
      appInstance = initializeApp(firebaseConfig);
    }
  }
  return appInstance;
}

export function isPushNotificationSupported(): boolean {
  return (
    typeof window !== 'undefined' &&
    'Notification' in window &&
    'serviceWorker' in navigator &&
    'PushManager' in window
  );
}

export function getFirebaseMessaging(): Messaging | null {
  if (!isPushNotificationSupported() || !isFirebaseConfigured()) {
    return null;
  }
  if (!messagingInstance) {
    const app = getFirebaseApp();
    if (app) {
      try {
        messagingInstance = getMessaging(app);
      } catch (err) {
        console.warn('Firebase Messaging initialization failed:', err);
        return null;
      }
    }
  }
  return messagingInstance;
}

/**
 * Registers the background service worker and requests an FCM device token.
 */
export async function requestFcmToken(): Promise<string | null> {
  if (!isPushNotificationSupported()) {
    throw new Error('Push notifications are not supported in this browser.');
  }

  if (!isFirebaseConfigured()) {
    throw new Error('Firebase web configuration is not configured in this environment.');
  }

  // 1. Request user permission
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') {
    return null;
  }

  // 2. Register Firebase Messaging Service Worker
  let registration: ServiceWorkerRegistration;
  try {
    registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js', {
      scope: '/',
    });
    await navigator.serviceWorker.ready;
  } catch (swErr) {
    console.error('Service worker registration failed:', swErr);
    throw new Error('Failed to register service worker for background push notifications.');
  }

  // 3. Get FCM token with public VAPID key
  const messaging = getFirebaseMessaging();
  if (!messaging) {
    throw new Error('Failed to initialize Firebase Messaging instance.');
  }

  try {
    const token = await getToken(messaging, {
      vapidKey: VAPID_KEY || undefined,
      serviceWorkerRegistration: registration,
    });
    return token;
  } catch (tokenErr) {
    console.error('Failed to obtain FCM registration token:', tokenErr);
    throw tokenErr;
  }
}

/**
 * Listens for incoming foreground messages when the EcoSense app tab is open.
 */
export function onForegroundMessage(callback: (payload: any) => void): (() => void) | null {
  const messaging = getFirebaseMessaging();
  if (!messaging) return null;

  try {
    return onMessage(messaging, (payload) => {
      callback(payload);
    });
  } catch (err) {
    console.warn('Could not register foreground message listener:', err);
    return null;
  }
}
