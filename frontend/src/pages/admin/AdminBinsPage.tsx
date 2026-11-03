import React, { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { binsApi } from '../../api/bins';
import { locationsApi } from '../../api/locations';
import { wasteTypesApi } from '../../api/wasteTypes';
import { Bin, Location, WasteType, BinStatus, BinCreate } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { ProgressBar } from '../../components/common/ProgressBar';
import { BinQRPrintSheet } from '../../components/common/BinQRPrintSheet';
import {
  Trash2,
  Plus,
  Search,
  Filter,
  QrCode,
  Edit2,
  MapPin,
  X,
  CheckCircle,
  Copy,
  Printer,
  FileText,
  ExternalLink,
} from 'lucide-react';
import { LuPrinter, LuDownload, LuQrCode, LuCopy, LuCircleCheck } from 'react-icons/lu';

export const AdminBinsPage: React.FC = () => {
  const [bins, setBins] = useState<Bin[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [wasteTypes, setWasteTypes] = useState<WasteType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [selectedLocation, setSelectedLocation] = useState<number | ''>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');

  // Modals & Exporting State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedQrBin, setSelectedQrBin] = useState<Bin | null>(null);
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [copiedToken, setCopiedToken] = useState(false);
  const [printBinsList, setPrintBinsList] = useState<Bin[] | null>(null);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Create Form State
  const [newBinCode, setNewBinCode] = useState('');
  const [newLocationId, setNewLocationId] = useState<number | ''>('');
  const [newWasteTypeId, setNewWasteTypeId] = useState<number | ''>('');
  const [newCapacity, setNewCapacity] = useState<number>(100);
  const [newStatus, setNewStatus] = useState<BinStatus>('ACTIVE');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [binsRes, locRes, wtRes] = await Promise.all([
        binsApi.getBins({ limit: 100 }),
        locationsApi.getLocations({ limit: 50 }),
        wasteTypesApi.getWasteTypes({ limit: 50 }),
      ]);
      // Sort bins ascending by bin_code
      const sorted = [...binsRes].sort((a, b) => a.bin_code.localeCompare(b.bin_code));
      setBins(sorted);
      setLocations(locRes);
      setWasteTypes(wtRes);
      if (locRes.length > 0) setNewLocationId(locRes[0].location_id);
      if (wtRes.length > 0) setNewWasteTypeId(wtRes[0].waste_type_id);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch bins inventory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const handleCreateBin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBinCode.trim() || !newLocationId || !newWasteTypeId) return;

    setIsSubmitting(true);
    try {
      await binsApi.createBin({
        bin_code: newBinCode.trim().toUpperCase(),
        location_id: Number(newLocationId),
        waste_type_id: Number(newWasteTypeId),
        capacity_liters: Number(newCapacity),
        status: newStatus,
      });

      setShowCreateModal(false);
      setNewBinCode('');
      fetchAllData();
    } catch (err: any) {
      alert(err.message || 'Failed to deploy new bin.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getBinUrl = (qrToken: string) => {
    return `${window.location.origin}/bin/${qrToken}`;
  };

  const handleCopyUrl = (url: string) => {
    navigator.clipboard.writeText(url);
    setCopiedUrl(true);
    setTimeout(() => setCopiedUrl(false), 2000);
  };

  const handleCopyQrToken = (token: string) => {
    navigator.clipboard.writeText(token);
    setCopiedToken(true);
    setTimeout(() => setCopiedToken(false), 2000);
  };

  const handleExportAllPdf = async () => {
    if (bins.length === 0) {
      alert('No bins available to export.');
      return;
    }

    setIsExportingPdf(true);
    setExportError(null);
    try {
      const { downloadBinQRPdf } = await import('../../utils/pdfGenerator');
      await downloadBinQRPdf(bins, 'EcoSense_Bin_QR_Codes.pdf');
    } catch (err: any) {
      setExportError(err.message || 'Failed to generate PDF.');
      alert(err.message || 'Failed to generate PDF.');
    } finally {
      setIsExportingPdf(false);
    }
  };

  const handleSingleExportPdf = async (bin: Bin) => {
    setIsExportingPdf(true);
    setExportError(null);
    try {
      const { downloadBinQRPdf } = await import('../../utils/pdfGenerator');
      await downloadBinQRPdf([bin], `EcoSense_Bin_${bin.bin_code}_QR.pdf`);
    } catch (err: any) {
      setExportError(err.message || 'Failed to generate PDF.');
      alert(err.message || 'Failed to generate PDF.');
    } finally {
      setIsExportingPdf(false);
    }
  };

  const handlePreviewPlacards = (binsToPreview: Bin[]) => {
    if (binsToPreview.length === 0) {
      alert('No bins available to preview or export.');
      return;
    }
    setPrintBinsList(binsToPreview);
  };

  const filteredBins = bins.filter((b) => {
    const matchSearch =
      b.bin_code.toLowerCase().includes(search.toLowerCase()) ||
      b.location?.name.toLowerCase().includes(search.toLowerCase()) ||
      b.waste_type?.name.toLowerCase().includes(search.toLowerCase());
    const matchLocation = selectedLocation === '' || b.location_id === Number(selectedLocation);
    const matchStatus = selectedStatus === '' || b.status === selectedStatus;
    return matchSearch && matchLocation && matchStatus;
  });

  return (
    <div className="max-w-6xl mx-auto py-4 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-purple-800 bg-purple-100 px-3 py-1 rounded-full border border-purple-200">
            Physical Assets
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Bin Management
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Deploy physical campus waste bins, inspect telemetry, and export standardized A4 QR placards.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* <button
            onClick={handleExportAllPdf}
            disabled={isExportingPdf || bins.length === 0}
            className="btn-3d btn-3d-white px-4 py-3 text-xs font-black flex items-center justify-center gap-1.5 border-slate-300 shrink-0"
            title="Download multi-page PDF with 1 page per bin"
          >
            <LuDownload className="w-4 h-4 text-purple-700" />
            <span>{isExportingPdf ? 'Generating PDF...' : `Export QR PDF (${bins.length})`}</span>
          </button> */}

          <button
            onClick={() => handlePreviewPlacards(filteredBins.length > 0 ? filteredBins : bins)}
            className="btn-3d btn-3d-white px-3.5 py-3 text-xs font-black flex items-center justify-center gap-1.5 border-slate-300 shrink-0"
            title="Preview all placards before downloading"
          >
            <LuQrCode className="w-4 h-4 text-slate-700" />
            <span>Preview Placards</span>
          </button>

          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-3d btn-3d-green px-5 py-3 text-xs font-black flex items-center justify-center gap-2 shadow-3d-green shrink-0"
          >
            <Plus className="w-4 h-4" />
            <span>Deploy New Bin</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="eco-card p-4 flex flex-col md:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by bin code, location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <select
            value={selectedLocation}
            onChange={(e) =>
              setSelectedLocation(e.target.value === '' ? '' : Number(e.target.value))
            }
            className="px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-purple-400 w-full md:w-44"
          >
            <option value="">All Locations</option>
            {locations.map((l) => (
              <option key={l.location_id} value={l.location_id}>
                {l.name}
              </option>
            ))}
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3.5 py-2.5 rounded-2xl border border-slate-200 text-xs font-bold text-slate-700 bg-white focus:outline-none focus:ring-2 focus:ring-purple-400 w-full md:w-36"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="FULL">FULL</option>
            <option value="MAINTENANCE">MAINTENANCE</option>
            <option value="DAMAGED">DAMAGED</option>
            <option value="INACTIVE">INACTIVE</option>
          </select>
        </div>
      </div>

      {loading ? (
        <LoadingState message="Loading bin inventory..." />
      ) : error ? (
        <ErrorState message={error} onRetry={fetchAllData} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredBins.map((bin) => (
            <div
              key={bin.bin_id}
              className="eco-card p-5 border-2 border-slate-200 hover:border-purple-300 transition-all space-y-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-black text-slate-900">{bin.bin_code}</h3>
                  <p className="text-xs font-semibold text-slate-500 flex items-center gap-1 mt-0.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{bin.location?.name || 'Main Campus'}</span>
                  </p>
                </div>
                <StatusBadge status={bin.status} type="bin" size="sm" />
              </div>

              <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200/80 text-xs font-bold flex items-center justify-between">
                <span className="text-slate-500">Waste Stream:</span>
                <span className="text-slate-900">{bin.waste_type?.name || 'General'}</span>
              </div>

              <ProgressBar
                value={bin.current_fill_percentage}
                label="Fill Telemetry"
                variant={
                  bin.current_fill_percentage >= 80
                    ? 'coral'
                    : bin.current_fill_percentage >= 50
                      ? 'yellow'
                      : 'green'
                }
              />

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
                <span className="text-[11px] font-bold text-slate-400">
                  Cap: {bin.capacity_liters} L
                </span>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => handleSingleExportPdf(bin)}
                    title="Export QR PDF"
                    className="btn-3d btn-3d-white p-2 text-xs font-bold flex items-center"
                  >
                    <LuDownload className="w-3.5 h-3.5 text-slate-700" />
                  </button>
                  <button
                    onClick={() => setSelectedQrBin(bin)}
                    className="btn-3d btn-3d-white px-3 py-1.5 text-xs font-bold flex items-center gap-1.5"
                  >
                    <LuQrCode className="w-3.5 h-3.5 text-purple-600" />
                    <span>View QR</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* QR Code Inspection Modal */}
      {selectedQrBin && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in" style={{ marginTop: 0 }}>
          <div className="bg-white rounded-3xl p-6 w-full max-w-md border-2 border-slate-200 shadow-2xl space-y-4 text-center">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-black text-slate-900">{selectedQrBin.bin_code}</h3>
                <p className="text-xs text-slate-500 font-semibold">{selectedQrBin.location?.name}</p>
              </div>
              <button
                onClick={() => setSelectedQrBin(null)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Visual High-Res QR Code Matrix with SVG */}
            <div className="w-52 h-52 mx-auto bg-white p-4 rounded-3xl flex flex-col items-center justify-center border-4 border-slate-900 shadow-md">
              <QRCodeSVG
                value={getBinUrl(selectedQrBin.qr_token)}
                size={168}
                level="H"
                includeMargin={true}
              />
            </div>

            {/* Resolved URL Display */}
            <div className="text-left space-y-1 bg-slate-50 p-3 rounded-2xl border border-slate-200 text-xs">
              <p className="text-slate-400 font-bold uppercase text-[10px]">Encoded Public URL</p>
              <p className="font-mono text-emerald-800 font-bold break-all text-[11px]">
                {getBinUrl(selectedQrBin.qr_token)}
              </p>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 gap-2 pt-1">
              <button
                onClick={() => handleCopyUrl(getBinUrl(selectedQrBin.qr_token))}
                className="btn-3d btn-3d-white py-2.5 text-xs font-black flex items-center justify-center gap-1.5"
              >
                {copiedUrl ? (
                  <>
                    <LuCircleCheck className="w-4 h-4 text-eco-600" />
                    <span>URL Copied!</span>
                  </>
                ) : (
                  <>
                    <LuCopy className="w-4 h-4" />
                    <span>Copy URL</span>
                  </>
                )}
              </button>

              <button
                onClick={() => {
                  const b = selectedQrBin;
                  setSelectedQrBin(null);
                  handleSingleExportPdf(b);
                }}
                className="btn-3d btn-3d-green py-2.5 text-xs font-black flex items-center justify-center gap-1.5 shadow-3d-green"
              >
                <LuDownload className="w-4 h-4" />
                <span>Export QR PDF</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Printable Sheet Modal (One Bin Per Page) */}
      {printBinsList && (
        <BinQRPrintSheet
          bins={printBinsList}
          onClose={() => setPrintBinsList(null)}
        />
      )}

      {/* Deploy Bin Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in" style={{ marginTop: 0 }}>
          <div className="bg-white rounded-3xl p-6 w-full max-w-md border-2 border-slate-200 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-black text-slate-900">Deploy Campus Bin</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateBin} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Bin Code
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. BIN-DBIT-099"
                  value={newBinCode}
                  onChange={(e) => setNewBinCode(e.target.value)}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold bg-surface-50 uppercase focus:outline-none focus:ring-2 focus:ring-purple-400"
                />
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Location
                </label>
                <select
                  required
                  value={newLocationId}
                  onChange={(e) => setNewLocationId(Number(e.target.value))}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
                >
                  {locations.map((l) => (
                    <option key={l.location_id} value={l.location_id}>
                      {l.name} ({l.building || 'Campus'})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Waste Type
                </label>
                <select
                  required
                  value={newWasteTypeId}
                  onChange={(e) => setNewWasteTypeId(Number(e.target.value))}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
                >
                  {wasteTypes.map((wt) => (
                    <option key={wt.waste_type_id} value={wt.waste_type_id}>
                      {wt.name} ({wt.code})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
                  Capacity (Liters)
                </label>
                <input
                  type="number"
                  required
                  min="10"
                  max="1000"
                  value={newCapacity}
                  onChange={(e) => setNewCapacity(Number(e.target.value))}
                  className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-sm font-semibold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-purple-400"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="btn-3d btn-3d-white flex-1 py-3 text-xs font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-3d btn-3d-green flex-1 py-3 text-xs font-black shadow-3d-green"
                >
                  {isSubmitting ? 'Deploying...' : 'Deploy Bin'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
