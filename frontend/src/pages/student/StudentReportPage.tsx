import React, { useState, useEffect } from 'react';
import { reportsApi } from '../../api/reports';
import { binsApi } from '../../api/bins';
import { Bin, ReportType, WasteReport } from '../../types';
import { StatusBadge } from '../../components/common/StatusBadge';
import {
  LuTrash2,
  LuWrench,
  LuCircleHelp,
  LuTriangleAlert,
  LuFileText,
  LuCircleCheck,
  LuArrowRight,
  LuSend,
  LuSparkles,
} from 'react-icons/lu';
import { Link, useNavigate } from 'react-router-dom';

export const StudentReportPage: React.FC = () => {
  const [reportType, setReportType] = useState<ReportType>('OVERFLOWING');
  const [binId, setBinId] = useState<string>('');
  const [description, setDescription] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [availableBins, setAvailableBins] = useState<Bin[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedReport, setSubmittedReport] = useState<WasteReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  const reportTypeOptions: { type: ReportType; label: string; Icon: React.ComponentType<{ className?: string }>; desc: string }[] = [
    { type: 'OVERFLOWING', label: 'Overflowing Bin', Icon: LuTrash2, desc: 'Waste piling up over bin rim' },
    { type: 'DAMAGED_BIN', label: 'Damaged Bin', Icon: LuWrench, desc: 'Broken lid, pedal, or cracked container' },
    { type: 'MISSING_BIN', label: 'Missing Bin', Icon: LuCircleHelp, desc: 'Bin removed from designated spot' },
    { type: 'WRONG_SEGREGATION', label: 'Wrong Segregation', Icon: LuTriangleAlert, desc: 'Contaminated waste in recyclable bin' },
    { type: 'OTHER', label: 'General Issue', Icon: LuFileText, desc: 'Other campus cleanliness issue' },
  ];

  useEffect(() => {
    binsApi
      .getBins({ limit: 50 })
      .then((bins) => setAvailableBins(bins))
      .catch((err) => console.warn('Could not load bins for report dropdown', err));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const res = await reportsApi.submitReport({
        report_type: reportType,
        bin_id: binId.trim() ? binId : undefined,
        description: description.trim() || undefined,
        image_url: imageUrl.trim() || undefined,
      });

      setSubmittedReport(res);
    } catch (err: any) {
      setError(err.message || 'Failed to submit report. Please check the fields and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-black uppercase tracking-wider text-coral-700 bg-coral-100 px-3 py-1 rounded-full border border-coral-200">
            Campus Cleanliness
          </span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
            Report Waste Issue
          </h1>
          <p className="text-slate-600 text-sm font-medium">
            Alert facilities about overflowing or damaged bins. Earn points once resolved!
          </p>
        </div>

        <Link
          to="/student/reports"
          className="btn-3d btn-3d-white px-4 py-2.5 text-xs font-bold flex items-center gap-1.5 shrink-0"
        >
          <LuFileText className="w-4 h-4" />
          <span>My Reports</span>
        </Link>
      </div>

      {/* Success State */}
      {submittedReport && (
        <div className="eco-card border-2 border-eco-300 shadow-soft-lg text-center p-8 space-y-5 animate-in fade-in">
          <div className="w-16 h-16 mx-auto rounded-3xl bg-eco-100 text-eco-600 flex items-center justify-center text-3xl shadow-3d-green">
            <LuCircleCheck className="w-9 h-9" />
          </div>
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-eco-50 text-eco-800 text-xs font-black uppercase tracking-wider mb-2 border border-eco-200">
              <LuSparkles className="w-3.5 h-3.5 text-eco-600" />
              <span>Report Submitted Successfully</span>
            </div>
            <h3 className="text-2xl font-black text-slate-900">
              Report #{submittedReport.report_id}
            </h3>
            <p className="text-slate-600 text-xs font-semibold mt-1">
              Facilities team has been notified. You will be awarded bonus points once this report is
              resolved!
            </p>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200/80 flex items-center justify-between text-left text-xs">
            <div>
              <p className="font-bold text-slate-500">Report Type</p>
              <p className="font-extrabold text-slate-800 capitalize">
                {submittedReport.report_type.replace(/_/g, ' ')}
              </p>
            </div>
            <StatusBadge status={submittedReport.status} type="report" />
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => {
                setSubmittedReport(null);
                setDescription('');
                setImageUrl('');
              }}
              className="btn-3d btn-3d-white flex-1 py-3 text-xs font-black"
            >
              Report Another Issue
            </button>
            <Link
              to="/student/reports"
              className="btn-3d btn-3d-green flex-1 py-3 text-xs font-black flex items-center justify-center gap-1.5"
            >
              <span>View Report History</span>
              <LuArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}

      {/* Form */}
      {!submittedReport && (
        <form onSubmit={handleSubmit} className="eco-card space-y-6">
          {error && (
            <div className="p-4 bg-coral-50 rounded-2xl border-2 border-coral-200 text-coral-700 text-xs font-bold flex items-center gap-2">
              <LuTriangleAlert className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Issue Type Selector */}
          <div>
            <label className="block text-xs font-black uppercase tracking-wider text-slate-600 mb-3">
              1. What is the issue?
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {reportTypeOptions.map((opt) => (
                <button
                  key={opt.type}
                  type="button"
                  onClick={() => setReportType(opt.type)}
                  className={`p-3.5 rounded-2xl border-2 text-left transition-all flex items-start gap-3 ${
                    reportType === opt.type
                      ? 'border-coral-500 bg-coral-50 text-coral-900 shadow-xs'
                      : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="w-9 h-9 rounded-xl bg-coral-100 text-coral-700 flex items-center justify-center shrink-0">
                    <opt.Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-black">{opt.label}</p>
                    <p className="text-[11px] font-medium text-slate-500 leading-tight mt-0.5">
                      {opt.desc}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Affected Bin Selector (Optional) */}
          <div>
            <label className="block text-xs font-black uppercase tracking-wider text-slate-600 mb-1.5">
              2. Specific Bin <span className="text-slate-400 font-normal">(optional)</span>
            </label>
            <select
              value={binId}
              onChange={(e) => setBinId(e.target.value)}
              className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-coral-400 bg-surface-50"
            >
              <option value="">General campus issue (No specific bin)</option>
              {availableBins.map((b) => (
                <option key={b.bin_id} value={b.bin_id}>
                  {b.bin_code} — {b.location?.name || 'Campus'} ({b.waste_type?.name || 'Bin'})
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-black uppercase tracking-wider text-slate-600 mb-1.5">
              3. Description / Details
            </label>
            <textarea
              required
              rows={3}
              placeholder="Provide context on the issue (e.g. Bin overflowing near cafeteria entrance)..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-coral-400 bg-surface-50"
            ></textarea>
          </div>

          {/* Optional Photo URL */}
          <div>
            <label className="block text-xs font-black uppercase tracking-wider text-slate-600 mb-1.5">
              4. Photo URL <span className="text-slate-400 font-normal">(optional)</span>
            </label>
            <input
              type="url"
              placeholder="https://..."
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-mono font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-coral-400 bg-surface-50"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-3d btn-3d-coral w-full py-4 text-base font-black flex items-center justify-center gap-2 shadow-3d-coral"
          >
            {isSubmitting ? (
              <span>Submitting Report...</span>
            ) : (
              <>
                <LuSend className="w-5 h-5" />
                <span>Submit Waste Issue Report</span>
              </>
            )}
          </button>
        </form>
      )}
    </div>
  );
};
