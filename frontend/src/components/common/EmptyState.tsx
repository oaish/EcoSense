import React from 'react';
import { IconType } from 'react-icons';
import { LuLeaf } from 'react-icons/lu';

interface EmptyStateProps {
  icon?: IconType | React.ComponentType<{ className?: string }> | React.ReactNode | string;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionText,
  onAction,
  className = 'py-12',
}) => {
  const renderIcon = () => {
    if (!icon) {
      return <LuLeaf className="w-10 h-10 text-eco-600" />;
    }
    if (typeof icon === 'string') {
      return <LuLeaf className="w-10 h-10 text-eco-600" />;
    }
    if (React.isValidElement(icon)) {
      return icon;
    }
    const IconComp = icon as React.ComponentType<{ className?: string }>;
    return <IconComp className="w-10 h-10 text-eco-600" />;
  };

  return (
    <div className={`flex flex-col items-center justify-center text-center p-8 bg-white/70 rounded-3xl border border-slate-200 shadow-soft-card max-w-md mx-auto ${className}`}>
      <div className="w-20 h-20 rounded-3xl bg-eco-50 flex items-center justify-center mb-4 border-2 border-eco-200 shadow-sm animate-bounce-subtle">
        {renderIcon()}
      </div>
      <h3 className="text-xl font-extrabold text-slate-800 mb-2">{title}</h3>
      <p className="text-slate-500 text-sm font-medium mb-6 leading-relaxed">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="btn-3d btn-3d-green px-6 py-2.5 text-sm shadow-3d-green"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};
