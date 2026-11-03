import React, { useEffect } from 'react';
import confetti from 'canvas-confetti';
import { LuSparkles, LuX, LuCircleCheck, LuLeaf, LuStar } from 'react-icons/lu';

interface CelebrationModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  pointsEarned?: number;
  badgeText?: string;
}

export const CelebrationModal: React.FC<CelebrationModalProps> = ({
  isOpen,
  onClose,
  title,
  subtitle = 'Your contribution helps DBIT stay clean & green!',
  pointsEarned,
  badgeText = 'Sustainability Hero',
}) => {
  useEffect(() => {
    if (isOpen) {
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          colors: ['#10B981', '#F59E0B', '#38BDF8', '#F43F5E'],
        });
      } catch {
        // Fallback if canvas is unavailable
      }
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-md bg-white rounded-3xl p-8 shadow-2xl border-4 border-eco-300 text-center animate-bounce-subtle">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 transition-colors"
        >
          <LuX className="w-5 h-5" />
        </button>

        <div className="w-20 h-20 mx-auto rounded-3xl bg-eco-100 border-2 border-eco-300 text-eco-600 flex items-center justify-center mb-5 shadow-3d-green">
          <LuLeaf className="w-10 h-10" />
        </div>

        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-eco-100 text-eco-800 text-xs font-black uppercase tracking-wider mb-2 border border-eco-300">
          <LuSparkles className="w-3.5 h-3.5 text-eco-600" />
          {badgeText}
        </div>

        <h3 className="text-2xl font-black text-slate-900 mb-2">{title}</h3>
        <p className="text-slate-600 text-sm font-medium mb-6">{subtitle}</p>

        {pointsEarned !== undefined && pointsEarned > 0 && (
          <div className="p-4 bg-sun-50 rounded-2xl border-2 border-sun-300 mb-6 flex items-center justify-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-sun-300 text-slate-950 flex items-center justify-center shadow-xs">
              <LuStar className="w-6 h-6 fill-slate-950 text-slate-950" />
            </div>
            <div className="text-left">
              <span className="text-2xl font-black text-sun-900">+{pointsEarned} Points</span>
              <p className="text-xs font-bold text-sun-700">Added to your EcoSense balance!</p>
            </div>
          </div>
        )}

        <button
          onClick={onClose}
          className="btn-3d btn-3d-green w-full py-3.5 text-base font-extrabold flex items-center justify-center gap-2"
        >
          <LuCircleCheck className="w-5 h-5" />
          <span>Awesome, Keep Going!</span>
        </button>
      </div>
    </div>
  );
};
