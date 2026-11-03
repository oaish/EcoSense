import React, { useState, useEffect } from 'react';
import { reportsApi } from '../../api/reports';
import { tasksApi } from '../../api/tasks';
import { attendanceApi } from '../../api/attendance';
import { WasteReport, ReportStatus, CollectorShiftSummary, TaskPriority } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { Filter, X, Calendar, User, MapPin } from 'lucide-react';
import {
  LuCircleCheck,
  LuCircleX,
  LuClipboardList,
  LuTriangleAlert,
} from 'react-icons/lu';

export const AdminReportsPage: React.FC = () => {
  const [reports, setReports] = useState<WasteReport[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Resolution Modal State
  const [resolvingReport, setResolvingReport] = useState<WasteReport | null>(null);
  const [resolutionStatus, setResolutionStatus] = useState<ReportStatus>('RESOLVED');
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Delegation Modal State
  const [delegatingReport, setDelegatingReport] = useState<WasteReport | null>(null);
  const [collectors, setCollectors] = useState<CollectorShiftSummary[]>([]);
  const [delegateCollectorId, setDelegateCollectorId] = useState('');
  const [delegatePriority, setDelegatePriority] = useState<TaskPriority>('HIGH');
  const [delegateInstructions, setDelegateInstructions] = useState('');
  const [delegateDueDate, setDelegateDueDate] = useState('');
  const [isDelegating, setIsDelegating] = useState(false);
  const [delegationFeedback, setDelegationFeedback] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchReports = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await reportsApi.getReports({
        status: statusFilter || undefined,
        limit: 100,
      });
      setReports(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch waste reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [statusFilter]);

  const handleUpdateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolvingReport) return;

    setIsSubmitting(true);
    try {
      await reportsApi.updateReport(resolvingReport.report_id, {
        status: resolutionStatus,
        resolution_notes: resolutionNotes.trim() || undefined,
      });
      setResolvingReport(null);
      setResolutionNotes('');
      fetchReports();
    } catch (err: any) {
      alert(err.message || 'Failed to update report status.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpenDelegate = async (report: WasteReport) => {
    setDelegatingReport(report);
    setDelegateCollectorId('');
    setDelegatePriority('HIGH');
    setDelegateInstructions(`Please investigate and address reported campus issue: ${report.report_type.replace(/_/g, ' ')}. ${report.description ? `Details: ${report.description}` : ''}`);
    setDelegateDueDate('');
    setDelegationFeedback(null);

    try {
      const overview = await attendanceApi.getAdminOverview();
      setCollectors(overview.collectors);
      // Pre-select first on-shift collector if available
      const onShift = overview.collectors.find((c) => c.status === 'ON_SHIFT');
      if (onShift) {
        setDelegateCollectorId(onShift.collector_id);
      }
    } catch {
      setCollectors([]);
    }
  };

  const handleDelegateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!delegatingReport || !delegateCollectorId) return;

    setIsDelegating(true);
    setDelegationFeedback(null);

    try {
      await tasksApi.delegateReport({
        report_id: delegatingReport.report_id,
        collector_id: delegateCollectorId,
        priority: delegatePriority,
        instructions: delegateInstructions.trim() || undefined,
        due_date: delegateDueDate ? new Date(delegateDueDate).toISOString() : undefined,
      });

      setDelegationFeedback({
        type: 'success',
        text: `Task successfully assigned to collector! Report #${delegatingReport.report_id} status updated to IN_PROGRESS.`,
      });
      setDelegatingReport(null);
      fetchReports();
    } catch (err: any) {
      setDelegationFeedback({
        type: 'error',
        text: err?.data?.detail || err.message || 'Failed to delegate report.',
      });
    } finally {
      setIsDelegating(false);
    }
  };

  const selectedCol = collectors.find((c) => c.collector_id === delegateCollectorId);
  const isSelectedOffShift = selectedCol && selectedCol.status !== 'ON_SHIFT';

  return (
    <div className="max-w-6xl mx-auto py-4 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-coral-700 bg-coral-100 px-3 py-1 rounded-full border border-coral-200">
            Operations & Quality
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Waste Reports Management
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Review reported campus issues, delegate response tasks to collectors, and resolve issues to award points.
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-coral-400"
          >
            <option value="">All Statuses</option>
            <option value="PENDING">Pending Review</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="RESOLVED">Resolved</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>
      </div>

      {delegationFeedback && (
        <div
          className={`p-4 rounded-2xl flex items-center justify-between border ${
            delegationFeedback.type === 'success'
              ? 'bg-eco-50 border-eco-300 text-eco-900'
              : 'bg-coral-50 border-coral-300 text-coral-900'
          }`}
        >
          <div className="flex items-center gap-2.5 text-xs font-bold">
            {delegationFeedback.type === 'success' ? (
              <LuCircleCheck className="w-5 h-5 text-eco-600 shrink-0" />
            ) : (
              <LuTriangleAlert className="w-5 h-5 text-coral-600 shrink-0" />
            )}
            <span>{delegationFeedback.text}</span>
          </div>
          <button
            onClick={() => setDelegationFeedback(null)}
            className="text-xs font-black px-2 py-0.5 hover:opacity-75"
          >
            Dismiss
          </button>
        </div>
      )}

      {loading ? (
        <LoadingState message="Loading waste reports..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchReports} />
      ) : reports.length === 0 ? (
        <EmptyState
          icon={LuCircleCheck}
          title="No Waste Reports"
          description="There are currently no waste reports requiring attention. Everything looks good!"
          actionText={statusFilter ? "Clear Filter" : undefined}
          onAction={statusFilter ? () => setStatusFilter('') : undefined}
          className="my-8"
        />
      ) : (
        <div className="space-y-3">
          {reports.map((r) => (
            <div
              key={r.report_id}
              className="eco-card p-5 border-2 border-slate-200 hover:border-coral-200 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center gap-2.5">
                  <span className="text-base font-black text-slate-900 capitalize">
                    {r.report_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs font-bold text-slate-400">Report #{r.report_id}</span>
                </div>

                {r.description && (
                  <p className="text-xs text-slate-600 font-medium bg-slate-50 p-2.5 rounded-xl border border-slate-200/80">
                    {r.description}
                  </p>
                )}

                <div className="flex flex-wrap items-center gap-3 text-[11px] font-semibold text-slate-400 pt-1">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(r.created_at).toLocaleDateString()}
                  </span>
                  {r.user && (
                    <span className="flex items-center gap-1 text-slate-600">
                      <User className="w-3 h-3" />
                      {r.user.name} ({r.user.email})
                    </span>
                  )}
                  {r.bin && (
                    <span className="flex items-center gap-1 text-slate-600">
                      <MapPin className="w-3 h-3" />
                      Bin {r.bin.bin_code}
                    </span>
                  )}
                </div>

                {r.resolution_notes && (
                  <p className="text-xs font-bold text-eco-800 bg-eco-50 p-2 rounded-xl border border-eco-200 mt-1">
                    Resolution: {r.resolution_notes}
                  </p>
                )}
              </div>

              <div className="flex sm:flex-col items-end gap-2 shrink-0">
                <StatusBadge status={r.status} type="report" />
                {r.status !== 'RESOLVED' && r.status !== 'REJECTED' && (
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => handleOpenDelegate(r)}
                      className="btn-3d btn-3d-amber px-3 py-1.5 text-xs font-black flex items-center gap-1 shadow-3d-yellow"
                    >
                      <LuClipboardList className="w-3.5 h-3.5" />
                      <span>Assign Collector</span>
                    </button>
                    <button
                      onClick={() => {
                        setResolvingReport(r);
                        setResolutionStatus('RESOLVED');
                      }}
                      className="btn-3d btn-3d-green px-3.5 py-1.5 text-xs font-black flex items-center gap-1 shadow-3d-green"
                    >
                      <span>Resolve</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delegation Modal */}
      {delegatingReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-3xl p-6 w-full max-w-md border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-black uppercase tracking-wider text-amber-800 bg-amber-100 px-2 py-0.5 rounded-full border border-amber-200">
                  Task Delegation
                </span>
                <h3 className="text-xl font-black text-slate-900 mt-1">
                  Assign Report #{delegatingReport.report_id}
                </h3>
              </div>
              <button
                onClick={() => setDelegatingReport(null)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-600 font-medium">
              Create an <strong>ISSUE_RESPONSE</strong> collection task for this campus report.
            </p>

            <form onSubmit={handleDelegateSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Select Collector *
                </label>
                <select
                  value={delegateCollectorId}
                  onChange={(e) => setDelegateCollectorId(e.target.value)}
                  required
                  className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-amber-400"
                >
                  <option value="">-- Choose Collector --</option>
                  {(collectors || [])
                    .filter((c) => (c.status === 'ON_SHIFT' || (c as any).attendance_status === 'ON_SHIFT'))
                    .map((c) => (
                      <option key={c.collector_id} value={c.collector_id}>
                        🟢 [ON SHIFT] {c.collector_name || (c as any).name || 'Collector'} ({c.active_task_count ?? (c as any).active_tasks_count ?? 0} active tasks)
                      </option>
                    ))}
                  {(collectors || [])
                    .filter((c) => (c.status !== 'ON_SHIFT' && (c as any).attendance_status !== 'ON_SHIFT'))
                    .map((c) => (
                      <option key={c.collector_id} value={c.collector_id}>
                        ⚪ [OFF SHIFT] {c.collector_name || (c as any).name || 'Collector'} ({c.active_task_count ?? (c as any).active_tasks_count ?? 0} active tasks)
                      </option>
                    ))}
                </select>

                {isSelectedOffShift && (
                  <div className="mt-2 p-2 bg-amber-50 rounded-xl border border-amber-200 text-xs font-bold text-amber-900 flex items-center gap-1.5">
                    <LuTriangleAlert className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>Warning: This collector is off-shift. Assignment will still be recorded.</span>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                    Priority *
                  </label>
                  <select
                    value={delegatePriority}
                    onChange={(e) => setDelegatePriority(e.target.value as TaskPriority)}
                    className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-amber-400"
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
                    value={delegateDueDate}
                    onChange={(e) => setDelegateDueDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-amber-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Instructions for Collector
                </label>
                <textarea
                  value={delegateInstructions}
                  onChange={(e) => setDelegateInstructions(e.target.value)}
                  rows={2}
                  className="w-full px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-400"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setDelegatingReport(null)}
                  className="px-4 py-2.5 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isDelegating}
                  className="btn-3d btn-3d-amber px-5 py-2.5 text-xs font-black flex items-center gap-2 shadow-3d-yellow disabled:opacity-50"
                >
                  <LuClipboardList className="w-4 h-4" />
                  <span>{isDelegating ? 'Assigning...' : 'Assign Task'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Resolution Modal */}
      {resolvingReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in" style={{ marginTop: 0 }}>
          <div className="bg-white rounded-3xl p-6 w-full max-w-md border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-black text-slate-900">
                Resolve Report #{resolvingReport.report_id}
              </h3>
              <button
                onClick={() => setResolvingReport(null)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateReport} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Action
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setResolutionStatus('RESOLVED')}
                    className={`py-2.5 rounded-2xl font-black text-xs border flex items-center justify-center gap-1.5 ${
                      resolutionStatus === 'RESOLVED'
                        ? 'bg-eco-50 border-eco-500 text-eco-700 shadow-xs'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <LuCircleCheck className="w-4 h-4 text-eco-600" />
                    <span>Mark Resolved</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setResolutionStatus('REJECTED')}
                    className={`py-2.5 rounded-2xl font-black text-xs border flex items-center justify-center gap-1.5 ${
                      resolutionStatus === 'REJECTED'
                        ? 'bg-coral-50 border-coral-500 text-coral-700 shadow-xs'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <LuCircleX className="w-4 h-4 text-coral-600" />
                    <span>Reject Report</span>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Resolution Notes
                </label>
                <textarea
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  placeholder="Explain what action was taken (e.g., 'Custodial team cleared overflow and sanitized bin')."
                  rows={3}
                  className="w-full p-3 rounded-2xl border border-slate-200 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-coral-400 font-medium"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setResolvingReport(null)}
                  className="px-4 py-2.5 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-3d btn-3d-green px-5 py-2.5 text-xs font-black shadow-3d-green disabled:opacity-50"
                >
                  {isSubmitting ? 'Updating...' : 'Submit Resolution'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
