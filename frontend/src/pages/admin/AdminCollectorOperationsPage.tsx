import React, { useState, useEffect } from 'react';
import { attendanceApi } from '../../api/attendance';
import { tasksApi } from '../../api/tasks';
import { binsApi } from '../../api/bins';
import {
  AdminAttendanceOverview,
  CollectorShiftSummary,
  AttendanceRecord,
  CollectionTask,
  TaskType,
  TaskPriority,
  TaskStatus,
  Bin,
} from '../../types';
import { StatCard } from '../../components/common/StatCard';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import {
  LuUsers,
  LuUserCheck,
  LuUserX,
  LuClipboardList,
  LuClock,
  LuPlus,
  LuSearch,
  LuFilter,
  LuHistory,
  LuCircleCheck,
  LuTriangleAlert,
  LuX,
  LuRotateCcw,
  LuBan,
  LuTrash2,
  LuMapPin,
  LuFileText,
  LuCalendar,
  LuPhone,
  LuMessageSquare,
} from 'react-icons/lu';

export const AdminCollectorOperationsPage: React.FC = () => {
  const [overview, setOverview] = useState<AdminAttendanceOverview | null>(null);
  const [tasks, setTasks] = useState<CollectionTask[]>([]);
  const [bins, setBins] = useState<Bin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // View state
  const [activeTab, setActiveTab] = useState<'COLLECTORS' | 'TASKS'>('COLLECTORS');
  const [collectorSearch, setCollectorSearch] = useState('');
  const [taskStatusFilter, setTaskStatusFilter] = useState<string>('');

  // Modals
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedCollectorHistory, setSelectedCollectorHistory] = useState<{
    collector: CollectorShiftSummary;
    records: AttendanceRecord[];
    loading: boolean;
  } | null>(null);
  const [reassigningTask, setReassigningTask] = useState<CollectionTask | null>(null);
  const [cancellingTask, setCancellingTask] = useState<CollectionTask | null>(null);

  // Form states
  const [assignCollectorId, setAssignCollectorId] = useState('');
  const [assignType, setAssignType] = useState<TaskType>('COLLECTION');
  const [assignPriority, setAssignPriority] = useState<TaskPriority>('MEDIUM');
  const [assignBinId, setAssignBinId] = useState('');
  const [assignTitle, setAssignTitle] = useState('');
  const [assignInstructions, setAssignInstructions] = useState('');
  const [assignDueDate, setAssignDueDate] = useState('');
  const [formSubmitting, setFormSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Reassign & cancel states
  const [newCollectorId, setNewCollectorId] = useState('');
  const [reassignNotes, setReassignNotes] = useState('');
  const [cancelReason, setCancelReason] = useState('');

  // Collector phone management state
  const [selectedCollectorPhone, setSelectedCollectorPhone] = useState<CollectorShiftSummary | null>(null);
  const [phoneInput, setPhoneInput] = useState('');
  const [phoneModalSubmitting, setPhoneModalSubmitting] = useState(false);
  const [phoneModalError, setPhoneModalError] = useState<string | null>(null);
  const [phoneModalSuccess, setPhoneModalSuccess] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [ovData, tasksData, binsData] = await Promise.all([
        attendanceApi.getAdminOverview(),
        tasksApi.getTasks(),
        binsApi.getBins({ limit: 100 }).catch(() => []),
      ]);
      setOverview(ovData);
      setTasks(tasksData);
      setBins(binsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load collector operational data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpenPhoneModal = (col: CollectorShiftSummary) => {
    setSelectedCollectorPhone(col);
    setPhoneInput(col.phone_number || '');
    setPhoneModalError(null);
    setPhoneModalSuccess(null);
  };

  const handleSavePhone = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCollectorPhone) return;

    const trimmed = phoneInput.trim();
    setPhoneModalSubmitting(true);
    setPhoneModalError(null);
    setPhoneModalSuccess(null);

    try {
      await attendanceApi.updateCollectorPhone(
        selectedCollectorPhone.collector_id,
        trimmed.length > 0 ? trimmed : null
      );
      setPhoneModalSuccess('Collector phone number updated successfully.');
      await loadData();
      setTimeout(() => {
        setSelectedCollectorPhone(null);
      }, 900);
    } catch (err: any) {
      setPhoneModalError(err.message || 'Failed to update collector phone number.');
    } finally {
      setPhoneModalSubmitting(false);
    }
  };

  const handleRemovePhone = async () => {
    if (!selectedCollectorPhone) return;
    setPhoneModalSubmitting(true);
    setPhoneModalError(null);
    setPhoneModalSuccess(null);

    try {
      await attendanceApi.updateCollectorPhone(
        selectedCollectorPhone.collector_id,
        null
      );
      setPhoneModalSuccess('Collector phone number removed.');
      setPhoneInput('');
      await loadData();
      setTimeout(() => {
        setSelectedCollectorPhone(null);
      }, 900);
    } catch (err: any) {
      setPhoneModalError(err.message || 'Failed to remove collector phone number.');
    } finally {
      setPhoneModalSubmitting(false);
    }
  };

  const handleOpenHistoryModal = async (col: CollectorShiftSummary) => {
    setSelectedCollectorHistory({ collector: col, records: [], loading: true });
    try {
      const records = await attendanceApi.getCollectorHistory(col.collector_id);
      setSelectedCollectorHistory({ collector: col, records, loading: false });
    } catch {
      setSelectedCollectorHistory({ collector: col, records: [], loading: false });
    }
  };

  const handleAssignTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignCollectorId || !assignTitle.trim()) {
      setFormError('Please select a collector and enter a task title.');
      return;
    }

    setFormSubmitting(true);
    setFormError(null);

    try {
      const created = await tasksApi.createTask({
        task_type: assignType,
        collector_id: assignCollectorId,
        priority: assignPriority,
        title: assignTitle.trim(),
        instructions: assignInstructions.trim() || undefined,
        bin_id: assignBinId || undefined,
        due_date: assignDueDate ? new Date(assignDueDate).toISOString() : undefined,
      });

      setTasks((prev) => [created, ...prev]);
      setShowAssignModal(false);
      resetAssignForm();
      // Refresh overview counts
      loadData();
    } catch (err: any) {
      setFormError(err?.data?.detail || err.message || 'Failed to assign task.');
    } finally {
      setFormSubmitting(false);
    }
  };

  const resetAssignForm = () => {
    setAssignCollectorId('');
    setAssignType('COLLECTION');
    setAssignPriority('MEDIUM');
    setAssignBinId('');
    setAssignTitle('');
    setAssignInstructions('');
    setAssignDueDate('');
    setFormError(null);
  };

  const handleReassignSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reassigningTask || !newCollectorId) return;

    setFormSubmitting(true);
    try {
      const updated = await tasksApi.reassignTask(reassigningTask.task_id, {
        collector_id: newCollectorId,
        notes: reassignNotes.trim() || undefined,
      });
      setTasks((prev) => prev.map((t) => (t.task_id === reassigningTask.task_id ? updated : t)));
      setReassigningTask(null);
      setNewCollectorId('');
      setReassignNotes('');
      loadData();
    } catch (err: any) {
      alert(err?.data?.detail || err.message || 'Failed to reassign task.');
    } finally {
      setFormSubmitting(false);
    }
  };

  const handleCancelSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cancellingTask || !cancelReason.trim()) return;

    setFormSubmitting(true);
    try {
      const updated = await tasksApi.cancelTask(cancellingTask.task_id, {
        reason: cancelReason.trim(),
      });
      setTasks((prev) => prev.map((t) => (t.task_id === cancellingTask.task_id ? updated : t)));
      setCancellingTask(null);
      setCancelReason('');
      loadData();
    } catch (err: any) {
      alert(err?.data?.detail || err.message || 'Failed to cancel task.');
    } finally {
      setFormSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingState message="Loading collector availability & operations..." />;
  }

  if (error || !overview) {
    return <ErrorState message={error || 'Could not load data.'} onRetry={loadData} />;
  }

  const selectedCollectorObj = (overview.collectors || []).find((c) => c.collector_id === assignCollectorId);
  const isSelectedCollectorOffShift =
    selectedCollectorObj &&
    (selectedCollectorObj.status || (selectedCollectorObj as any).attendance_status) !== 'ON_SHIFT';

  // Filter collectors
  const filteredCollectors = (overview.collectors || []).filter((c) => {
    const name = c.collector_name || (c as any).name || '';
    const email = c.collector_email || (c as any).email || '';
    const query = (collectorSearch || '').toLowerCase();
    return name.toLowerCase().includes(query) || email.toLowerCase().includes(query);
  });

  // Filter tasks
  const filteredTasks = tasks.filter((t) => {
    if (taskStatusFilter && t.status !== taskStatusFilter) return false;
    return true;
  });

  return (
    <div className="max-w-6xl mx-auto py-4 space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-eco-800 bg-eco-100 px-3 py-1 rounded-full border border-eco-200">
            Field Workforce Management
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Collector Operations
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Daily shift attendance, real-time availability, and collection task assignments for DBIT campus.
          </p>
        </div>

        <button
          onClick={() => {
            resetAssignForm();
            setShowAssignModal(true);
          }}
          className="btn-3d btn-3d-green px-5 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-green shrink-0"
        >
          <LuPlus className="w-4 h-4" />
          <span>Assign Task</span>
        </button>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3.5">
        <StatCard
          title="Active Accounts"
          value={overview.total_collectors ?? 0}
          subtitle="Registered staff"
          icon={LuUsers}
          variant="blue"
        />
        <StatCard
          title="On Shift Today"
          value={overview.on_shift_count ?? (overview as any).on_shift_collectors ?? 0}
          subtitle="Checked in"
          icon={LuUserCheck}
          variant="green"
        />
        <StatCard
          title="Not Checked In"
          value={overview.not_checked_in_count ?? (overview as any).not_checked_in_collectors ?? 0}
          subtitle="Off-shift collectors"
          icon={LuUserX}
          variant="coral"
        />
        <StatCard
          title="Active Workload"
          value={overview.with_active_tasks_count ?? (overview as any).collectors_with_active_tasks ?? 0}
          subtitle="Collectors with jobs"
          icon={LuClipboardList}
          variant="yellow"
        />
        <StatCard
          title="Overdue Tasks"
          value={overview.overdue_tasks_count ?? 0}
          subtitle="Past due deadline"
          icon={LuClock}
          variant="coral"
        />
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('COLLECTORS')}
            className={`px-4 py-2 rounded-2xl text-xs font-black transition-all ${
              activeTab === 'COLLECTORS'
                ? 'bg-slate-900 text-white shadow-md'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Collector Availability ({(overview.collectors || []).length})
          </button>
          <button
            onClick={() => setActiveTab('TASKS')}
            className={`px-4 py-2 rounded-2xl text-xs font-black transition-all ${
              activeTab === 'TASKS'
                ? 'bg-slate-900 text-white shadow-md'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            All Campus Tasks ({tasks.length})
          </button>
        </div>

        <span className="text-[11px] font-bold text-slate-400">
          Campus Date: {overview.campus_date || new Date().toISOString().split('T')[0]} (IST)
        </span>
      </div>

      {/* TAB 1: COLLECTOR AVAILABILITY TABLE */}
      {activeTab === 'COLLECTORS' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div className="relative flex-1 max-w-sm">
              <LuSearch className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={collectorSearch}
                onChange={(e) => setCollectorSearch(e.target.value)}
                placeholder="Search collectors by name or email..."
                className="w-full pl-9 pr-4 py-2 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-eco-400"
              />
            </div>
          </div>

          <div className="eco-card p-0 overflow-hidden border border-slate-200">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-black uppercase tracking-wider text-slate-500">
                    <th className="py-3 px-4">Collector</th>
                    <th className="py-3 px-4">Contact Phone</th>
                    <th className="py-3 px-4">Attendance Status</th>
                    <th className="py-3 px-4">Shift Check-In</th>
                    <th className="py-3 px-4">Shift Check-Out</th>
                    <th className="py-3 px-4">Active Tasks</th>
                    <th className="py-3 px-4">Workload</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-xs">
                  {filteredCollectors.map((col) => (
                    <tr key={col.collector_id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-black text-slate-900">{col.collector_name || (col as any).name || 'Collector'}</div>
                        <div className="text-[11px] font-medium text-slate-500">{col.collector_email || (col as any).email || ''}</div>
                      </td>
                      <td className="py-3.5 px-4">
                        {col.phone_number ? (
                          <div className="space-y-1">
                            <div className="font-mono text-slate-900 font-bold flex items-center gap-1.5 text-xs">
                              <LuPhone className="w-3.5 h-3.5 text-slate-400" />
                              <span>{col.phone_number}</span>
                            </div>
                            <div>
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-black uppercase bg-eco-100 text-eco-800 border border-eco-200">
                                <LuPhone className="w-3 h-3 text-eco-600" />
                                Phone Set
                              </span>
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-1">
                            <span className="text-[11px] font-medium text-slate-400 italic block">No phone set</span>
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-black uppercase bg-slate-100 text-slate-600 border border-slate-200">
                              Unset
                            </span>
                          </div>
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        {(col.status === 'ON_SHIFT' || (col as any).attendance_status === 'ON_SHIFT') ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-black uppercase bg-eco-100 text-eco-800 border border-eco-300">
                            <span className="w-1.5 h-1.5 rounded-full bg-eco-500 animate-ping"></span>
                            ON SHIFT
                          </span>
                        ) : (col.status === 'CHECKED_OUT' || (col as any).attendance_status === 'CHECKED_OUT') ? (
                          <span className="px-2.5 py-1 rounded-full text-[10px] font-black uppercase bg-slate-100 text-slate-700 border border-slate-200">
                            CHECKED OUT
                          </span>
                        ) : (
                          <span className="px-2.5 py-1 rounded-full text-[10px] font-black uppercase bg-coral-100 text-coral-700 border border-coral-200">
                            NOT CHECKED IN
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-slate-700 font-medium">
                        {(col.active_session?.check_in_at || (col as any).check_in_at) ? (
                          new Date(col.active_session?.check_in_at || (col as any).check_in_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })
                        ) : col.last_session?.check_in_at ? (
                          <span className="text-slate-400">
                            {new Date(col.last_session.check_in_at).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </span>
                        ) : (
                          <span className="text-slate-300">—</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-slate-700 font-medium">
                        {((col.last_session?.check_out_at || (col as any).check_out_at) &&
                          (col.status === 'CHECKED_OUT' || (col as any).attendance_status === 'CHECKED_OUT')) ? (
                          new Date(col.last_session?.check_out_at || (col as any).check_out_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })
                        ) : (
                          <span className="text-slate-300">—</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="font-black text-slate-900">{col.active_task_count ?? (col as any).active_tasks_count ?? 0}</span>{' '}
                        <span className="text-slate-400 text-[11px]">tasks</span>
                      </td>
                      <td className="py-3.5 px-4">
                        {(col.active_task_count ?? (col as any).active_tasks_count ?? 0) === 0 ? (
                          <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded-md bg-eco-100 text-eco-800">
                            Available
                          </span>
                        ) : (col.active_task_count ?? (col as any).active_tasks_count ?? 0) <= 2 ? (
                          <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded-md bg-amber-100 text-amber-800">
                            Moderate
                          </span>
                        ) : (
                          <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded-md bg-coral-100 text-coral-800">
                            Heavy
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleOpenPhoneModal(col)}
                            title="Manage Phone & SMS"
                            className="p-1.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-100 text-xs font-bold flex items-center gap-1"
                          >
                            <LuPhone className="w-3.5 h-3.5 text-eco-600" />
                            <span>Phone</span>
                          </button>
                          <button
                            onClick={() => handleOpenHistoryModal(col)}
                            title="View Attendance History"
                            className="p-1.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-100 text-xs font-bold flex items-center gap-1"
                          >
                            <LuHistory className="w-3.5 h-3.5" />
                            <span>History</span>
                          </button>
                          <button
                            onClick={() => {
                              resetAssignForm();
                              setAssignCollectorId(col.collector_id);
                              setShowAssignModal(true);
                            }}
                            className="btn-3d btn-3d-green px-2.5 py-1 text-[11px] font-black flex items-center gap-1"
                          >
                            <LuPlus className="w-3 h-3" />
                            <span>Assign</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: TASKS MANAGEMENT TABLE */}
      {activeTab === 'TASKS' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <LuFilter className="w-4 h-4 text-slate-400" />
              <select
                value={taskStatusFilter}
                onChange={(e) => setTaskStatusFilter(e.target.value)}
                className="px-3.5 py-1.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-eco-400"
              >
                <option value="">All Statuses</option>
                <option value="ASSIGNED">Assigned</option>
                <option value="ACCEPTED">Accepted</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="COMPLETED">Completed</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </div>
          </div>

          <div className="eco-card p-0 overflow-hidden border border-slate-200">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/80 border-b border-slate-200 text-[11px] font-black uppercase tracking-wider text-slate-500">
                    <th className="py-3 px-4">Task</th>
                    <th className="py-3 px-4">Type</th>
                    <th className="py-3 px-4">Collector</th>
                    <th className="py-3 px-4">Priority</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Context</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-xs">
                  {filteredTasks.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-xs font-bold text-slate-400">
                        No tasks match the filter criteria.
                      </td>
                    </tr>
                  ) : (
                    filteredTasks.map((t) => (
                      <tr key={t.task_id} className="hover:bg-slate-50/60 transition-colors">
                        <td className="py-3.5 px-4">
                          <div className="font-black text-slate-900">#{t.task_id} {t.title}</div>
                          {t.instructions && (
                            <div className="text-[11px] text-slate-500 font-medium truncate max-w-xs">
                              {t.instructions}
                            </div>
                          )}
                        </td>
                        <td className="py-3.5 px-4">
                          <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded-md bg-slate-100 text-slate-700">
                            {t.task_type}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 font-bold text-slate-800">
                          {t.collector_name || t.collector_id}
                        </td>
                        <td className="py-3.5 px-4">
                          <span
                            className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-md ${
                              t.priority === 'URGENT'
                                ? 'bg-red-100 text-red-700'
                                : t.priority === 'HIGH'
                                ? 'bg-coral-100 text-coral-700'
                                : t.priority === 'MEDIUM'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-slate-100 text-slate-600'
                            }`}
                          >
                            {t.priority}
                          </span>
                        </td>
                        <td className="py-3.5 px-4">
                          <span
                            className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-md ${
                              t.status === 'COMPLETED'
                                ? 'bg-eco-100 text-eco-800'
                                : t.status === 'IN_PROGRESS'
                                ? 'bg-purple-100 text-purple-800'
                                : t.status === 'ACCEPTED'
                                ? 'bg-blue-100 text-blue-800'
                                : t.status === 'ASSIGNED'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-slate-100 text-slate-500'
                            }`}
                          >
                            {t.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-[11px] text-slate-600">
                          {t.bin_code && <div>Bin: {t.bin_code}</div>}
                          {t.report_id && <div>Report #{t.report_id}</div>}
                          {t.due_date && <div>Due: {new Date(t.due_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>}
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            {t.status !== 'COMPLETED' && t.status !== 'CANCELLED' && (
                              <>
                                <button
                                  onClick={() => {
                                    setReassigningTask(t);
                                    setNewCollectorId(t.collector_id);
                                    setReassignNotes('');
                                  }}
                                  title="Reassign Task"
                                  className="p-1.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-100 text-xs font-bold"
                                >
                                  <LuRotateCcw className="w-3.5 h-3.5" />
                                </button>
                                <button
                                  onClick={() => {
                                    setCancellingTask(t);
                                    setCancelReason('');
                                  }}
                                  title="Cancel Task"
                                  className="p-1.5 rounded-xl border border-slate-200 text-coral-600 hover:bg-coral-50 text-xs font-bold"
                                >
                                  <LuBan className="w-3.5 h-3.5" />
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ASSIGN TASK MODAL */}
      {showAssignModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-3xl p-6 w-full max-w-lg border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-black uppercase tracking-wider text-eco-700 bg-eco-100 px-2 py-0.5 rounded-full border border-eco-200">
                  Task Assignment
                </span>
                <h3 className="text-xl font-black text-slate-900 mt-1">Assign Task to Collector</h3>
              </div>
              <button
                onClick={() => setShowAssignModal(false)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <LuX className="w-5 h-5" />
              </button>
            </div>

            {formError && (
              <div className="p-3 rounded-xl bg-coral-50 border border-coral-200 text-xs font-bold text-coral-800 flex items-center gap-2">
                <LuTriangleAlert className="w-4 h-4 shrink-0" />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleAssignTask} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Task Type *
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['COLLECTION', 'INSPECTION', 'ISSUE_RESPONSE'] as TaskType[]).map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setAssignType(type)}
                      className={`py-2 rounded-xl text-xs font-black border transition-all ${
                        assignType === type
                          ? 'bg-slate-900 text-white border-slate-900'
                          : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Select Collector *
                </label>
                <select
                  value={assignCollectorId}
                  onChange={(e) => setAssignCollectorId(e.target.value)}
                  required
                  className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-eco-400"
                >
                  <option value="">-- Choose Collector --</option>
                  {/* On-shift first */}
                  {(overview.collectors || [])
                    .filter((c) => (c.status === 'ON_SHIFT' || (c as any).attendance_status === 'ON_SHIFT'))
                    .map((c) => (
                      <option key={c.collector_id} value={c.collector_id}>
                        🟢 [ON SHIFT] {c.collector_name || (c as any).name || 'Collector'} ({c.active_task_count ?? (c as any).active_tasks_count ?? 0} active tasks)
                      </option>
                    ))}
                  {/* Off-shift */}
                  {(overview.collectors || [])
                    .filter((c) => (c.status !== 'ON_SHIFT' && (c as any).attendance_status !== 'ON_SHIFT'))
                    .map((c) => (
                      <option key={c.collector_id} value={c.collector_id}>
                        ⚪ [OFF SHIFT] {c.collector_name || (c as any).name || 'Collector'} ({c.active_task_count ?? (c as any).active_tasks_count ?? 0} active tasks)
                      </option>
                    ))}
                </select>

                {isSelectedCollectorOffShift && (
                  <div className="mt-2 p-2.5 bg-amber-50 rounded-xl border border-amber-200 text-xs font-bold text-amber-900 flex items-center gap-2">
                    <LuTriangleAlert className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>
                      Notice: This collector has not checked in for today's shift. You may still assign this task for urgent campus requirements.
                    </span>
                  </div>
                )}
              </div>

              {assignType === 'COLLECTION' || assignType === 'INSPECTION' ? (
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                    Select Campus Bin (Optional)
                  </label>
                  <select
                    value={assignBinId}
                    onChange={(e) => setAssignBinId(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-eco-400"
                  >
                    <option value="">-- Choose Bin (Optional) --</option>
                    {bins.map((b) => (
                      <option key={b.bin_id} value={b.bin_id}>
                        {b.bin_code} - {b.location?.name || 'Location'} ({b.current_fill_percentage}% full)
                      </option>
                    ))}
                  </select>
                </div>
              ) : null}

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                    Priority *
                  </label>
                  <select
                    value={assignPriority}
                    onChange={(e) => setAssignPriority(e.target.value as TaskPriority)}
                    className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-eco-400"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                    Due Date / Time
                  </label>
                  <input
                    type="datetime-local"
                    value={assignDueDate}
                    onChange={(e) => setAssignDueDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-eco-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Task Title *
                </label>
                <input
                  type="text"
                  value={assignTitle}
                  onChange={(e) => setAssignTitle(e.target.value)}
                  placeholder="e.g. Empty 3rd Floor East Wing Organic Bin"
                  required
                  className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-eco-400"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Instructions (Optional)
                </label>
                <textarea
                  value={assignInstructions}
                  onChange={(e) => setAssignInstructions(e.target.value)}
                  placeholder="Provide specific instructions or precautions for the collector..."
                  rows={2}
                  className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-eco-400"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAssignModal(false)}
                  className="px-4 py-2.5 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={formSubmitting}
                  className="btn-3d btn-3d-green px-5 py-2.5 text-xs font-black flex items-center gap-2 shadow-3d-green disabled:opacity-50"
                >
                  <LuCircleCheck className="w-4 h-4" />
                  <span>{formSubmitting ? 'Assigning...' : 'Assign Task'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* COLLECTOR ATTENDANCE HISTORY MODAL */}
      {selectedCollectorHistory && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-3xl p-6 w-full max-w-lg border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-black uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
                  Attendance Records
                </span>
                <h3 className="text-xl font-black text-slate-900 mt-1">
                  {selectedCollectorHistory.collector.collector_name || (selectedCollectorHistory.collector as any).name || 'Collector'}
                </h3>
              </div>
              <button
                onClick={() => setSelectedCollectorHistory(null)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <LuX className="w-5 h-5" />
              </button>
            </div>

            {selectedCollectorHistory.loading ? (
              <div className="py-8 text-center text-xs font-bold text-slate-400">Loading history...</div>
            ) : selectedCollectorHistory.records.length === 0 ? (
              <div className="py-8 text-center text-xs font-bold text-slate-400">
                No past attendance records found for this collector.
              </div>
            ) : (
              <div className="max-h-72 overflow-y-auto space-y-2">
                {selectedCollectorHistory.records.map((rec) => (
                  <div
                    key={rec.attendance_id}
                    className="p-3 bg-slate-50 rounded-2xl border border-slate-200 text-xs flex items-center justify-between"
                  >
                    <div>
                      <div className="font-black text-slate-900 flex items-center gap-2">
                        <span>{rec.attendance_date}</span>
                        <span
                          className={`text-[9px] font-black uppercase px-2 py-0.5 rounded-full ${
                            rec.status === 'ON_SHIFT'
                              ? 'bg-eco-100 text-eco-800'
                              : 'bg-slate-200 text-slate-700'
                          }`}
                        >
                          {rec.status}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        In: {new Date(rec.check_in_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        {rec.check_out_at && (
                          <> • Out: {new Date(rec.check_out_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</>
                        )}
                      </div>
                    </div>
                    {rec.notes && (
                      <span className="text-[11px] text-slate-400 italic max-w-xs truncate">
                        "{rec.notes}"
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* REASSIGN TASK MODAL */}
      {reassigningTask && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-3xl p-6 w-full max-w-md border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-black text-slate-900">
                Reassign Task #{reassigningTask.task_id}
              </h3>
              <button
                onClick={() => setReassigningTask(null)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <LuX className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-600 font-medium">
              Currently assigned to: <strong>{reassigningTask.collector_name || reassigningTask.collector_id}</strong>
            </p>

            <form onSubmit={handleReassignSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  New Collector *
                </label>
                <select
                  value={newCollectorId}
                  onChange={(e) => setNewCollectorId(e.target.value)}
                  required
                  className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-eco-400"
                >
                  <option value="">-- Select New Collector --</option>
                  {(overview.collectors || []).map((c) => (
                    <option key={c.collector_id} value={c.collector_id}>
                      {(c.status === 'ON_SHIFT' || (c as any).attendance_status === 'ON_SHIFT') ? '🟢' : '⚪'} {c.collector_name || (c as any).name || 'Collector'} ({c.active_task_count ?? (c as any).active_tasks_count ?? 0} active tasks)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Reassignment Reason / Note
                </label>
                <textarea
                  value={reassignNotes}
                  onChange={(e) => setReassignNotes(e.target.value)}
                  placeholder="e.g. Workload redistribution or shift handoff"
                  rows={2}
                  className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-eco-400"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setReassigningTask(null)}
                  className="px-4 py-2 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={formSubmitting}
                  className="btn-3d btn-3d-blue px-4 py-2 text-xs font-black shadow-3d-blue disabled:opacity-50"
                >
                  {formSubmitting ? 'Reassigning...' : 'Confirm Reassign'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CANCEL TASK MODAL */}
      {cancellingTask && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-3xl p-6 w-full max-w-md border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-black text-slate-900">
                Cancel Task #{cancellingTask.task_id}
              </h3>
              <button
                onClick={() => setCancellingTask(null)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <LuX className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-600 font-medium">
              Are you sure you want to cancel "{cancellingTask.title}"?
            </p>

            <form onSubmit={handleCancelSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Cancellation Reason *
                </label>
                <textarea
                  value={cancelReason}
                  onChange={(e) => setCancelReason(e.target.value)}
                  placeholder="e.g. Issue resolved by housekeeping staff; no longer needed."
                  required
                  rows={3}
                  className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-coral-400"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setCancellingTask(null)}
                  className="px-4 py-2 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={formSubmitting}
                  className="btn-3d btn-3d-coral px-4 py-2 text-xs font-black shadow-3d-coral disabled:opacity-50"
                >
                  {formSubmitting ? 'Cancelling...' : 'Confirm Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* MANAGE COLLECTOR PHONE MODAL */}
      {selectedCollectorPhone && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-3xl p-6 w-full max-w-md border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-xl bg-eco-100 text-eco-700 flex items-center justify-center">
                  <LuPhone className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-black text-slate-900">
                    Collector Contact & Phone
                  </h3>
                  <p className="text-xs text-slate-500 font-medium">
                    {selectedCollectorPhone.collector_name || (selectedCollectorPhone as any).name || 'Collector'} ({selectedCollectorPhone.collector_email || (selectedCollectorPhone as any).email || ''})
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedCollectorPhone(null)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <LuX className="w-5 h-5" />
              </button>
            </div>

            {phoneModalError && (
              <div className="p-3 rounded-xl bg-coral-50 border border-coral-200 text-xs font-bold text-coral-700 flex items-center gap-2">
                <LuTriangleAlert className="w-4 h-4 shrink-0 text-coral-500" />
                <span>{phoneModalError}</span>
              </div>
            )}

            {phoneModalSuccess && (
              <div className="p-3 rounded-xl bg-eco-50 border border-eco-200 text-xs font-bold text-eco-700 flex items-center gap-2">
                <LuCircleCheck className="w-4 h-4 shrink-0 text-eco-600" />
                <span>{phoneModalSuccess}</span>
              </div>
            )}

            <form onSubmit={handleSavePhone} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Mobile Number (Indian 10-digit / E.164)
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <LuPhone className="w-4 h-4" />
                  </span>
                  <input
                    type="tel"
                    value={phoneInput}
                    onChange={(e) => {
                      setPhoneInput(e.target.value);
                      setPhoneModalError(null);
                    }}
                    placeholder="+919876543210 or 9876543210"
                    className="w-full pl-10 pr-4 py-2.5 rounded-2xl border border-slate-200 text-xs font-mono font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-eco-400"
                  />
                </div>
                <p className="text-[11px] text-slate-500 mt-1.5 leading-relaxed">
                  Enter an Indian 10-digit mobile number (e.g. 9876543210) or with country code (+919876543210). Numbers are normalized to standard E.164 format. Clear and save empty to remove.
                </p>
              </div>

              <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200 space-y-1">
                <div className="text-[11px] font-black uppercase text-slate-600 flex items-center gap-1">
                  <LuPhone className="w-3.5 h-3.5 text-eco-600" />
                  Direct Collector Contact
                </div>
                <p className="text-[11px] text-slate-500 leading-relaxed">
                  Phone numbers are maintained for administrator records and operational communications. Push alerts are dispatched via Firebase Cloud Messaging.
                </p>
              </div>

              <div className="flex items-center justify-between pt-2">
                {selectedCollectorPhone.phone_number ? (
                  <button
                    type="button"
                    onClick={handleRemovePhone}
                    disabled={phoneModalSubmitting}
                    className="px-3 py-1.5 rounded-xl text-xs font-bold text-coral-600 hover:bg-coral-50 border border-coral-200 transition-colors disabled:opacity-50"
                  >
                    Remove Number
                  </button>
                ) : <div />}

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setSelectedCollectorPhone(null)}
                    className="px-4 py-2 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={phoneModalSubmitting}
                    className="btn-3d btn-3d-green px-4 py-2 text-xs font-black shadow-3d-green disabled:opacity-50"
                  >
                    {phoneModalSubmitting ? 'Saving...' : 'Save Phone'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
