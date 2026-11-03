import React, { useState } from 'react';
import { gamificationApi } from '../../api/gamification';
import { PointBalanceRead, PointTransaction } from '../../types';
import { Award, Search, PlusCircle, MinusCircle, CheckCircle, Calendar, AlertCircle } from 'lucide-react';

export const AdminPointsPage: React.FC = () => {
  const [targetUserId, setTargetUserId] = useState('');
  const [userBalance, setUserBalance] = useState<PointBalanceRead | null>(null);
  const [transactions, setTransactions] = useState<PointTransaction[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Adjustment Form State
  const [adjustmentPoints, setAdjustmentPoints] = useState<number>(50);
  const [adjustmentReason, setAdjustmentReason] = useState('');
  const [isAdjusting, setIsAdjusting] = useState(false);
  const [adjustSuccess, setAdjustSuccess] = useState<string | null>(null);

  const handleLookupUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUserId.trim()) return;

    setIsSearching(true);
    setError(null);
    setAdjustSuccess(null);

    try {
      const [balanceRes, txnsRes] = await Promise.all([
        gamificationApi.getUserPoints(targetUserId.trim()),
        gamificationApi.getUserTransactions(targetUserId.trim(), { limit: 20 }),
      ]);
      setUserBalance(balanceRes);
      setTransactions(txnsRes);
    } catch (err: any) {
      setError(err.message || 'User not found or invalid User ID format (UUID required).');
      setUserBalance(null);
      setTransactions([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleExecuteAdjustment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUserId.trim() || !adjustmentReason.trim() || adjustmentPoints === 0) return;

    setIsAdjusting(true);
    setError(null);
    try {
      await gamificationApi.adjustUserPoints(targetUserId.trim(), {
        points: Number(adjustmentPoints),
        reason: adjustmentReason.trim(),
      });

      setAdjustSuccess(`Ledger adjusted: ${adjustmentPoints > 0 ? `+${adjustmentPoints}` : adjustmentPoints} points recorded.`);
      setAdjustmentReason('');

      // Refresh user balance & transactions
      const [balanceRes, txnsRes] = await Promise.all([
        gamificationApi.getUserPoints(targetUserId.trim()),
        gamificationApi.getUserTransactions(targetUserId.trim(), { limit: 20 }),
      ]);
      setUserBalance(balanceRes);
      setTransactions(txnsRes);
    } catch (err: any) {
      setError(err.message || 'Failed to adjust points.');
    } finally {
      setIsAdjusting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-4 space-y-6">
      <div>
        <span className="text-xs font-black uppercase tracking-wider text-purple-800 bg-purple-100 px-3 py-1 rounded-full border border-purple-200">
          Financial & Gamification Ledger
        </span>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
          Points Ledger & Adjustments
        </h1>
        <p className="text-slate-600 text-sm font-medium">
          Audit student point balances and execute immutable administrative ledger adjustments.
        </p>
      </div>

      {/* User Search Card */}
      <div className="eco-card p-6 space-y-4">
        <h3 className="text-base font-black text-slate-900">Lookup User Balance</h3>

        <form onSubmit={handleLookupUser} className="flex gap-2">
          <input
            type="text"
            required
            placeholder="Enter Student UUID (e.g. 550e8400-e29b-41d4-a716-446655440000)"
            value={targetUserId}
            onChange={(e) => setTargetUserId(e.target.value)}
            className="flex-1 px-4 py-3 rounded-2xl border border-slate-200 text-xs font-mono font-medium bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
          <button
            type="submit"
            disabled={isSearching}
            className="btn-3d btn-3d-green px-6 py-3 text-xs font-black shadow-3d-green"
          >
            {isSearching ? 'Auditing...' : 'Inspect'}
          </button>
        </form>

        {error && (
          <div className="p-3.5 bg-coral-50 rounded-2xl border border-coral-200 text-coral-700 text-xs font-bold">
            {error}
          </div>
        )}
      </div>

      {/* User Balance & Adjustment Section */}
      {userBalance && (
        <div className="space-y-6 animate-in fade-in">
          {/* User Balance Card */}
          <div className="eco-card p-6 border-2 border-sun-200 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  User Point Ledger
                </p>
                <p className="text-xs font-mono font-bold text-slate-600">{userBalance.user_id}</p>
              </div>
              <span className="points-badge text-sm">⭐ {userBalance.current_balance} pts</span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <p className="text-slate-400 font-bold uppercase text-[10px]">Lifetime Earned</p>
                <p className="text-lg font-black text-eco-700">+{userBalance.total_earned} pts</p>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <p className="text-slate-400 font-bold uppercase text-[10px]">Lifetime Redeemed</p>
                <p className="text-lg font-black text-amber-700">-{userBalance.total_redeemed} pts</p>
              </div>
            </div>
          </div>

          {/* Adjustment Form */}
          <div className="eco-card p-6 space-y-4">
            <h3 className="text-base font-black text-slate-900">Execute Ledger Adjustment</h3>

            {adjustSuccess && (
              <div className="p-3 bg-eco-100 border border-eco-300 rounded-2xl text-eco-900 text-xs font-black flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-eco-700" />
                <span>{adjustSuccess}</span>
              </div>
            )}

            <form onSubmit={handleExecuteAdjustment} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                    Adjustment Points (+ or -)
                  </label>
                  <input
                    type="number"
                    required
                    placeholder="e.g. 50 or -20"
                    value={adjustmentPoints}
                    onChange={(e) => setAdjustmentPoints(Number(e.target.value))}
                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-black bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                    Reason / Audit Notes
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Campus cleanup event award"
                    value={adjustmentReason}
                    onChange={(e) => setAdjustmentReason(e.target.value)}
                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isAdjusting}
                className="btn-3d btn-3d-yellow w-full py-3.5 text-xs font-black flex items-center justify-center gap-2 shadow-3d-yellow"
              >
                {isAdjusting ? 'Executing Adjustment...' : 'Record Ledger Adjustment'}
              </button>
            </form>
          </div>

          {/* User Transactions Table */}
          <div className="eco-card space-y-3">
            <h3 className="text-base font-black text-slate-900">Transaction History</h3>
            {transactions.length === 0 ? (
              <p className="text-xs text-slate-400 font-bold text-center py-4">No transactions on record</p>
            ) : (
              <div className="space-y-2">
                {transactions.map((t) => (
                  <div
                    key={t.transaction_id}
                    className="p-3 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between text-xs"
                  >
                    <div>
                      <span className="font-bold text-slate-800">{t.reason || t.transaction_type}</span>
                      <p className="text-[10px] text-slate-400">{new Date(t.created_at).toLocaleString()}</p>
                    </div>
                    <span
                      className={`font-black px-2.5 py-1 rounded-full text-xs ${
                        t.points > 0 ? 'text-eco-800 bg-eco-100' : 'text-amber-800 bg-amber-100'
                      }`}
                    >
                      {t.points > 0 ? `+${t.points}` : t.points} pts
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
