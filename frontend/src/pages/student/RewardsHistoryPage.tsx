import React, { useState, useEffect } from 'react';
import { rewardsApi } from '../../api/rewards';
import { RewardRedemption } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { LuGift, LuCalendar, LuArrowLeft } from 'react-icons/lu';
import { Link } from 'react-router-dom';

export const RewardsHistoryPage: React.FC = () => {
  const [redemptions, setRedemptions] = useState<RewardRedemption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRedemptions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await rewardsApi.getMyRedemptions({ limit: 50 });
      setRedemptions(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load redemption history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRedemptions();
  }, []);

  if (loading) {
    return <LoadingState message="Loading your reward redemptions..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchRedemptions} />;
  }

  return (
    <div className="max-w-4xl mx-auto py-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-sun-800 bg-sun-100 px-3 py-1 rounded-full border border-sun-300">
            Perks Log
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Redemption History
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Track fulfillment status of your redeemed canteen vouchers and eco gear.
          </p>
        </div>

        <Link
          to="/rewards"
          className="btn-3d btn-3d-white px-4 py-2.5 text-xs font-bold flex items-center justify-center gap-1.5 shrink-0"
        >
          <LuArrowLeft className="w-4 h-4" />
          <span>Back to Rewards Store</span>
        </Link>
      </div>

      {redemptions.length === 0 ? (
        <EmptyState
          icon={LuGift}
          title="No redemptions yet"
          description="You haven't claimed any rewards yet. Earn points by scanning bins to unlock exciting campus perks!"
          actionText="Browse Rewards Catalog"
          onAction={() => window.location.assign('/rewards')}
        />
      ) : (
        <div className="space-y-3">
          {redemptions.map((item) => (
            <div
              key={item.redemption_id}
              className="eco-card p-5 border-2 border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-sun-300 transition-all"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-sun-100 text-sun-800 flex items-center justify-center border border-sun-300 shadow-xs shrink-0">
                  <LuGift className="w-6 h-6 text-sun-700" />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-slate-900">
                    {item.reward_name || item.reward?.name || `Reward #${item.reward_id}`}
                  </h3>
                  <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-500 font-semibold">
                    <span className="flex items-center gap-1 text-[11px]">
                      <LuCalendar className="w-3 h-3" />
                      {new Date(item.redeemed_at).toLocaleDateString()}
                    </span>
                    <span>•</span>
                    <span className="font-extrabold text-sun-800">-{item.points_spent} pts</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <StatusBadge status={item.status} type="redemption" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
