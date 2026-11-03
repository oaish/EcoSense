import React, { useState, useEffect } from 'react';
import { processingApi } from '../../api/processing';
import { collectionsApi } from '../../api/collections';
import { ProcessingRecord, ProcessingType, Collection } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { Recycle, Plus, Calendar, CheckCircle2 } from 'lucide-react';
import { LuRecycle, LuLeaf } from 'react-icons/lu';

export const CollectorProcessingPage: React.FC = () => {
  const [records, setRecords] = useState<ProcessingRecord[]>([]);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New Record Form State
  const [showModal, setShowModal] = useState(false);
  const [collectionId, setCollectionId] = useState<number | ''>('');
  const [processingType, setProcessingType] = useState<ProcessingType>('RECYCLING');
  const [quantityKg, setQuantityKg] = useState<number | ''>('');
  const [facilityName, setFacilityName] = useState('');
  const [batchNumber, setBatchNumber] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchProcessingData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [procRes, colRes] = await Promise.all([
        processingApi.getProcessingRecords({ limit: 50 }),
        collectionsApi.getCollections({ limit: 20 }).catch(() => []),
      ]);
      setRecords(procRes);
      setCollections(colRes);
    } catch (err: any) {
      setError(err.message || 'Failed to load processing logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProcessingData();
  }, []);

  const handleCreateProcessing = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!collectionId || !quantityKg) return;

    setIsSubmitting(true);
    try {
      await processingApi.createProcessingRecord({
        collection_id: Number(collectionId),
        processing_type: processingType,
        quantity_kg: Number(quantityKg),
        facility_name: facilityName.trim() || undefined,
        batch_number: batchNumber.trim() || undefined,
      });

      setShowModal(false);
      fetchProcessingData();
    } catch (err: any) {
      alert(err.message || 'Failed to create processing record.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-4 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-ocean-800 bg-ocean-100 px-3 py-1 rounded-full border border-ocean-200">
            Recycling & Composting
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Waste Processing Logs
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Log diversion batches transferred to campus composting or external recyclers.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="btn-3d btn-3d-blue px-5 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-blue shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Log Processing Batch</span>
        </button>
      </div>

      {loading ? (
        <LoadingState message="Loading processing records..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchProcessingData} />
      ) : records.length === 0 ? (
        <EmptyState
          icon={<LuRecycle className="w-12 h-12 text-slate-400" />}
          title="No processing batches recorded"
          description="Record your first campus recycling or composting batch."
          actionText="Log New Batch"
          onAction={() => setShowModal(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {records.map((rec) => (
            <div
              key={rec.processing_id}
              className="eco-card p-5 border-2 border-slate-200/80 hover:border-ocean-300 transition-all space-y-3"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-black text-slate-900">
                    Batch #{rec.batch_number || rec.processing_id}
                  </h3>
                  <p className="text-xs font-bold text-slate-400">
                    Collection #{rec.collection_id}
                  </p>
                </div>
                <StatusBadge status={rec.processing_type} type="processing" />
              </div>

              <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200/80 flex items-center justify-between text-xs font-extrabold">
                <span className="text-slate-500">Processed Quantity:</span>
                <span className="text-slate-900 text-sm">{rec.quantity_kg} kg</span>
              </div>

              {rec.facility_name && (
                <p className="text-xs font-semibold text-slate-600">
                  Facility: <span className="font-bold text-slate-800">{rec.facility_name}</span>
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Log Processing Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-3xl p-6 w-full max-w-md border-2 border-slate-200 shadow-2xl space-y-4">
            <h3 className="text-xl font-black text-slate-900">Log Waste Processing</h3>

            <form onSubmit={handleCreateProcessing} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Source Collection
                </label>
                <select
                  required
                  value={collectionId}
                  onChange={(e) => setCollectionId(Number(e.target.value))}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50"
                >
                  <option value="">Select a recent collection...</option>
                  {collections.map((c) => (
                    <option key={c.collection_id} value={c.collection_id}>
                      Collection #{c.collection_id} ({c.collected_quantity_kg || '—'} kg)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Processing Type
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setProcessingType('RECYCLING')}
                    className={`py-2.5 rounded-2xl font-black text-xs border flex items-center justify-center gap-1.5 ${
                      processingType === 'RECYCLING'
                        ? 'bg-ocean-500 text-white border-ocean-600 shadow-3d-blue'
                        : 'bg-slate-50 text-slate-700'
                    }`}
                  >
                    <LuRecycle className="w-4 h-4" />
                    <span>Recycling</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setProcessingType('COMPOSTING')}
                    className={`py-2.5 rounded-2xl font-black text-xs border flex items-center justify-center gap-1.5 ${
                      processingType === 'COMPOSTING'
                        ? 'bg-eco-500 text-white border-eco-600 shadow-3d-green'
                        : 'bg-slate-50 text-slate-700'
                    }`}
                  >
                    <LuLeaf className="w-4 h-4" />
                    <span>Composting</span>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Processed Weight (kg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  required
                  placeholder="e.g. 8.5"
                  value={quantityKg}
                  onChange={(e) =>
                    setQuantityKg(e.target.value === '' ? '' : parseFloat(e.target.value))
                  }
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold bg-surface-50"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Facility Name
                </label>
                <input
                  type="text"
                  placeholder="e.g. DBIT Organic Compost Pit / Mumbai Recyclers"
                  value={facilityName}
                  onChange={(e) => setFacilityName(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-semibold bg-surface-50"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn-3d btn-3d-white flex-1 py-3 text-xs font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-3d btn-3d-blue flex-1 py-3 text-xs font-black shadow-3d-blue"
                >
                  {isSubmitting ? 'Saving...' : 'Save Record'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
