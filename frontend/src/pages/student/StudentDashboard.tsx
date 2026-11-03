import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { gamificationApi } from '../../api/gamification';
import { disposalsApi } from '../../api/disposals';
import { reportsApi } from '../../api/reports';
import { PointBalanceRead, Disposal, WasteReport, EcoStage } from '../../types';
import { PointsCard } from '../../components/common/PointsCard';
import { EcoStageCard } from '../../components/common/EcoStageCard';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { StatusBadge } from '../../components/common/StatusBadge';
import {
  LuQrCode,
  LuBrainCircuit,
  LuTriangleAlert,
  LuArrowRight,
  LuLeaf,
  LuRecycle,
  LuFileText,
  LuSparkles,
  LuTrophy,
} from 'react-icons/lu';
import { Link } from 'react-router-dom';

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [pointsData, setPointsData] = useState<PointBalanceRead | null>(null);
  const [ecoStage, setEcoStage] = useState<EcoStage | null>(null);
  const [recentDisposals, setRecentDisposals] = useState<Disposal[]>([]);
  const [recentReports, setRecentReports] = useState<WasteReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [pointsRes, stageRes, disposalsRes, reportsRes] = await Promise.all([
        gamificationApi.getMyPoints().catch(() => ({
          user_id: user?.user_id || '',
          current_balance: 0,
          total_earned: 0,
          total_redeemed: 0,
        })),
        gamificationApi.getMyStage().catch(() => null),
        disposalsApi.getDisposals({ limit: 5 }).catch(() => []),
        reportsApi.getReports({ limit: 3 }).catch(() => []),
      ]);

      setPointsData(pointsRes);
      setEcoStage(stageRes);
      setRecentDisposals(disposalsRes);
      setRecentReports(reportsRes);
    } catch (err: any) {
      setError(err.message || 'Unable to load your sustainability progress.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return <LoadingState message="Loading your eco achievements..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchDashboardData} />;
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Playful Greeting Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="inline-flex items-center gap-1.5 text-xs font-black uppercase tracking-wider text-eco-700 bg-eco-100 px-3 py-1 rounded-full border border-eco-200">
            <LuLeaf className="w-3.5 h-3.5 text-eco-600" />
            <span>Zero Waste Campus DBIT</span>
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-2">
            Hey, {user?.name || 'Eco Warrior'}!
          </h1>
          <p className="text-slate-600 font-medium text-sm mt-0.5">
            Keep campus clean and earn rewards with every verified disposal.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/leaderboard"
            className="btn-3d btn-3d-yellow px-5 py-3 text-sm flex items-center justify-center gap-2 shadow-3d-yellow shrink-0"
          >
            <LuTrophy className="w-4 h-4 text-slate-950" />
            <span>Eco League</span>
          </Link>
          <Link
            to="/scan"
            className="btn-3d btn-3d-green px-6 py-3 text-sm flex items-center justify-center gap-2.5 shadow-3d-green shrink-0"
          >
            <LuQrCode className="w-5 h-5" />
            <span>Scan Bin QR</span>
          </Link>
        </div>
      </div>

      {/* Gamified Points & Eco Stage Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PointsCard
          points={pointsData?.current_balance ?? 0}
          totalEarned={pointsData?.total_earned ?? 0}
          streakDays={recentDisposals.length > 0 ? Math.min(recentDisposals.length, 7) : 1}
        />

        {ecoStage && (
          <EcoStageCard
            stage={ecoStage}
            totalEarnedPoints={pointsData?.total_earned ?? 0}
          />
        )}
      </div>

      {/* Quick Action Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Scan & Earn */}
        <Link
          to="/scan"
          className="eco-card-interactive group border-2 hover:border-eco-300 flex flex-col justify-between"
        >
          <div>
            <div className="w-12 h-12 rounded-2xl bg-eco-100 text-eco-700 flex items-center justify-center mb-4 border border-eco-200 shadow-xs group-hover:scale-110 transition-transform">
              <LuQrCode className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-extrabold text-slate-900 mb-1">Scan a Bin</h3>
            <p className="text-xs text-slate-500 font-medium leading-relaxed">
              Scan any campus bin QR code to verify waste segregation and collect instant points.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center text-xs font-bold text-eco-600 gap-1 group-hover:translate-x-1 transition-transform">
            <span>Start Scanning</span>
            <LuArrowRight className="w-4 h-4" />
          </div>
        </Link>

        {/* AI Classifier */}
        <Link
          to="/classify"
          className="eco-card-interactive group border-2 hover:border-ocean-300 flex flex-col justify-between"
        >
          <div>
            <div className="w-12 h-12 rounded-2xl bg-ocean-100 text-ocean-700 flex items-center justify-center mb-4 border border-ocean-200 shadow-xs group-hover:scale-110 transition-transform">
              <LuBrainCircuit className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-extrabold text-slate-900 mb-1">AI Waste Classifier</h3>
            <p className="text-xs text-slate-500 font-medium leading-relaxed">
              Unsure which bin to use? Upload or take a photo and let our AI helper classify the material.
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center text-xs font-bold text-ocean-600 gap-1 group-hover:translate-x-1 transition-transform">
            <span>Classify Waste</span>
            <LuArrowRight className="w-4 h-4" />
          </div>
        </Link>

        {/* Report Waste Issue */}
        <Link
          to="/student/report"
          className="eco-card-interactive group border-2 hover:border-coral-300 flex flex-col justify-between"
        >
          <div>
            <div className="w-12 h-12 rounded-2xl bg-coral-100 text-coral-700 flex items-center justify-center mb-4 border border-coral-200 shadow-xs group-hover:scale-110 transition-transform">
              <LuTriangleAlert className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-extrabold text-slate-900 mb-1">Report Waste Issue</h3>
            <p className="text-xs text-slate-500 font-medium leading-relaxed">
              Report overflowing or damaged campus bins. Earn points once resolved by staff!
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center text-xs font-bold text-coral-600 gap-1 group-hover:translate-x-1 transition-transform">
            <span>File Report</span>
            <LuArrowRight className="w-4 h-4" />
          </div>
        </Link>
      </div>

      {/* Recent Disposals & Activity Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Disposals */}
        <div className="eco-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
              <LuRecycle className="w-5 h-5 text-eco-600" />
              <span>Recent Disposals</span>
            </h3>
            <Link
              to="/student/activity"
              className="text-xs font-bold text-eco-600 hover:text-eco-700"
            >
              View All
            </Link>
          </div>

          {recentDisposals.length === 0 ? (
            <div className="text-center py-8 text-slate-400">
              <LuRecycle className="w-8 h-8 mx-auto text-slate-300 mb-1.5" />
              <p className="text-xs font-bold text-slate-500">No disposal recorded yet</p>
              <p className="text-[11px] text-slate-400 mt-0.5">Scan a bin on campus to get started!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentDisposals.map((item) => (
                <div
                  key={item.disposal_id}
                  className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 hover:bg-slate-100/80 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-eco-100 text-eco-700 flex items-center justify-center font-bold text-xs border border-eco-200">
                      <LuLeaf className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-xs font-extrabold text-slate-800">
                        Disposal #{item.disposal_id}
                      </p>
                      <p className="text-[10px] font-semibold text-slate-500">
                        {item.disposal_timestamp
                          ? new Date(item.disposal_timestamp).toLocaleDateString()
                          : 'Recent'}
                      </p>
                    </div>
                  </div>
                  <span className="points-badge text-xs">+10 pts</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* My Reported Issues */}
        <div className="eco-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
              <LuFileText className="w-5 h-5 text-ocean-600" />
              <span>My Reports</span>
            </h3>
            <Link
              to="/student/reports"
              className="text-xs font-bold text-eco-600 hover:text-eco-700"
            >
              View All
            </Link>
          </div>

          {recentReports.length === 0 ? (
            <div className="text-center py-8 text-slate-400">
              <LuSparkles className="w-8 h-8 mx-auto text-slate-300 mb-1.5" />
              <p className="text-xs font-bold text-slate-500">No open issue reports</p>
              <p className="text-[11px] text-slate-400 mt-0.5">All campus bins are looking good!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentReports.map((report) => (
                <div
                  key={report.report_id}
                  className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80"
                >
                  <div>
                    <p className="text-xs font-extrabold text-slate-800 capitalize">
                      {report.report_type.replace(/_/g, ' ')}
                    </p>
                    <p className="text-[10px] font-medium text-slate-500 truncate max-w-[200px]">
                      {report.description || 'Issue reported on campus'}
                    </p>
                  </div>
                  <StatusBadge status={report.status} type="report" size="sm" />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
