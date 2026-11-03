import React from 'react';
import { BinStatus, ReportStatus, RedemptionStatus, ProcessingType } from '../../types';

interface StatusBadgeProps {
  status: BinStatus | ReportStatus | RedemptionStatus | ProcessingType | string;
  type?: 'bin' | 'report' | 'redemption' | 'processing' | 'generic';
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  type = 'generic',
  size = 'md',
}) => {
  const sizeClasses = size === 'sm' ? 'px-2.5 py-0.5 text-xs' : 'px-3.5 py-1 text-xs font-bold';

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-200';
  let label = status;

  // Format Status display
  const upper = String(status).toUpperCase();

  switch (upper) {
    case 'ACTIVE':
    case 'RESOLVED':
    case 'APPROVED':
    case 'FULFILLED':
    case 'COMPLETED':
      colorClasses = 'bg-eco-100 text-eco-800 border-eco-300';
      break;

    case 'PENDING':
    case 'IN_PROGRESS':
    case 'IN_REVIEW':
      colorClasses = 'bg-sun-100 text-sun-800 border-sun-300';
      break;

    case 'FULL':
    case 'MAINTENANCE':
    case 'HIGH':
    case 'OVERFLOWING':
      colorClasses = 'bg-amber-100 text-amber-800 border-amber-300';
      break;

    case 'DAMAGED':
    case 'DAMAGED_BIN':
    case 'REJECTED':
    case 'CANCELLED':
    case 'CRITICAL':
    case 'MISSING_BIN':
    case 'WRONG_SEGREGATION':
      colorClasses = 'bg-coral-100 text-coral-800 border-coral-300';
      break;

    case 'INACTIVE':
    case 'OFFLINE':
      colorClasses = 'bg-slate-100 text-slate-600 border-slate-300';
      break;

    case 'RECYCLING':
      colorClasses = 'bg-ocean-100 text-ocean-800 border-ocean-300';
      label = 'Recycling';
      break;

    case 'COMPOSTING':
      colorClasses = 'bg-eco-100 text-eco-800 border-eco-300';
      label = 'Composting';
      break;

    default:
      colorClasses = 'bg-slate-100 text-slate-700 border-slate-200';
  }

  // Readable format
  if (type === 'report' || type === 'bin') {
    label = upper.replace(/_/g, ' ');
  }

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-extrabold uppercase tracking-wider border shadow-xs ${sizeClasses} ${colorClasses}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80"></span>
      <span>{label}</span>
    </span>
  );
};
