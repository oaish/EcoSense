import React, { useState, useEffect } from 'react';
import { rewardsApi } from '../../api/rewards';
import { gamificationApi } from '../../api/gamification';
import { Reward, PointBalanceRead } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { CelebrationModal } from '../../components/common/CelebrationModal';
import { ConfirmModal } from '../../components/common/ConfirmModal';
import { PointsCard } from '../../components/common/PointsCard';
import { LuGift, LuHistory, LuSparkles, LuCheck, LuCircleAlert, LuStar } from 'react-icons/lu';
import { Link } from 'react-router-dom';

export const RewardsCatalogPage: React.FC = () => {
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [pointsData, setPointsData] = useState<PointBalanceRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [redeemingId, setRedeemingId] = useState<number | null>(null);
  const [selectedRewardToRedeem, setSelectedRewardToRedeem] = useState<Reward | null>(null);
  const [redeemSuccess, setRedeemSuccess] = useState<string | null>(null);
  const [showCelebration, setShowCelebration] = useState(false);
  const [noticeMessage, setNoticeMessage] = useState<string | null>(null);

  const fetchCatalogData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [rewardsRes, pointsRes] = await Promise.all([
        rewardsApi.getRewards({ limit: 50 }),
        gamificationApi.getMyPoints().catch(() => ({
          user_id: '',
          current_balance: 0,
          total_earned: 0,
          total_redeemed: 0,
        })),
      ]);
      setRewards(rewardsRes);
      setPointsData(pointsRes);
    } catch (err: any) {
      setError(err.message || 'Failed to load rewards catalog.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCatalogData();
  }, []);

  const handleOpenRedeemModal = (reward: Reward) => {
    const currentBalance = pointsData?.current_balance ?? 0;
    if (currentBalance < reward.points_cost) {
      setNoticeMessage(`You need ${reward.points_cost - currentBalance} more points to redeem "${reward.name}".`);
      return;
    }
    setSelectedRewardToRedeem(reward);
  };

  const handleConfirmRedeem = async () => {
    if (!selectedRewardToRedeem) return;
    const reward = selectedRewardToRedeem;
    setSelectedRewardToRedeem(null);
    setRedeemingId(reward.reward_id);

    try {
      await rewardsApi.redeemReward(reward.reward_id);
      setRedeemSuccess(reward.name);
      setShowCelebration(true);
      // Refresh points
      const updatedPoints = await gamificationApi.getMyPoints();
      setPointsData(updatedPoints);
    } catch (err: any) {
      setError(err.message || 'Redemption failed. Please try again.');
    } finally {
      setRedeemingId(null);
    }
  };

  if (loading) {
    return <LoadingState message="Loading eco rewards store..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchCatalogData} />;
  }

  const currentBalance = pointsData?.current_balance ?? 0;

  return (
    <div className="max-w-5xl mx-auto py-4 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="inline-flex items-center gap-1.5 text-xs font-black uppercase tracking-wider text-sun-800 bg-sun-100 px-3 py-1 rounded-full border border-sun-300">
            <LuSparkles className="w-3.5 h-3.5 text-sun-700" />
            <span>EcoSense Reward Store</span>
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Redeem Campus Perks
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Turn your verified recycling points into canteen vouchers, badges, and eco gear!
          </p>
        </div>

        <Link
          to="/rewards/history"
          className="btn-3d btn-3d-white px-4 py-2.5 text-xs font-bold flex items-center justify-center gap-1.5 shrink-0"
        >
          <LuHistory className="w-4 h-4" />
          <span>Redemption History</span>
        </Link>
      </div>

      {noticeMessage && (
        <div className="p-4 rounded-2xl bg-amber-50 border-2 border-amber-200 text-amber-900 text-xs font-bold flex items-center justify-between">
          <div className="flex items-center gap-2">
            <LuCircleAlert className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{noticeMessage}</span>
          </div>
          <button onClick={() => setNoticeMessage(null)} className="text-amber-700 hover:text-amber-900 font-extrabold">
            Dismiss
          </button>
        </div>
      )}

      {/* Points Balance Banner */}
      <PointsCard
        points={currentBalance}
        totalEarned={pointsData?.total_earned ?? 0}
        showRedeemLink={false}
      />

      {/* Reward Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {rewards.map((reward) => {
          const canAfford = currentBalance >= reward.points_cost;
          const pointsNeeded = Math.max(0, reward.points_cost - currentBalance);

          const isOutOfStock =
            reward.stock_quantity !== null &&
            reward.stock_quantity !== undefined &&
            reward.stock_quantity <= 0;

          return (
            <div
              key={reward.reward_id}
              className={`eco-card p-6 border-2 flex flex-col justify-between transition-all ${canAfford && !isOutOfStock
                  ? 'border-sun-200 hover:border-sun-400 hover:shadow-soft-lg'
                  : 'border-slate-200/80 opacity-90'
                }`}
            >
              <div>
                <div className="w-16 h-16 rounded-3xl bg-sun-100 border-2 border-sun-300 text-sun-800 flex items-center justify-center mb-4 shadow-3d-yellow">
                  <LuGift className="w-8 h-8 text-sun-700" />
                </div>

                <div className="flex items-center justify-between mb-2">
                  <span className="points-badge text-xs flex items-center gap-1">
                    <LuStar className="w-3.5 h-3.5 fill-current" />
                    <span>{reward.points_cost} pts</span>
                  </span>

                  {reward.stock_quantity !== null &&
                    reward.stock_quantity !== undefined && (
                      <span className="text-[10px] font-bold text-slate-400">
                        {isOutOfStock
                          ? 'Out of stock'
                          : `${reward.stock_quantity} left`}
                      </span>
                    )}
                </div>

                <h3 className="text-lg font-black text-slate-900 mb-1">
                  {reward.name}
                </h3>

                <p className="text-xs text-slate-500 font-medium leading-relaxed mb-4">
                  {reward.description}
                </p>
              </div>

              <button
                type="button"
                disabled={
                  !canAfford ||
                  isOutOfStock ||
                  redeemingId === reward.reward_id
                }
                onClick={() => handleOpenRedeemModal(reward)}
                className={`w-full py-3 text-xs font-black rounded-2xl transition-all select-none ${canAfford && !isOutOfStock
                    ? 'btn-3d btn-3d-yellow shadow-3d-yellow'
                    : 'bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed'
                  }`}
              >
                {redeemingId === reward.reward_id ? (
                  <span>Processing...</span>
                ) : isOutOfStock ? (
                  <span>Out of Stock</span>
                ) : canAfford ? (
                  <span>Redeem for {reward.points_cost} pts</span>
                ) : (
                  <span>Need {pointsNeeded} more pts</span>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {/* Confirmation Modal */}
      <ConfirmModal
        isOpen={Boolean(selectedRewardToRedeem)}
        title="Redeem Campus Perk"
        message={`Are you sure you want to redeem "${selectedRewardToRedeem?.name}" for ${selectedRewardToRedeem?.points_cost} Eco Points?`}
        confirmLabel={`Redeem (${selectedRewardToRedeem?.points_cost} Pts)`}
        confirmVariant="primary"
        onConfirm={handleConfirmRedeem}
        onCancel={() => setSelectedRewardToRedeem(null)}
      />

      {/* Celebration Modal */}
      <CelebrationModal
        isOpen={showCelebration}
        onClose={() => setShowCelebration(false)}
        title="Perk Redeemed!"
        subtitle={`Your redemption for "${redeemSuccess}" was recorded. Check your redemption history for fulfillment details.`}
        badgeText="Reward Unlocked"
      />
    </div>
  );
};
