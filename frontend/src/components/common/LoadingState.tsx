import React from 'react';
import { LuSparkles, LuLeaf } from 'react-icons/lu';

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading eco data...',
  className = 'py-12',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center text-center p-6 ${className}`}>
      <div className="relative mb-4">
        <div className="w-16 h-16 rounded-3xl bg-eco-100 flex items-center justify-center animate-bounce-subtle shadow-soft-card border-2 border-eco-200 text-eco-600">
          <LuLeaf className="w-8 h-8" />
        </div>
        <div className="absolute -top-1 -right-1 animate-pulse">
          <LuSparkles className="w-5 h-5 text-sun-500" />
        </div>
      </div>
      <p className="text-slate-600 font-bold text-base tracking-wide">{message}</p>
      <div className="mt-3 flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full bg-eco-400 animate-pulse"></span>
        <span className="w-2 h-2 rounded-full bg-eco-500 animate-pulse delay-150"></span>
        <span className="w-2 h-2 rounded-full bg-eco-600 animate-pulse delay-300"></span>
      </div>
    </div>
  );
};
