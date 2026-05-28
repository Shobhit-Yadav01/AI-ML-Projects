import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../context/AuthContext';
import { 
  Search, 
  X, 
  Activity, 
  Plus,
  ShieldCheck, 
  Pizza, 
  Dumbbell, 
  Pill, 
  Info,
  ChevronRight
} from 'lucide-react';

export default function SymptomChecker() {
  const [allSymptoms, setAllSymptoms] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSymptomsList();
  }, []);

  const fetchSymptomsList = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/symptoms`);
      if (response.ok) {
        const data = await response.json();
        setAllSymptoms(data.symptoms || []);
      }
    } catch (e) {
      console.error("Failed to load symptom dictionary:", e);
    }
  };

  const handleAddSymptom = (sym) => {
    if (!selectedSymptoms.includes(sym)) {
      setSelectedSymptoms([...selectedSymptoms, sym]);
    }
    setSearchQuery('');
  };

  const handleRemoveSymptom = (sym) => {
    setSelectedSymptoms(selectedSymptoms.filter(s => s !== sym));
  };

  const handlePredict = async () => {
    if (selectedSymptoms.length === 0) {
      setError("Please select at least one symptom.");
      return;
    }
    setLoading(true);
    setError('');
    setPrediction(null);

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms: selectedSymptoms }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to analyze symptoms.');
      }
      setPrediction(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredSuggestions = searchQuery.trim()
    ? allSymptoms.filter(
        sym => 
          sym.toLowerCase().includes(searchQuery.toLowerCase()) && 
          !selectedSymptoms.includes(sym)
      )
    : [];

  return (
    <div className="p-8 space-y-8 animate-fade-in max-w-5xl">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">
          Symptom-Based Disease Prediction
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Input your symptoms to execute Aegis's Random Forest classifier and extract structured medical recommendations.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Input Side */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel p-6 rounded-3xl space-y-6 relative">
            <h3 className="text-base font-bold text-slate-800 dark:text-white">Symptom Selector</h3>
            
            {/* Search inputs */}
            <div className="relative">
              <Search className="absolute left-4 top-3.5 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Type symptoms (e.g. headache, fever, cough)"
                className="w-full pl-12 pr-4 py-3 rounded-xl border border-slate-200/50 dark:border-slate-800/50 bg-slate-100/50 dark:bg-slate-900/50 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/50 text-slate-800 dark:text-white placeholder-slate-400"
              />
              
              {/* Autocomplete Dropdown */}
              {filteredSuggestions.length > 0 && (
                <div className="absolute left-0 right-0 mt-2 max-h-48 overflow-y-auto glass-card border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl z-20">
                  {filteredSuggestions.map((sym, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleAddSymptom(sym)}
                      className="w-full text-left px-4 py-2.5 text-xs text-slate-700 dark:text-slate-300 hover:bg-brand-500 hover:text-white flex items-center justify-between"
                    >
                      <span>{sym.replace(/_/g, ' ')}</span>
                      <Plus className="w-3.5 h-3.5" />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Selected Badges */}
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Selected Symptoms</p>
              {selectedSymptoms.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No symptoms selected. Type above to add.</p>
              ) : (
                <div className="flex flex-wrap gap-2 max-h-44 overflow-y-auto p-1">
                  {selectedSymptoms.map((sym, idx) => (
                    <span 
                      key={idx} 
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-brand-500/10 text-brand-500 dark:text-brand-400 border border-brand-500/15"
                    >
                      {sym.replace(/_/g, ' ')}
                      <button 
                        onClick={() => handleRemoveSymptom(sym)}
                        className="hover:bg-brand-500/20 rounded-full p-0.5"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {error && (
              <p className="text-xs text-rose-500 font-medium">{error}</p>
            )}

            <button
              onClick={handlePredict}
              disabled={loading || selectedSymptoms.length === 0}
              className="w-full py-3.5 gradient-btn-primary rounded-xl flex items-center justify-center gap-2 font-semibold shadow-md active:scale-95 transition-transform"
            >
              <Activity className="w-5 h-5 animate-pulse" />
              {loading ? 'Analyzing...' : 'Predict Disease'}
            </button>
          </div>
        </div>

        {/* Right Output Side */}
        <div className="lg:col-span-7">
          {!prediction ? (
            <div className="glass-panel p-12 rounded-3xl flex flex-col items-center justify-center text-center h-full min-h-[400px]">
              <div className="p-4 bg-slate-100 dark:bg-slate-900/50 rounded-2xl mb-4 text-slate-400">
                <Activity className="w-12 h-12" />
              </div>
              <h4 className="text-base font-bold text-slate-700 dark:text-slate-300">Awaiting Diagnostic Input</h4>
              <p className="text-xs text-slate-400 max-w-sm mt-2">
                Add your symptoms in the selector and trigger prediction. The ML classifier will analyze correlation weights.
              </p>
            </div>
          ) : (
            <div className="glass-panel rounded-3xl overflow-hidden shadow-sm border border-slate-200/50 dark:border-slate-800/50 animate-slide-up">
              {/* Prediction header */}
              <div className="p-6 bg-gradient-to-r from-brand-500 to-accent-teal text-white">
                <span className="text-[10px] uppercase font-bold tracking-widest bg-white/20 px-2 py-0.5 rounded">Diagnosis Model Ready</span>
                <h3 className="text-2xl font-black mt-2 tracking-tight">{prediction.predicted_disease}</h3>
                <p className="text-xs text-brand-100 mt-1 max-w-xl leading-relaxed">
                  Based on symptom set: {prediction.corrected_symptoms.join(', ').replace(/_/g, ' ')}
                </p>
              </div>

              {/* Navigation Tabs */}
              <div className="flex border-b border-slate-200 dark:border-slate-800 px-4 py-2 gap-2 bg-slate-100/30 dark:bg-slate-900/30">
                {['overview', 'treatment', 'routines'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-4 py-2.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-colors ${
                      activeTab === tab 
                        ? 'bg-slate-200 dark:bg-slate-800 text-slate-800 dark:text-white' 
                        : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Tab Content Panels */}
              <div className="p-6 min-h-[250px]">
                {activeTab === 'overview' && (
                  <div className="space-y-6">
                    <div className="flex gap-3">
                      <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-900/50 text-brand-500 shrink-0 h-9 w-9 flex items-center justify-center">
                        <Info className="w-5 h-5" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-slate-800 dark:text-white mb-1.5">Description</h4>
                        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                          {prediction.description}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'treatment' && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Medications */}
                    <div className="p-4 bg-slate-100/50 dark:bg-slate-900/50 rounded-2xl space-y-3">
                      <h4 className="text-xs font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                        <Pill className="w-4 h-4 text-rose-500" /> Prescribed Medications
                      </h4>
                      <ul className="space-y-1.5">
                        {prediction.medications.map((item, idx) => (
                          <li key={idx} className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
                            <ChevronRight className="w-3.5 h-3.5 text-brand-500 shrink-0" /> {item}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Diets */}
                    <div className="p-4 bg-slate-100/50 dark:bg-slate-900/50 rounded-2xl space-y-3">
                      <h4 className="text-xs font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                        <Pizza className="w-4 h-4 text-emerald-500" /> Recommended Diets
                      </h4>
                      <ul className="space-y-1.5">
                        {prediction.diets.map((item, idx) => (
                          <li key={idx} className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
                            <ChevronRight className="w-3.5 h-3.5 text-accent-teal shrink-0" /> {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {activeTab === 'routines' && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Precautions */}
                    <div className="p-4 bg-slate-100/50 dark:bg-slate-900/50 rounded-2xl space-y-3">
                      <h4 className="text-xs font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                        <ShieldCheck className="w-4 h-4 text-brand-500" /> Actionable Precautions
                      </h4>
                      <ul className="space-y-1.5">
                        {prediction.precautions.map((item, idx) => (
                          <li key={idx} className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
                            <ChevronRight className="w-3.5 h-3.5 text-brand-500 shrink-0" /> {item}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Workouts */}
                    <div className="p-4 bg-slate-100/50 dark:bg-slate-900/50 rounded-2xl space-y-3">
                      <h4 className="text-xs font-bold text-slate-800 dark:text-white flex items-center gap-1.5">
                        <Dumbbell className="w-4 h-4 text-accent-indigo" /> Workout Routines
                      </h4>
                      <ul className="space-y-1.5">
                        {prediction.workout.map((item, idx) => (
                          <li key={idx} className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
                            <ChevronRight className="w-3.5 h-3.5 text-accent-indigo shrink-0" /> {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
