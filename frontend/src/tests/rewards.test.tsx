import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { RewardsCatalogPage } from '../pages/student/RewardsCatalogPage';
import { rewardsApi } from '../api/rewards';
import { gamificationApi } from '../api/gamification';
import { Reward, PointBalanceRead } from '../types';

vi.mock('../api/rewards');
vi.mock('../api/gamification');

describe('RewardsCatalogPage points calculation and display', () => {
  const mockReward: Reward = {
    reward_id: 1,
    name: 'Campus Canteen Meal Voucher',
    description: 'Enjoy a free meal voucher worth ₹100 at the DBIT campus canteen.',
    points_cost: 100,
    stock_quantity: 50,
    is_active: true,
    created_at: '2026-10-04T00:00:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays 100 pts and "Need 100 more pts" when user balance is 0', async () => {
    vi.mocked(rewardsApi.getRewards).mockResolvedValue([mockReward]);
    vi.mocked(gamificationApi.getMyPoints).mockResolvedValue({
      user_id: 'test-user',
      current_balance: 0,
      total_earned: 10,
      total_redeemed: 10,
    });

    render(
      <BrowserRouter>
        <RewardsCatalogPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Campus Canteen Meal Voucher')).toBeDefined();
    });

    expect(screen.getByText('100 pts')).toBeDefined();
    expect(screen.getByText('Need 100 more pts')).toBeDefined();
    const button = screen.getByText('Need 100 more pts').closest('button');
    expect(button?.disabled).toBe(true);
  });

  it('displays "Need 50 more pts" when user balance is 50', async () => {
    vi.mocked(rewardsApi.getRewards).mockResolvedValue([mockReward]);
    vi.mocked(gamificationApi.getMyPoints).mockResolvedValue({
      user_id: 'test-user',
      current_balance: 50,
      total_earned: 50,
      total_redeemed: 0,
    });

    render(
      <BrowserRouter>
        <RewardsCatalogPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Campus Canteen Meal Voucher')).toBeDefined();
    });

    expect(screen.getByText('Need 50 more pts')).toBeDefined();
    const button = screen.getByText('Need 50 more pts').closest('button');
    expect(button?.disabled).toBe(true);
  });

  it('displays "Redeem for 100 pts" and enables button when user balance is 100', async () => {
    vi.mocked(rewardsApi.getRewards).mockResolvedValue([mockReward]);
    vi.mocked(gamificationApi.getMyPoints).mockResolvedValue({
      user_id: 'test-user',
      current_balance: 100,
      total_earned: 100,
      total_redeemed: 0,
    });

    render(
      <BrowserRouter>
        <RewardsCatalogPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Campus Canteen Meal Voucher')).toBeDefined();
    });

    expect(screen.getByText('Redeem for 100 pts')).toBeDefined();
    const button = screen.getByText('Redeem for 100 pts').closest('button');
    expect(button?.disabled).toBe(false);
  });

  it('allows redemption when user balance is 150', async () => {
    vi.mocked(rewardsApi.getRewards).mockResolvedValue([mockReward]);
    vi.mocked(gamificationApi.getMyPoints).mockResolvedValue({
      user_id: 'test-user',
      current_balance: 150,
      total_earned: 150,
      total_redeemed: 0,
    });

    render(
      <BrowserRouter>
        <RewardsCatalogPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Campus Canteen Meal Voucher')).toBeDefined();
    });

    expect(screen.getByText('Redeem for 100 pts')).toBeDefined();
    const button = screen.getByText('Redeem for 100 pts').closest('button');
    expect(button?.disabled).toBe(false);
  });
});
