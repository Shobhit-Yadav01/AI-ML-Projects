import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../context/AuthContext';
import { 
  Upload, 
  BrainCircuit, 
  Activity, 
  FileText, 
  ChevronRight,
  ShieldCheck,
  CheckCircle,
  HelpCircle,
  Eye
} from 'lucide-react';

export default function MRIAnalyzer() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const loadingSteps = [
    "Opening contrast files...",
    "Segmenting white matter volumes...",
    "Locating ventricular margins...",
    "Querying Keras CNN classifier...",
    "Executing Gemini Neuroradiology Vision Analysis..."
  ];

  const processFile = (file) => {
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(file));
        setAnalysis(null);
        setError('');
      } else {
        setError('Please select, drag, or paste a valid image file.');
      }
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    processFile(file);
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    processFile(file);
  };

  useEffect(() => {
    const handlePaste = (e) => {
      // Don't intercept paste events inside normal text input/textarea controls if they exist
      if (
        (e.target.tagName === 'INPUT' && e.target.type !== 'file') ||
        e.target.tagName === 'TEXTAREA'
      ) {
        return;
      }

      const items = e.clipboardData?.items;
      if (!items) return;

      for (const item of items) {
        if (item.type.indexOf('image') !== -1) {
          const file = item.getAsFile();
          if (file) {
            processFile(file);
            e.preventDefault();
            break;
          }
        }
      }
    };

    window.addEventListener('paste', handlePaste);
    return () => {
      window.removeEventListener('paste', handlePaste);
    };
  }, []);

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setLoadingStep(0);
    setError('');
    setAnalysis(null);

    // Dynamic loading steps simulation
    const interval = setInterval(() => {
      setLoadingStep(prev => {
        if (prev < loadingSteps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 1500);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/mri/analyze`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to complete brain MRI scan review.');
      }
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      clearInterval(interval);
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8 animate-fade-in max-w-5xl">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">
          Brain MRI Visual Diagnosis
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Upload T1/T2 weighted contrast-enhanced brain MRI scans to run local CNN classifiers and generate detailed Gemini Vision Neuroradiology summaries.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Upload Side */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel p-6 rounded-3xl space-y-6 flex flex-col items-center justify-center text-center">
            <h3 className="text-sm font-bold text-slate-800 dark:text-white self-start">Scan Uploader</h3>
            
            {/* Drag & drop box */}
            <div className="w-full">
              <label 
                onDragEnter={handleDragEnter}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`w-full h-64 border-2 border-dashed rounded-3xl flex flex-col items-center justify-center cursor-pointer transition-all duration-200 relative overflow-hidden group ${
                  isDragging 
                    ? 'border-brand-500 bg-brand-50/20 dark:bg-brand-500/10' 
                    : 'border-slate-300 dark:border-slate-800 hover:bg-slate-100/50 dark:hover:bg-slate-900/30'
                }`}
              >
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={handleFileChange} 
                  className="hidden" 
                />
                {previewUrl ? (
                  <div className="absolute inset-0 w-full h-full">
                    <img 
                      src={previewUrl} 
                      alt="MRI Preview" 
                      className="w-full h-full object-cover rounded-3xl group-hover:scale-105 transition-transform duration-300" 
                    />
                    <div className="absolute inset-0 bg-slate-950/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center text-white p-4">
                      <Upload className="w-8 h-8 mb-2 animate-bounce" />
                      <span className="text-xs font-bold">Replace MRI Scan</span>
                      <span className="text-[10px] text-slate-200 mt-1">Choose, drag or paste new image</span>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center p-6 text-slate-400">
                    <div className="p-4 bg-slate-100 dark:bg-slate-900/50 rounded-2xl mb-3 group-hover:text-brand-500 transition-colors">
                      <Upload className="w-8 h-8" />
                    </div>
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-300">Choose, drag or paste T1-Weighted MRI scan</span>
                    <span className="text-[10px] text-slate-400 mt-1">Supports JPEG, PNG, JPG or Clipboard paste</span>
                    <span className="text-[9px] text-brand-500 dark:text-brand-400 font-medium mt-2 bg-brand-50/50 dark:bg-brand-950/30 px-2 py-0.5 rounded-full border border-brand-100/30 animate-pulse-slow">
                      Press Cmd+V or Ctrl+V anywhere to paste
                    </span>
                  </div>
                )}
              </label>
            </div>

            {error && (
              <p className="text-xs text-rose-500 font-medium">{error}</p>
            )}

            <button
              onClick={handleAnalyze}
              disabled={loading || !selectedFile}
              className="w-full py-3.5 gradient-btn-primary rounded-xl flex items-center justify-center gap-2 font-semibold shadow-md active:scale-95 transition-transform"
            >
              <BrainCircuit className="w-5 h-5 shrink-0" />
              {loading ? 'Analyzing structures...' : 'Analyze MRI Scan'}
            </button>
          </div>
        </div>

        {/* Right Report Side */}
        <div className="lg:col-span-7">
          {loading && (
            <div className="glass-panel p-12 rounded-3xl flex flex-col items-center justify-center text-center h-full min-h-[400px] space-y-6">
              {/* Spinner */}
              <div className="relative w-20 h-20">
                <div className="absolute inset-0 rounded-full border-4 border-slate-200/50 dark:border-slate-800/50" />
                <div className="absolute inset-0 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
                <Activity className="absolute left-[30px] top-[30px] w-5 h-5 text-brand-500 animate-pulse" />
              </div>
              <div className="space-y-1.5">
                <h4 className="text-sm font-bold text-slate-700 dark:text-slate-300">Evaluating Neural Scan...</h4>
                <p className="text-xs text-brand-500 font-bold tracking-wide uppercase">{loadingSteps[loadingStep]}</p>
              </div>
            </div>
          )}

          {!loading && !analysis && (
            <div className="glass-panel p-12 rounded-3xl flex flex-col items-center justify-center text-center h-full min-h-[400px]">
              <div className="p-4 bg-slate-100 dark:bg-slate-900/50 rounded-2xl mb-4 text-slate-400">
                <BrainCircuit className="w-12 h-12" />
              </div>
              <h4 className="text-base font-bold text-slate-700 dark:text-slate-300">Awaiting Radiological Image</h4>
              <p className="text-xs text-slate-400 max-w-sm mt-2">
                Provide T1-weighted contrast brain MRI scans in the left upload container. Aegis will classify pathologies and generate Neuroradiology summaries.
              </p>
            </div>
          )}

          {!loading && analysis && (
            <div className="glass-panel rounded-3xl overflow-hidden shadow-sm border border-slate-200/50 dark:border-slate-800/50 animate-slide-up">
              {/* Diagnosis Banner */}
              <div className="p-6 bg-gradient-to-r from-accent-indigo to-accent-violet text-white">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] uppercase font-bold tracking-widest bg-white/20 px-2 py-0.5 rounded">Expert AI Assessment</span>
                  <span className="text-xs font-bold text-emerald-300 bg-emerald-500/20 px-2 py-1 rounded-full flex items-center gap-1">
                    <CheckCircle className="w-3.5 h-3.5" /> High Confidence: {analysis.confidence}
                  </span>
                </div>
                <h3 className="text-2xl font-black mt-3 tracking-tight">{analysis.diagnosis}</h3>
                <p className="text-xs text-brand-100 mt-1">Classification performed via T1/T2 MRI Visual Segmentation.</p>
              </div>

              {/* Multi-Model Comparison Overlay */}
              <div className="p-6 border-b border-slate-200/50 dark:border-slate-800/50 bg-slate-100/30 dark:bg-slate-900/30 space-y-3">
                <h4 className="text-xs font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                  <Eye className="w-4 h-4 text-accent-indigo" /> Pathological Diagnostics Comparison
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-white dark:bg-slate-900/50 rounded-xl border border-slate-200/40 dark:border-slate-800/40">
                    <span className="text-[9px] uppercase font-bold text-slate-400">Google Gemini Vision API</span>
                    <p className="text-sm font-bold text-brand-500 mt-1 truncate">{analysis.diagnosis}</p>
                    <span className="text-[10px] font-semibold text-slate-400">Clinical Radiologist persona</span>
                  </div>
                  <div className="p-3 bg-white dark:bg-slate-900/50 rounded-xl border border-slate-200/40 dark:border-slate-800/40">
                    <span className="text-[9px] uppercase font-bold text-slate-400">Local CNN Keras Model</span>
                    <p className="text-sm font-bold text-accent-teal mt-1 truncate">{analysis.local_cnn_result}</p>
                    <span className="text-[10px] font-semibold text-slate-400">Conf: {analysis.local_cnn_confidence}</span>
                  </div>
                </div>
              </div>

              {/* Main Report Blocks */}
              <div className="p-6 space-y-6">
                {/* Visual observation */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                    <Activity className="w-4 h-4 text-brand-500" /> Anatomical Observations
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed pl-5.5">
                    {analysis.clinical_observation}
                  </p>
                </div>

                {/* Radiology written report */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-accent-teal" /> Radiology Assessment Report
                  </h4>
                  <div className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed pl-5.5 whitespace-pre-line">
                    {analysis.radiology_report}
                  </div>
                </div>

                {/* Recommendations */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-500" /> Suggested Clinical Pathway
                  </h4>
                  <div className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed pl-5.5 whitespace-pre-line">
                    {analysis.recommendation}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
