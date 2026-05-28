import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { 
  Activity, 
  LayoutDashboard, 
  MessageSquareHeart, 
  FileSearch, 
  BrainCircuit, 
  Sun, 
  Moon, 
  LogOut,
  User
} from 'lucide-react';

export default function Sidebar({ currentPage, setCurrentPage }) {
  const { user, logout } = useAuth();
  const { darkMode, toggleTheme } = useTheme();

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'chat', label: 'AI Health Assistant', icon: MessageSquareHeart },
    { id: 'symptom', label: 'Symptom Analyzer', icon: FileSearch },
    { id: 'mri', label: 'MRI Brain Scan', icon: BrainCircuit },
  ];

  return (
    <aside className="w-80 h-screen sticky top-0 flex flex-col glass-panel border-r border-slate-200/50 dark:border-slate-800/50 z-30">
      {/* Branding */}
      <div className="p-6 flex items-center gap-3 border-b border-slate-200/50 dark:border-slate-800/50">
        <div className="p-2.5 bg-gradient-to-tr from-brand-500 to-accent-teal rounded-xl shadow-md text-white">
          <Activity className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-slate-800 dark:text-white flex items-center gap-1">
            Aegis<span className="text-brand-500 font-semibold">Health</span>
          </h1>
          <span className="text-[10px] uppercase font-bold text-brand-500/80 dark:text-accent-teal tracking-widest bg-brand-50/50 dark:bg-slate-900/50 px-1.5 py-0.5 rounded">
            AI Platform v2.0
          </span>
        </div>
      </div>

      {/* Navigation menu */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3.5 px-4.5 py-3.5 rounded-2xl text-sm font-semibold transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-brand-500 to-brand-600 text-white shadow-md shadow-brand-500/10'
                  : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100/50 dark:hover:bg-slate-900/50 hover:text-slate-800 dark:hover:text-white'
              }`}
            >
              <Icon className={`w-5 h-5 shrink-0 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-600'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer controls & Profile block */}
      <div className="p-4 border-t border-slate-200/50 dark:border-slate-800/50 space-y-4">
        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="w-full flex items-center justify-between px-4.5 py-3 rounded-2xl text-xs font-bold text-slate-500 dark:text-slate-400 hover:bg-slate-100/50 dark:hover:bg-slate-900/50 transition-colors"
        >
          <span className="flex items-center gap-2">
            {darkMode ? <Sun className="w-4 h-4 text-amber-500" /> : <Moon className="w-4 h-4 text-brand-500" />}
            <span>{darkMode ? 'Switch to Light' : 'Switch to Dark'}</span>
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
            {darkMode ? 'Dark ON' : 'Light ON'}
          </span>
        </button>

        {/* User Card */}
        <div className="flex items-center justify-between p-3 bg-slate-100/50 dark:bg-slate-900/50 rounded-2xl">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-500 to-accent-indigo flex items-center justify-center text-white shrink-0 shadow-inner">
              <User className="w-5 h-5" />
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-bold text-slate-800 dark:text-white truncate">
                {user?.username || 'Clinician'}
              </p>
              <p className="text-[10px] text-slate-400 truncate">
                {user?.email || 'authenticated'}
              </p>
            </div>
          </div>
          <button
            onClick={logout}
            title="Sign Out"
            className="p-2.5 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-400 hover:text-rose-500 dark:hover:text-rose-400 rounded-xl transition-all active:scale-95 shrink-0"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
