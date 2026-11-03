import React, { useState } from 'react';
import {
  LuBell,
  LuBellOff,
  LuCheck,
  LuCircleAlert,
  LuSmartphone,
  LuSend,
  LuInfo,
  LuX,
  LuShieldCheck,
  LuLoader,
} from 'react-icons/lu';
import { usePushNotifications } from '../../context/NotificationContext';

interface NotificationSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationSettingsModal: React.FC<NotificationSettingsModalProps> = ({
  isOpen,
  onClose,
}) => {
  const {
    isSupported,
    isConfigured,
    permission,
    token,
    preferences,
    loading,
    error,
    enableNotifications,
    disableNotifications,
    sendTestPush,
  } = usePushNotifications();

  const [testResult, setTestResult] = useState<string | null>(null);
  const [testing, setTesting] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleToggleEnable = async () => {
    setTestResult(null);
    if (token && preferences?.push_notifications_enabled) {
      await disableNotifications();
    } else {
      await enableNotifications();
    }
  };

  const handleTestNotification = async () => {
    setTesting(true);
    setTestResult(null);
    const res = await sendTestPush();
    setTestResult(res.message);
    setTesting(false);
  };

  const isEnabled = Boolean(token && preferences?.push_notifications_enabled);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-in fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="notification-settings-title"
    >
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 overflow-hidden relative">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-eco-50 text-eco-600 flex items-center justify-center border border-eco-100">
              <LuBell className="w-5 h-5" />
            </div>
            <div>
              <h2 id="notification-settings-title" className="text-lg font-extrabold text-slate-900">
                Notification Settings
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                Manage operational push alerts on this device
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 rounded-xl hover:bg-slate-50 transition-colors"
            aria-label="Close modal"
          >
            <LuX className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="py-5 space-y-5">
          {/* Status Banners */}
          {!isSupported && (
            <div className="p-3.5 bg-amber-50 border border-amber-200 rounded-2xl flex items-start gap-3">
              <LuCircleAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div className="text-xs text-amber-800">
                <p className="font-bold">Browser Push Unsupported</p>
                <p>This browser does not support Web Push notifications or Service Workers.</p>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3.5 bg-coral-50 border border-coral-200 rounded-2xl flex items-start gap-3">
              <LuCircleAlert className="w-5 h-5 text-coral-600 shrink-0 mt-0.5" />
              <div className="text-xs text-coral-800">
                <p className="font-bold">Notification Error</p>
                <p>{error}</p>
              </div>
            </div>
          )}

          {/* Operational explanation */}
          <div className="p-3.5 bg-slate-50 border border-slate-200/80 rounded-2xl text-xs text-slate-600 space-y-1.5">
            <div className="flex items-center gap-2 font-bold text-slate-800">
              <LuInfo className="w-4 h-4 text-eco-600" />
              Operational Updates Delivered
            </div>
            <p>
              EcoSense dispatches push notifications for real-time task assignments, waste-report resolution updates, and campus response alerts.
            </p>
          </div>

          {/* Device & Permission Status Cards */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 bg-surface-50 border border-slate-200/80 rounded-2xl">
              <span className="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">
                Browser Permission
              </span>
              <div className="flex items-center gap-1.5 mt-1">
                {permission === 'granted' ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span className="text-xs font-extrabold text-emerald-700">Granted</span>
                  </>
                ) : permission === 'denied' ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-coral-500" />
                    <span className="text-xs font-extrabold text-coral-700">Blocked</span>
                  </>
                ) : (
                  <>
                    <span className="w-2 h-2 rounded-full bg-amber-500" />
                    <span className="text-xs font-extrabold text-amber-700">Not Prompted</span>
                  </>
                )}
              </div>
            </div>

            <div className="p-3.5 bg-surface-50 border border-slate-200/80 rounded-2xl">
              <span className="text-[10px] uppercase font-bold text-slate-400 block tracking-wider">
                FCM Device Token
              </span>
              <div className="flex items-center gap-1.5 mt-1">
                {token ? (
                  <>
                    <LuShieldCheck className="w-3.5 h-3.5 text-eco-600" />
                    <span className="text-xs font-extrabold text-eco-800">Registered</span>
                  </>
                ) : (
                  <>
                    <LuSmartphone className="w-3.5 h-3.5 text-slate-400" />
                    <span className="text-xs font-extrabold text-slate-500">Not Registered</span>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Permission Blocked Guidance */}
          {permission === 'denied' && (
            <div className="p-3.5 bg-amber-50 border border-amber-200 rounded-2xl text-xs text-amber-900 space-y-1">
              <p className="font-bold">Notifications Blocked by Browser</p>
              <p>
                To enable notifications, click the lock/settings icon in your browser address bar, change Notifications from &quot;Block&quot; to &quot;Allow&quot;, and refresh the page.
              </p>
            </div>
          )}

          {/* Push Toggle Control */}
          <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-2xl flex items-center justify-between">
            <div className="space-y-0.5">
              <p className="text-xs font-extrabold text-slate-900">Push Notifications</p>
              <p className="text-[11px] text-slate-500">
                {isEnabled ? 'Active and receiving campus alerts' : 'Disabled for this browser'}
              </p>
            </div>
            <button
              onClick={handleToggleEnable}
              disabled={loading || !isSupported}
              className={`px-4 py-2 rounded-xl text-xs font-extrabold transition-all flex items-center gap-1.5 active:scale-95 ${
                isEnabled
                  ? 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                  : 'bg-eco-600 text-white hover:bg-eco-700 shadow-3d-green'
              } disabled:opacity-50`}
            >
              {loading ? (
                <LuLoader className="w-3.5 h-3.5 animate-spin" />
              ) : isEnabled ? (
                <>
                  <LuBellOff className="w-3.5 h-3.5" />
                  Disable
                </>
              ) : (
                <>
                  <LuBell className="w-3.5 h-3.5" />
                  Enable Push
                </>
              )}
            </button>
          </div>

          {/* Test Notification Section */}
          {isEnabled && (
            <div className="pt-2">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-extrabold text-slate-800">Verify Push Delivery</p>
                  <p className="text-[11px] text-slate-500">
                    Send a test payload to your registered devices
                  </p>
                </div>
                <button
                  onClick={handleTestNotification}
                  disabled={testing}
                  className="px-3.5 py-1.5 border border-slate-200 hover:border-slate-300 bg-white text-slate-700 text-xs font-bold rounded-xl flex items-center gap-1.5 hover:bg-slate-50 transition-colors disabled:opacity-50"
                >
                  {testing ? (
                    <LuLoader className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <LuSend className="w-3.5 h-3.5 text-eco-600" />
                  )}
                  Send Test Alert
                </button>
              </div>

              {testResult && (
                <p className="mt-2 text-xs text-eco-700 font-medium bg-eco-50 p-2.5 rounded-xl border border-eco-200 flex items-center gap-1.5">
                  <LuCheck className="w-4 h-4 text-eco-600 shrink-0" />
                  {testResult}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-extrabold transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
