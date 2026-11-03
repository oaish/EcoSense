import React, { useState, useEffect } from 'react';
import { collectionsApi } from '../../api/collections';
import { Collection } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { EmptyState } from '../../components/common/EmptyState';
import { Layers, Calendar, ArrowRight, User } from 'lucide-react';
import { LuTruck, LuPackage } from 'react-icons/lu';
import { Link } from 'react-router-dom';

export const CollectorCollectionsPage: React.FC = () => {
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCollections = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await collectionsApi.getCollections({ limit: 50 });
      setCollections(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load collections history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollections();
  }, []);

  return (
    <div className="max-w-5xl mx-auto py-4 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-amber-800 bg-amber-100 px-3 py-1 rounded-full border border-amber-200">
            Log Book
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Collections History
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Review completed waste collections and weight metrics.
          </p>
        </div>

        <Link
          to="/collector/scan"
          className="btn-3d btn-3d-yellow px-5 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-yellow shrink-0"
        >
          <Layers className="w-4 h-4" />
          <span>New Collection</span>
        </Link>
      </div>

      {loading ? (
        <LoadingState message="Loading collection logs..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchCollections} />
      ) : collections.length === 0 ? (
        <EmptyState
          icon={<LuTruck className="w-12 h-12 text-slate-400" />}
          title="No collections logged"
          description="Scan campus bins to start logging your daily collection route."
          actionText="Scan Bin"
          onAction={() => window.location.assign('/collector/scan')}
        />
      ) : (
        <div className="space-y-3">
          {collections.map((col) => (
            <div
              key={col.collection_id}
              className="eco-card p-5 border-2 border-slate-200/80 hover:border-amber-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-amber-100 text-amber-800 flex items-center justify-center text-xl shadow-xs shrink-0">
                    <LuPackage className="w-5 h-5 text-amber-700" />
                  </div>
                  <div>
                    <h3 className="text-base font-extrabold text-slate-900">
                      Collection #{col.collection_id}
                    </h3>
                    <p className="text-xs font-bold text-slate-500 flex items-center gap-2 mt-0.5">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {new Date(col.collection_timestamp).toLocaleString()}
                      </span>
                      {col.collected_quantity_kg && (
                        <span>• <b>{col.collected_quantity_kg} kg</b></span>
                      )}
                    </p>
                  </div>
                </div>
                {col.notes && (
                  <p className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-xl mt-2 font-medium">
                    {col.notes}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs font-black text-eco-800 bg-eco-100 px-3.5 py-1.5 rounded-full border border-eco-200 shadow-xs">
                  Fill: {col.fill_level_before}% → {col.fill_level_after}%
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
