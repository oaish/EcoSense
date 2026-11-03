import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { EcoStageBadge } from '../components/common/EcoStageBadge';
import { EcoStageCard } from '../components/common/EcoStageCard';
import { ConfirmModal } from '../components/common/ConfirmModal';
import { EcoStage } from '../types';

describe('Phase 12: Gamification & UI Components', () => {
  const mockStage: EcoStage = {
    stage_id: 3,
    stage_name: 'Eco Explorer',
    description: 'Actively exploring waste diversion opportunities.',
    flair_icon: 'compass',
    color_hex: '#0284c7',
    min_points: 300,
    next_stage_name: 'Sustainability Champion',
    next_stage_min_points: 750,
    points_to_next_stage: 300,
    progress_percentage: 42.5,
    lifetime_earned_points: 450,
    is_max_stage: false,
  };

  it('renders EcoStageBadge with correct stage name and styles', () => {
    render(<EcoStageBadge stageName="Eco Explorer" size="md" />);
    expect(screen.getByText('Eco Explorer')).toBeDefined();
  });

  it('renders EcoStageCard with progress bar and target points', () => {
    render(<EcoStageCard stage={mockStage} totalEarnedPoints={450} />);
    const stageTitles = screen.getAllByText('Eco Explorer');
    expect(stageTitles.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('450 / 750 pts')).toBeDefined();
    expect(screen.getByText(/300 pts to reach/i)).toBeDefined();
    expect(screen.getByText(/Sustainability Champion/i)).toBeDefined();
  });

  it('handles ConfirmModal callbacks correctly', () => {
    const handleConfirm = vi.fn();
    const handleCancel = vi.fn();

    render(
      <ConfirmModal
        isOpen={true}
        title="Deactivate User?"
        message="Are you sure you want to deactivate this account?"
        confirmText="Yes, Deactivate"
        isDestructive={true}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    );

    expect(screen.getByText('Deactivate User?')).toBeDefined();
    expect(screen.getByText('Are you sure you want to deactivate this account?')).toBeDefined();

    const confirmBtn = screen.getByText('Yes, Deactivate');
    fireEvent.click(confirmBtn);
    expect(handleConfirm).toHaveBeenCalledTimes(1);

    const cancelBtn = screen.getByText('Cancel');
    fireEvent.click(cancelBtn);
    expect(handleCancel).toHaveBeenCalledTimes(1);
  });
});
