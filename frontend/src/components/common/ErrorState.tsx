import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went sideways',
  message = 'We could not fetch the latest sustainability records. Please verify backend connectivity.',
  onRetry,
  className = 'py-10',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center text-center p-8 bg-coral-50/60 rounded-3xl border-2 border-coral-200 shadow-soft-card max-w-lg mx-auto my-6 ${className}`}>
      <div className="w-16 h-16 rounded-3xl bg-coral-100 flex items-center justify-center mb-4 text-coral-600 shadow-sm border border-coral-300">
        <AlertCircle className="w-8 h-8" />
      </div>
      <h3 className="text-xl font-extrabold text-slate-800 mb-2">{title}</h3>
      <p className="text-slate-600 text-sm font-medium mb-6 leading-relaxed">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn-3d btn-3d-coral px-6 py-2.5 text-sm flex items-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Try Again</span>
        </button>
      )}
    </div>
  );
};
