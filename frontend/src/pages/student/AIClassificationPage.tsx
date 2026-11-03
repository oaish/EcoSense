import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  LuBrainCircuit,
  LuUpload,
  LuCamera,
  LuSparkles,
  LuCircleCheck,
  LuTriangleAlert,
  LuQrCode,
  LuRefreshCw,
  LuX,
  LuImage,
  LuRecycle,
  LuLeaf,
  LuZap,
  LuTrash2,
  LuInfo,
} from 'react-icons/lu';
import { classificationApi } from '../../api/classifications';
import { WasteClassification } from '../../types';

type Mode = 'upload' | 'camera';

export const AIClassificationPage: React.FC = () => {
  const [mode, setMode] = useState<Mode>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Camera states
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Classification states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<WasteClassification | null>(null);

  // Demo sample images
  const sampleImages = [
    { label: 'Plastic Bottle', url: 'https://images.unsplash.com/photo-1595278069441-2cf29f8005a4?w=500', categoryHint: 'Dry Recyclable' },
    { label: 'Cardboard Box', url: 'https://images.unsplash.com/photo-1507560461415-997cd00bfd45?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=NHwxMjA3fDA%3D', categoryHint: 'Dry Recyclable' },
    { label: 'Banana Peel / Food', url: 'https://images.unsplash.com/photo-1729368630046-8f0051467115?q=80&w=464&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=NHwxMjA3fDA%3D', categoryHint: 'Wet / Organic' },
    { label: 'Soda Can', url: 'https://images.unsplash.com/photo-1561503412-852800622772?q=80&w=435&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=NHwxMjA3fDA%3D', categoryHint: 'Metal Recyclable' },
  ];

  // Stop camera when switching mode or unmounting
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setIsCameraActive(false);
  };

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async (currentFacing: 'environment' | 'user' = facingMode) => {
    stopCamera();
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: currentFacing, width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setIsCameraActive(true);
    } catch (err: any) {
      setCameraError(
        err.name === 'NotAllowedError'
          ? 'Camera permission was denied. Please allow camera access in your browser settings.'
          : 'Unable to access device camera. Please check your camera permissions or use upload mode.'
      );
      setIsCameraActive(false);
    }
  };

  const handleModeChange = (newMode: Mode) => {
    if (newMode === mode) return;
    setMode(newMode);
    setError(null);
    if (newMode === 'camera') {
      startCamera(facingMode);
    } else {
      stopCamera();
    }
  };

  const toggleCameraFacing = () => {
    const nextFacing = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(nextFacing);
    startCamera(nextFacing);
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (blob) {
          const file = new File([blob], `camera-capture-${Date.now()}.jpg`, { type: 'image/jpeg' });
          setSelectedFile(file);
          setPreviewUrl(URL.createObjectURL(blob));
          stopCamera();
        }
      },
      'image/jpeg',
      0.92
    );
  };

  const validateAndSetFile = (file: File) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('Invalid file type. Please upload a JPEG, PNG, or WEBP image.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File size exceeds the 10MB limit. Please upload a smaller image.');
      return;
    }
    setError(null);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const handleSelectDemo = async (url: string) => {
    setSelectedFile(null);
    setPreviewUrl(url);
    setResult(null);
    setError(null);
    stopCamera();
    setMode('upload');
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (mode === 'camera') {
      startCamera();
    }
  };

  const handleClassify = async () => {
    if (!previewUrl && !selectedFile) {
      setError('Please provide an image first by uploading a file, taking a photo, or selecting a demo.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      let classification: WasteClassification;
      if (selectedFile) {
        // Use multipart binary upload
        classification = await classificationApi.classifyWasteUpload(selectedFile);
      } else if (previewUrl) {
        // Fallback for demo / URL images
        classification = await classificationApi.classifyWaste({ image_url: previewUrl });
      } else {
        throw new Error('No image provided.');
      }
      setResult(classification);

      // Store in session storage so scan page can auto-populate disposal notes
      const category =
        classification.predicted_waste_type?.name ||
        classification.predicted_category ||
        'Recyclable Waste';
      const formatted = category.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase());
      sessionStorage.setItem('ecosense_last_ai_note', formatted);
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'AI Classification failed. Please ensure the backend AI service is running.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const getCategoryDetails = (category?: string) => {
    const upper = String(category || '').toUpperCase();
    if (
      upper.includes('DRY') ||
      upper.includes('RECYCL') ||
      upper.includes('PLASTIC') ||
      upper.includes('PAPER') ||
      upper.includes('CARDBOARD') ||
      upper.includes('METAL') ||
      upper.includes('GLASS')
    ) {
      return {
        bg: 'bg-ocean-50 border-ocean-300 text-ocean-900',
        badge: 'bg-ocean-100 text-ocean-800 border-ocean-300',
        Icon: LuRecycle,
        binText: 'Dry Recyclables Bin (Blue)',
        tips: 'Ensure container is rinsed and free from leftover liquid or food residue.',
      };
    }
    if (
      upper.includes('WET') ||
      upper.includes('ORGANIC') ||
      upper.includes('COMPOST') ||
      upper.includes('FOOD')
    ) {
      return {
        bg: 'bg-eco-50 border-eco-300 text-eco-900',
        badge: 'bg-eco-100 text-eco-800 border-eco-300',
        Icon: LuLeaf,
        binText: 'Organic / Wet Compost Bin (Green)',
        tips: 'Compostable organic matter will be processed in DBIT campus composting units.',
      };
    }
    if (
      upper.includes('E-WASTE') ||
      upper.includes('ELECTRONIC') ||
      upper.includes('BATTER') ||
      upper.includes('CIRCUIT')
    ) {
      return {
        bg: 'bg-purple-50 border-purple-300 text-purple-900',
        badge: 'bg-purple-100 text-purple-800 border-purple-300',
        Icon: LuZap,
        binText: 'E-Waste Bin (Purple / DBIT Lab Collection Point)',
        tips: 'Electronic items contain hazardous components requiring designated DBIT e-waste disposal.',
      };
    }
    return {
      bg: 'bg-slate-50 border-slate-300 text-slate-900',
      badge: 'bg-slate-100 text-slate-800 border-slate-300',
      Icon: LuTrash2,
      binText: 'General Non-Recyclable Waste Bin',
      tips: 'Dispose into regular campus non-recyclable bin.',
    };
  };

  const categoryName =
    result?.predicted_waste_type?.name || result?.predicted_category || 'General Recyclable';
  const confidencePercent =
    result?.confidence_score !== null && result?.confidence_score !== undefined
      ? Math.round(result.confidence_score * 100)
      : 92;
  const isLowConfidence = Boolean(result?.low_confidence || result?.is_low_confidence || confidencePercent < 70);
  const categoryDetails = getCategoryDetails(categoryName);

  return (
    <div className="max-w-3xl mx-auto py-4 space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="w-16 h-16 mx-auto rounded-3xl bg-ocean-100 border-2 border-ocean-300 text-ocean-600 flex items-center justify-center shadow-3d-blue animate-bounce-subtle">
          <LuBrainCircuit className="w-9 h-9" />
        </div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-ocean-50 text-ocean-700 text-xs font-black uppercase tracking-wider border border-ocean-200">
          <LuSparkles className="w-3.5 h-3.5 text-ocean-500" />
          Neural Waste Classification
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">AI Waste Classifier</h1>
        <p className="text-slate-600 text-sm font-medium max-w-lg mx-auto">
          Take a photo or upload an image of waste to instantly detect its material and find the correct campus bin.
        </p>
      </div>

      {/* Mode Switcher */}
      <div className="flex p-1.5 bg-slate-100 rounded-2xl max-w-md mx-auto border border-slate-200">
        <button
          type="button"
          onClick={() => handleModeChange('upload')}
          className={`flex-1 py-2.5 px-4 rounded-xl text-xs font-black transition-all flex items-center justify-center gap-2 ${mode === 'upload'
            ? 'bg-white text-ocean-700 shadow-sm border border-slate-200'
            : 'text-slate-500 hover:text-slate-800'
            }`}
        >
          <LuUpload className="w-4 h-4" />
          <span>Upload Image</span>
        </button>
        <button
          type="button"
          onClick={() => handleModeChange('camera')}
          className={`flex-1 py-2.5 px-4 rounded-xl text-xs font-black transition-all flex items-center justify-center gap-2 ${mode === 'camera'
            ? 'bg-white text-ocean-700 shadow-sm border border-slate-200'
            : 'text-slate-500 hover:text-slate-800'
            }`}
        >
          <LuCamera className="w-4 h-4" />
          <span>Use Device Camera</span>
        </button>
      </div>

      {/* Main Interaction Card */}
      <div className="eco-card space-y-6">
        {/* Upload Mode UI */}
        {mode === 'upload' && !previewUrl && (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-3xl p-8 sm:p-12 text-center transition-all cursor-pointer flex flex-col items-center justify-center gap-4 ${isDragging
              ? 'border-ocean-500 bg-ocean-50/70 scale-[1.01]'
              : 'border-slate-300 hover:border-ocean-400 bg-slate-50/50 hover:bg-ocean-50/20'
              }`}
            onClick={() => document.getElementById('waste-file-input')?.click()}
          >
            <input
              id="waste-file-input"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={handleFileInputChange}
            />
            <div className="w-16 h-16 rounded-2xl bg-ocean-100 border border-ocean-200 text-ocean-600 flex items-center justify-center shadow-sm">
              <LuUpload className="w-8 h-8" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-black text-slate-800">
                Click to upload or drag & drop waste image
              </p>
              <p className="text-xs text-slate-500 font-medium">
                Supports JPG, PNG, or WEBP (Max 10MB)
              </p>
            </div>
          </div>
        )}

        {/* Camera Mode UI */}
        {mode === 'camera' && !previewUrl && (
          <div className="space-y-4">
            {cameraError ? (
              <div className="p-6 bg-coral-50 rounded-2xl border-2 border-coral-200 text-center space-y-3">
                <LuTriangleAlert className="w-8 h-8 text-coral-600 mx-auto" />
                <p className="text-xs font-bold text-coral-800">{cameraError}</p>
                <button
                  type="button"
                  onClick={() => startCamera(facingMode)}
                  className="btn-3d btn-3d-blue py-2 px-4 text-xs font-black inline-flex items-center gap-1.5"
                >
                  <LuRefreshCw className="w-3.5 h-3.5" />
                  <span>Retry Camera Access</span>
                </button>
              </div>
            ) : (
              <div className="relative rounded-3xl overflow-hidden bg-slate-900 aspect-video max-h-[360px] flex items-center justify-center border-2 border-slate-700 shadow-inner">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />

                {/* Viewfinder Overlay */}
                <div className="absolute inset-0 pointer-events-none border-2 border-white/20 rounded-3xl m-4 flex flex-col justify-between p-4">
                  <div className="flex justify-between items-center">
                    <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full bg-black/60 text-white border border-white/20">
                      Live Camera
                    </span>
                    <span className="text-[10px] font-mono text-emerald-400 font-bold bg-black/60 px-2 py-0.5 rounded-full">
                      Ready
                    </span>
                  </div>
                  <div className="text-center">
                    <p className="text-xs font-bold text-white/90 drop-shadow-md bg-black/40 inline-block px-3 py-1 rounded-full">
                      Align waste item inside frame
                    </p>
                  </div>
                </div>

                {/* Camera Controls */}
                <div className="absolute bottom-4 inset-x-0 flex items-center justify-center gap-4 z-10">
                  <button
                    type="button"
                    onClick={toggleCameraFacing}
                    title="Flip Camera"
                    className="w-10 h-10 rounded-full bg-black/60 hover:bg-black/80 text-white flex items-center justify-center backdrop-blur-md border border-white/20 transition-transform active:scale-95"
                  >
                    <LuRefreshCw className="w-4 h-4" />
                  </button>

                  <button
                    type="button"
                    onClick={capturePhoto}
                    className="w-16 h-16 rounded-full bg-white border-4 border-ocean-500 shadow-lg flex items-center justify-center transition-transform active:scale-90 hover:scale-105"
                    title="Capture Photo"
                  >
                    <div className="w-11 h-11 rounded-full bg-ocean-600 flex items-center justify-center text-white">
                      <LuCamera className="w-6 h-6" />
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Image Preview Card (When file / photo is ready) */}
        {previewUrl && (
          <div className="space-y-4">
            <div className="relative rounded-3xl overflow-hidden border-2 border-slate-200 bg-slate-900 aspect-video max-h-[320px] flex items-center justify-center shadow-sm">
              <img
                src={previewUrl}
                alt="Selected waste preview"
                className="w-full h-full object-contain"
              />

              {/* Action buttons on preview */}
              <button
                type="button"
                onClick={handleReset}
                className="absolute top-3 right-3 p-2 rounded-xl bg-black/60 hover:bg-black/80 text-white backdrop-blur-md border border-white/20 transition-all flex items-center gap-1 text-xs font-bold"
                title="Remove image"
              >
                <LuX className="w-4 h-4" />
                <span>Remove</span>
              </button>

              {/* Scanning visual overlay when loading */}
              {isLoading && (
                <div className="absolute inset-0 bg-ocean-950/60 backdrop-blur-xs flex flex-col items-center justify-center text-white space-y-3">
                  <div className="w-12 h-12 rounded-full border-4 border-ocean-400 border-t-transparent animate-spin" />
                  <p className="text-xs font-black uppercase tracking-widest text-ocean-200 animate-pulse">
                    Analyzing Material Patterns...
                  </p>
                </div>
              )}
            </div>

            {/* Action Bar */}
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                type="button"
                onClick={handleClassify}
                disabled={isLoading}
                className="btn-3d btn-3d-blue flex-1 py-4 text-sm font-black flex items-center justify-center gap-2 shadow-3d-blue"
              >
                {isLoading ? (
                  <span>Processing with AI...</span>
                ) : (
                  <>
                    <LuSparkles className="w-4 h-4" />
                    <span>Classify Waste Item</span>
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={handleReset}
                disabled={isLoading}
                className="btn-3d btn-3d-slate py-4 px-6 text-sm font-black flex items-center justify-center gap-2"
              >
                <LuRefreshCw className="w-4 h-4" />
                <span>Change Image</span>
              </button>
            </div>
          </div>
        )}

        {/* Demo Samples Section */}
        <div className="pt-4 border-t border-slate-100 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <LuImage className="w-3.5 h-3.5 text-slate-400" />
              Try a Demo Sample
            </span>
            <span className="text-[11px] font-bold text-slate-400">Preloaded test images</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {sampleImages.map((sample) => (
              <button
                key={sample.label}
                type="button"
                onClick={() => handleSelectDemo(sample.url)}
                className="p-2.5 rounded-2xl border border-slate-200 hover:border-ocean-300 hover:bg-ocean-50/50 text-left transition-all group"
              >
                <p className="text-xs font-bold text-slate-800 truncate group-hover:text-ocean-700">
                  {sample.label}
                </p>
                <p className="text-[10px] text-slate-400 font-medium truncate">
                  {sample.categoryHint}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-4 bg-coral-50 rounded-2xl border-2 border-coral-200 text-coral-700 text-xs font-bold flex items-center gap-2">
            <LuTriangleAlert className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* AI Classification Result Card */}
      {result && (
        <div className="eco-card border-2 border-ocean-300 shadow-soft-lg space-y-6 animate-in fade-in duration-300">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase tracking-wider text-ocean-700 bg-ocean-50 px-3 py-1 rounded-full border border-ocean-200 flex items-center gap-1.5">
                <LuCircleCheck className="w-3.5 h-3.5 text-ocean-600" />
                AI Inference Result
              </span>
            </div>
            <span className="text-[11px] font-bold text-slate-400">
              Model: {result.model_version || 'v1.0.0-eco'}
            </span>
          </div>

          {/* Classification Details */}
          <div className="flex flex-col sm:flex-row items-center gap-6">
            {/* Thumbnail */}
            <div className="w-28 h-28 rounded-2xl overflow-hidden border-2 border-slate-200 shrink-0 bg-slate-100 shadow-sm">
              <img
                src={previewUrl || result.image_url}
                alt="Classified waste item"
                className="w-full h-full object-cover"
              />
            </div>

            {/* AI Decision & Confidence */}
            <div className="flex-1 text-center sm:text-left space-y-3 w-full">
              <div>
                <p className="text-xs font-black uppercase tracking-wider text-slate-400">
                  Detected Category
                </p>
                <h3 className="text-2xl font-black text-slate-900 tracking-tight mt-0.5">
                  {categoryName}
                </h3>
              </div>

              {/* Confidence Progress */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-bold">
                  <span className="text-slate-500">Confidence Score</span>
                  <span
                    className={
                      isLowConfidence ? 'text-amber-600 font-extrabold' : 'text-emerald-700 font-extrabold'
                    }
                  >
                    {confidencePercent}%
                  </span>
                </div>
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${isLowConfidence ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                    style={{ width: `${Math.min(100, Math.max(5, confidencePercent))}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Low Confidence Warning Banner if applicable */}
          {isLowConfidence && (
            <div className="p-3.5 rounded-2xl bg-amber-50 border-2 border-amber-200 flex items-start gap-3 text-amber-900 text-xs">
              <LuTriangleAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-black">Low Confidence Notice</p>
                <p className="font-medium text-amber-800 mt-0.5">
                  The AI is not fully certain about this item. Please verify the bin label on campus before disposal.
                </p>
              </div>
            </div>
          )}

          {/* Segregation Action Banner */}
          <div className={`p-4 rounded-2xl border-2 flex items-start gap-4 ${categoryDetails.bg}`}>
            <div className="w-10 h-10 rounded-xl bg-white/80 border border-current/20 flex items-center justify-center shrink-0 shadow-xs">
              <categoryDetails.Icon className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <p className="text-xs font-black uppercase tracking-wider text-slate-600">
                Recommended Campus Bin
              </p>
              <p className="text-sm font-black text-slate-900">
                {categoryDetails.binText}
              </p>
              <p className="text-xs font-medium text-slate-600">
                {categoryDetails.tips}
              </p>
            </div>
          </div>

          {/* Important Architecture Note: No auto disposal */}
          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200 flex items-center gap-2.5 text-slate-600 text-xs">
            <LuInfo className="w-4 h-4 text-ocean-600 shrink-0" />
            <span>
              <b>Note:</b> AI recommendations do not automatically record disposals. Please scan the campus bin QR to record disposal and earn <b>+10 Eco Points</b>.
            </span>
          </div>

          {/* Scan Bin CTA */}
          <Link
            to="/scan"
            state={{
              aiNote: categoryName,
              category: categoryName,
            }}
            className="btn-3d btn-3d-green w-full py-4 text-sm font-black flex items-center justify-center gap-2 shadow-3d-green"
          >
            <LuQrCode className="w-5 h-5" />
            <span>Proceed to Scan Bin (+10 Pts)</span>
          </Link>
        </div>
      )}
    </div>
  );
};
