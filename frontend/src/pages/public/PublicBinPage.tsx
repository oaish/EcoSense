import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { binsApi } from '../../api/bins';
import { disposalsApi } from '../../api/disposals';
import { useAuth } from '../../context/AuthContext';
import { BinQRRead } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { ProgressBar } from '../../components/common/ProgressBar';
import { CelebrationModal } from '../../components/common/CelebrationModal';
import {
  LuRecycle,
  LuMapPin,
  LuCircleCheck,
  LuTriangleAlert,
  LuLogIn,
  LuTrash2,
  LuStar,
  LuSparkles,
  LuShieldAlert,
  LuRotateCcw,
  LuSettings,
  LuTruck,
} from 'react-icons/lu';

export const PublicBinPage: React.FC = () => {
  const { qr_token } = useParams<{ qr_token: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const isAuthenticated = Boolean(user);

  const [bin, setBin] = useState<BinQRRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Disposal form state for authenticated student
  const [quantityKg, setQuantityKg] = useState<number | ''>('');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [disposalError, setDisposalError] = useState<string | null>(null);
  const [showCelebration, setShowCelebration] = useState(false);
  const [pointsEarned, setPointsEarned] = useState(10);

  const fetchPublicBin = async () => {
    if (!qr_token) {
      setNotFound(true);
      setLoading(false);
      return;
    }

    setLoading(true);
    setNotFound(false);
    setErrorMessage(null);

    try {
      const data = await binsApi.getPublicBinByQrToken(qr_token);
      setBin(data);
    } catch (err: any) {
      if (err.status === 404 || err.message?.toLowerCase().includes('not found')) {
        setNotFound(true);
      } else {
        setErrorMessage(err.message || 'Unable to load bin details. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPublicBin();
  }, [qr_token]);

  const handleRecordDisposalClick = () => {
    if (!isAuthenticated) {
      // Preserve the current public bin URL as returnUrl
      navigate(`/login?returnUrl=${encodeURIComponent(`/bin/${qr_token}`)}`);
      return;
    }
  };

  const handleDisposalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bin) return;

    setIsSubmitting(true);
    setDisposalError(null);

    try {
      await disposalsApi.recordDisposal({
        bin_id: bin.bin_id,
        quantity_kg: quantityKg !== '' ? Number(quantityKg) : undefined,
        notes: notes.trim() || undefined,
      });

      setPointsEarned(10);
      setShowCelebration(true);
      setQuantityKg('');
      setNotes('');
    } catch (err: any) {
      setDisposalError(err.message || 'Failed to record disposal. Please verify your connection and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <LoadingState message="Connecting to EcoSense smart bin node..." />
      </div>
    );
  }

  // Friendly Bin Not Found State
  if (notFound) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="eco-card max-w-md w-full text-center space-y-6 p-8 border-2 border-slate-200">
          <div className="w-16 h-16 rounded-3xl bg-coral-50 border-2 border-coral-200 text-coral-600 flex items-center justify-center mx-auto text-2xl shadow-xs">
            <LuShieldAlert className="w-8 h-8" />
          </div>

          <div>
            <span className="text-xs font-black uppercase tracking-wider text-slate-400">
              EcoSense DBIT Mumbai
            </span>
            <h1 className="text-2xl font-black text-slate-900 mt-1">Bin Not Found</h1>
            <p className="text-slate-600 text-sm font-medium mt-2 leading-relaxed">
              This QR code does not belong to an active registered EcoSense waste bin on the DBIT campus.
            </p>
          </div>

          <div className="pt-2 flex flex-col gap-2">
            <Link
              to="/"
              className="btn-3d btn-3d-green py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-green"
            >
              <span>Go to EcoSense Home</span>
            </Link>
            <button
              onClick={fetchPublicBin}
              className="btn-3d btn-3d-white py-3 text-xs font-bold flex items-center justify-center gap-1.5"
            >
              <LuRotateCcw className="w-3.5 h-3.5" />
              <span>Retry Scan Lookup</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Generic Error State
  if (errorMessage || !bin) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="eco-card max-w-md w-full text-center space-y-6 p-8 border-2 border-coral-200">
          <div className="w-16 h-16 rounded-3xl bg-coral-100 text-coral-700 flex items-center justify-center mx-auto">
            <LuTriangleAlert className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-xl font-black text-slate-900">Connection Error</h2>
            <p className="text-slate-600 text-sm font-medium mt-1">{errorMessage}</p>
          </div>
          <button
            onClick={fetchPublicBin}
            className="btn-3d btn-3d-green w-full py-3 text-xs font-black shadow-3d-green"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Clean, soft-3D mobile-first Public Bin Information Display
  const wasteColor = bin.color_code || '#10B981';
  const fillPct = bin.current_fill_percentage ?? 0;

  return (
    <div className="min-h-screen bg-slate-100/60 py-6 px-4 flex flex-col justify-between">
      <div className="max-w-md w-full mx-auto space-y-5">
        {/* Brand Banner */}
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-eco-500 text-white flex items-center justify-center shadow-xs">
              <LuRecycle className="w-5 h-5" />
            </div>
            <div>
              <span className="text-sm font-black tracking-tight text-slate-900 block leading-tight">
                ECOSENSE
              </span>
              <span className="text-[10px] font-bold text-slate-500 block leading-tight">
                DBIT Zero Waste Campus
              </span>
            </div>
          </div>

          <StatusBadge status={bin.status} type="bin" />
        </div>

        {/* Physical Bin Asset Card */}
        <div className="eco-card border-2 border-slate-200 shadow-soft-lg space-y-5 relative overflow-hidden">
          {/* Top Waste Type Tag */}
          <div
            className="p-4 rounded-2xl border-2 flex items-center gap-3.5"
            style={{
              backgroundColor: `${wasteColor}15`,
              borderColor: wasteColor,
            }}
          >
            <div
              className="w-12 h-12 rounded-2xl flex items-center justify-center text-white shadow-xs shrink-0"
              style={{ backgroundColor: wasteColor }}
            >
              <LuRecycle className="w-7 h-7" />
            </div>
            <div className="flex-1">
              <span className="text-[10px] font-black uppercase tracking-wider text-slate-500 block">
                Designated Waste Stream
              </span>
              <h2 className="text-lg font-black text-slate-900 leading-snug">
                {bin.waste_type_name || 'General Waste'}
              </h2>
            </div>
          </div>

          {/* Bin Code & Location Details */}
          <div className="space-y-3">
            <div>
              <span className="text-[10px] font-black uppercase tracking-wider text-slate-400 block">
                Bin Code
              </span>
              <h1 className="text-3xl font-black text-slate-900 tracking-tight">
                {bin.bin_code}
              </h1>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-start gap-3">
              <div className="w-9 h-9 rounded-xl bg-slate-200/80 text-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                <LuMapPin className="w-5 h-5" />
              </div>
              <div className="text-xs">
                <p className="font-extrabold text-slate-900">{bin.location_name}</p>
                {(bin.building || bin.floor) && (
                  <p className="text-slate-500 font-semibold mt-0.5">
                    {bin.building || 'Campus'} {bin.floor ? `• ${bin.floor}` : ''}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Telemetry Grid: Capacity & Fill Level */}
          <div className="space-y-2 pt-1">
            <div className="flex items-center justify-between text-xs font-extrabold text-slate-700">
              <span>Bin Fill Status</span>
              <span>{fillPct}% Full</span>
            </div>
            <ProgressBar
              value={fillPct}
              variant={fillPct > 80 ? 'coral' : fillPct > 50 ? 'yellow' : 'green'}
              showPercentage={false}
            />
            {bin.capacity_liters != null && (
              <p className="text-[11px] font-bold text-slate-400 text-right">
                Total Capacity: {bin.capacity_liters} Litres
              </p>
            )}
          </div>
        </div>

        {/* Action Area based on Authentication & Role */}
        {!isAuthenticated ? (
          /* Unauthenticated Public Call-To-Action */
          <div className="eco-card border-2 border-eco-200 bg-linear-to-b from-white to-eco-50/50 space-y-4 text-center">
            <div className="space-y-1">
              <h3 className="text-base font-black text-slate-900">
                Disposing waste at this bin?
              </h3>
              <p className="text-xs text-slate-600 font-medium">
                Log in with your DBIT account to record this disposal and earn eco-points!
              </p>
            </div>

            <button
              onClick={handleRecordDisposalClick}
              className="btn-3d btn-3d-green w-full py-3.5 text-sm font-black flex items-center justify-center gap-2 shadow-3d-green"
            >
              <LuLogIn className="w-4 h-4" />
              <span>Log In to Record Disposal</span>
            </button>
          </div>
        ) : user?.role === 'STUDENT' ? (
          /* Authenticated Student Action Card */
          <div className="eco-card border-2 border-eco-200 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-sun-100 text-sun-800 flex items-center justify-center">
                  <LuStar className="w-4 h-4 fill-current" />
                </div>
                <h3 className="text-sm font-black text-slate-900">
                  Ready to Dispose (+10 Pts)
                </h3>
              </div>
              <span className="text-xs font-bold text-slate-500">{user.name}</span>
            </div>

            {disposalError && (
              <div className="p-3 bg-coral-50 rounded-xl border border-coral-200 text-coral-700 text-xs font-bold">
                {disposalError}
              </div>
            )}

            <form onSubmit={handleDisposalSubmit} className="space-y-3">
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                  Approximate Weight (kg) <span className="text-slate-400 lowercase">(optional)</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="50"
                  placeholder="e.g. 0.2"
                  value={quantityKg}
                  onChange={(e) => setQuantityKg(e.target.value === '' ? '' : parseFloat(e.target.value))}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-semibold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-eco-400"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                  Notes <span className="text-slate-400 lowercase">(optional)</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Clean food container"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-semibold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-eco-400"
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-3d btn-3d-green w-full py-3.5 text-xs font-black flex items-center justify-center gap-2 shadow-3d-green"
              >
                {isSubmitting ? (
                  <span>Recording Disposal...</span>
                ) : (
                  <>
                    <LuCircleCheck className="w-4 h-4" />
                    <span>Confirm Disposal & Collect Points</span>
                  </>
                )}
              </button>
            </form>

            <div className="pt-1 border-t border-slate-100 flex justify-between items-center text-xs">
              <Link
                to={`/student/report?bin_id=${bin.bin_id}`}
                className="text-coral-600 font-bold hover:underline flex items-center gap-1"
              >
                <LuTriangleAlert className="w-3.5 h-3.5" />
                <span>Report Issue with this Bin</span>
              </Link>
              <Link to="/student/dashboard" className="text-slate-500 font-bold hover:underline">
                Dashboard
              </Link>
            </div>
          </div>
        ) : user?.role === 'COLLECTOR' ? (
          /* Authenticated Collector Action Card */
          <div className="eco-card border-2 border-slate-200 space-y-3">
            <div className="flex items-center gap-2">
              <LuTruck className="w-5 h-5 text-ocean-600" />
              <h3 className="text-sm font-black text-slate-900">Collector Actions</h3>
            </div>
            <p className="text-xs text-slate-600 font-medium">
              You are logged in as field collector <b>{user.name}</b>.
            </p>
            <Link
              to="/collector/scan"
              className="btn-3d btn-3d-blue w-full py-3 text-xs font-black flex items-center justify-center gap-2"
            >
              <span>Service This Bin (Collector Console)</span>
            </Link>
          </div>
        ) : (
          /* Authenticated Admin / Staff Action Card */
          <div className="eco-card border-2 border-slate-200 space-y-3">
            <div className="flex items-center gap-2">
              <LuSettings className="w-5 h-5 text-purple-600" />
              <h3 className="text-sm font-black text-slate-900">Admin Controls</h3>
            </div>
            <p className="text-xs text-slate-600 font-medium">
              You are logged in as {user?.role.toLowerCase()} <b>{user?.name}</b>.
            </p>
            <Link
              to="/admin/bins"
              className="btn-3d btn-3d-white border-slate-300 w-full py-3 text-xs font-black flex items-center justify-center gap-2"
            >
              <span>Manage Campus Bins</span>
            </Link>
          </div>
        )}
      </div>

      {/* Footer Branding */}
      <div className="text-center py-4 text-slate-400 text-[11px] font-bold">
        EcoSense DBIT Mumbai • Zero-Waste Smart Campus Management
      </div>

      {/* Celebratory Points Modal on Student Disposal */}
      <CelebrationModal
        isOpen={showCelebration}
        onClose={() => {
          setShowCelebration(false);
          fetchPublicBin();
        }}
        title="Points Credited!"
        subtitle={`Your disposal was recorded in ${bin.bin_code}. +10 points added to your student account!`}
        pointsEarned={pointsEarned}
      />
    </div>
  );
};
