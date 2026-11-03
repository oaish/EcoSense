import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PointsCard } from '../components/common/PointsCard';
import { StatCard } from '../components/common/StatCard';
import { ProgressBar } from '../components/common/ProgressBar';
import { StatusBadge } from '../components/common/StatusBadge';
import { LuPackage } from 'react-icons/lu';

describe('EcoSense Design System Components', () => {
  it('renders PointsCard with ledger points and streak badge', () => {
    render(
      <BrowserRouter>
        <PointsCard points={250} totalEarned={500} streakDays={5} />
      </BrowserRouter>
    );
    expect(screen.getByText('250')).toBeDefined();
    expect(screen.getByText('5 Day Active')).toBeDefined();
    expect(screen.getByText(/500 pts/)).toBeDefined();
  });

  it('renders StatCard with numeric value and title', () => {
    render(
      <StatCard
        title="Total Waste"
        value="1,240 kg"
        subtitle="Campus collection"
        icon={LuPackage}
        variant="green"
      />
    );
    expect(screen.getByText('Total Waste')).toBeDefined();
    expect(screen.getByText('1,240 kg')).toBeDefined();
    expect(screen.getByText('Campus collection')).toBeDefined();
  });

  it('renders ProgressBar with correct percentage calculation', () => {
    render(<ProgressBar value={75} max={100} label="Bin Fill Level" />);
    expect(screen.getByText('Bin Fill Level')).toBeDefined();
    expect(screen.getByText('75%')).toBeDefined();
  });

  it('renders StatusBadge with formatted status classes', () => {
    const { container } = render(<StatusBadge status="ACTIVE" type="bin" />);
    expect(screen.getByText('ACTIVE')).toBeDefined();
    expect(container.textContent).toContain('ACTIVE');
  });
});
