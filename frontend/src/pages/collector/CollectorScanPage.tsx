import React, { useState } from 'react';
import { binsApi } from '../../api/bins';
import { fillReadingsApi } from '../../api/fillReadings';
import { collectionsApi } from '../../api/collections';
import { BinQRRead } from '../../types';
import { QRScanner } from '../../components/common/QRScanner';
import { ProgressBar } from '../../components/common/ProgressBar';
import { StatusBadge } from '../../components/common/StatusBadge';
import {
  RotateCcw,
  CheckCircle,
  Layers,
  Activity,
  MapPin,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { LuSearch } from 'react-icons/lu';
import { useNavigate } from 'react-router-dom';

export const CollectorScanPage: React.FC = () => {
  const [scannedBin, setScannedBin] = useState<BinQRRead | null>(null);
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [activeAction, setActiveAction] = useState<'reading' | 'collection'>('collection');

  // Fill Reading Form State
  const [fillPercentage, setFillPercentage] = useState<number>(85);
  const [readingSource, setReadingSource] = useState<'MANUAL' | 'SENSOR'>('MANUAL');

  // Collection Form State
  const [fillBefore, setFillBefore] = useState<number>(85);
  const [fillAfter, setFillAfter] = useState<number>(0);
  const [collectedKg, setCollectedKg] = useState<number | ''>('');
  const [notes, setNotes] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleScanSuccess = async (qrToken: string) => {
    setIsLookingUp(true);
    setLookupError(null);
    try {
      const binData = await binsApi.getBinByQrToken(qrToken);
      setScannedBin(binData);
      setFillPercentage(binData.current_fill_percentage);
      setFillBefore(binData.current_fill_percentage);
      setFillAfter(0);
    } catch (err: any) {
      setLookupError(err.message || 'No bin found for this QR token.');
    } finally {
      setIsLookingUp(false);
    }
  };

  const handleReadingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scannedBin) return;

    setIsSubmitting(true);
    try {
      await fillReadingsApi.recordFillReading(scannedBin.bin_id, {
        fill_percentage: fillPercentage,
        source: readingSource,
      });
      setActionSuccess(`Fill reading of ${fillPercentage}% logged for ${scannedBin.bin_code}!`);
      // Update local state
      setScannedBin({
        ...scannedBin,
        current_fill_percentage: fillPercentage,
      });
    } catch (err: any) {
      alert(err.message || 'Failed to log fill reading.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCollectionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scannedBin) return;

    setIsSubmitting(true);
    try {
      await collectionsApi.recordCollection({
        bin_id: scannedBin.bin_id,
        fill_level_before: fillBefore,
        fill_level_after: fillAfter,
        collected_quantity_kg: collectedKg !== '' ? Number(collectedKg) : undefined,
        notes: notes.trim() || undefined,
      });

      setActionSuccess(`Collection successfully logged for ${scannedBin.bin_code}!`);
      setScannedBin({
        ...scannedBin,
        current_fill_percentage: fillAfter,
      });
    } catch (err: any) {
      alert(err.message || 'Failed to record collection.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-4 space-y-6">
      {!scannedBin && (
        <div className="space-y-6">
          <QRScanner
            onScanSuccess={handleScanSuccess}
            title="Collector Bin Scanner"
            subtitle="Scan bin QR to record fill measurements or complete waste collection."
          />

          {isLookingUp && (
            <div className="flex items-center justify-center gap-2 p-4 bg-amber-50 rounded-2xl border border-amber-200 text-amber-800 text-xs font-bold animate-pulse">
              <LuSearch className="w-4 h-4 animate-spin" />
              <span>Looking up bin telemetry...</span>
            </div>
          )}

          {lookupError && (
            <div className="p-4 bg-coral-50 rounded-2xl border-2 border-coral-200 text-coral-700 text-xs font-bold text-center">
              {lookupError}
            </div>
          )}
        </div>
      )}

      {scannedBin && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-black uppercase tracking-wider text-amber-800 bg-amber-100 px-3 py-1 rounded-full border border-amber-200">
                Collector Field Mode
              </span>
              <h2 className="text-2xl font-black text-slate-900 mt-1">{scannedBin.bin_code}</h2>
            </div>
            <button
              onClick={() => {
                setScannedBin(null);
                setActionSuccess(null);
              }}
              className="btn-3d btn-3d-white px-3 py-2 text-xs font-bold flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Scan Another</span>
            </button>
          </div>

          {/* Success Banner */}
          {actionSuccess && (
            <div className="p-4 bg-eco-100 border-2 border-eco-300 rounded-2xl text-eco-900 text-xs font-black flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-eco-700 shrink-0" />
              <span>{actionSuccess}</span>
            </div>
          )}

          {/* Bin Details Card */}
          <div className="eco-card space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-bold text-slate-500 flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  <span>{scannedBin.location_name}</span>
                </p>
                <p className="text-sm font-black text-slate-900 mt-0.5">
                  {scannedBin.waste_type_name}
                </p>
              </div>
              <StatusBadge status={scannedBin.status} type="bin" />
            </div>

            <ProgressBar
              value={scannedBin.current_fill_percentage}
              label="Synchronized Fill Level"
              variant={
                scannedBin.current_fill_percentage >= 80
                  ? 'coral'
                  : scannedBin.current_fill_percentage >= 50
                  ? 'yellow'
                  : 'green'
              }
            />
          </div>

          {/* Action Selector Tabs */}
          <div className="flex gap-2">
            <button
              onClick={() => setActiveAction('collection')}
              className={`flex-1 py-3 px-4 rounded-2xl font-black text-xs transition-all flex items-center justify-center gap-2 ${
                activeAction === 'collection'
                  ? 'bg-amber-500 text-slate-950 shadow-3d-yellow'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              <Layers className="w-4 h-4" />
              <span>Record Collection (Empty Bin)</span>
            </button>
            <button
              onClick={() => setActiveAction('reading')}
              className={`flex-1 py-3 px-4 rounded-2xl font-black text-xs transition-all flex items-center justify-center gap-2 ${
                activeAction === 'reading'
                  ? 'bg-amber-500 text-slate-950 shadow-3d-yellow'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Log Fill Reading</span>
            </button>
          </div>

          {/* Collection Form */}
          {activeAction === 'collection' && (
            <form onSubmit={handleCollectionSubmit} className="eco-card space-y-4">
              <h3 className="text-base font-black text-slate-900">Record Waste Collection</h3>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                    Fill Before (%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    required
                    value={fillBefore}
                    onChange={(e) => setFillBefore(Number(e.target.value))}
                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-amber-400"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                    Fill After (%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    required
                    value={fillAfter}
                    onChange={(e) => setFillAfter(Number(e.target.value))}
                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-amber-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Collected Weight (kg) <span className="text-slate-400 font-normal">(optional)</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  placeholder="e.g. 12.5"
                  value={collectedKg}
                  onChange={(e) =>
                    setCollectedKg(e.target.value === '' ? '' : parseFloat(e.target.value))
                  }
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-amber-400"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Operational Notes <span className="text-slate-400 font-normal">(optional)</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Bin washed & replaced liner..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-amber-400"
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-3d btn-3d-yellow w-full py-4 text-base font-black flex items-center justify-center gap-2 shadow-3d-yellow mt-4"
              >
                {isSubmitting ? (
                  <span>Saving Collection Log...</span>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    <span>Complete & Log Collection</span>
                  </>
                )}
              </button>
            </form>
          )}

          {/* Fill Reading Form */}
          {activeAction === 'reading' && (
            <form onSubmit={handleReadingSubmit} className="eco-card space-y-4">
              <h3 className="text-base font-black text-slate-900">Record Bin Fill Reading</h3>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Observed Fill Percentage (0 - 100%)
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={fillPercentage}
                    onChange={(e) => setFillPercentage(Number(e.target.value))}
                    className="flex-1 accent-amber-500 h-2 bg-slate-200 rounded-lg cursor-pointer"
                  />
                  <span className="w-16 text-center text-lg font-black text-slate-900">
                    {fillPercentage}%
                  </span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Measurement Source
                </label>
                <select
                  value={readingSource}
                  onChange={(e) => setReadingSource(e.target.value as any)}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-amber-400"
                >
                  <option value="MANUAL">Manual Field Inspection</option>
                  <option value="SENSOR">Sensor Telemetry</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-3d btn-3d-yellow w-full py-4 text-base font-black flex items-center justify-center gap-2 shadow-3d-yellow mt-4"
              >
                {isSubmitting ? <span>Updating Fill State...</span> : <span>Update Fill State</span>}
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  );
};
