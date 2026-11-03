import React from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { MobileNav } from './MobileNav';
import { ForegroundNotificationBanner } from '../components/common/ForegroundNotificationBanner';

export const AppShell: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-surface-50 text-slate-800">
      <Header />
      <div className="flex-1 flex max-w-7xl w-full mx-auto">
        <Sidebar />
        <main className="flex-1 p-4 md:p-6 lg:p-8 pb-24 lg:pb-12 overflow-x-hidden min-w-0">
          <Outlet />
        </main>
      </div>
      <MobileNav />
      <ForegroundNotificationBanner />
    </div>
  );
};
