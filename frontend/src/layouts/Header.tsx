import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { usePushNotifications } from '../context/NotificationContext';
import { LuLogOut, LuLeaf, LuShield, LuBriefcase, LuTruck, LuGraduationCap, LuBell } from 'react-icons/lu';
import { Link, useNavigate } from 'react-router-dom';
import { NotificationSettingsModal } from '../components/common/NotificationSettingsModal';

export const Header: React.FC<{ onMenuToggle?: () => void }> = () => {
  const { user, logout } = useAuth();
  const { token, preferences } = usePushNotifications();
  const [showNotificationModal, setShowNotificationModal] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getRoleInfo = (role?: string) => {
    switch (role) {
      case 'ADMIN':
        return {
          color: 'bg-purple-100 text-purple-800 border-purple-200',
          Icon: LuShield,
        };
      case 'STAFF':
        return {
          color: 'bg-blue-100 text-blue-800 border-blue-200',
          Icon: LuBriefcase,
        };
      case 'COLLECTOR':
        return {
          color: 'bg-amber-100 text-amber-800 border-amber-200',
          Icon: LuTruck,
        };
      case 'STUDENT':
      default:
        return {
          color: 'bg-eco-100 text-eco-800 border-eco-200',
          Icon: LuGraduationCap,
        };
    }
  };

  const roleInfo = getRoleInfo(user?.role);

  return (
    <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-200/80 px-4 lg:px-8 py-3.5 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand & Institution */}
        <div className="flex items-center gap-3">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-2xl bg-eco-500 text-white flex items-center justify-center shadow-3d-green group-hover:scale-105 transition-transform">
              <LuLeaf className="w-5 h-5" />
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight text-slate-900 flex items-center gap-1">
                EcoSense
                <span className="text-eco-600">.</span>
              </span>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 -mt-1">
                DBIT Mumbai
              </p>
            </div>
          </Link>
        </div>

        {/* User Profile & Actions */}
        {user && (
          <div className="flex items-center gap-3">
            {/* Role Badge */}
            <span
              className={`hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider border ${roleInfo.color}`}
            >
              <roleInfo.Icon className="w-3.5 h-3.5" />
              <span>{user.role}</span>
            </span>

            {/* Profile Pill */}
            <div className="flex items-center gap-2.5 bg-slate-50 border border-slate-200/80 rounded-2xl px-3 py-1.5 shadow-xs">
              <div className="w-7 h-7 rounded-xl bg-eco-200 text-eco-800 flex items-center justify-center font-black text-xs">
                {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
              </div>
              <div className="hidden md:block text-left">
                <p className="text-xs font-extrabold text-slate-800 leading-none">{user.name}</p>
                <p className="text-[10px] font-medium text-slate-400 leading-tight truncate max-w-[120px]">
                  {user.email}
                </p>
              </div>
            </div>

            {/* Notification Settings Button */}
            <button
              onClick={() => setShowNotificationModal(true)}
              title="Notification Settings"
              aria-label="Notification Settings"
              className="relative p-2 rounded-2xl text-slate-500 hover:text-eco-600 hover:bg-eco-50 border border-slate-200/80 hover:border-eco-200 transition-all active:scale-95"
            >
              <LuBell className="w-5 h-5" />
              {token && preferences?.push_notifications_enabled && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-eco-500 ring-2 ring-white" />
              )}
            </button>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              title="Sign Out"
              aria-label="Sign Out"
              className="p-2 rounded-2xl text-slate-400 hover:text-coral-600 hover:bg-coral-50 border border-transparent hover:border-coral-200 transition-all active:scale-95"
            >
              <LuLogOut className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>

      {/* Notification Settings Modal */}
      <NotificationSettingsModal
        isOpen={showNotificationModal}
        onClose={() => setShowNotificationModal(false)}
      />
    </header>
  );
};
