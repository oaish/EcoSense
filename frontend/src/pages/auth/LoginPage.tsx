import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { getRoleDefaultPath } from '../../routes/RoleRoute';
import {
  LuLeaf,
  LuMail,
  LuLock,
  LuArrowRight,
  LuCircleAlert,
  LuGraduationCap,
  LuBriefcase,
  LuTruck,
  LuShield,
} from 'react-icons/lu';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const user = await login({ email: email.trim(), password });
      const searchParams = new URLSearchParams(location.search);
      const returnUrl = searchParams.get('returnUrl');
      const from = returnUrl || (location.state as any)?.from?.pathname;
      const targetPath = from && from !== '/login' ? from : getRoleDefaultPath(user.role);
      navigate(targetPath, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Invalid email or password. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickDemo = (demoEmail: string, demoPass: string = 'Password123!') => {
    setEmail(demoEmail);
    setPassword(demoPass);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-eco-50/70 via-surface-50 to-emerald-50/40 p-4">
      <div className="w-full max-w-md">
        {/* Playful Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-eco-500 text-white shadow-3d-green mb-4 border-2 border-eco-600 animate-bounce-subtle">
            <LuLeaf className="w-10 h-10" />
          </div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">EcoSense</h1>
          <p className="text-xs font-extrabold uppercase tracking-widest text-eco-700 mt-1">
            Don Bosco Institute of Technology (DBIT), Mumbai
          </p>
          <p className="text-slate-600 text-sm font-medium mt-2">
            AI-Based Zero Waste Campus Management Platform
          </p>
        </div>

        {/* Login Card */}
        <div className="eco-card p-8 border-2 border-slate-200/80 shadow-soft-lg">
          <h2 className="text-xl font-extrabold text-slate-800 mb-1">Welcome Back</h2>
          <p className="text-xs text-slate-500 font-medium mb-6">
            Sign in to track disposals, earn points, and manage campus recycling.
          </p>

          {error && (
            <div className="mb-6 p-4 rounded-2xl bg-coral-50 border-2 border-coral-200 text-coral-700 text-xs font-bold flex items-start gap-2.5">
              <LuCircleAlert className="w-4 h-4 text-coral-500 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-black uppercase tracking-wider text-slate-600 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <LuMail className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  placeholder="student@dbit.mumbai"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-eco-400 bg-surface-50"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-black uppercase tracking-wider text-slate-600 mb-1.5">
                Password
              </label>
              <div className="relative">
                <LuLock className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-eco-400 bg-surface-50"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-3d btn-3d-green w-full py-3.5 text-base font-extrabold flex items-center justify-center gap-2 mt-6 shadow-3d-green"
            >
              {isSubmitting ? (
                <span>Signing In...</span>
              ) : (
                <>
                  <span>Continue</span>
                  <LuArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Role Selector */}
          <div className="mt-8 pt-6 border-t border-slate-100">
            <p className="text-[11px] font-black uppercase tracking-wider text-slate-400 text-center mb-3">
              Quick Demo Logins
            </p>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickDemo('student@dbit.in', 'studentpassword')}
                className="px-3 py-2 rounded-xl text-xs font-bold text-slate-700 bg-eco-50 hover:bg-eco-100 border border-eco-200 transition-colors flex items-center gap-2"
              >
                <LuGraduationCap className="w-4 h-4 text-eco-700 shrink-0" />
                <span>Student</span>
              </button>
              <button
                type="button"
                onClick={() => handleQuickDemo('staff@dbit.in', 'staffpassword')}
                className="px-3 py-2 rounded-xl text-xs font-bold text-slate-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 transition-colors flex items-center gap-2"
              >
                <LuBriefcase className="w-4 h-4 text-blue-700 shrink-0" />
                <span>Staff</span>
              </button>
              <button
                type="button"
                onClick={() => handleQuickDemo('collector@dbit.in', 'collectorpassword')}
                className="px-3 py-2 rounded-xl text-xs font-bold text-slate-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 transition-colors flex items-center gap-2"
              >
                <LuTruck className="w-4 h-4 text-amber-700 shrink-0" />
                <span>Collector</span>
              </button>
              <button
                type="button"
                onClick={() => handleQuickDemo('admin@dbit.in', 'adminpassword')}
                className="px-3 py-2 rounded-xl text-xs font-bold text-slate-700 bg-purple-50 hover:bg-purple-100 border border-purple-200 transition-colors flex items-center gap-2"
              >
                <LuShield className="w-4 h-4 text-purple-700 shrink-0" />
                <span>Admin</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
