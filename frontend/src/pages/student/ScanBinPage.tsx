import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { binsApi } from '../../api/bins';
import { disposalsApi } from '../../api/disposals';
import { BinQRRead } from '../../types';
import { QRScanner } from '../../components/common/QRScanner';
import { CelebrationModal } from '../../components/common/CelebrationModal';
import { ProgressBar } from '../../components/common/ProgressBar';
import { StatusBadge } from '../../components/common/StatusBadge';
import {
  LuMapPin,
  LuRecycle,
  LuCircleCheck,
  LuRotateCcw,
  LuSearch,
  LuStar,
  LuBrainCircuit,
  LuSparkles,
  LuArrowRight,
  LuX,
} from 'react-icons/lu';

export const ScanBinPage: React.FC = () => {
  const [scannedBin, setScannedBin] = useState<BinQRRead | null>(null);
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [quantityKg, setQuantityKg] = useState<number | ''>('');
  const [notes, setNotes] = useState('');
  const [isAiPrefilled, setIsAiPrefilled] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);
  const [pointsEarned, setPointsEarned] = useState(10);

  const navigate = useNavigate();
  const location = useLocation();

  // Auto-fill from AI Classifier output (via location state or sessionStorage)
  useEffect(() => {
    const aiNoteState = (location.state as any)?.aiNote;
    const aiNoteSession = sessionStorage.getItem('ecosense_last_ai_note');
    const autoNote = aiNoteState || aiNoteSession;

    if (autoNote && !notes) {
      setNotes(autoNote);
      setIsAiPrefilled(true);
    }
  }, [location.state]);

  const formatWasteTypeName = (name?: string) => {
    if (!name) return 'General Waste';
    const upper = name.toUpperCase();
    if (upper === 'DRY_RECYCLABLE' || upper === 'DRY RECYCLABLE') return 'Dry Recyclable';
    if (upper === 'WET_ORGANIC' || upper === 'WET ORGANIC') return 'Wet / Organic';
    if (upper === 'E_WASTE' || upper === 'E-WASTE') return 'E-Waste / Electronic';
    if (upper === 'HAZARDOUS') return 'Hazardous Waste';
    return name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const getWasteTypeColor = (wasteType?: string, defaultColor?: string) => {
    if (defaultColor) return defaultColor;
    const upper = (wasteType || '').toUpperCase();
    if (
      upper.includes('DRY') ||
      upper.includes('RECYCL') ||
      upper.includes('PLASTIC') ||
      upper.includes('PAPER') ||
      upper.includes('CARDBOARD') ||
      upper.includes('METAL')
    ) {
      return '#0284C7'; // Ocean blue
    }
    if (
      upper.includes('WET') ||
      upper.includes('ORGANIC') ||
      upper.includes('COMPOST') ||
      upper.includes('FOOD')
    ) {
      return '#10B981'; // Eco green
    }
    if (
      upper.includes('E-WASTE') ||
      upper.includes('ELECTR') ||
      upper.includes('BATTER')
    ) {
      return '#8B5CF6'; // Purple
    }
    if (upper.includes('HAZARD')) {
      return '#EF4444'; // Red
    }
    return '#10B981';
  };

  const handleScanSuccess = async (qrToken: string) => {
    setIsLookingUp(true);
    setLookupError(null);
    try {
      const binData = await binsApi.getBinByQrToken(qrToken);
      setScannedBin(binData);
    } catch (err: any) {
      setLookupError(
        err.message || 'No active bin found for this QR code. Please check the code and try again.'
      );
    } finally {
      setIsLookingUp(false);
    }
  };

  const handleDisposalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scannedBin) return;

    setIsSubmitting(true);
    try {
      await disposalsApi.recordDisposal({
        bin_id: scannedBin.bin_id,
        // quantity_kg: quantityKg !== '' ? Number(quantityKg) : undefined,
        notes: notes.trim() || undefined,
      });

      // Default backend disposal gives points
      setPointsEarned(10);
      setShowCelebration(true);
    } catch (err: any) {
      setLookupError(err.message || 'Failed to record disposal. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResetScan = () => {
    setScannedBin(null);
    setLookupError(null);
    setQuantityKg('');
    setNotes('');
  };

  // Derived display values
  const rawWasteType = scannedBin?.waste_type_name || scannedBin?.waste_type?.name || 'General Recyclable';
  const formattedWasteType = formatWasteTypeName(rawWasteType);
  const locationName = scannedBin?.location_name || scannedBin?.location?.name || 'Campus Bin Station';
  const buildingName = scannedBin?.building || scannedBin?.location?.building;
  const floorName = scannedBin?.floor || scannedBin?.location?.floor;
  const binThemeColor = getWasteTypeColor(rawWasteType, scannedBin?.color_code);

  return (
    <div className="max-w-2xl mx-auto py-4 space-y-6">
      {/* Scanner Screen */}
      {!scannedBin && (
        <div className="space-y-6">
          <QRScanner
            onScanSuccess={handleScanSuccess}
            title="Scan Campus Bin"
            subtitle="Point camera at the QR code on the waste bin to record disposal & earn points."
          />

          {/* AI Waste Classifier Quick Banner */}
          <div className="p-4 rounded-3xl bg-gradient-to-r from-ocean-50 to-eco-50 border-2 border-ocean-200/80 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3.5">
              <div className="w-12 h-12 rounded-2xl bg-ocean-500 text-white flex items-center justify-center shrink-0 shadow-sm">
                <LuBrainCircuit className="w-6 h-6" />
              </div>
              <div>
                <div className="inline-flex items-center gap-1 text-[10px] font-black uppercase tracking-wider text-ocean-700 bg-ocean-100/80 px-2 py-0.5 rounded-full mb-0.5">
                  <LuSparkles className="w-3 h-3 text-ocean-600" />
                  Not sure which bin to use?
                </div>
                <h4 className="text-sm font-black text-slate-900">
                  Identify with AI Waste Classifier
                </h4>
                <p className="text-xs text-slate-600 font-medium">
                  Snap or upload a photo to instantly detect waste materials and find the right bin.
                </p>
              </div>
            </div>

            <Link
              to="/classify"
              className="btn-3d btn-3d-blue py-2.5 px-4 text-xs font-black shrink-0 flex items-center gap-1.5 w-full sm:w-auto justify-center"
            >
              <span>AI Classifier</span>
              <LuArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {isLookingUp && (
            <div className="text-center p-4 bg-eco-50 rounded-2xl border border-eco-200 text-eco-800 text-xs font-bold animate-pulse flex items-center justify-center gap-2">
              <LuSearch className="w-4 h-4 animate-spin" />
              <span>Resolving DBIT bin telemetry...</span>
            </div>
          )}

          {lookupError && (
            <div className="p-4 bg-coral-50 rounded-2xl border-2 border-coral-200 text-coral-700 text-xs font-bold text-center">
              {lookupError}
            </div>
          )}
        </div>
      )}

      {/* Scanned Bin Details & Disposal Submission */}
      {scannedBin && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-black uppercase tracking-wider text-eco-700 bg-eco-100 px-3 py-1 rounded-full border border-eco-200">
                Bin Identified
              </span>
              <h2 className="text-2xl font-black text-slate-900 mt-1">Ready for Disposal</h2>
            </div>
            <div className="flex items-center gap-2">
              <Link
                to="/classify"
                className="btn-3d btn-3d-blue px-3 py-2 text-xs font-bold flex items-center gap-1.5"
                title="Open AI Waste Classifier"
              >
                <LuBrainCircuit className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">AI Classifier</span>
              </Link>
              <button
                onClick={handleResetScan}
                className="btn-3d btn-3d-white px-3 py-2 text-xs font-bold flex items-center gap-1.5"
              >
                <LuRotateCcw className="w-3.5 h-3.5" />
                <span>Rescan</span>
              </button>
            </div>
          </div>

          {/* Bin Details Card */}
          <div className="eco-card border-2 border-eco-200 shadow-soft-lg space-y-5">
            {/* Header info */}
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Bin Identifier
                </span>
                <h3 className="text-xl font-black text-slate-900">{scannedBin.bin_code}</h3>
              </div>
              <StatusBadge status={scannedBin.status} type="bin" />
            </div>

            {/* Location & Waste Type Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Designated Waste Type */}
              <div
                className="p-4 rounded-2xl border-2 bg-slate-50 flex items-center gap-3.5 transition-all"
                style={{
                  borderColor: binThemeColor,
                }}
              >
                <div
                  className="w-11 h-11 rounded-xl flex items-center justify-center shadow-xs text-white font-black shrink-0"
                  style={{ backgroundColor: binThemeColor }}
                >
                  <LuRecycle className="w-6 h-6" />
                </div>
                <div className="min-w-0">
                  <p className="text-[10px] font-black uppercase tracking-wider text-slate-500">
                    Designated Waste Type
                  </p>
                  <p className="text-sm font-black text-slate-900 truncate">
                    {formattedWasteType}
                  </p>
                </div>
              </div>

              {/* Location */}
              <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50 flex items-center gap-3.5">
                <div className="w-11 h-11 rounded-xl bg-slate-200 text-slate-700 flex items-center justify-center shadow-xs shrink-0">
                  <LuMapPin className="w-5 h-5" />
                </div>
                <div className="min-w-0">
                  <p className="text-[10px] font-black uppercase tracking-wider text-slate-500">
                    Campus Location
                  </p>
                  <p className="text-sm font-extrabold text-slate-900 truncate">
                    {locationName}
                  </p>
                  {(buildingName || floorName) && (
                    <p className="text-[11px] font-medium text-slate-500 truncate">
                      {buildingName || 'Campus'} {floorName ? `• ${floorName}` : ''}
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Current Fill Progress */}
            <div className="pt-2">
              <ProgressBar
                value={scannedBin.current_fill_percentage ?? 0}
                label="Current Bin Fill Level"
                variant={
                  scannedBin.current_fill_percentage > 80
                    ? 'coral'
                    : scannedBin.current_fill_percentage > 50
                      ? 'yellow'
                      : 'green'
                }
              />
            </div>

            {/* Gamification Reminder Banner */}
            <div className="p-3.5 bg-sun-50 rounded-2xl border border-sun-300 flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-sun-200 text-sun-900 flex items-center justify-center shrink-0">
                <LuStar className="w-5 h-5 fill-current" />
              </div>
              <div>
                <p className="text-xs font-black text-sun-900">Earn +10 Eco Points</p>
                <p className="text-[11px] font-medium text-sun-700">
                  Ensure waste is cleanly separated into this <b>{formattedWasteType}</b> bin.
                </p>
              </div>
            </div>
          </div>

          {/* Disposal Submission Form */}
          <div className="eco-card">
            <h4 className="text-base font-extrabold text-slate-900 mb-4">
              Confirm Waste Disposal
            </h4>

            {lookupError && (
              <div className="p-3 mb-4 bg-coral-50 rounded-2xl border border-coral-200 text-coral-700 text-xs font-bold">
                {lookupError}
              </div>
            )}

            <form onSubmit={handleDisposalSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Approximate Weight (kg) <span className="text-slate-400 font-normal">(optional)</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="50"
                  placeholder="e.g. 0.25"
                  value={quantityKg}
                  onChange={(e) =>
                    setQuantityKg(e.target.value === '' ? '' : parseFloat(e.target.value))
                  }
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-eco-400 bg-surface-50"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600">
                    Disposal Notes <span className="text-slate-400 font-normal">(optional)</span>
                  </label>
                  {isAiPrefilled && (
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold text-ocean-700 bg-ocean-100 px-2.5 py-0.5 rounded-full border border-ocean-200 animate-fade-in">
                      <LuSparkles className="w-3 h-3 text-ocean-600" />
                      Auto-filled from AI
                    </span>
                  )}
                </div>

                <div className="relative">
                  <input
                    type="text"
                    placeholder="e.g. plastic bottle, paper cup..."
                    value={notes}
                    onChange={(e) => {
                      setNotes(e.target.value);
                      setIsAiPrefilled(false);
                    }}
                    className="w-full px-4 py-3 pr-10 rounded-2xl border border-slate-200 text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-eco-400 bg-surface-50"
                  />
                  {notes && (
                    <button
                      type="button"
                      onClick={() => {
                        setNotes('');
                        setIsAiPrefilled(false);
                      }}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 p-1 rounded-lg hover:bg-slate-200/50 transition-colors"
                      title="Clear notes"
                    >
                      <LuX className="w-4 h-4" />
                    </button>
                  )}
                </div>

                {/* Quick auto-suggestion chips */}
                <div className="flex flex-wrap items-center gap-1.5 mt-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mr-1">
                    Quick tags:
                  </span>
                  {[
                    formattedWasteType,
                    'Plastic Bottle',
                    'Food / Organic Waste',
                    'Paper / Cardboard',
                    'Aluminium Can',
                  ]
                    .filter(Boolean)
                    .filter((item, idx, arr) => arr.indexOf(item) === idx)
                    .slice(0, 4)
                    .map((tag) => (
                      <button
                        key={tag}
                        type="button"
                        onClick={() => {
                          setNotes(tag);
                          setIsAiPrefilled(false);
                        }}
                        className="px-2.5 py-1 rounded-xl bg-slate-100 hover:bg-ocean-50 hover:text-ocean-700 hover:border-ocean-200 border border-slate-200 text-[11px] font-bold text-slate-600 transition-all active:scale-95"
                      >
                        + {tag}
                      </button>
                    ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="btn-3d btn-3d-green w-full py-4 text-base font-black flex items-center justify-center gap-2 shadow-3d-green mt-6"
              >
                {isSubmitting ? (
                  <span>Logging Disposal...</span>
                ) : (
                  <>
                    <LuCircleCheck className="w-5 h-5" />
                    <span>Record Disposal & Earn Points</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Celebratory Points Modal */}
      <CelebrationModal
        isOpen={showCelebration}
        onClose={() => {
          setShowCelebration(false);
          navigate('/student/dashboard');
        }}
        title="Nice Work!"
        subtitle={`Your waste was recorded in ${scannedBin?.bin_code || 'the bin'}. Thanks for keeping DBIT clean!`}
        pointsEarned={pointsEarned}
      />
    </div>
  );
};
