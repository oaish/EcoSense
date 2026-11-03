import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LuBell, LuX, LuExternalLink } from 'react-icons/lu';
import { usePushNotifications } from '../../context/NotificationContext';

export const ForegroundNotificationBanner: React.FC = () => {
  const { foregroundAlert, clearForegroundAlert } = usePushNotifications();
  const navigate = useNavigate();

  if (!foregroundAlert) return null;

  const handleNavigate = () => {
    const targetUrl = foregroundAlert.target_url || '/';
    clearForegroundAlert();
    try {
      // If full url with origin, extract path
      const parsed = new URL(targetUrl, window.location.origin);
      if (parsed.origin === window.location.origin) {
        navigate(parsed.pathname + parsed.search + parsed.hash);
      } else {
        navigate('/');
      }
    } catch {
      navigate('/');
    }
  };

  return (
    <div
      className="fixed bottom-20 md:bottom-6 right-4 z-50 max-w-sm w-full bg-white rounded-2xl shadow-xl border border-eco-200 p-4 animate-in slide-in-from-bottom-5 duration-200"
      role="alert"
    >
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-xl bg-eco-100 text-eco-700 flex items-center justify-center shrink-0 mt-0.5">
          <LuBell className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-extrabold text-slate-900 truncate">
            {foregroundAlert.title}
          </p>
          <p className="text-xs text-slate-600 line-clamp-2 mt-0.5">
            {foregroundAlert.body}
          </p>
          <button
            onClick={handleNavigate}
            className="mt-2 text-xs font-bold text-eco-600 hover:text-eco-700 flex items-center gap-1 group"
          >
            <span>View Details</span>
            <LuExternalLink className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>
        <button
          onClick={clearForegroundAlert}
          className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors"
          aria-label="Dismiss alert"
        >
          <LuX className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
