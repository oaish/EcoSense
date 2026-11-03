import React, { useState, useEffect } from 'react';
import { predictionsApi } from '../../api/predictions';
import { binsApi } from '../../api/bins';
import { Bin, FillPrediction } from '../../types';
import { LoadingState } from '../../components/common/LoadingState';
import { ErrorState } from '../../components/common/ErrorState';
import { ProgressBar } from '../../components/common/ProgressBar';
import { TrendingUp, Sparkles, MapPin, Calendar, Clock, ArrowRight } from 'lucide-react';

export const CollectorPredictionsPage: React.FC = () => {
  const [bins, setBins] = useState<Bin[]>([]);
  const [selectedBinId, setSelectedBinId] = useState<string>('');
  const [horizonMinutes, setHorizonMinutes] = useState<number>(120);
  const [prediction, setPrediction] = useState<FillPrediction | null>(null);
  const [recentPredictions, setRecentPredictions] = useState<FillPrediction[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    binsApi
      .getBins({ limit: 50 })
      .then((bList) => {
        setBins(bList);
        if (bList.length > 0) {
          setSelectedBinId(bList[0].bin_id);
        }
      })
      .catch((err) => console.warn('Could not load bins for prediction selector', err))
      .finally(() => setPageLoading(false));
  }, []);

  const handleGeneratePrediction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBinId) return;

    setIsLoading(true);
    setError(null);
    try {
      const result = await predictionsApi.generatePrediction(selectedBinId, {
        horizon_minutes: horizonMinutes,
      });
      setPrediction(result);
      setRecentPredictions((prev) => [result, ...prev.slice(0, 4)]);
    } catch (err: any) {
      setError(err.message || 'Unable to generate prediction (requires historical telemetry).');
    } finally {
      setIsLoading(false);
    }
  };

  if (pageLoading) {
    return <LoadingState message="Initializing prediction models..." />;
  }

  return (
    <div className="max-w-4xl mx-auto py-4 space-y-6">
      <div>
        <span className="text-xs font-black uppercase tracking-wider text-amber-800 bg-amber-100 px-3 py-1 rounded-full border border-amber-200">
          AI Forecasting
        </span>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight mt-1">
          Bin Fill Predictions
        </h1>
        <p className="text-slate-600 text-sm font-medium">
          Generate on-demand predictive forecasts for campus bin fill accumulation.
        </p>
      </div>

      {/* Prediction Generator Form */}
      <div className="eco-card border-2 border-amber-200 shadow-soft-card space-y-4">
        <h3 className="text-base font-black text-slate-900 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-500" />
          <span>Generate Fill Level Forecast</span>
        </h3>

        <form onSubmit={handleGeneratePrediction} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="sm:col-span-2">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Select Campus Bin
            </label>
            <select
              value={selectedBinId}
              onChange={(e) => setSelectedBinId(e.target.value)}
              className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-amber-400"
            >
              {bins.map((b) => (
                <option key={b.bin_id} value={b.bin_id}>
                  {b.bin_code} — {b.location?.name || 'Campus'} ({b.waste_type?.name || 'Bin'})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1.5">
              Forecast Horizon
            </label>
            <select
              value={horizonMinutes}
              onChange={(e) => setHorizonMinutes(Number(e.target.value))}
              className="w-full px-4 py-3 rounded-2xl border border-slate-200 text-xs font-bold bg-surface-50 focus:outline-none focus:ring-2 focus:ring-amber-400"
            >
              <option value={30}>30 Minutes</option>
              <option value={60}>1 Hour</option>
              <option value={120}>2 Hours</option>
              <option value={240}>4 Hours</option>
              <option value={480}>8 Hours</option>
            </select>
          </div>

          <div className="sm:col-span-3">
            <button
              type="submit"
              disabled={isLoading}
              className="btn-3d btn-3d-yellow w-full py-3.5 text-sm font-black flex items-center justify-center gap-2 shadow-3d-yellow"
            >
              {isLoading ? (
                <span>Running ML Predictor...</span>
              ) : (
                <>
                  <TrendingUp className="w-4 h-4" />
                  <span>Generate Forecast</span>
                </>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="p-3.5 bg-coral-50 rounded-2xl border border-coral-200 text-coral-700 text-xs font-bold">
            {error}
          </div>
        )}
      </div>

      {/* Prediction Output Card */}
      {prediction && (
        <div className="eco-card border-2 border-amber-300 shadow-soft-lg space-y-4 animate-in fade-in">
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-wider text-amber-800 bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
              Prediction Result
            </span>
            <span className="text-xs font-bold text-slate-400">
              Confidence: {Math.round(prediction.confidence_score * 100)}%
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200/80">
              <p className="text-[10px] font-black uppercase tracking-wider text-slate-400">
                Forecasted Fill Level
              </p>
              <h4 className="text-3xl font-black text-slate-900 mt-1">
                {Math.round(prediction.predicted_fill_percentage)}%
              </h4>
              <div className="mt-3">
                <ProgressBar
                  value={prediction.predicted_fill_percentage}
                  variant={prediction.predicted_fill_percentage >= 80 ? 'coral' : 'yellow'}
                  showPercentage={false}
                />
              </div>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200/80 space-y-2">
              <p className="text-[10px] font-black uppercase tracking-wider text-slate-400">
                Model Telemetry
              </p>
              <p className="text-xs font-bold text-slate-700">
                Model: <span className="font-extrabold text-slate-900">{prediction.model_name}</span>
              </p>
              <p className="text-xs font-bold text-slate-700">
                Target Timestamp:{' '}
                <span className="font-extrabold text-slate-900">
                  {new Date(prediction.target_timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
