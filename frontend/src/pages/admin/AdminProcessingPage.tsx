import React, { useState, useEffect } from 'react';
import { processingApi } from '../../api/processing';
import { ProcessingRecord } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { Recycle, Calendar, Building } from 'lucide-react';
import { LuRecycle } from 'react-icons/lu';

export const AdminProcessingPage: React.FC = () => {
  const [records, setRecords] = useState<ProcessingRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProcessing = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await processingApi.getProcessingRecords({ limit: 100 });
      setRecords(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load processing records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProcessing();
  }, []);

  return (
    <div className="max-w-6xl mx-auto py-4 space-y-6">
      <div>
        <span className="text-xs font-black uppercase tracking-wider text-purple-800 bg-purple-100 px-3 py-1 rounded-full border border-purple-200">
          Landfill Diversion
        </span>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
          Recycling & Composting Logs
        </h1>
        <p className="text-slate-600 text-sm font-medium">
          Comprehensive log of all organic composting and recycling processing batches.
        </p>
      </div>

      {loading ? (
        <LoadingState message="Loading processing batches..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchProcessing} />
      ) : records.length === 0 ? (
        <EmptyState
          icon={<LuRecycle className="w-12 h-12 text-slate-400" />}
          title="No processing batches recorded"
          description="Processing records from collectors and facilities will appear here."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {records.map((rec) => (
            <div
              key={rec.processing_id}
              className="eco-card p-5 border-2 border-slate-200 hover:border-purple-300 transition-all space-y-3"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-black text-slate-900">
                    Batch #{rec.batch_number || rec.processing_id}
                  </h3>
                  <p className="text-xs font-semibold text-slate-400">
                    Source Collection #{rec.collection_id}
                  </p>
                </div>
                <StatusBadge status={rec.processing_type} type="processing" />
              </div>

              <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200/80 flex items-center justify-between text-xs font-extrabold">
                <span className="text-slate-500">Processed Quantity:</span>
                <span className="text-slate-900 text-sm">{rec.quantity_kg} kg</span>
              </div>

              {rec.facility_name && (
                <div className="flex items-center gap-2 text-xs font-bold text-slate-600">
                  <Building className="w-3.5 h-3.5 text-slate-400" />
                  <span>Facility: {rec.facility_name}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
