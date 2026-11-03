import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { binsApi } from '../../api/bins';
import { collectionsApi } from '../../api/collections';
import { attendanceApi } from '../../api/attendance';
import { tasksApi } from '../../api/tasks';
import { Bin, Collection, AttendanceRecord } from '../../types';
import { StatCard } from '../../components/common/StatCard';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { ProgressBar } from '../../components/common/ProgressBar';
import {
  LuTriangleAlert,
  LuTruck,
  LuQrCode,
  LuRecycle,
  LuTrendingUp,
  LuClock,
  LuClipboardList,
  LuCircleCheck,
  LuLogOut,
  LuLogIn,
  LuCircleAlert,
  LuArrowRight,
} from 'react-icons/lu';
import { Link } from 'react-router-dom';

export const CollectorDashboard: React.FC = () => {
  const { user } = useAuth();
  const [bins, setBins] = useState<Bin[]>([]);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [activeShift, setActiveShift] = useState<AttendanceRecord | null>(null);
  const [activeTaskCount, setActiveTaskCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Attendance shift action state
  const [shiftActionLoading, setShiftActionLoading] = useState(false);
  const [shiftNotes, setShiftNotes] = useState('');
  const [attendanceMessage, setAttendanceMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchCollectorData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [binsRes, collectionsRes, shiftRes, tasksRes] = await Promise.all([
        binsApi.getBins({ limit: 50 }).catch(() => []),
        collectionsApi.getCollections({ limit: 10 }).catch(() => []),
        attendanceApi.getMyActiveShift().catch(() => null),
        tasksApi.getMyTasks().catch(() => []),
      ]);
      setBins(binsRes);
      setCollections(collectionsRes);
      setActiveShift(shiftRes);
      
      const ongoing = tasksRes.filter(
        (t) => t.status === 'ASSIGNED' || t.status === 'ACCEPTED' || t.status === 'IN_PROGRESS'
      );
      setActiveTaskCount(ongoing.length);
    } catch (err: any) {
      setError(err.message || 'Failed to load collector dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollectorData();
  }, []);

  const handleStartShift = async () => {
    setShiftActionLoading(true);
    setAttendanceMessage(null);
    try {
      const newShift = await attendanceApi.checkIn(shiftNotes.trim() || undefined);
      setActiveShift(newShift);
      setShiftNotes('');
      setAttendanceMessage({ type: 'success', text: 'Shift started successfully! Ready for campus tasks.' });
    } catch (err: any) {
      setAttendanceMessage({
        type: 'error',
        text: err?.data?.detail || err.message || 'Failed to start shift.',
      });
    } finally {
      setShiftActionLoading(false);
    }
  };

  const handleEndShift = async () => {
    setShiftActionLoading(true);
    setAttendanceMessage(null);
    try {
      await attendanceApi.checkOut(shiftNotes.trim() || undefined);
      setActiveShift(null);
      setShiftNotes('');
      setAttendanceMessage({ type: 'success', text: 'Shift completed. Great work today!' });
    } catch (err: any) {
      setAttendanceMessage({
        type: 'error',
        text: err?.data?.detail || err.message || 'Failed to end shift.',
      });
    } finally {
      setShiftActionLoading(false);
    }
  };

  if (loading) {
    return <LoadingState message="Loading collector operational hub..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchCollectorData} />;
  }

  const highFillBins = bins.filter((b) => b.current_fill_percentage >= 80);
  const totalCollectionsToday = collections.length;

  return (
    <div className="max-w-5xl mx-auto py-4 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-amber-800 bg-amber-100 px-3 py-1 rounded-full border border-amber-200">
            Field Operations Hub
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Collector Dashboard
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Daily shift attendance, assigned tasks, bin telemetry, and collection logging.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/collector/tasks"
            className="btn-3d btn-3d-amber px-5 py-3 text-xs font-black flex items-center gap-2 shadow-3d-yellow shrink-0"
          >
            <LuClipboardList className="w-4 h-4" />
            <span>My Tasks ({activeTaskCount})</span>
          </Link>
          <Link
            to="/collector/scan"
            className="btn-3d btn-3d-green px-5 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-green shrink-0"
          >
            <LuQrCode className="w-4 h-4" />
            <span>Scan Bin</span>
          </Link>
        </div>
      </div>

      {/* Attendance Feedback Alert */}
      {attendanceMessage && (
        <div
          className={`p-4 rounded-2xl flex items-center justify-between border ${
            attendanceMessage.type === 'success'
              ? 'bg-eco-50 border-eco-300 text-eco-900'
              : 'bg-coral-50 border-coral-300 text-coral-900'
          }`}
        >
          <div className="flex items-center gap-2.5 text-xs font-bold">
            {attendanceMessage.type === 'success' ? (
              <LuCircleCheck className="w-5 h-5 text-eco-600 shrink-0" />
            ) : (
              <LuCircleAlert className="w-5 h-5 text-coral-600 shrink-0" />
            )}
            <span>{attendanceMessage.text}</span>
          </div>
          <button
            onClick={() => setAttendanceMessage(null)}
            className="text-xs font-black px-2 py-0.5 hover:opacity-75"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Daily Attendance Shift Card */}
      <div
        className={`eco-card border-2 p-6 transition-all ${
          activeShift
            ? 'border-eco-300 bg-eco-50/30'
            : 'border-amber-300 bg-amber-50/30'
        }`}
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-start gap-4">
            <div
              className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 text-xl shadow-xs ${
                activeShift
                  ? 'bg-eco-500 text-white shadow-3d-green'
                  : 'bg-amber-400 text-slate-900 shadow-3d-yellow'
              }`}
            >
              <LuClock className="w-6 h-6" />
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2.5">
                <h3 className="text-lg font-black text-slate-900">
                  {activeShift ? 'Currently On Shift' : 'Shift Not Started'}
                </h3>
                <span
                  className={`text-[11px] font-black uppercase px-2.5 py-0.5 rounded-full border ${
                    activeShift
                      ? 'bg-eco-100 text-eco-800 border-eco-200 animate-pulse'
                      : 'bg-amber-100 text-amber-800 border-amber-200'
                  }`}
                >
                  {activeShift ? 'ACTIVE' : 'OFF SHIFT'}
                </span>
              </div>

              <p className="text-xs font-medium text-slate-600">
                {activeShift ? (
                  <>
                    Shift commenced at{' '}
                    <strong className="text-slate-900">
                      {new Date(activeShift.check_in_at).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </strong>{' '}
                    on {activeShift.attendance_date} (DBIT Campus Time).
                  </>
                ) : (
                  'Start your daily shift to acknowledge campus presence and receive task assignments.'
                )}
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5">
            {activeShift ? (
              <button
                onClick={handleEndShift}
                disabled={shiftActionLoading}
                className="btn-3d btn-3d-coral px-6 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-coral disabled:opacity-50"
              >
                <LuLogOut className="w-4 h-4" />
                <span>{shiftActionLoading ? 'Ending Shift...' : 'End Shift'}</span>
              </button>
            ) : (
              <button
                onClick={handleStartShift}
                disabled={shiftActionLoading}
                className="btn-3d btn-3d-green px-6 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-green disabled:opacity-50"
              >
                <LuLogIn className="w-4 h-4" />
                <span>{shiftActionLoading ? 'Starting Shift...' : 'Start Shift'}</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Operational Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Link to="/collector/tasks">
          <StatCard
            title="Assigned Tasks"
            value={activeTaskCount}
            subtitle="Pending & active jobs"
            icon={LuClipboardList}
            variant="blue"
          />
        </Link>
        <StatCard
          title="High Fill Bins"
          value={highFillBins.length}
          subtitle="Priority units filled ≥ 80%"
          icon={LuTriangleAlert}
          variant="coral"
        />
        <StatCard
          title="Recent Collections"
          value={totalCollectionsToday}
          subtitle="Operations logged"
          icon={LuTruck}
          variant="yellow"
        />
        <StatCard
          title="Campus Bins"
          value={bins.length}
          subtitle="Monitored stations"
          icon={LuRecycle}
          variant="green"
        />
      </div>

      {/* High Priority Bins Alert */}
      {highFillBins.length > 0 && (
        <div className="eco-card border-2 border-coral-300 bg-coral-50/40 p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-black text-coral-950 flex items-center gap-2">
              <LuTriangleAlert className="w-5 h-5 text-coral-600" />
              <span>Priority Collection Required ({highFillBins.length} Bins)</span>
            </h3>
            <Link
              to="/collector/scan"
              className="text-xs font-extrabold text-coral-700 hover:text-coral-800"
            >
              Start Servicing →
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {highFillBins.map((bin) => (
              <div
                key={bin.bin_id}
                className="bg-white p-4 rounded-2xl border border-coral-200 shadow-xs space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-slate-800">{bin.bin_code}</span>
                  <span className="text-xs font-black text-coral-600">
                    {bin.current_fill_percentage}% Full
                  </span>
                </div>
                <p className="text-[11px] font-semibold text-slate-500 truncate">
                  {bin.location?.name || 'Campus Building'}
                </p>
                <ProgressBar
                  value={bin.current_fill_percentage}
                  variant="coral"
                  showPercentage={false}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Two Column Layout: Recent Collections & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Collections */}
        <div className="eco-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-extrabold text-slate-900 flex items-center gap-2">
              <LuTruck className="w-5 h-5 text-slate-700" />
              <span>Recent Collections</span>
            </h3>
            <Link
              to="/collector/collections"
              className="text-xs font-bold text-amber-700 hover:text-amber-800"
            >
              View All
            </Link>
          </div>

          {collections.length === 0 ? (
            <p className="text-center py-8 text-xs font-bold text-slate-400">
              No collection operations recorded yet
            </p>
          ) : (
            <div className="space-y-3">
              {collections.slice(0, 5).map((col) => (
                <div
                  key={col.collection_id}
                  className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-center justify-between"
                >
                  <div>
                    <p className="text-xs font-extrabold text-slate-800">
                      Collection #{col.collection_id}
                    </p>
                    <p className="text-[11px] font-medium text-slate-500">
                      {new Date(col.collection_timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                      {col.collected_quantity_kg && ` • ${col.collected_quantity_kg} kg collected`}
                    </p>
                  </div>
                  <span className="text-xs font-extrabold text-eco-700 bg-eco-100 px-3 py-1 rounded-full border border-eco-200">
                    {col.fill_level_before}% → {col.fill_level_after}%
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Operations Links */}
        <div className="eco-card space-y-3">
          <h3 className="text-lg font-extrabold text-slate-900 mb-2">Operations Center</h3>

          <Link
            to="/collector/tasks"
            className="p-4 rounded-2xl bg-amber-50 border border-amber-200 hover:border-amber-300 transition-all flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500 text-slate-900 flex items-center justify-center text-xl shadow-xs">
                <LuClipboardList className="w-5 h-5 text-slate-900" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-900">Task Management</p>
                <p className="text-[11px] text-slate-500 font-medium">
                  Accept, work, and complete assigned campus tasks.
                </p>
              </div>
            </div>
            <LuArrowRight className="w-4 h-4 text-amber-700 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            to="/collector/scan"
            className="p-4 rounded-2xl bg-eco-50 border border-eco-200 hover:border-eco-300 transition-all flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-eco-500 text-white flex items-center justify-center text-xl shadow-xs">
                <LuQrCode className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-900">Scan & Record Collection</p>
                <p className="text-[11px] text-slate-500 font-medium">
                  Scan QR, log fill readings, or empty bin.
                </p>
              </div>
            </div>
            <LuArrowRight className="w-4 h-4 text-eco-700 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            to="/collector/processing"
            className="p-4 rounded-2xl bg-ocean-50 border border-ocean-200 hover:border-ocean-300 transition-all flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-ocean-500 text-white flex items-center justify-center text-xl shadow-xs">
                <LuRecycle className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-900">Recycling & Composting Logs</p>
                <p className="text-[11px] text-slate-500 font-medium">
                  Record processing batches for collected waste.
                </p>
              </div>
            </div>
            <LuArrowRight className="w-4 h-4 text-ocean-700 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            to="/collector/predictions"
            className="p-4 rounded-2xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition-all flex items-center justify-between group"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-slate-700 text-white flex items-center justify-center text-xl shadow-xs">
                <LuTrendingUp className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs font-black text-slate-900">AI Fill Level Predictions</p>
                <p className="text-[11px] text-slate-500 font-medium">
                  Forecast when bins will require emptying.
                </p>
              </div>
            </div>
            <LuArrowRight className="w-4 h-4 text-slate-700 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </div>
    </div>
  );
};
