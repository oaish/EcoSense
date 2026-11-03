import React, { useState, useEffect } from 'react';
import { tasksApi } from '../../api/tasks';
import { collectionsApi } from '../../api/collections';
import { CollectionTask, TaskStatus, Collection } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import {
  LuClipboardList,
  LuCircleCheck,
  LuPlay,
  LuCheck,
  LuClock,
  LuMapPin,
  LuTrash2,
  LuFileText,
  LuTriangleAlert,
  LuFilter,
  LuQrCode,
  LuX,
  LuArrowRight,
  LuSearch,
} from 'react-icons/lu';
import { Link } from 'react-router-dom';

export const CollectorTasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<CollectionTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('ACTIVE');
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  // Completion modal state
  const [completingTask, setCompletingTask] = useState<CollectionTask | null>(null);
  const [completionNotes, setCompletionNotes] = useState('');
  const [collectionIdInput, setCollectionIdInput] = useState<string>('');
  const [recentCollections, setRecentCollections] = useState<Collection[]>([]);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await tasksApi.getMyTasks();
      setTasks(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load assigned tasks.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleUpdateStatus = async (taskId: number, newStatus: TaskStatus) => {
    setActionLoading(taskId);
    try {
      const updated = await tasksApi.updateStatus(taskId, { status: newStatus });
      setTasks((prev) => prev.map((t) => (t.task_id === taskId ? updated : t)));
    } catch (err: any) {
      alert(err?.data?.detail || err.message || 'Failed to update task status.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleOpenCompletionModal = async (task: CollectionTask) => {
    setCompletingTask(task);
    setCompletionNotes('');
    setCollectionIdInput('');
    setModalError(null);

    if (task.task_type === 'COLLECTION' && task.bin_id) {
      setModalLoading(true);
      try {
        const cols = await collectionsApi.getCollections({ bin_id: task.bin_id, limit: 5 });
        setRecentCollections(cols);
        if (cols.length > 0) {
          setCollectionIdInput(String(cols[0].collection_id));
        }
      } catch {
        setRecentCollections([]);
      } finally {
        setModalLoading(false);
      }
    }
  };

  const handleCompleteTaskSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!completingTask) return;

    if (completingTask.task_type === 'COLLECTION') {
      const colId = parseInt(collectionIdInput, 10);
      if (isNaN(colId) || colId <= 0) {
        setModalError('A valid Collection Record ID is required to verify the bin was emptied.');
        return;
      }
    } else {
      if (!completionNotes.trim()) {
        setModalError('Please enter completion notes describing the action taken.');
        return;
      }
    }

    setModalLoading(true);
    setModalError(null);

    try {
      const updated = await tasksApi.updateStatus(completingTask.task_id, {
        status: 'COMPLETED',
        completion_notes: completionNotes.trim() || undefined,
        collection_id: completingTask.task_type === 'COLLECTION' ? parseInt(collectionIdInput, 10) : undefined,
      });

      setTasks((prev) => prev.map((t) => (t.task_id === completingTask.task_id ? updated : t)));
      setCompletingTask(null);
    } catch (err: any) {
      setModalError(err?.data?.detail || err.message || 'Failed to complete task.');
    } finally {
      setModalLoading(false);
    }
  };

  const filteredTasks = tasks.filter((t) => {
    if (statusFilter === 'ACTIVE') {
      return t.status === 'ASSIGNED' || t.status === 'ACCEPTED' || t.status === 'IN_PROGRESS';
    }
    if (statusFilter === 'ALL') return true;
    return t.status === statusFilter;
  });

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-red-100 text-red-700 border border-red-200">Urgent</span>;
      case 'HIGH':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-coral-100 text-coral-700 border border-coral-200">High</span>;
      case 'MEDIUM':
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-amber-100 text-amber-800 border border-amber-200">Medium</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-slate-100 text-slate-700 border border-slate-200">Low</span>;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'COLLECTION':
        return (
          <span className="flex items-center gap-1 text-[11px] font-bold text-eco-700 bg-eco-50 px-2 py-0.5 rounded-md border border-eco-200">
            <LuTrash2 className="w-3 h-3" /> Empty Bin
          </span>
        );
      case 'INSPECTION':
        return (
          <span className="flex items-center gap-1 text-[11px] font-bold text-ocean-700 bg-ocean-50 px-2 py-0.5 rounded-md border border-ocean-200">
            <LuSearch className="w-3 h-3" /> Inspect Bin
          </span>
        );
      case 'ISSUE_RESPONSE':
        return (
          <span className="flex items-center gap-1 text-[11px] font-bold text-coral-700 bg-coral-50 px-2 py-0.5 rounded-md border border-coral-200">
            <LuTriangleAlert className="w-3 h-3" /> Report Response
          </span>
        );
      default:
        return null;
    }
  };

  const getStatusBadge = (status: TaskStatus) => {
    switch (status) {
      case 'ASSIGNED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-black uppercase bg-amber-100 text-amber-800 border border-amber-300">Assigned</span>;
      case 'ACCEPTED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-black uppercase bg-blue-100 text-blue-800 border border-blue-300">Accepted</span>;
      case 'IN_PROGRESS':
        return <span className="px-2.5 py-1 rounded-full text-xs font-black uppercase bg-purple-100 text-purple-800 border border-purple-300 animate-pulse">In Progress</span>;
      case 'COMPLETED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-black uppercase bg-eco-100 text-eco-800 border border-eco-300">Completed</span>;
      case 'CANCELLED':
        return <span className="px-2.5 py-1 rounded-full text-xs font-black uppercase bg-slate-100 text-slate-500 border border-slate-300">Cancelled</span>;
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-amber-800 bg-amber-100 px-3 py-1 rounded-full border border-amber-200">
            Collector Workflow
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            My Assigned Tasks
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Review and progress collection, inspection, and waste issue tasks assigned by campus administrators.
          </p>
        </div>

        {/* Status Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {[
            { id: 'ACTIVE', label: 'Active Jobs' },
            { id: 'ASSIGNED', label: 'Assigned' },
            { id: 'IN_PROGRESS', label: 'In Progress' },
            { id: 'COMPLETED', label: 'Completed' },
            { id: 'ALL', label: 'All Tasks' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStatusFilter(tab.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-black transition-all shrink-0 ${statusFilter === tab.id
                  ? 'bg-amber-500 text-slate-950 shadow-3d-yellow'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <LoadingState message="Loading your assigned tasks..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchTasks} />
      ) : filteredTasks.length === 0 ? (
        <EmptyState
          icon={LuCircleCheck}
          title="No Tasks Found"
          description={
            statusFilter === 'ACTIVE'
              ? 'You have completed all active tasks! Great job keeping DBIT clean.'
              : 'No tasks match the selected filter criteria.'
          }
          actionText={statusFilter !== 'ALL' ? 'Show All Tasks' : undefined}
          onAction={statusFilter !== 'ALL' ? () => setStatusFilter('ALL') : undefined}
        />
      ) : (
        <div className="space-y-4">
          {filteredTasks.map((task) => (
            <div
              key={task.task_id}
              className={`eco-card p-5 border-2 transition-all flex flex-col md:flex-row md:items-start justify-between gap-5 ${task.status === 'COMPLETED'
                  ? 'border-slate-200 bg-slate-50/50 opacity-90'
                  : task.priority === 'URGENT'
                    ? 'border-red-300 bg-red-50/20 shadow-md'
                    : 'border-slate-200 hover:border-amber-300'
                }`}
            >
              <div className="space-y-3 flex-1">
                {/* Meta header */}
                <div className="flex flex-wrap items-center gap-2">
                  {getTypeBadge(task.task_type)}
                  {getPriorityBadge(task.priority)}
                  {getStatusBadge(task.status)}
                  <span className="text-xs font-bold text-slate-400">Task #{task.task_id}</span>
                </div>

                {/* Title & Instructions */}
                <div>
                  <h3 className="text-base font-black text-slate-900">{task.title}</h3>
                  {task.instructions && (
                    <p className="text-xs text-slate-600 mt-1 leading-relaxed bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                      {task.instructions}
                    </p>
                  )}
                </div>

                {/* Location / Bin / Report Context */}
                <div className="flex flex-wrap items-center gap-4 text-xs font-semibold text-slate-500">
                  {task.bin_code && (
                    <span className="flex items-center gap-1.5 text-slate-700 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
                      <LuTrash2 className="w-3.5 h-3.5 text-eco-600" />
                      Bin: <strong>{task.bin_code}</strong>
                    </span>
                  )}
                  {task.location_name && (
                    <span className="flex items-center gap-1.5 text-slate-700 bg-white px-2.5 py-1 rounded-lg border border-slate-200">
                      <LuMapPin className="w-3.5 h-3.5 text-ocean-600" />
                      Location: {task.location_name}
                    </span>
                  )}
                  {task.report_id && (
                    <span className="flex items-center gap-1.5 text-coral-700 bg-coral-50 px-2.5 py-1 rounded-lg border border-coral-200">
                      <LuFileText className="w-3.5 h-3.5" />
                      Report #{task.report_id} {task.report_title ? `(${task.report_title})` : ''}
                    </span>
                  )}
                  {task.due_date && (
                    <span className="flex items-center gap-1 text-amber-700">
                      <LuClock className="w-3.5 h-3.5" />
                      Due: {new Date(task.due_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  )}
                </div>

                {/* Completion Details if already completed */}
                {task.status === 'COMPLETED' && (
                  <div className="p-3 bg-eco-50 rounded-xl border border-eco-200 text-xs text-eco-900 space-y-1">
                    <p className="font-black flex items-center gap-1">
                      <LuCircleCheck className="w-4 h-4 text-eco-600" /> Completed on{' '}
                      {task.completed_at ? new Date(task.completed_at).toLocaleString() : 'N/A'}
                    </p>
                    {task.completion_notes && (
                      <p className="text-slate-700 font-medium">Notes: {task.completion_notes}</p>
                    )}
                    {task.collection_id && (
                      <p className="text-slate-700 font-medium">
                        Linked Collection Record: #{task.collection_id}
                      </p>
                    )}
                  </div>
                )}
              </div>

              {/* Action Buttons based on status */}
              <div className="flex flex-col sm:flex-row md:flex-col items-stretch md:items-end gap-2 shrink-0">
                {task.status === 'ASSIGNED' && (
                  <button
                    onClick={() => handleUpdateStatus(task.task_id, 'ACCEPTED')}
                    disabled={actionLoading === task.task_id}
                    className="btn-3d btn-3d-amber px-4 py-2 text-xs font-black flex items-center justify-center gap-1.5 shadow-3d-yellow disabled:opacity-50"
                  >
                    <LuCheck className="w-4 h-4" />
                    <span>{actionLoading === task.task_id ? 'Accepting...' : 'Accept Task'}</span>
                  </button>
                )}

                {task.status === 'ACCEPTED' && (
                  <button
                    onClick={() => handleUpdateStatus(task.task_id, 'IN_PROGRESS')}
                    disabled={actionLoading === task.task_id}
                    className="btn-3d btn-3d-blue px-4 py-2 text-xs font-black flex items-center justify-center gap-1.5 shadow-3d-blue disabled:opacity-50"
                  >
                    <LuPlay className="w-4 h-4" />
                    <span>{actionLoading === task.task_id ? 'Starting...' : 'Start Work'}</span>
                  </button>
                )}

                {task.status === 'IN_PROGRESS' && (
                  <div className="flex flex-col gap-2 w-full sm:w-auto">
                    {task.task_type === 'COLLECTION' && (
                      <Link
                        to="/collector/scan"
                        className="btn-3d btn-3d-ocean px-3.5 py-1.5 text-xs font-black flex items-center justify-center gap-1.5 shadow-3d-ocean"
                      >
                        <LuQrCode className="w-4 h-4" />
                        <span>Scan & Empty Bin</span>
                      </Link>
                    )}

                    <button
                      onClick={() => handleOpenCompletionModal(task)}
                      className="btn-3d btn-3d-green px-4 py-2 text-xs font-black flex items-center justify-center gap-1.5 shadow-3d-green"
                    >
                      <LuCircleCheck className="w-4 h-4" />
                      <span>Complete Task</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Completion Evidence Modal */}
      {completingTask && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in">
          <div className="bg-white rounded-3xl p-6 w-full max-w-lg border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-black uppercase tracking-wider text-eco-700 bg-eco-100 px-2 py-0.5 rounded-full border border-eco-200">
                  Verification & Evidence
                </span>
                <h3 className="text-xl font-black text-slate-900 mt-1">
                  Complete Task #{completingTask.task_id}
                </h3>
              </div>
              <button
                onClick={() => setCompletingTask(null)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <LuX className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-600 font-medium">
              {completingTask.title}
            </p>

            {modalError && (
              <div className="p-3 rounded-xl bg-coral-50 border border-coral-200 text-xs font-bold text-coral-800 flex items-center gap-2">
                <LuTriangleAlert className="w-4 h-4 shrink-0" />
                <span>{modalError}</span>
              </div>
            )}

            <form onSubmit={handleCompleteTaskSubmit} className="space-y-4">
              {completingTask.task_type === 'COLLECTION' ? (
                <div className="space-y-2">
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-700">
                    Linked Collection Record ID <span className="text-red-500">*</span>
                  </label>
                  <p className="text-[11px] text-slate-500 font-medium">
                    Evidence required: Enter the ID of the collection record logged when this bin was emptied.
                  </p>

                  {recentCollections.length > 0 && (
                    <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1.5">
                      <span className="text-[11px] font-bold text-slate-600">Recent Collections for this Bin:</span>
                      <div className="flex flex-wrap gap-2">
                        {recentCollections.map((col) => (
                          <button
                            key={col.collection_id}
                            type="button"
                            onClick={() => setCollectionIdInput(String(col.collection_id))}
                            className={`px-2.5 py-1 rounded-lg text-xs font-black border transition-all ${collectionIdInput === String(col.collection_id)
                                ? 'bg-eco-500 text-white border-eco-600'
                                : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                              }`}
                          >
                            #{col.collection_id} ({col.fill_level_before}% → {col.fill_level_after}%)
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  <input
                    type="number"
                    value={collectionIdInput}
                    onChange={(e) => setCollectionIdInput(e.target.value)}
                    placeholder="e.g. 14"
                    required
                    className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-eco-400"
                  />
                </div>
              ) : null}

              <div className="space-y-1.5">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700">
                  {completingTask.task_type === 'COLLECTION' ? 'Additional Notes (Optional)' : 'Completion Notes / Resolution *'}
                </label>
                <textarea
                  value={completionNotes}
                  onChange={(e) => setCompletionNotes(e.target.value)}
                  placeholder={
                    completingTask.task_type === 'COLLECTION'
                      ? 'e.g. Bin cleared, liner replaced, surroundings swept.'
                      : 'e.g. Inspected hinge and sensor; replaced sensor battery, bin clean.'
                  }
                  rows={3}
                  className="w-full px-4 py-2.5 rounded-2xl border border-slate-200 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-eco-400"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setCompletingTask(null)}
                  className="px-4 py-2.5 rounded-2xl text-xs font-bold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={modalLoading}
                  className="btn-3d btn-3d-green px-5 py-2.5 text-xs font-black flex items-center gap-2 shadow-3d-green disabled:opacity-50"
                >
                  <LuCircleCheck className="w-4 h-4" />
                  <span>{modalLoading ? 'Verifying...' : 'Confirm & Complete'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
