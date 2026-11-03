import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { safePercentage, formatPercentage, formatWeight, formatNumber, formatDate } from '../utils/formatters';
import { BinQRPrintSheet } from '../components/common/BinQRPrintSheet';
import { EmptyState } from '../components/common/EmptyState';
import { Bin } from '../types';
import { LuCircleCheck } from 'react-icons/lu';

describe('Formatters and Global Null-Safety Utilities', () => {
  it('safePercentage protects against division by zero, null, undefined, and NaN', () => {
    expect(safePercentage(0, 0)).toBe(0);
    expect(safePercentage(10, 0)).toBe(0);
    expect(safePercentage(null, 100)).toBe(0);
    expect(safePercentage(50, null)).toBe(0);
    expect(safePercentage(undefined, undefined)).toBe(0);
    expect(safePercentage(NaN, 100)).toBe(0);
    expect(safePercentage(50, NaN)).toBe(0);
    expect(safePercentage(-5, 0)).toBe(0);
    expect(safePercentage(25, 100)).toBe(25);
    expect(safePercentage('25', '100')).toBe(25);
    expect(safePercentage(1, 3, 1)).toBe(33.3);
  });

  it('formatPercentage formats percentage strings safely', () => {
    expect(formatPercentage(null)).toBe('0%');
    expect(formatPercentage(undefined)).toBe('0%');
    expect(formatPercentage(NaN)).toBe('0%');
    expect(formatPercentage(0)).toBe('0%');
    expect(formatPercentage(75.4, 0)).toBe('75%');
    expect(formatPercentage(75.456, 1)).toBe('75.5%');
  });

  it('formatWeight formats weights in kg safely', () => {
    expect(formatWeight(null)).toBe('0 kg');
    expect(formatWeight(undefined)).toBe('0 kg');
    expect(formatWeight(0)).toBe('0 kg');
    expect(formatWeight(12.5)).toBe('12.5 kg');
    expect(formatWeight('45.2')).toBe('45.2 kg');
  });

  it('formatNumber formats numbers and counts safely', () => {
    expect(formatNumber(null)).toBe('0');
    expect(formatNumber(undefined)).toBe('0');
    expect(formatNumber(0)).toBe('0');
    expect(formatNumber(1500)).toBe('1,500');
  });

  it('formatDate formats dates safely', () => {
    expect(formatDate(null)).toBe('—');
    expect(formatDate(undefined)).toBe('—');
    expect(formatDate('invalid-date')).toBe('—');
  });
});

describe('EmptyState Component', () => {
  it('renders title, description, and action button', () => {
    const handleAction = vi.fn();
    render(
      <EmptyState
        icon={LuCircleCheck}
        title="No Waste Reports"
        description="There are currently no waste reports requiring attention. Everything looks good!"
        actionText="Clear Filter"
        onAction={handleAction}
      />
    );

    expect(screen.getByText('No Waste Reports')).toBeDefined();
    expect(screen.getByText(/There are currently no waste reports requiring attention/)).toBeDefined();
    
    const actionBtn = screen.getByText('Clear Filter');
    fireEvent.click(actionBtn);
    expect(handleAction).toHaveBeenCalledTimes(1);
  });
});

describe('BinQRPrintSheet Component (Bulk and Single QR Export)', () => {
  const mockBins: Bin[] = [
    {
      bin_id: 'bin-1-uuid',
      bin_code: 'AMPHI-WET-01',
      location_id: 1,
      waste_type_id: 1,
      status: 'ACTIVE',
      capacity_liters: 80,
      current_fill_percentage: 25,
      qr_token: '11111111-1111-1111-1111-111111111111',
      location: {
        location_id: 1,
        name: 'DBIT Amphitheatre',
        code: 'AMPHI',
        building: 'Central Plaza',
        floor: 'Ground Floor',
        is_active: true,
      },
      waste_type: {
        waste_type_id: 1,
        name: 'WET ORGANIC',
        code: 'WET',
        is_active: true,
      },
    },
    {
      bin_id: 'bin-2-uuid',
      bin_code: 'MAIN-DRY-02',
      location_id: 2,
      waste_type_id: 2,
      status: 'ACTIVE',
      capacity_liters: 100,
      current_fill_percentage: 60,
      qr_token: '22222222-2222-2222-2222-222222222222',
      location: {
        location_id: 2,
        name: 'Main Academic Building',
        code: 'MAIN',
        building: 'Main Block',
        floor: '2nd Floor',
        is_active: true,
      },
      waste_type: {
        waste_type_id: 2,
        name: 'DRY RECYCLABLE',
        code: 'DRY',
        is_active: true,
      },
    },
  ];

  it('renders printable placards for each bin with correct QR URLs', () => {
    const handleClose = vi.fn();
    render(<BinQRPrintSheet bins={mockBins} onClose={handleClose} />);

    // Header count
    expect(screen.getByText(/Bin QR Placards/)).toBeDefined();

    // Bin codes on separate placards
    expect(screen.getByText('AMPHI-WET-01')).toBeDefined();
    expect(screen.getByText('MAIN-DRY-02')).toBeDefined();

    // Waste streams
    expect(screen.getByText('WET ORGANIC')).toBeDefined();
    expect(screen.getByText('DRY RECYCLABLE')).toBeDefined();

    // Locations
    expect(screen.getByText('DBIT Amphitheatre')).toBeDefined();
    expect(screen.getByText('Main Academic Building')).toBeDefined();

    // Encoded URL displayed on sheet
    const origin = window.location.origin;
    expect(screen.getByText(`URL: ${origin}/bin/11111111-1111-1111-1111-111111111111`)).toBeDefined();
    expect(screen.getByText(`URL: ${origin}/bin/22222222-2222-2222-2222-222222222222`)).toBeDefined();

    // Close button
    const closeBtn = screen.getByText('Close');
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});

