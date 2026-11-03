import React, { useState, useEffect } from 'react';
import { gamificationApi } from '../../api/gamification';
import { disposalsApi } from '../../api/disposals';
import { PointTransaction, Disposal } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { LuCalendar, LuTrash2, LuRecycle, LuStar, LuArrowUpRight, LuArrowDownLeft } from 'react-icons/lu';

export const StudentActivityPage: React.FC = () => {
  const [transactions, setTransactions] = useState<PointTransaction[]>([]);
  const [disposals, setDisposals] = useState<Disposal[]>([]);
  const [activeTab, setActiveTab] = useState<'all' | 'disposals' | 'ledger'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchActivityData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [txnsRes, disposalsRes] = await Promise.all([
        gamificationApi.getMyTransactions({ limit: 50 }).catch(() => []),
        disposalsApi.getDisposals({ limit: 50 }).catch(() => []),
      ]);
      setTransactions(txnsRes);
      setDisposals(disposalsRes);
    } catch (err: any) {
      setError(err.message || 'Failed to load sustainability activity.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivityData();
  }, []);

  if (loading) {
    return <LoadingState message="Loading your activity timeline..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchActivityData} />;
  }

  return (
    <div className="max-w-4xl mx-auto py-4 space-y-6">
      {/* Header */}
      <div>
        <span className="text-xs font-black uppercase tracking-wider text-eco-700 bg-eco-100 px-3 py-1 rounded-full border border-eco-200">
          Eco Timeline
        </span>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
          Activity & Points Log
        </h1>
        <p className="text-slate-600 text-sm font-medium">
          A full chronological record of your campus disposals and earned gamification points.
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 border-b border-slate-200 pb-3">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-4 py-2 rounded-2xl text-xs font-black transition-all ${
            activeTab === 'all'
              ? 'bg-eco-500 text-white shadow-3d-green'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          All Activity
        </button>
        <button
          onClick={() => setActiveTab('disposals')}
          className={`px-4 py-2 rounded-2xl text-xs font-black transition-all ${
            activeTab === 'disposals'
              ? 'bg-eco-500 text-white shadow-3d-green'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          Disposals ({disposals.length})
        </button>
        <button
          onClick={() => setActiveTab('ledger')}
          className={`px-4 py-2 rounded-2xl text-xs font-black transition-all ${
            activeTab === 'ledger'
              ? 'bg-eco-500 text-white shadow-3d-green'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          Points Transactions ({transactions.length})
        </button>
      </div>

      {/* Disposals Tab View */}
      {activeTab === 'disposals' && (
        <div className="space-y-3">
          {disposals.length === 0 ? (
            <EmptyState
              icon={LuTrash2}
              title="No disposals recorded"
              description="Scan a campus bin to record your first disposal!"
            />
          ) : (
            disposals.map((item) => (
              <div
                key={item.disposal_id}
                className="eco-card p-4 border-2 border-slate-200/80 flex items-center justify-between hover:border-eco-300 transition-all"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-eco-100 text-eco-700 flex items-center justify-center shadow-xs shrink-0">
                    <LuRecycle className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-extrabold text-slate-900">
                      Disposal #{item.disposal_id}
                    </h3>
                    <p className="text-[11px] font-semibold text-slate-400 flex items-center gap-2">
                      <span className="flex items-center gap-1">
                        <LuCalendar className="w-3 h-3" />
                        {new Date(item.disposal_timestamp).toLocaleString()}
                      </span>
                      {item.quantity_kg && (
                        <span>• {item.quantity_kg} kg</span>
                      )}
                    </p>
                  </div>
                </div>
                <span className="points-badge text-xs">+10 pts</span>
              </div>
            ))
          )}
        </div>
      )}

      {/* Ledger Transactions View */}
      {(activeTab === 'ledger' || activeTab === 'all') && (
        <div className="space-y-3">
          {transactions.length === 0 ? (
            <EmptyState
              icon={LuStar}
              title="No points transactions yet"
              description="Keep contributing to campus zero-waste goals to earn points!"
            />
          ) : (
            transactions.map((txn) => {
              const isEarn = txn.points > 0;
              return (
                <div
                  key={txn.transaction_id}
                  className="eco-card p-4 border-2 border-slate-200/80 flex items-center justify-between hover:border-slate-300 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-2xl flex items-center justify-center text-xl shadow-xs shrink-0 ${
                        isEarn ? 'bg-eco-100 text-eco-700' : 'bg-sun-100 text-sun-700'
                      }`}
                    >
                      {isEarn ? <LuArrowUpRight className="w-5 h-5 text-eco-600" /> : <LuArrowDownLeft className="w-5 h-5 text-sun-600" />}
                    </div>
                    <div>
                      <h3 className="text-sm font-extrabold text-slate-900">
                        {txn.reason || (isEarn ? 'Disposal Eco Points' : 'Reward Redemption')}
                      </h3>
                      <p className="text-[11px] font-semibold text-slate-400 flex items-center gap-2">
                        <span className="flex items-center gap-1">
                          <LuCalendar className="w-3 h-3" />
                          {new Date(txn.created_at).toLocaleDateString()}
                        </span>
                        <span>•</span>
                        <span className="uppercase font-bold tracking-wider text-[10px]">
                          {txn.transaction_type}
                        </span>
                      </p>
                    </div>
                  </div>

                  <span
                    className={`font-black text-sm px-3.5 py-1.5 rounded-full border shadow-xs ${
                      isEarn
                        ? 'bg-eco-100 border-eco-300 text-eco-800'
                        : 'bg-amber-100 border-amber-300 text-amber-800'
                    }`}
                  >
                    {isEarn ? `+${txn.points}` : `${txn.points}`} pts
                  </span>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};
