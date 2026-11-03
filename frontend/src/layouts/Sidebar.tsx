import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LuLayoutDashboard,
  LuQrCode,
  LuBrainCircuit,
  LuTriangleAlert,
  LuGift,
  LuHistory,
  LuTrash2,
  LuMapPin,
  LuChartNoAxesCombined,
  LuRecycle,
  LuLayers,
  LuAward,
  LuTrendingUp,
  LuFileText,
  LuTrophy,
  LuUsers,
  LuLeaf,
  LuClipboardList,
  LuUserCheck,
} from 'react-icons/lu';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const role = user?.role;

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 px-4 py-3 rounded-2xl font-extrabold text-sm transition-all duration-150 select-none ${isActive
      ? 'bg-eco-500 text-white shadow-3d-green translate-y-0.5'
      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
    }`;

  return (
    <aside className="hidden lg:flex flex-col w-64 bg-white border-r border-slate-200/80 p-4 shrink-0 min-h-[calc(100vh-65px)]">
      <div className="space-y-1">
        {/* STUDENT NAV */}
        {role === 'STUDENT' && (
          <>
            <p className="px-4 text-[11px] font-black uppercase tracking-wider text-slate-400 mb-2 mt-1">
              Student Eco-Hub
            </p>
            <NavLink to="/student/dashboard" className={linkClass}>
              <LuLayoutDashboard className="w-5 h-5" />
              <span>Dashboard</span>
            </NavLink>
            <NavLink to="/scan" className={linkClass}>
              <LuQrCode className="w-5 h-5" />
              <span>Scan Bin & Earn</span>
            </NavLink>
            <NavLink to="/classify" className={linkClass}>
              <LuBrainCircuit className="w-5 h-5 text-ocean-500" />
              <span>AI Classifier</span>
            </NavLink>
            <NavLink to="/leaderboard" className={linkClass}>
              <LuTrophy className="w-5 h-5 text-amber-500" />
              <span>Eco League</span>
            </NavLink>
            <NavLink to="/rewards" className={linkClass}>
              <LuGift className="w-5 h-5" />
              <span>Rewards & Store</span>
            </NavLink>
            <NavLink to="/student/report" className={linkClass}>
              <LuTriangleAlert className="w-5 h-5" />
              <span>Report Waste</span>
            </NavLink>
            <NavLink to="/student/activity" className={linkClass}>
              <LuHistory className="w-5 h-5" />
              <span>My Activity</span>
            </NavLink>
          </>
        )}

        {/* STAFF NAV */}
        {role === 'STAFF' && (
          <>
            <p className="px-4 text-[11px] font-black uppercase tracking-wider text-slate-400 mb-2 mt-1">
              Staff Operations
            </p>
            <NavLink to="/staff/dashboard" className={linkClass}>
              <LuLayoutDashboard className="w-5 h-5" />
              <span>Overview</span>
            </NavLink>
            <NavLink to="/staff/reports" className={linkClass}>
              <LuFileText className="w-5 h-5" />
              <span>Waste Reports</span>
            </NavLink>
            <NavLink to="/staff/bins" className={linkClass}>
              <LuTrash2 className="w-5 h-5" />
              <span>Inspect Bins</span>
            </NavLink>
            <NavLink to="/classify" className={linkClass}>
              <LuBrainCircuit className="w-5 h-5 text-ocean-500" />
              <span>AI Classifier</span>
            </NavLink>
            <NavLink to="/scan" className={linkClass}>
              <LuQrCode className="w-5 h-5" />
              <span>Dispose Waste</span>
            </NavLink>
          </>
        )}

        {/* COLLECTOR NAV */}
        {role === 'COLLECTOR' && (
          <>
            <p className="px-4 text-[11px] font-black uppercase tracking-wider text-slate-400 mb-2 mt-1">
              Collection Ops
            </p>
            <NavLink to="/collector/dashboard" className={linkClass}>
              <LuLayoutDashboard className="w-5 h-5" />
              <span>Collector Hub</span>
            </NavLink>
            <NavLink to="/collector/tasks" className={linkClass}>
              <LuClipboardList className="w-5 h-5 text-amber-500" />
              <span>My Tasks</span>
            </NavLink>
            <NavLink to="/collector/scan" className={linkClass}>
              <LuQrCode className="w-5 h-5 text-eco-600" />
              <span>Scan & Collect</span>
            </NavLink>
            <NavLink to="/collector/collections" className={linkClass}>
              <LuHistory className="w-5 h-5" />
              <span>Collections Log</span>
            </NavLink>
            <NavLink to="/collector/processing" className={linkClass}>
              <LuRecycle className="w-5 h-5" />
              <span>Recycling / Compost</span>
            </NavLink>
            <NavLink to="/collector/predictions" className={linkClass}>
              <LuTrendingUp className="w-5 h-5" />
              <span>Fill Predictions</span>
            </NavLink>
          </>
        )}

        {/* ADMIN NAV */}
        {role === 'ADMIN' && (
          <>
            <p className="px-4 text-[11px] font-black uppercase tracking-wider text-slate-400 mb-2 mt-1">
              Administration
            </p>
            <NavLink to="/admin/dashboard" className={linkClass}>
              <LuLayoutDashboard className="w-5 h-5" />
              <span>Control Center</span>
            </NavLink>
            <NavLink to="/admin/collector-operations" className={linkClass}>
              <LuUserCheck className="w-5 h-5 text-eco-600" />
              <span>Collector Ops</span>
            </NavLink>
            <NavLink to="/admin/users" className={linkClass}>
              <LuUsers className="w-5 h-5 text-ocean-600" />
              <span>User Management</span>
            </NavLink>
            <NavLink to="/admin/analytics" className={linkClass}>
              <LuChartNoAxesCombined className="w-5 h-5" />
              <span>Deep Analytics</span>
            </NavLink>
            <NavLink to="/admin/bins" className={linkClass}>
              <LuTrash2 className="w-5 h-5" />
              <span>Bin Management</span>
            </NavLink>
            <NavLink to="/admin/locations" className={linkClass}>
              <LuMapPin className="w-5 h-5" />
              <span>Locations</span>
            </NavLink>
            <NavLink to="/admin/reports" className={linkClass}>
              <LuTriangleAlert className="w-5 h-5" />
              <span>Waste Reports</span>
            </NavLink>
            <NavLink to="/admin/collections" className={linkClass}>
              <LuLayers className="w-5 h-5" />
              <span>Collections Log</span>
            </NavLink>
            <NavLink to="/admin/processing" className={linkClass}>
              <LuRecycle className="w-5 h-5" />
              <span>Processing Logs</span>
            </NavLink>
            <NavLink to="/admin/rewards" className={linkClass}>
              <LuGift className="w-5 h-5" />
              <span>Rewards Catalog</span>
            </NavLink>
            <NavLink to="/admin/points" className={linkClass}>
              <LuAward className="w-5 h-5" />
              <span>Points Ledger</span>
            </NavLink>
          </>
        )}
      </div>

      {/* Sustainability Tip Footer */}
      {/* <div className="mt-auto pt-4 border-t border-slate-100">
        <div className="p-3.5 bg-eco-50 rounded-2xl border border-eco-200 text-slate-700">
          <p className="text-xs font-bold text-eco-900 flex items-center gap-1.5 mb-1">
            <LuLeaf className="w-4 h-4 text-eco-600 shrink-0" />
            <span>Zero Waste Campus</span>
          </p>
          <p className="text-[11px] font-medium text-slate-500 leading-tight">
            Every properly sorted disposal reduces campus landfill waste at DBIT.
          </p>
        </div>
      </div> */}
    </aside>
  );
};
