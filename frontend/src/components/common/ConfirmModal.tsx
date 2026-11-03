import React from 'react';
import { LuTriangleAlert, LuCheck, LuX } from 'react-icons/lu';

export interface ConfirmModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  confirmText?: string;
  cancelLabel?: string;
  cancelText?: string;
  confirmVariant?: 'danger' | 'primary' | 'warning';
  isDestructive?: boolean;
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  isOpen,
  title,
  message,
  confirmLabel,
  confirmText,
  cancelLabel,
  cancelText,
  confirmVariant,
  isDestructive = false,
  loading = false,
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;

  const actualConfirmText = confirmText || confirmLabel || 'Confirm';
  const actualCancelText = cancelText || cancelLabel || 'Cancel';
  const effectiveVariant = isDestructive ? 'danger' : (confirmVariant || 'primary');

  const variantStyles = {
    danger: 'bg-rose-500 hover:bg-rose-600 border-rose-700 text-white',
    warning: 'bg-amber-500 hover:bg-amber-600 border-amber-700 text-white',
    primary: 'bg-emerald-500 hover:bg-emerald-600 border-emerald-700 text-white',
  }[effectiveVariant];

  const iconStyles = {
    danger: 'bg-rose-100 text-rose-600',
    warning: 'bg-amber-100 text-amber-600',
    primary: 'bg-emerald-100 text-emerald-600',
  }[effectiveVariant];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-md bg-white rounded-3xl p-6 sm:p-7 shadow-2xl border border-slate-100 transition-all duration-300">
        <div className="flex items-start gap-4">
          <div className={`flex-shrink-0 w-12 h-12 rounded-2xl flex items-center justify-center shadow-inner ${iconStyles}`}>
            <LuTriangleAlert className="w-6 h-6" />
          </div>

          <div className="flex-1">
            <h3 className="text-xl font-bold text-slate-900 mb-1">{title}</h3>
            <p className="text-sm text-slate-600 leading-relaxed mb-6">{message}</p>

            <div className="flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={onCancel}
                disabled={loading}
                className="px-4 py-2.5 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-100 border border-slate-200 transition-all active:scale-95 disabled:opacity-50 flex items-center gap-1.5"
              >
                <LuX className="w-4 h-4" />
                {actualCancelText}
              </button>

              <button
                type="button"
                onClick={onConfirm}
                disabled={loading}
                className={`px-5 py-2.5 rounded-xl text-sm font-bold border-b-2 shadow-md transition-all active:scale-95 disabled:opacity-50 flex items-center gap-1.5 ${variantStyles}`}
              >
                {loading ? (
                  <span className="inline-block w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin"></span>
                ) : (
                  <LuCheck className="w-4 h-4" />
                )}
                {actualConfirmText}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
