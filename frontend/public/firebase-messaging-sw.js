// EcoSense Web Push Background Service Worker
// DBIT Mumbai - EcoSense AI-Based Zero Waste Campus Management Platform

// Give the service worker access to Firebase Messaging.
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js');

// Self-contained public Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDh9gifE03OIwUoKP1ARwvdLEoaNneBMao",
  authDomain: "ecosense-98229.firebaseapp.com",
  projectId: "ecosense-98229",
  storageBucket: "ecosense-98229.firebasestorage.app",
  messagingSenderId: "237010630633",
  appId: "1:237010630633:web:6919b6bc7af6e869933d78"
};

try {
  firebase.initializeApp(firebaseConfig);

  const messaging = firebase.messaging();

  messaging.onBackgroundMessage((payload) => {
    const title = payload.notification?.title || payload.data?.title || 'EcoSense Update';
    const body = payload.notification?.body || payload.data?.body || 'New operational update on campus.';
    const targetUrl = payload.data?.target_url || payload.fcmOptions?.link || '/';

    const notificationOptions = {
      body: body,
      icon: '/leaf.svg',
      badge: '/leaf.svg',
      data: {
        target_url: targetUrl,
        timestamp: Date.now(),
      },
      tag: payload.data?.event_type || 'ecosense-notification',
      renotify: true,
      requireInteraction: false,
    };

    return self.registration.showNotification(title, notificationOptions);
  });
} catch (e) {
  // Graceful fallback to native Web Push listener
}

// Native Push Event Fallback (for direct webpush delivery)
self.addEventListener('push', (event) => {
  if (!event.data) return;

  try {
    const data = event.data.json();
    const title = data.notification?.title || data.title || 'EcoSense Update';
    const body = data.notification?.body || data.body || 'Campus waste management notification.';
    const targetUrl = data.data?.target_url || data.target_url || '/';

    event.waitUntil(
      self.registration.showNotification(title, {
        body: body,
        icon: '/leaf.svg',
        badge: '/leaf.svg',
        data: { target_url: targetUrl },
        tag: data.event_type || 'ecosense-push',
      })
    );
  } catch (err) {
    // Plain text push payload
    const text = event.data.text();
    event.waitUntil(
      self.registration.showNotification('EcoSense Notification', {
        body: text,
        icon: '/leaf.svg',
        badge: '/leaf.svg',
        data: { target_url: '/' },
      })
    );
  }
});

// Notification Click Handler: Safely Focus or Open Internal Application Routes
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  const rawUrl = event.notification.data?.target_url || '/';

  // Security: only allow navigation to relative paths or current origin
  let targetUrl = '/';
  try {
    const parsed = new URL(rawUrl, self.location.origin);
    if (parsed.origin === self.location.origin) {
      targetUrl = parsed.pathname + parsed.search + parsed.hash;
    }
  } catch {
    targetUrl = '/';
  }

  const destination = new URL(targetUrl, self.location.origin).href;

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      // If a window is already open on this origin, focus it and navigate
      for (const client of clientList) {
        if (client.url && 'focus' in client) {
          if ('navigate' in client) {
            client.navigate(destination);
          }
          return client.focus();
        }
      }
      // If no window is currently open, open a new window
      if (clients.openWindow) {
        return clients.openWindow(destination);
      }
    })
  );
});
