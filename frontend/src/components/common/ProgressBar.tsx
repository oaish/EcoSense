import React from 'react';

interface ProgressBarProps {
  value: number; // 0 to 100
  max?: number;
  label?: string;
  sublabel?: string;
  variant?: 'green' | 'yellow' | 'coral' | 'blue';
  showPercentage?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  label,
  sublabel,
  variant = 'green',
  showPercentage = true,
}) => {
  const percentage = Math.min(Math.max(Math.round((value / max) * 100), 0), 100);

  const fillColors = {
    green: 'from-eco-400 to-eco-500',
    yellow: 'from-sun-400 to-sun-500',
    coral: 'from-coral-400 to-coral-500',
    blue: 'from-ocean-400 to-ocean-500',
  };

  return (
    <div className="w-full">
      {(label || showPercentage) && (
        <div className="flex items-center justify-between text-xs font-bold text-slate-700 mb-1.5">
          <span>{label}</span>
          {showPercentage && <span className="font-extrabold text-slate-900">{percentage}%</span>}
        </div>
      )}
      <div className="eco-progress-track">
        <div
          className={`eco-progress-fill bg-gradient-to-r ${fillColors[variant]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {sublabel && <p className="text-xs font-semibold text-slate-400 mt-1">{sublabel}</p>}
    </div>
  );
};
