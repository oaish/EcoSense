import React from 'react';
import { LuStar, LuFlame, LuGift, LuArrowRight, LuSparkles } from 'react-icons/lu';
import { Link } from 'react-router-dom';

interface PointsCardProps {
  points: number;
  totalEarned?: number;
  streakDays?: number;
  showRedeemLink?: boolean;
}

export const PointsCard: React.FC<PointsCardProps> = ({
  points,
  totalEarned = 0,
  streakDays = 1,
  showRedeemLink = true,
}) => {
  return (
    <div className="eco-card-sun relative overflow-hidden">
      {/* Background Soft Glow Illustration */}
      <div className="absolute -top-6 -right-6 w-32 h-32 bg-sun-200/50 rounded-full blur-2xl pointer-events-none"></div>

      <div className="relative z-10 flex flex-col md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-3xl bg-sun-400 text-slate-950 flex items-center justify-center shadow-3d-yellow border-2 border-sun-600 animate-bounce-subtle shrink-0">
            <LuStar className="w-8 h-8 fill-slate-950 text-slate-950" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider text-sun-800 bg-sun-200/80 px-2.5 py-0.5 rounded-full border border-sun-300 flex items-center gap-1">
                <LuSparkles className="w-3 h-3 text-sun-700" />
                <span>EcoSense Balance</span>
              </span>
              {streakDays > 0 && (
                <span className="streak-badge text-xs">
                  <LuFlame className="w-3.5 h-3.5 text-orange-600 fill-orange-500" />
                  {streakDays} Day Active
                </span>
              )}
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-4xl font-extrabold text-slate-900 tracking-tight">{points}</span>
              <span className="text-sm font-bold text-slate-600">points</span>
            </div>
            {totalEarned > 0 && (
              <p className="text-xs font-semibold text-slate-500 mt-0.5">
                Lifetime contribution: <span className="font-bold text-eco-700">{totalEarned} pts</span> earned
              </p>
            )}
          </div>
        </div>

        {showRedeemLink && (
          <div className="flex items-center w-full justify-center gap-3">
            <Link
              to="/rewards"
              className="btn-3d btn-3d-yellow px-5 py-3 text-sm flex items-center gap-2 shadow-3d-yellow w-full text-center justify-center font-extrabold"
            >
              <LuGift className="w-4 h-4 text-slate-950" />
              <span>Redeem Rewards</span>
              <LuArrowRight className="w-4 h-4 text-slate-950" />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};
