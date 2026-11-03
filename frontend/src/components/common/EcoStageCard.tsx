import React from 'react';
import { LuSparkles, LuArrowRight, LuFlame, LuAward } from 'react-icons/lu';
import { EcoStage } from '../../types';
import { EcoStageBadge } from './EcoStageBadge';

interface EcoStageCardProps {
  stage: EcoStage | null;
  totalEarnedPoints?: number;
  loading?: boolean;
  className?: string;
  onExploreClick?: () => void;
}

export const EcoStageCard: React.FC<EcoStageCardProps> = ({
  stage,
  totalEarnedPoints = 0,
  loading = false,
  className = '',
  onExploreClick,
}) => {
  if (loading || !stage) {
    return (
      <div className={`bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm animate-pulse ${className}`}>
        <div className="h-6 w-32 bg-slate-200 rounded-full mb-4"></div>
        <div className="h-4 w-48 bg-slate-100 rounded-full mb-6"></div>
        <div className="h-4 w-full bg-slate-100 rounded-full"></div>
      </div>
    );
  }

  const earned = stage.lifetime_earned_points ?? totalEarnedPoints ?? 0;
  const nextTarget = stage.next_stage_min_points ?? (stage.points_to_next_stage ? earned + stage.points_to_next_stage : 0);

  return (
    <div
      className={`relative overflow-hidden bg-gradient-to-br from-emerald-500 via-teal-600 to-emerald-700 text-white rounded-3xl p-6 sm:p-7 shadow-lg border-b-4 border-emerald-800 transition-all duration-300 hover:shadow-xl ${className}`}
    >
      {/* Soft 3D Glow overlay */}
      <div className="absolute top-0 right-0 -mt-8 -mr-8 w-48 h-48 bg-white/10 rounded-full blur-2xl pointer-events-none"></div>

      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-200 flex items-center gap-1.5">
              <LuAward className="w-4 h-4" />
              Sustainability Progression
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-3 mb-2">
            <h2 className="text-2xl sm:text-3xl font-black tracking-tight">{stage.stage_name}</h2>
            <EcoStageBadge stageName={stage.stage_name} size="sm" className="bg-white/20 text-white border-white/30 backdrop-blur-sm" />
          </div>

          <p className="text-sm text-emerald-100 max-w-xl mb-4 leading-relaxed">
            {stage.description || 'Keep sorting and disposing waste cleanly across DBIT campus to unlock higher sustainability tiers.'}
          </p>

          {/* Progress Bar Container */}
          <div className="space-y-2 max-w-md">
            <div className="flex justify-between items-center text-xs font-bold text-emerald-100">
              <span className="flex items-center gap-1">
                <LuFlame className="w-3.5 h-3.5 text-amber-300" />
                {nextTarget > 0 ? `${earned.toLocaleString()} / ${nextTarget.toLocaleString()} pts` : `${earned.toLocaleString()} Lifetime Pts Earned`}
              </span>
              <span>
                {stage.is_max_stage ? (
                  <span className="text-amber-300 font-extrabold">Max Stage Reached</span>
                ) : (
                  `${(stage.points_to_next_stage ?? 0).toLocaleString()} pts to reach ${stage.next_stage_name || 'Next Tier'}`
                )}
              </span>
            </div>

            <div className="w-full bg-black/20 rounded-full h-3.5 p-0.5 backdrop-blur-sm">
              <div
                className="bg-gradient-to-r from-amber-300 to-yellow-400 h-2.5 rounded-full transition-all duration-700 shadow-inner"
                style={{ width: `${Math.min(100, Math.max(0, stage.progress_percentage ?? 0))}%` }}
              ></div>
            </div>
          </div>
        </div>

        {onExploreClick && (
          <div className="flex-shrink-0">
            <button
              onClick={onExploreClick}
              className="inline-flex items-center gap-2 bg-white text-emerald-800 hover:bg-emerald-50 font-bold px-5 py-3 rounded-2xl shadow-md transition-transform duration-200 active:scale-95 border-b-2 border-slate-200"
            >
              <LuSparkles className="w-4 h-4 text-amber-500" />
              <span>Campus League</span>
              <LuArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
