import React from 'react';
import { 
  Activity, 
  Users, 
  Clock, 
  Database,
  CheckCircle,
  AlertTriangle,
  Brain,
  Cpu
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend
} from 'recharts';

const usageData = [
  { name: 'Mon', queries: 40, chatTurns: 240 },
  { name: 'Tue', queries: 80, chatTurns: 310 },
  { name: 'Wed', queries: 65, chatTurns: 290 },
  { name: 'Thu', queries: 95, chatTurns: 480 },
  { name: 'Fri', queries: 75, chatTurns: 410 },
  { name: 'Sat', queries: 50, chatTurns: 220 },
  { name: 'Sun', queries: 60, chatTurns: 280 },
];

const pathologyData = [
  { name: 'Fungal Inf.', count: 42 },
  { name: 'Allergy', count: 35 },
  { name: 'GERD', count: 28 },
  { name: 'Hypertension', count: 50 },
  { name: 'Diabetes', count: 62 },
  { name: 'Migraine', count: 19 },
];

export default function Dashboard() {
  const stats = [
    { label: 'Total AI Analyses', value: '1,842', icon: Activity, change: '+12% this week', color: 'text-brand-500' },
    { label: 'RAG Database Size', value: '41 Diseases', icon: Database, change: '100% data coverage', color: 'text-accent-teal' },
    { label: 'Average Latency', value: '180ms', icon: Clock, change: '-45ms reduction', color: 'text-accent-indigo' },
    { label: 'Platform Security', value: 'JWT Active', icon: ShieldActiveIcon, change: 'BCrypt Encryption', color: 'text-accent-violet' },
  ];

  function ShieldActiveIcon(props) {
    return <CheckCircle className="w-5 h-5 text-emerald-500" {...props} />;
  }

  return (
    <div className="p-8 space-y-8 animate-fade-in">
      {/* Header title */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white">
          Clinical Overview
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Real-time metrics, active RAG databases, and platform diagnostic activity.
        </p>
      </div>

      {/* Stats Cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:scale-[1.02] transition-transform duration-200 cursor-pointer">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{stat.label}</span>
                <div className={`p-2 rounded-xl bg-slate-100 dark:bg-slate-900/50 ${stat.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <div>
                <p className="text-3xl font-extrabold text-slate-800 dark:text-white mb-1">{stat.value}</p>
                <span className="text-[10px] font-bold text-slate-400">{stat.change}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Search activity chart */}
        <div className="glass-panel p-6 rounded-3xl flex flex-col">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-800 dark:text-white">AI Search & Chat Activity</h3>
            <p className="text-xs text-slate-400">Weekly breakdown of symptom searches and RAG chatbot dialogue turns.</p>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={usageData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(15, 23, 42, 0.9)', 
                    border: '1px solid rgba(255,255,255,0.1)', 
                    borderRadius: '12px',
                    color: '#fff',
                    fontSize: '12px'
                  }} 
                />
                <Area type="monotone" dataKey="queries" stroke="#0ea5e9" strokeWidth={2} fillOpacity={1} fill="url(#colorQueries)" name="Symptom Checkers" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pathology Chart */}
        <div className="glass-panel p-6 rounded-3xl flex flex-col">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-800 dark:text-white">Top Diagnosed Pathologies</h3>
            <p className="text-xs text-slate-400">Frequency breakdown of diagnostic predictions made via platform classifiers.</p>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={pathologyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{ 
                    background: 'rgba(15, 23, 42, 0.9)', 
                    border: '1px solid rgba(255,255,255,0.1)', 
                    borderRadius: '12px',
                    color: '#fff',
                    fontSize: '12px'
                  }}
                />
                <Bar dataKey="count" fill="#14b8a6" radius={[6, 6, 0, 0]} name="Patient Matches" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Services status board */}
      <div className="glass-panel p-6 rounded-3xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-base font-bold text-slate-800 dark:text-white">Active Pipelines</h3>
            <p className="text-xs text-slate-400">Health checks of connected AI models, storage collections, and gateway routers.</p>
          </div>
          <span className="flex items-center gap-1.5 text-xs text-emerald-500 bg-emerald-500/10 dark:bg-emerald-500/5 px-2.5 py-1 rounded-full font-semibold">
            <CheckCircle className="w-4 h-4 animate-pulse" /> All Systems Online
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-start gap-3 p-4 bg-slate-100/50 dark:bg-slate-900/50 rounded-2xl">
            <div className="p-2 rounded-xl bg-brand-500/15 text-brand-500 shrink-0">
              <Brain className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-800 dark:text-white">Google Gemini LLM Engine</p>
              <p className="text-[10px] text-slate-400 mt-0.5">Model: gemini-2.0-flash</p>
              <span className="inline-block mt-2 text-[9px] font-bold text-emerald-500 bg-emerald-500/15 px-1.5 py-0.5 rounded">Connected</span>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-slate-100/50 dark:bg-slate-900/50 rounded-2xl">
            <div className="p-2 rounded-xl bg-accent-teal/15 text-accent-teal shrink-0">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-800 dark:text-white">Vector Knowledge Store</p>
              <p className="text-[10px] text-slate-400 mt-0.5">Mode: NumPy/Chroma Hybrid</p>
              <span className="inline-block mt-2 text-[9px] font-bold text-emerald-500 bg-emerald-500/15 px-1.5 py-0.5 rounded">Synchronized</span>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-slate-100/50 dark:bg-slate-900/50 rounded-2xl">
            <div className="p-2 rounded-xl bg-accent-indigo/15 text-accent-indigo shrink-0">
              <Cpu className="w-5 h-5 animate-spin" style={{ animationDuration: '3s' }} />
            </div>
            <div>
              <p className="text-xs font-bold text-slate-800 dark:text-white">FastAPI Gateway Router</p>
              <p className="text-[10px] text-slate-400 mt-0.5">Host: Uvicorn / port 8000</p>
              <span className="inline-block mt-2 text-[9px] font-bold text-emerald-500 bg-emerald-500/15 px-1.5 py-0.5 rounded">99.98% SLA</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
