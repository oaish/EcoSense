import React, { useState, useEffect, useRef } from 'react';
import { Html5Qrcode } from 'html5-qrcode';
import { Camera, QrCode, AlertCircle, RefreshCw } from 'lucide-react';

interface QRScannerProps {
  onScanSuccess: (token: string) => void;
  title?: string;
  subtitle?: string;
}

export const QRScanner: React.FC<QRScannerProps> = ({
  onScanSuccess,
  title = 'Scan Campus Bin QR',
  subtitle = 'Point your camera at the QR code located on any DBIT waste bin.',
}) => {
  const [manualToken, setManualToken] = useState('');
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const scannerContainerId = 'ecosense-qr-reader';

  useEffect(() => {
    let isMounted = true;

    const startScanner = async () => {
      try {
        const qrScanner = new Html5Qrcode(scannerContainerId);
        scannerRef.current = qrScanner;

        const config = {
          fps: 10,
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0,
        };

        await qrScanner.start(
          { facingMode: 'environment' },
          config,
          (decodedText) => {
            if (isMounted) {
              // Extract UUID or raw token if URL is scanned
              let token = decodedText.trim();
              if (token.includes('/bin/')) {
                const parts = token.split('/bin/');
                token = parts[parts.length - 1].split('?')[0].split('#')[0];
              } else if (token.includes('/qr/')) {
                const parts = token.split('/qr/');
                token = parts[parts.length - 1].split('?')[0].split('#')[0];
              }
              onScanSuccess(token);
            }
          },
          () => {
            // Ignore scan parse frame errors
          }
        );

        if (isMounted) {
          setIsScanning(true);
          setCameraError(null);
        }
      } catch (err: any) {
        if (isMounted) {
          console.warn('Camera access unavailable or declined:', err);
          setCameraError(
            'Camera access is unavailable or denied. You can manually enter the Bin QR Token below.'
          );
          setIsScanning(false);
        }
      }
    };

    startScanner();

    return () => {
      isMounted = false;
      if (scannerRef.current && scannerRef.current.isScanning) {
        scannerRef.current
          .stop()
          .then(() => scannerRef.current?.clear())
          .catch((e) => console.warn('Error stopping scanner:', e));
      }
    };
  }, [onScanSuccess]);

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualToken.trim()) {
      let token = manualToken.trim();
      if (token.includes('/bin/')) {
        const parts = token.split('/bin/');
        token = parts[parts.length - 1].split('?')[0].split('#')[0];
      } else if (token.includes('/qr/')) {
        const parts = token.split('/qr/');
        token = parts[parts.length - 1].split('?')[0].split('#')[0];
      }
      onScanSuccess(token);
    }
  };

  return (
    <div className="flex flex-col items-center w-full max-w-md mx-auto">
      <div className="text-center mb-6">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-eco-100 border-2 border-eco-300 text-eco-700 flex items-center justify-center mb-3 shadow-3d-green">
          <QrCode className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-black text-slate-900">{title}</h2>
        <p className="text-slate-600 text-xs font-semibold mt-1 px-4">{subtitle}</p>
      </div>

      {/* Video Scanner Container */}
      <div className="w-full relative bg-slate-950 rounded-3xl overflow-hidden shadow-2xl border-4 border-eco-400 aspect-square flex items-center justify-center mb-6">
        <div id={scannerContainerId} className="w-full h-full object-cover"></div>

        {/* Overlay frame guide */}
        {isScanning && (
          <div className="absolute inset-0 pointer-events-none flex flex-col items-center justify-center">
            <div className="w-56 h-56 border-4 border-dashed border-eco-300 rounded-3xl animate-pulse flex items-center justify-center">
              <span className="text-eco-200 text-xs font-bold uppercase tracking-widest bg-slate-900/80 px-3 py-1 rounded-full border border-eco-400/40">
                Align QR Code
              </span>
            </div>
          </div>
        )}

        {/* Camera Error / Fallback State */}
        {cameraError && (
          <div className="absolute inset-0 bg-slate-900/90 text-white p-6 flex flex-col items-center justify-center text-center">
            <div className="w-12 h-12 rounded-2xl bg-coral-500/20 text-coral-400 flex items-center justify-center mb-3 border border-coral-400">
              <Camera className="w-6 h-6" />
            </div>
            <p className="text-xs text-slate-300 mb-4">{cameraError}</p>
            <span className="text-xs font-bold text-sun-300">Use manual entry below:</span>
          </div>
        )}
      </div>

      {/* Manual QR Token Input Fallback */}
      <div className="w-full eco-card">
        <p className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
          <QrCode className="w-4 h-4 text-eco-600" />
          <span>Manual QR Token Entry</span>
        </p>

        <form onSubmit={handleManualSubmit} className="flex gap-2">
          <input
            type="text"
            placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000"
            value={manualToken}
            onChange={(e) => setManualToken(e.target.value)}
            className="flex-1 px-4 py-2.5 rounded-2xl border border-slate-200 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-eco-400 bg-surface-50 font-mono text-xs"
          />
          <button
            type="submit"
            disabled={!manualToken.trim()}
            className="btn-3d btn-3d-green px-5 py-2.5 text-xs font-black disabled:opacity-50"
          >
            Lookup
          </button>
        </form>
      </div>
    </div>
  );
};
