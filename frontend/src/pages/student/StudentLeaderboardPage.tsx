import React, { useState, useEffect } from 'react';
import {
  LuTrophy,
  LuMedal,
  LuAward,
  LuSparkles,
  LuCalendar,
  LuFlame,
  LuUsers,
  LuShieldCheck,
  LuTrendingUp,
} from 'react-icons/lu';
import { gamificationApi } from '../../api/gamification';
import { LeaderboardEntry, LeaderboardResponse, UserRank } from '../../types';
import { EcoStageBadge } from '../../components/common/EcoStageBadge';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';

export const StudentLeaderboardPage: React.FC = () => {
  const [period, setPeriod] = useState<'all-time' | 'month' | 'week'>('all-time');
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLeaderboard = async (selectedPeriod: 'all-time' | 'month' | 'week') => {
    setLoading(true);
    setError(null);
    try {
      const res = await gamificationApi.getLeaderboard(selectedPeriod, 50);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaderboard(period);
  }, [period]);

  const topThree = data?.leaderboard.slice(0, 3) || [];
  const remainingEntries = data?.leaderboard.slice(3) || [];
  const currentUserRank = data?.current_user_rank;

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="relative overflow-hidden bg-gradient-to-r from-emerald-600 via-teal-600 to-sky-600 text-white rounded-3xl p-7 shadow-lg border-b-4 border-emerald-800">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-48 h-48 bg-white/10 rounded-full blur-2xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-200 flex items-center gap-1.5 mb-1">
              <LuTrophy className="w-4 h-4 text-amber-300" />
              Campus Zero-Waste Champions
            </span>
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight">EcoSense League</h1>
            <p className="text-sm text-emerald-100 max-w-xl mt-1 leading-relaxed">
              Earn lifetime points through verified waste disposals and campus issue reporting. Compete with fellow DBIT students!
            </p>
          </div>

          {/* Time Filter Tabs */}
          <div className="flex bg-black/20 backdrop-blur-md p-1.5 rounded-2xl border border-white/20 self-start md:self-auto">
            <button
              onClick={() => setPeriod('all-time')}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                period === 'all-time'
                  ? 'bg-white text-emerald-800 shadow-md scale-105'
                  : 'text-white/80 hover:text-white'
              }`}
            >
              All-Time
            </button>
            <button
              onClick={() => setPeriod('month')}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                period === 'month'
                  ? 'bg-white text-emerald-800 shadow-md scale-105'
                  : 'text-white/80 hover:text-white'
              }`}
            >
              This Month
            </button>
            <button
              onClick={() => setPeriod('week')}
              className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                period === 'week'
                  ? 'bg-white text-emerald-800 shadow-md scale-105'
                  : 'text-white/80 hover:text-white'
              }`}
            >
              This Week
            </button>
          </div>
        </div>
      </div>

      {/* Current User Rank Sticky Card */}
      {currentUserRank && (
        <div className="bg-gradient-to-r from-amber-500 to-yellow-500 text-white rounded-2xl p-5 shadow-md border-b-4 border-amber-700 flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-md flex items-center justify-center font-black text-2xl shadow-inner">
              #{currentUserRank.rank}
            </div>
            <div>
              <span className="text-xs font-bold text-amber-100 uppercase tracking-wider block">
                Your Campus Ranking
              </span>
              <h3 className="text-lg sm:text-xl font-bold">{currentUserRank.display_name}</h3>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <span className="text-2xl font-black tracking-tight flex items-center justify-end gap-1">
                <LuFlame className="w-5 h-5 text-amber-200" />
                {currentUserRank.earned_points.toLocaleString()}
              </span>
              <span className="text-xs text-amber-100 font-medium">pts in period</span>
            </div>
            <EcoStageBadge stageName={currentUserRank.stage_name} size="md" className="hidden sm:inline-flex bg-white/20 text-white border-white/30" />
          </div>
        </div>
      )}

      {loading && <LoadingState message="Calculating student rankings and Eco Stages..." />}
      {error && <ErrorState message={error} onRetry={() => fetchLeaderboard(period)} />}

      {!loading && !error && data && (
        <div className="space-y-8">
          {/* Top 3 Podium Cards */}
          {topThree.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
              {/* Silver: Rank 2 */}
              {topThree[1] && (
                <div className="order-2 md:order-1 bg-white rounded-3xl p-6 shadow-sm border-2 border-slate-200 border-b-4 hover:shadow-md transition-all flex flex-col items-center text-center relative overflow-hidden">
                  <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-600 flex items-center justify-center mb-3 shadow-inner">
                    <LuMedal className="w-7 h-7 text-slate-400" />
                  </div>
                  <span className="text-xs font-extrabold uppercase tracking-widest text-slate-400">#2 Silver</span>
                  <h3 className="text-xl font-bold text-slate-900 mt-1 mb-2">{topThree[1].display_name}</h3>
                  <EcoStageBadge stageName={topThree[1].stage_name} size="sm" className="mb-4" />
                  <div className="mt-auto w-full bg-slate-50 py-2.5 px-4 rounded-2xl font-black text-slate-800 flex items-center justify-center gap-1.5 border border-slate-100">
                    <LuFlame className="w-4 h-4 text-emerald-500" />
                    <span>{topThree[1].earned_points.toLocaleString()} pts</span>
                  </div>
                </div>
              )}

              {/* Gold: Rank 1 */}
              {topThree[0] && (
                <div className="order-1 md:order-2 bg-gradient-to-b from-amber-50 to-white rounded-3xl p-7 shadow-md border-2 border-amber-300 border-b-4 border-b-amber-400 hover:shadow-lg transition-all flex flex-col items-center text-center relative overflow-hidden -mt-2">
                  <div className="w-16 h-16 rounded-3xl bg-amber-400 text-white flex items-center justify-center mb-3 shadow-md">
                    <LuTrophy className="w-9 h-9 text-amber-100" />
                  </div>
                  <span className="text-xs font-black uppercase tracking-widest text-amber-600 flex items-center gap-1">
                    <LuTrophy className="w-3.5 h-3.5" />
                    <span>#1 Champion</span>
                  </span>
                  <h3 className="text-2xl font-black text-slate-900 mt-1 mb-2">{topThree[0].display_name}</h3>
                  <EcoStageBadge stageName={topThree[0].stage_name} size="md" className="mb-4" />
                  <div className="mt-auto w-full bg-amber-100/60 py-3 px-4 rounded-2xl font-black text-amber-900 flex items-center justify-center gap-1.5 border border-amber-200">
                    <LuFlame className="w-5 h-5 text-amber-600" />
                    <span className="text-lg">{topThree[0].earned_points.toLocaleString()} pts</span>
                  </div>
                </div>
              )}

              {/* Bronze: Rank 3 */}
              {topThree[2] && (
                <div className="order-3 md:order-3 bg-white rounded-3xl p-6 shadow-sm border-2 border-amber-700/20 border-b-4 hover:shadow-md transition-all flex flex-col items-center text-center relative overflow-hidden">
                  <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center mb-3 shadow-inner">
                    <LuAward className="w-7 h-7 text-amber-700" />
                  </div>
                  <span className="text-xs font-extrabold uppercase tracking-widest text-amber-700/70">#3 Bronze</span>
                  <h3 className="text-xl font-bold text-slate-900 mt-1 mb-2">{topThree[2].display_name}</h3>
                  <EcoStageBadge stageName={topThree[2].stage_name} size="sm" className="mb-4" />
                  <div className="mt-auto w-full bg-slate-50 py-2.5 px-4 rounded-2xl font-black text-slate-800 flex items-center justify-center gap-1.5 border border-slate-100">
                    <LuFlame className="w-4 h-4 text-emerald-500" />
                    <span>{topThree[2].earned_points.toLocaleString()} pts</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 shadow-sm">
              <LuUsers className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h3 className="text-lg font-bold text-slate-700">No student activity in this period</h3>
              <p className="text-sm text-slate-500 max-w-sm mx-auto mt-1">
                Be the first student to scan a bin and dispose waste properly to take the top spot!
              </p>
            </div>
          )}

          {/* Remaining Rank List */}
          {remainingEntries.length > 0 && (
            <div className="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
                <h3 className="font-bold text-slate-800 flex items-center gap-2 text-sm uppercase tracking-wider">
                  <LuTrendingUp className="w-4 h-4 text-emerald-600" />
                  All Campus Contributors
                </h3>
                <span className="text-xs font-semibold text-slate-500">
                  {data.total_participants} Registered Participants
                </span>
              </div>

              <div className="divide-y divide-slate-100">
                {remainingEntries.map((entry) => (
                  <div
                    key={entry.user_id}
                    className={`p-4 sm:px-6 flex items-center justify-between gap-4 transition-colors ${
                      entry.is_current_user ? 'bg-amber-50/60 font-semibold' : 'hover:bg-slate-50/80'
                    }`}
                  >
                    <div className="flex items-center gap-4 min-w-0">
                      <span className="w-8 text-center font-black text-slate-400 text-sm">
                        #{entry.rank}
                      </span>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="font-bold text-slate-900 truncate text-sm sm:text-base">
                            {entry.display_name}
                          </p>
                          {entry.is_current_user && (
                            <span className="px-2 py-0.5 rounded-full text-xs font-extrabold bg-amber-200 text-amber-800">
                              You
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 flex-shrink-0">
                      <EcoStageBadge stageName={entry.stage_name} size="sm" className="hidden sm:inline-flex" />
                      <span className="font-black text-slate-900 text-sm sm:text-base flex items-center gap-1">
                        <LuFlame className="w-4 h-4 text-emerald-500" />
                        {entry.earned_points.toLocaleString()} pts
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
