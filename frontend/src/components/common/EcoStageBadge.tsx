import React from 'react';
import { LuSprout, LuCompass, LuMedal, LuShield, LuTrophy, LuSparkles } from 'react-icons/lu';

interface EcoStageBadgeProps {
  stageName: string;
  flairIcon?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

const STAGE_CONFIG: Record<string, { bg: string; text: string; border: string; icon: React.ComponentType<{ className?: string }> }> = {
  'Eco Seed': {
    bg: 'bg-emerald-50 text-emerald-700',
    text: 'text-emerald-700',
    border: 'border-emerald-200',
    icon: LuSprout,
  },
  'Green Sprout': {
    bg: 'bg-teal-50 text-teal-700',
    text: 'text-teal-700',
    border: 'border-teal-200',
    icon: LuSprout,
  },
  'Eco Explorer': {
    bg: 'bg-sky-50 text-sky-700',
    text: 'text-sky-700',
    border: 'border-sky-200',
    icon: LuCompass,
  },
  'Sustainability Champion': {
    bg: 'bg-purple-50 text-purple-700',
    text: 'text-purple-700',
    border: 'border-purple-200',
    icon: LuMedal,
  },
  'Eco Guardian': {
    bg: 'bg-amber-50 text-amber-700',
    text: 'text-amber-700',
    border: 'border-amber-200',
    icon: LuShield,
  },
  'Campus Earth Hero': {
    bg: 'bg-rose-50 text-rose-700',
    text: 'text-rose-700',
    border: 'border-rose-200',
    icon: LuTrophy,
  },
};

export const EcoStageBadge: React.FC<EcoStageBadgeProps> = ({
  stageName,
  size = 'md',
  showLabel = true,
  className = '',
}) => {
  const config = STAGE_CONFIG[stageName] || {
    bg: 'bg-emerald-50 text-emerald-700',
    text: 'text-emerald-700',
    border: 'border-emerald-200',
    icon: LuSparkles,
  };

  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-sm px-3 py-1 gap-1.5 font-medium',
    lg: 'text-base px-4 py-1.5 gap-2 font-semibold',
  }[size];

  const iconSizes = {
    sm: 'w-3.5 h-3.5',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded-full border shadow-sm transition-all duration-200 ${config.bg} ${config.border} ${sizeClasses} ${className}`}
      title={`Eco Stage: ${stageName}`}
    >
      <Icon className={`${iconSizes} flex-shrink-0 animate-pulse`} />
      {showLabel && <span>{stageName}</span>}
    </span>
  );
};
