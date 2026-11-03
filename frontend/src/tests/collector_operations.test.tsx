import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { CollectorDashboard } from '../pages/collector/CollectorDashboard';
import { CollectorTasksPage } from '../pages/collector/CollectorTasksPage';
import { AdminCollectorOperationsPage } from '../pages/admin/AdminCollectorOperationsPage';
import { attendanceApi } from '../api/attendance';
import { tasksApi } from '../api/tasks';
import { binsApi } from '../api/bins';
import { collectionsApi } from '../api/collections';
import { AttendanceRecord, CollectionTask, AdminAttendanceOverview } from '../types';

vi.mock('../api/attendance');
vi.mock('../api/tasks');
vi.mock('../api/bins');
vi.mock('../api/collections');
vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: {
      user_id: 'col-user-1',
      name: 'John Collector',
      email: 'john@dbit.ac.in',
      role: 'COLLECTOR',
      is_active: true,
    },
  }),
}));

describe('Collector Operations & Attendance Module', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('CollectorDashboard shows off-shift state and allows check-in', async () => {
    vi.mocked(binsApi.getBins).mockResolvedValue([]);
    vi.mocked(collectionsApi.getCollections).mockResolvedValue([]);
    vi.mocked(attendanceApi.getMyActiveShift).mockResolvedValue(null);
    vi.mocked(tasksApi.getMyTasks).mockResolvedValue([]);

    const mockNewShift: AttendanceRecord = {
      attendance_id: 101,
      collector_id: 'col-user-1',
      attendance_date: '2026-10-13',
      check_in_at: '2026-10-13T08:00:00Z',
      status: 'ON_SHIFT',
    };
    vi.mocked(attendanceApi.checkIn).mockResolvedValue(mockNewShift);

    render(
      <BrowserRouter>
        <CollectorDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Shift Not Started/i)).toBeDefined();
      expect(screen.getByText(/Start Shift/i)).toBeDefined();
    });

    const startShiftBtn = screen.getByText(/Start Shift/i);
    fireEvent.click(startShiftBtn);

    await waitFor(() => {
      expect(attendanceApi.checkIn).toHaveBeenCalled();
      expect(screen.getByText(/Currently On Shift/i)).toBeDefined();
      expect(screen.getByText(/End Shift/i)).toBeDefined();
    });
  });

  it('CollectorTasksPage renders assigned tasks and supports accepting task', async () => {
    const mockTasks: CollectionTask[] = [
      {
        task_id: 201,
        task_type: 'COLLECTION',
        collector_id: 'col-user-1',
        bin_id: 'bin-123',
        priority: 'HIGH',
        title: 'Empty Main Cafeteria Bin',
        instructions: 'Clean area after emptying',
        status: 'ASSIGNED',
        created_by: 'admin-1',
        assigned_at: '2026-10-13T08:30:00Z',
        created_at: '2026-10-13T08:30:00Z',
        bin_code: 'BIN-CAFE-01',
      },
    ];
    vi.mocked(tasksApi.getMyTasks).mockResolvedValue(mockTasks);

    const acceptedTask: CollectionTask = {
      ...mockTasks[0],
      status: 'ACCEPTED',
    };
    vi.mocked(tasksApi.updateStatus).mockResolvedValue(acceptedTask);

    render(
      <BrowserRouter>
        <CollectorTasksPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Empty Main Cafeteria Bin/i)).toBeDefined();
      expect(screen.getByText(/Accept Task/i)).toBeDefined();
    });

    fireEvent.click(screen.getByText(/Accept Task/i));

    await waitFor(() => {
      expect(tasksApi.updateStatus).toHaveBeenCalledWith(201, { status: 'ACCEPTED' });
      expect(screen.getByText(/Start Work/i)).toBeDefined();
    });
  });

  it('AdminCollectorOperationsPage renders overview cards and collector table', async () => {
    const mockOverview: AdminAttendanceOverview = {
      total_collectors: 2,
      on_shift_count: 1,
      not_checked_in_count: 1,
      with_active_tasks_count: 1,
      overdue_tasks_count: 0,
      campus_date: '2026-10-13',
      collectors: [
        {
          collector_id: 'col-user-1',
          collector_name: 'John Collector',
          collector_email: 'john@dbit.ac.in',
          is_active: true,
          status: 'ON_SHIFT',
          active_task_count: 1,
          active_session: {
            attendance_id: 101,
            collector_id: 'col-user-1',
            attendance_date: '2026-10-13',
            check_in_at: '2026-10-13T08:00:00Z',
            status: 'ON_SHIFT',
          },
        },
        {
          collector_id: 'col-user-2',
          collector_name: 'Jane Collector',
          collector_email: 'jane@dbit.ac.in',
          is_active: true,
          status: 'NOT_CHECKED_IN',
          active_task_count: 0,
        },
      ],
    };

    vi.mocked(attendanceApi.getAdminOverview).mockResolvedValue(mockOverview);
    vi.mocked(tasksApi.getTasks).mockResolvedValue([]);
    vi.mocked(binsApi.getBins).mockResolvedValue([]);

    render(
      <BrowserRouter>
        <AdminCollectorOperationsPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /Collector Operations/i })).toBeDefined();
      expect(screen.getByText('John Collector')).toBeDefined();
      expect(screen.getByText('Jane Collector')).toBeDefined();
      expect(screen.getAllByText(/ON SHIFT/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/NOT CHECKED IN/i).length).toBeGreaterThan(0);
    });
  });

  it('AdminCollectorOperationsPage allows viewing and updating collector phone number', async () => {
    const mockOverview: AdminAttendanceOverview = {
      total_collectors: 1,
      on_shift_count: 1,
      not_checked_in_count: 0,
      with_active_tasks_count: 0,
      overdue_tasks_count: 0,
      campus_date: '2026-10-13',
      collectors: [
        {
          collector_id: 'col-user-1',
          collector_name: 'Rajesh Collector',
          collector_email: 'rajesh@dbit.ac.in',
          phone_number: '+919876543210',
          has_sms_configured: true,
          is_active: true,
          status: 'ON_SHIFT',
          active_task_count: 0,
        },
      ],
    };

    vi.mocked(attendanceApi.getAdminOverview).mockResolvedValue(mockOverview);
    vi.mocked(tasksApi.getTasks).mockResolvedValue([]);
    vi.mocked(binsApi.getBins).mockResolvedValue([]);
    vi.mocked(attendanceApi.updateCollectorPhone).mockResolvedValue(undefined as any);

    render(
      <BrowserRouter>
        <AdminCollectorOperationsPage />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('+919876543210')).toBeDefined();
      expect(screen.getByText(/Phone Set/i)).toBeDefined();
    });

    // Click Phone action button
    const phoneBtn = screen.getByRole('button', { name: /Phone/i });
    fireEvent.click(phoneBtn);

    await waitFor(() => {
      expect(screen.getByText(/Collector Contact & Phone/i)).toBeDefined();
    });

    const input = screen.getByPlaceholderText(/\+919876543210 or 9876543210/i);
    fireEvent.change(input, { target: { value: '+919123456789' } });

    const saveBtn = screen.getByRole('button', { name: /Save Phone/i });
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(attendanceApi.updateCollectorPhone).toHaveBeenCalledWith('col-user-1', '+919123456789');
    });
  });
});

