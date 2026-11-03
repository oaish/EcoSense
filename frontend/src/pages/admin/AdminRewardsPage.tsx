import React, { useState, useEffect } from 'react';
import { rewardsApi } from '../../api/rewards';
import { Reward, RewardRedemption } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { Gift, Plus, Edit2, Layers, X, CheckCircle, Calendar } from 'lucide-react';
import { LuGift, LuStar } from 'react-icons/lu';

export const AdminRewardsPage: React.FC = () => {
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [redemptions, setRedemptions] = useState<RewardRedemption[]>([]);
  const [activeTab, setActiveTab] = useState<'rewards' | 'redemptions'>('rewards');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create/Edit Modal State
  const [showModal, setShowModal] = useState(false);
  const [editingReward, setEditingReward] = useState<Reward | null>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [pointsCost, setPointsCost] = useState<number>(100);
  const [stockQuantity, setStockQuantity] = useState<number | ''>(50);
  const [isActive, setIsActive] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [rewardsRes, redemptionsRes] = await Promise.all([
        rewardsApi.getRewards({ limit: 100 }),
        rewardsApi.getAllRedemptions({ limit: 50 }).catch(() => []),
      ]);
      setRewards(rewardsRes);
      setRedemptions(redemptionsRes);
    } catch (err: any) {
      setError(err.message || 'Failed to load rewards inventory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenCreate = () => {
    setEditingReward(null);
    setName('');
    setDescription('');
    setPointsCost(100);
    setStockQuantity(50);
    setIsActive(true);
    setShowModal(true);
  };

  const handleOpenEdit = (r: Reward) => {
    setEditingReward(r);
    setName(r.name);
    setDescription(r.description);
    setPointsCost(r.points_cost);
    setStockQuantity(r.stock_quantity ?? '');
    setIsActive(r.is_active);
    setShowModal(true);
  };

  const handleSaveReward = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !description.trim()) return;

    setIsSubmitting(true);
    try {
      if (editingReward) {
        await rewardsApi.updateReward(editingReward.reward_id, {
          name: name.trim(),
          description: description.trim(),
          points_cost: Number(pointsCost),
          stock_quantity: stockQuantity !== '' ? Number(stockQuantity) : null,
          is_active: isActive,
        });
      } else {
        await rewardsApi.createReward({
          name: name.trim(),
          description: description.trim(),
          points_cost: Number(pointsCost),
          stock_quantity: stockQuantity !== '' ? Number(stockQuantity) : null,
          is_active: isActive,
        });
      }

      setShowModal(false);
      fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to save reward.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-4 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-sun-800 bg-sun-100 px-3 py-1 rounded-full border border-sun-300">
            Gamification Management
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Rewards & Redemptions
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Manage campus incentives, point requirements, and track student claims.
          </p>
        </div>

        <button
          onClick={handleOpenCreate}
          className="btn-3d btn-3d-yellow px-5 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-yellow shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Create New Reward</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200 pb-3">
        <button
          onClick={() => setActiveTab('rewards')}
          className={`px-4 py-2 rounded-2xl text-xs font-black transition-all ${activeTab === 'rewards'
            ? 'bg-sun-500 text-slate-950 shadow-3d-yellow'
            : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
        >
          Rewards Catalog ({rewards.length})
        </button>
        <button
          onClick={() => setActiveTab('redemptions')}
          className={`px-4 py-2 rounded-2xl text-xs font-black transition-all ${activeTab === 'redemptions'
            ? 'bg-sun-500 text-slate-950 shadow-3d-yellow'
            : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
        >
          Platform Redemptions ({redemptions.length})
        </button>
      </div>

      {loading ? (
        <LoadingState message="Loading reward items..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchData} />
      ) : activeTab === 'rewards' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {rewards.map((reward) => (
            <div
              key={reward.reward_id}
              className="eco-card p-5 border-2 border-slate-200 hover:border-sun-300 transition-all flex flex-col justify-between space-y-4"
            >
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className="w-12 h-12 rounded-2xl bg-sun-100 text-sun-800 flex items-center justify-center text-2xl shadow-xs">
                    <LuGift className="w-6 h-6 text-sun-700" />
                  </div>
                  <span
                    className={`text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full border ${reward.is_active
                      ? 'bg-eco-100 text-eco-800 border-eco-200'
                      : 'bg-slate-100 text-slate-500 border-slate-200'
                      }`}
                  >
                    {reward.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>

                <div className="flex items-center justify-between mb-1">
                  <span className="points-badge text-xs flex items-center gap-1">
                    <LuStar className="w-3.5 h-3.5 text-sun-600" />
                    <span>{reward.points_cost} pts</span>
                  </span>
                  {reward.stock_quantity !== null && (
                    <span className="text-xs font-bold text-slate-500">
                      Stock: {reward.stock_quantity}
                    </span>
                  )}
                </div>

                <h3 className="text-base font-black text-slate-900 mt-2">{reward.name}</h3>
                <p className="text-xs text-slate-500 font-medium leading-relaxed mt-1">
                  {reward.description}
                </p>
              </div>

              <button
                onClick={() => handleOpenEdit(reward)}
                className="btn-3d btn-3d-white w-full py-2 text-xs font-bold flex items-center justify-center gap-1.5"
              >
                <Edit2 className="w-3.5 h-3.5" />
                <span>Edit Reward</span>
              </button>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {redemptions.map((red) => (
            <div
              key={red.redemption_id}
              className="eco-card p-4 border-2 border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div>
                <h4 className="text-sm font-black text-slate-900">
                  {red.reward_name || `Reward #${red.reward_id}`}
                </h4>
                <p className="text-xs font-semibold text-slate-500 flex items-center gap-2 mt-0.5">
                  <span className="flex items-center gap-1 text-[11px]">
                    <Calendar className="w-3 h-3" />
                    {new Date(red.redeemed_at).toLocaleString()}
                  </span>
                  <span>• User: {red.user_id.slice(0, 8)}...</span>
                  <span className="font-extrabold text-sun-800">-{red.points_spent} pts</span>
                </p>
              </div>

              <StatusBadge status={red.status} type="redemption" />
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in" style={{ marginTop: 0 }}>
          <div className="bg-white rounded-3xl p-6 w-full max-w-md border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-black text-slate-900">
                {editingReward ? 'Edit Reward' : 'Create Campus Reward'}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveReward} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Reward Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Free Cafeteria Coffee Coupon"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-sun-400"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Description
                </label>
                <textarea
                  rows={2}
                  required
                  placeholder="e.g. Redeemable at the Main DBIT Cafeteria counter."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-medium bg-surface-50 focus:outline-none focus:ring-2 focus:ring-sun-400"
                ></textarea>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                    Point Cost
                  </label>
                  <input
                    type="number"
                    min="10"
                    required
                    value={pointsCost}
                    onChange={(e) => setPointsCost(Number(e.target.value))}
                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-sun-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                    Stock Quantity
                  </label>
                  <input
                    type="number"
                    min="0"
                    placeholder="Infinite"
                    value={stockQuantity}
                    onChange={(e) =>
                      setStockQuantity(e.target.value === '' ? '' : Number(e.target.value))
                    }
                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-sun-400"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="isActive"
                  checked={isActive}
                  onChange={(e) => setIsActive(e.target.checked)}
                  className="w-4 h-4 text-sun-500 rounded accent-sun-500 cursor-pointer"
                />
                <label
                  htmlFor="isActive"
                  className="text-xs font-bold text-slate-700 cursor-pointer"
                >
                  Active in Student Store
                </label>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn-3d btn-3d-white flex-1 py-3 text-xs font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-3d btn-3d-yellow flex-1 py-3 text-xs font-black shadow-3d-yellow"
                >
                  {isSubmitting ? 'Saving...' : 'Save Reward'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
