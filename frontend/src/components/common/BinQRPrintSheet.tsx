import React, { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { Bin } from '../../types';
import { LuDownload, LuX, LuRecycle, LuMapPin, LuInfo, LuLoader } from 'react-icons/lu';
import { downloadBinQRPdf } from '../../utils/pdfGenerator';

interface BinQRPrintSheetProps {
  bins: Bin[];
  onClose: () => void;
}

export const BinQRPrintSheet: React.FC<BinQRPrintSheetProps> = ({ bins, onClose }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getBinUrl = (qrToken: string) => {
    const origin = window.location.origin;
    return `${origin}/bin/${qrToken}`;
  };

  const handleExportPdf = async () => {
    if (!bins || bins.length === 0) {
      alert('No bins available to export.');
      return;
    }

    setIsGenerating(true);
    setError(null);
    try {
      await downloadBinQRPdf(bins);
    } catch (err: any) {
      setError(err.message || 'Failed to generate PDF. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-sm overflow-y-auto p-4 sm:p-6 print:p-0 print:bg-white print:static print:overflow-visible" style={{ marginTop: 0 }}>
      {/* Non-Printable Header Bar */}
      <div className="max-w-4xl mx-auto mb-6 bg-white p-4 rounded-3xl border-2 border-slate-200 shadow-xl flex flex-col sm:flex-row items-center justify-between gap-4 print:hidden">
        <div>
          <h2 className="text-lg font-black text-slate-900">
            Bin QR Placards ({bins.length} {bins.length === 1 ? 'Bin' : 'Bins'})
          </h2>
          <p className="text-xs text-slate-500 font-medium">
            Each bin is formatted on exactly one A4 page in the downloadable PDF.
          </p>
          {error && (
            <p className="text-xs text-coral-600 font-bold mt-1">{error}</p>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleExportPdf}
            disabled={isGenerating}
            className="btn-3d btn-3d-green px-5 py-2.5 text-xs font-black flex items-center gap-2 shadow-3d-green"
          >
            {isGenerating ? (
              <>
                <LuLoader className="w-4 h-4 animate-spin" />
                <span>Generating PDF...</span>
              </>
            ) : (
              <>
                <LuDownload className="w-4 h-4" />
                <span>Export QR PDF ({bins.length === 1 ? '1 Page' : `${bins.length} Pages`})</span>
              </>
            )}
          </button>
          <button
            onClick={onClose}
            disabled={isGenerating}
            className="btn-3d btn-3d-white px-3 py-2.5 text-xs font-bold flex items-center gap-1"
          >
            <LuX className="w-4 h-4" />
            <span>Close</span>
          </button>
        </div>
      </div>

      {/* Printable Placard Pages */}
      <div className="max-w-xl mx-auto space-y-8 print:space-y-0 print:max-w-none print:w-full">
        {bins.map((bin) => {
          const binUrl = getBinUrl(bin.qr_token);
          return (
            <div
              key={bin.bin_id}
              className="bg-white p-8 sm:p-12 rounded-3xl border-2 border-slate-300 shadow-xl print:shadow-none print:border-2 print:border-black print:rounded-none print:p-8 print:m-0 flex flex-col justify-between items-center text-center print:break-after-page print:page-break-after-always print:min-h-screen"
              style={{
                pageBreakAfter: 'always',
                breakAfter: 'page',
                minHeight: '85vh',
              }}
            >
              {/* Institution & Platform Branding */}
              <div className="w-full border-b-2 border-slate-200 pb-4 print:border-black">
                <div className="flex items-center justify-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-black text-sm">
                    <LuRecycle className="w-5 h-5" />
                  </div>
                  <span className="text-2xl font-black tracking-tight text-slate-900 print:text-black">
                    ECOSENSE
                  </span>
                </div>
                <p className="text-xs font-extrabold uppercase tracking-widest text-slate-500 print:text-black mt-1">
                  Don Bosco Institute of Technology (DBIT), Mumbai
                </p>
                <p className="text-[11px] font-semibold text-slate-400 print:text-gray-700">
                  AI-Based Zero Waste Smart Campus Management
                </p>
              </div>

              {/* Large Centered High-Res QR Matrix */}
              <div className="my-6 p-6 bg-white rounded-3xl border-4 border-slate-900 print:border-4 print:border-black shadow-md flex flex-col items-center justify-center">
                <QRCodeSVG
                  value={binUrl}
                  size={240}
                  level="H"
                  includeMargin={true}
                  className="w-56 h-56 print:w-64 print:h-64"
                />
                <span className="text-[10px] font-mono text-slate-400 print:text-gray-600 mt-2">
                  Scan with any camera or QR app
                </span>
              </div>

              {/* Prominent Bin Asset Metadata */}
              <div className="w-full space-y-4">
                <div>
                  <span className="text-xs font-black uppercase tracking-wider text-slate-400 print:text-gray-600">
                    Physical Bin Code
                  </span>
                  <h1 className="text-3xl font-black text-slate-900 print:text-black tracking-tight">
                    {bin.bin_code}
                  </h1>
                </div>

                {/* Waste Type Banner */}
                <div className="p-3 bg-slate-100 rounded-2xl border-2 border-slate-800 print:border-black print:bg-gray-100 max-w-sm mx-auto">
                  <span className="text-[10px] font-black uppercase tracking-wider text-slate-500 print:text-gray-700 block">
                    Designated Waste Stream
                  </span>
                  <span className="text-lg font-black text-slate-900 print:text-black">
                    {bin.waste_type?.name || 'GENERAL RECYCLABLE'}
                  </span>
                </div>

                {/* Location & Capacity Details */}
                <div className="grid grid-cols-2 gap-3 max-w-md mx-auto text-left text-xs">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 print:border-black">
                    <p className="text-[10px] font-bold text-slate-400 uppercase print:text-gray-600">
                      Location
                    </p>
                    <p className="font-black text-slate-900 print:text-black">
                      {bin.location?.name || 'Campus Grounds'}
                    </p>
                    {(bin.location?.building || bin.location?.floor) && (
                      <p className="text-[11px] text-slate-500 font-semibold print:text-gray-700">
                        {bin.location.building} {bin.location.floor ? `• ${bin.location.floor}` : ''}
                      </p>
                    )}
                  </div>

                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 print:border-black">
                    <p className="text-[10px] font-bold text-slate-400 uppercase print:text-gray-600">
                      Capacity & Status
                    </p>
                    <p className="font-black text-slate-900 print:text-black">
                      {bin.capacity_liters || 100} Litres
                    </p>
                    <p className="text-[11px] text-emerald-700 font-bold print:text-black">
                      Status: {bin.status}
                    </p>
                  </div>
                </div>
              </div>

              {/* Bottom Instructions */}
              <div className="w-full border-t-2 border-slate-200 pt-4 mt-6 print:border-black text-center text-xs text-slate-600 print:text-black font-semibold">
                <p>Scan to view this bin in EcoSense and record waste disposal.</p>
                <p className="text-[10px] font-mono text-slate-400 print:text-gray-600 mt-1">
                  URL: {binUrl}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
