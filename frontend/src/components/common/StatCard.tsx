import React from 'react';
import { LucideIcon } from 'lucide-react';
import { IconType } from 'react-icons';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon | IconType | React.ComponentType<{ className?: string }> | string;
  variant?: 'green' | 'yellow' | 'blue' | 'coral' | 'slate';
  badge?: string;
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  variant = 'green',
  badge,
  onClick,
}) => {
  const variantStyles = {
    green: {
      bg: 'bg-white hover:border-eco-300',
      iconBg: 'bg-eco-100 text-eco-700 border-eco-200',
      textColor: 'text-eco-900',
      accent: 'border-b-4 border-b-eco-400',
    },
    yellow: {
      bg: 'bg-white hover:border-sun-300',
      iconBg: 'bg-sun-100 text-sun-700 border-sun-200',
      textColor: 'text-slate-900',
      accent: 'border-b-4 border-b-sun-400',
    },
    blue: {
      bg: 'bg-white hover:border-ocean-300',
      iconBg: 'bg-ocean-100 text-ocean-700 border-ocean-200',
      textColor: 'text-slate-900',
      accent: 'border-b-4 border-b-ocean-400',
    },
    coral: {
      bg: 'bg-white hover:border-coral-300',
      iconBg: 'bg-coral-100 text-coral-700 border-coral-200',
      textColor: 'text-slate-900',
      accent: 'border-b-4 border-b-coral-400',
    },
    slate: {
      bg: 'bg-white hover:border-slate-300',
      iconBg: 'bg-slate-100 text-slate-700 border-slate-200',
      textColor: 'text-slate-900',
      accent: 'border-b-4 border-b-slate-300',
    },
  };

  const current = variantStyles[variant];

  return (
    <div
      onClick={onClick}
      className={`rounded-3xl p-6 shadow-soft-card border border-slate-200/80 transition-all duration-200 relative overflow-hidden ${current.bg} ${current.accent} ${
        onClick ? 'cursor-pointer hover:-translate-y-1 active:translate-y-0' : ''
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">{title}</p>
          <h3 className={`text-3xl font-extrabold ${current.textColor} tracking-tight`}>{value}</h3>
          {subtitle && <p className="text-xs font-semibold text-slate-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center text-2xl border shadow-xs shrink-0 ${current.iconBg}`}>
          {typeof icon === 'string' ? (
            <span>{icon}</span>
          ) : (
            React.createElement(icon, { className: 'w-7 h-7' })
          )}
        </div>
      </div>

      {badge && (
        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-600 bg-slate-50 px-2.5 py-0.5 rounded-full border border-slate-200">
            {badge}
          </span>
        </div>
      )}
    </div>
  );
};
