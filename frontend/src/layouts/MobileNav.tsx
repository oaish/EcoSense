import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LuLayoutDashboard,
  LuQrCode,
  LuBrainCircuit,
  LuGift,
  LuTriangleAlert,
  LuHistory,
  LuTrash2,
  LuChartNoAxesCombined,
  LuRecycle,
  LuTrophy,
  LuUsers,
  LuFileText,
  LuClipboardList,
  LuUserCheck,
} from 'react-icons/lu';

export const MobileNav: React.FC = () => {
  const { user } = useAuth();
  const role = user?.role;

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex flex-col items-center justify-center flex-1 py-2 font-black text-[10px] transition-all duration-100 select-none ${
      isActive ? 'text-eco-600 font-extrabold scale-105' : 'text-slate-500 hover:text-slate-800'
    }`;

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-md border-t border-slate-200 px-2 py-1 shadow-lg flex items-center justify-around">
      {role === 'STUDENT' && (
        <>
          <NavLink to="/student/dashboard" className={linkClass}>
            <LuLayoutDashboard className="w-5 h-5 mb-0.5" />
            <span>Home</span>
          </NavLink>
          <NavLink to="/classify" className={linkClass}>
            <LuBrainCircuit className="w-5 h-5 mb-0.5 text-ocean-600" />
            <span>AI Assist</span>
          </NavLink>
          <NavLink to="/scan" className={linkClass}>
            <div className="w-11 h-11 -mt-5 rounded-full bg-eco-500 text-white flex items-center justify-center shadow-3d-green border-2 border-white">
              <LuQrCode className="w-6 h-6" />
            </div>
            <span className="mt-1">Scan</span>
          </NavLink>
          <NavLink to="/leaderboard" className={linkClass}>
            <LuTrophy className="w-5 h-5 mb-0.5 text-amber-500" />
            <span>League</span>
          </NavLink>
          <NavLink to="/rewards" className={linkClass}>
            <LuGift className="w-5 h-5 mb-0.5" />
            <span>Rewards</span>
          </NavLink>
        </>
      )}

      {role === 'STAFF' && (
        <>
          <NavLink to="/staff/dashboard" className={linkClass}>
            <LuLayoutDashboard className="w-5 h-5 mb-0.5" />
            <span>Overview</span>
          </NavLink>
          <NavLink to="/staff/reports" className={linkClass}>
            <LuFileText className="w-5 h-5 mb-0.5" />
            <span>Reports</span>
          </NavLink>
          <NavLink to="/scan" className={linkClass}>
            <div className="w-11 h-11 -mt-5 rounded-full bg-eco-500 text-white flex items-center justify-center shadow-3d-green border-2 border-white">
              <LuQrCode className="w-6 h-6" />
            </div>
            <span className="mt-1">Dispose</span>
          </NavLink>
          <NavLink to="/staff/bins" className={linkClass}>
            <LuTrash2 className="w-5 h-5 mb-0.5" />
            <span>Bins</span>
          </NavLink>
          <NavLink to="/classify" className={linkClass}>
            <LuBrainCircuit className="w-5 h-5 mb-0.5 text-ocean-600" />
            <span>AI</span>
          </NavLink>
        </>
      )}

      {role === 'COLLECTOR' && (
        <>
          <NavLink to="/collector/dashboard" className={linkClass}>
            <LuLayoutDashboard className="w-5 h-5 mb-0.5" />
            <span>Hub</span>
          </NavLink>
          <NavLink to="/collector/tasks" className={linkClass}>
            <LuClipboardList className="w-5 h-5 mb-0.5 text-amber-500" />
            <span>Tasks</span>
          </NavLink>
          <NavLink to="/collector/scan" className={linkClass}>
            <div className="w-11 h-11 -mt-5 rounded-full bg-eco-500 text-white flex items-center justify-center shadow-3d-green border-2 border-white">
              <LuQrCode className="w-6 h-6" />
            </div>
            <span className="mt-1">Collect</span>
          </NavLink>
          <NavLink to="/collector/collections" className={linkClass}>
            <LuHistory className="w-5 h-5 mb-0.5" />
            <span>History</span>
          </NavLink>
        </>
      )}

      {role === 'ADMIN' && (
        <>
          <NavLink to="/admin/dashboard" className={linkClass}>
            <LuLayoutDashboard className="w-5 h-5 mb-0.5" />
            <span>Overview</span>
          </NavLink>
          <NavLink to="/admin/collector-operations" className={linkClass}>
            <LuUserCheck className="w-5 h-5 mb-0.5 text-eco-600" />
            <span>Ops</span>
          </NavLink>
          <NavLink to="/admin/users" className={linkClass}>
            <LuUsers className="w-5 h-5 mb-0.5 text-ocean-600" />
            <span>Users</span>
          </NavLink>
          <NavLink to="/admin/analytics" className={linkClass}>
            <LuChartNoAxesCombined className="w-5 h-5 mb-0.5" />
            <span>Analytics</span>
          </NavLink>
          <NavLink to="/admin/bins" className={linkClass}>
            <LuTrash2 className="w-5 h-5 mb-0.5" />
            <span>Bins</span>
          </NavLink>
          <NavLink to="/admin/rewards" className={linkClass}>
            <LuGift className="w-5 h-5 mb-0.5" />
            <span>Rewards</span>
          </NavLink>
        </>
      )}
    </nav>
  );
};
