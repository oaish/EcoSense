import React, { useState, useEffect } from 'react';
import { locationsApi } from '../../api/locations';
import { Location } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { MapPin, Plus, Building, X } from 'lucide-react';
import { LuMapPin } from 'react-icons/lu';

export const AdminLocationsPage: React.FC = () => {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [building, setBuilding] = useState('');
  const [floor, setFloor] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchLocations = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await locationsApi.getLocations({ limit: 50 });
      setLocations(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load locations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLocations();
  }, []);

  const handleCreateLocation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !code.trim()) return;

    setIsSubmitting(true);
    try {
      await locationsApi.createLocation({
        name: name.trim(),
        code: code.trim().toUpperCase(),
        building: building.trim() || undefined,
        floor: floor.trim() || undefined,
        description: description.trim() || undefined,
      });

      setShowModal(false);
      setName('');
      setCode('');
      setBuilding('');
      setFloor('');
      setDescription('');
      fetchLocations();
    } catch (err: any) {
      alert(err.message || 'Failed to create location.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-4 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-purple-800 bg-purple-100 px-3 py-1 rounded-full border border-purple-200">
            Spatial Assets
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Campus Locations
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Manage DBIT campus buildings, wings, and floor designated waste zones.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="btn-3d btn-3d-green px-5 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-green shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Add Location</span>
        </button>
      </div>

      {loading ? (
        <LoadingState message="Loading campus locations..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchLocations} />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {locations.map((loc) => (
            <div
              key={loc.location_id}
              className="eco-card p-5 border-2 border-slate-200 hover:border-purple-300 transition-all space-y-3"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-purple-100 text-purple-700 flex items-center justify-center text-xl shadow-xs shrink-0">
                  <LuMapPin className="w-5 h-5 text-purple-700" />
                </div>
                <div>
                  <h3 className="text-base font-black text-slate-900">{loc.name}</h3>
                  <span className="text-[10px] font-mono font-bold bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full border border-slate-200">
                    {loc.code}
                  </span>
                </div>
              </div>

              {(loc.building || loc.floor) && (
                <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 flex items-center gap-2">
                  <Building className="w-3.5 h-3.5 text-slate-400" />
                  <span>
                    {loc.building} {loc.floor ? `• ${loc.floor}` : ''}
                  </span>
                </div>
              )}

              {loc.description && (
                <p className="text-xs text-slate-500 font-medium">{loc.description}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add Location Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in" style={{ marginTop: 0 }}>
          <div className="bg-white rounded-3xl p-6 w-full max-w-md border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-black text-slate-900">Add Campus Location</h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateLocation} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Location Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Canteen Hall North"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Location Code
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. LOC-CAN-N"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 uppercase focus:outline-none focus:ring-2 focus:ring-purple-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                    Building
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Main Block"
                    value={building}
                    onChange={(e) => setBuilding(e.target.value)}
                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                    Floor
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Floor 1"
                    value={floor}
                    onChange={(e) => setFloor(e.target.value)}
                    className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Description
                </label>
                <input
                  type="text"
                  placeholder="e.g. Near cafeteria beverage counter"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-semibold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
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
                  className="btn-3d btn-3d-green flex-1 py-3 text-xs font-black shadow-3d-green"
                >
                  {isSubmitting ? 'Saving...' : 'Save Location'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
