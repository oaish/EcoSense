import React, { useState, useEffect } from 'react';
import { binsApi } from '../../api/bins';
import { Bin } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { ProgressBar } from '../../components/common/ProgressBar';
import { Trash2, MapPin, Search } from 'lucide-react';

export const StaffBinsPage: React.FC = () => {
  const [bins, setBins] = useState<Bin[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBins = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await binsApi.getBins({ limit: 50 });
      setBins(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load bins list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBins();
  }, []);

  const filteredBins = bins.filter(
    (b) =>
      b.bin_code.toLowerCase().includes(search.toLowerCase()) ||
      b.location?.name.toLowerCase().includes(search.toLowerCase()) ||
      b.waste_type?.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-5xl mx-auto py-4 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-blue-700 bg-blue-100 px-3 py-1 rounded-full border border-blue-200">
            Monitoring
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Campus Bins Inspection
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Inspect physical telemetry, fill levels, and status of all DBIT campus bins.
          </p>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search bin code or building..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-4 py-2 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white shadow-xs focus:outline-none focus:ring-2 focus:ring-blue-400 w-full sm:w-64"
          />
        </div>
      </div>

      {loading ? (
        <LoadingState message="Inspecting campus bins..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchBins} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredBins.map((bin) => (
            <div
              key={bin.bin_id}
              className="eco-card p-5 border-2 border-slate-200/80 hover:border-blue-300 transition-all space-y-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-black text-slate-900">{bin.bin_code}</h3>
                  <p className="text-xs font-bold text-slate-500 flex items-center gap-1 mt-0.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{bin.location?.name || 'Main Campus'}</span>
                  </p>
                </div>
                <StatusBadge status={bin.status} type="bin" size="sm" />
              </div>

              <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200/80 text-xs font-bold flex items-center justify-between">
                <span className="text-slate-500">Waste Type:</span>
                <span className="text-slate-900">{bin.waste_type?.name || 'General'}</span>
              </div>

              <ProgressBar
                value={bin.current_fill_percentage}
                label="Fill Level"
                variant={
                  bin.current_fill_percentage >= 80
                    ? 'coral'
                    : bin.current_fill_percentage >= 50
                    ? 'yellow'
                    : 'green'
                }
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
