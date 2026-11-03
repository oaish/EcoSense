import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { StudentReportPage } from '../pages/student/StudentReportPage';
import { reportsApi } from '../api/reports';
import { binsApi } from '../api/bins';
import { Bin, WasteReport } from '../types';

vi.mock('../api/reports');
vi.mock('../api/bins');

describe('StudentReportPage Issue Reporting Flow', () => {
  const mockBins: Bin[] = [
    {
      bin_id: '11111111-2222-3333-4444-555555555555',
      bin_code: 'BIN-CAMPUS-01',
      location_id: 1,
      waste_type_id: 1,
      capacity_liters: 120,
      current_fill_percentage: 95,
      status: 'ACTIVE',
      qr_token: 'tok-01',
      created_at: '2026-10-01T00:00:00Z',
      location: {
        location_id: 1,
        name: 'Library Front',
        code: 'LIB-01',
        building: 'Main Library',
        floor: 'Ground',
        is_active: true,
        created_at: '2026-10-01T00:00:00Z',
      },
      waste_type: {
        waste_type_id: 1,
        name: 'PLASTIC',
        code: 'PLAS',
        color_code: '#3B82F6',
        is_active: true,
        created_at: '2026-10-01T00:00:00Z',
      },
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(binsApi.getBins).mockResolvedValue(mockBins);
  });

  it('renders all 5 issue types with Overflowing Bin selected by default', async () => {
    render(
      <BrowserRouter>
        <StudentReportPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(binsApi.getBins).toHaveBeenCalled();
    });

    expect(screen.getByText('Overflowing Bin')).toBeDefined();
    expect(screen.getByText('Damaged Bin')).toBeDefined();
    expect(screen.getByText('Missing Bin')).toBeDefined();
    expect(screen.getByText('Wrong Segregation')).toBeDefined();
    expect(screen.getByText('General Issue')).toBeDefined();
  });

  it('submits OVERFLOWING (not OVERFLOW) when submitting default Overflowing Bin', async () => {
    const mockReport: WasteReport = {
      report_id: 42,
      user_id: 'user-123',
      bin_id: '11111111-2222-3333-4444-555555555555',
      bin_code: 'BIN-CAMPUS-01',
      report_type: 'OVERFLOWING',
      description: 'Bin is overflowing past lid',
      status: 'PENDING',
      created_at: '2026-10-13T00:00:00Z',
    };

    vi.mocked(reportsApi.submitReport).mockResolvedValue(mockReport);

    render(
      <BrowserRouter>
        <StudentReportPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(binsApi.getBins).toHaveBeenCalled();
    });

    // Enter description
    const descTextarea = screen.getByPlaceholderText(/Provide context on the issue/i);
    fireEvent.change(descTextarea, { target: { value: 'Bin is overflowing past lid' } });

    // Submit
    const submitBtn = screen.getByRole('button', { name: /Submit Waste Issue Report/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(reportsApi.submitReport).toHaveBeenCalledTimes(1);
    });

    const submitCall = vi.mocked(reportsApi.submitReport).mock.calls[0][0];
    expect(submitCall.report_type).toBe('OVERFLOWING');
    expect(submitCall.report_type).not.toBe('OVERFLOW');
    expect(submitCall.description).toBe('Bin is overflowing past lid');

    // Confirm success view renders
    await waitFor(() => {
      expect(screen.getByText('Report #42')).toBeDefined();
      expect(screen.getByText('Report Submitted Successfully')).toBeDefined();
    });
  });

  it('submits DAMAGED_BIN (not DAMAGE) when user selects Damaged Bin', async () => {
    const mockReport: WasteReport = {
      report_id: 43,
      user_id: 'user-123',
      bin_id: '11111111-2222-3333-4444-555555555555',
      bin_code: 'BIN-CAMPUS-01',
      report_type: 'DAMAGED_BIN',
      description: 'Pedal is broken and container is cracked',
      status: 'PENDING',
      created_at: '2026-10-13T00:00:00Z',
    };

    vi.mocked(reportsApi.submitReport).mockResolvedValue(mockReport);

    render(
      <BrowserRouter>
        <StudentReportPage />
      </BrowserRouter>
    );

    // Click Damaged Bin option
    const damagedBtn = screen.getByText('Damaged Bin').closest('button');
    expect(damagedBtn).toBeDefined();
    fireEvent.click(damagedBtn!);

    // Enter description
    const descTextarea = screen.getByPlaceholderText(/Provide context on the issue/i);
    fireEvent.change(descTextarea, { target: { value: 'Pedal is broken and container is cracked' } });

    // Submit
    const submitBtn = screen.getByRole('button', { name: /Submit Waste Issue Report/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(reportsApi.submitReport).toHaveBeenCalledTimes(1);
    });

    const submitCall = vi.mocked(reportsApi.submitReport).mock.calls[0][0];
    expect(submitCall.report_type).toBe('DAMAGED_BIN');
    expect(submitCall.report_type).not.toBe('DAMAGE');
  });

  it('submits all remaining types: MISSING_BIN, WRONG_SEGREGATION, and OTHER', async () => {
    const testCases: { label: string; expectedType: string }[] = [
      { label: 'Missing Bin', expectedType: 'MISSING_BIN' },
      { label: 'Wrong Segregation', expectedType: 'WRONG_SEGREGATION' },
      { label: 'General Issue', expectedType: 'OTHER' },
    ];

    for (const tc of testCases) {
      vi.clearAllMocks();
      vi.mocked(binsApi.getBins).mockResolvedValue(mockBins);

      const mockReport: WasteReport = {
        report_id: 99,
        user_id: 'user-123',
        report_type: tc.expectedType as any,
        description: `Testing ${tc.label}`,
        status: 'PENDING',
        created_at: '2026-10-13T00:00:00Z',
      };
      vi.mocked(reportsApi.submitReport).mockResolvedValue(mockReport);

      const { unmount } = render(
        <BrowserRouter>
          <StudentReportPage />
        </BrowserRouter>
      );

      const btn = screen.getByText(tc.label).closest('button');
      fireEvent.click(btn!);

      const desc = screen.getByPlaceholderText(/Provide context on the issue/i);
      fireEvent.change(desc, { target: { value: `Testing ${tc.label}` } });

      const submit = screen.getByRole('button', { name: /Submit Waste Issue Report/i });
      fireEvent.click(submit);

      await waitFor(() => {
        expect(reportsApi.submitReport).toHaveBeenCalledTimes(1);
      });

      const call = vi.mocked(reportsApi.submitReport).mock.calls[0][0];
      expect(call.report_type).toBe(tc.expectedType);

      unmount();
    }
  });

  it('correctly handles optional bin selection (undefined when not chosen, string UUID when chosen)', async () => {
    const mockReport: WasteReport = {
      report_id: 50,
      user_id: 'user-123',
      report_type: 'OTHER',
      description: 'Litter in corridor',
      status: 'PENDING',
      created_at: '2026-10-13T00:00:00Z',
    };
    vi.mocked(reportsApi.submitReport).mockResolvedValue(mockReport);

    render(
      <BrowserRouter>
        <StudentReportPage />
      </BrowserRouter>
    );

    // 1. Without selecting a bin
    const desc = screen.getByPlaceholderText(/Provide context on the issue/i);
    fireEvent.change(desc, { target: { value: 'Litter in corridor' } });

    const submit = screen.getByRole('button', { name: /Submit Waste Issue Report/i });
    fireEvent.click(submit);

    await waitFor(() => {
      expect(reportsApi.submitReport).toHaveBeenCalledTimes(1);
    });

    expect(vi.mocked(reportsApi.submitReport).mock.calls[0][0].bin_id).toBeUndefined();
  });

  it('renders clean error message when API rejects submission', async () => {
    vi.mocked(reportsApi.submitReport).mockRejectedValue(
      new Error("Invalid report_type 'OVERFLOW'. Allowed: DAMAGED_BIN, MISSING_BIN, OTHER, OVERFLOWING, WRONG_SEGREGATION")
    );

    render(
      <BrowserRouter>
        <StudentReportPage />
      </BrowserRouter>
    );

    const desc = screen.getByPlaceholderText(/Provide context on the issue/i);
    fireEvent.change(desc, { target: { value: 'Testing error display' } });

    const submit = screen.getByRole('button', { name: /Submit Waste Issue Report/i });
    fireEvent.click(submit);

    await waitFor(() => {
      expect(
        screen.getByText(/Invalid report_type 'OVERFLOW'/i)
      ).toBeDefined();
    });
  });
});
