import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import SymptomChecker from './pages/SymptomChecker';
import MRIAnalyzer from './pages/MRIAnalyzer';

function ProtectedLayout() {
  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-950 transition-colors duration-200 font-sans overflow-x-hidden relative">
      {/* Premium blurred ambient lighting */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full bg-brand-500/5 blur-[120px] pointer-events-none z-0" />
      <div className="absolute bottom-0 left-[20%] w-[400px] h-[400px] rounded-full bg-accent-teal/5 blur-[100px] pointer-events-none z-0" />

      <Sidebar />

      <main className="flex-1 h-screen overflow-y-auto relative z-10 flex flex-col justify-between">
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/symptom" element={<SymptomChecker />} />
            <Route path="/mri" element={<MRIAnalyzer />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>

        <footer className="py-6 px-8 border-t border-slate-200/50 dark:border-slate-800/80 bg-slate-100/10 dark:bg-slate-900/10 text-center text-xs text-slate-400 dark:text-slate-500 font-semibold relative z-10">
          <p>© {new Date().getFullYear()} Aegis Health. All rights reserved. | Developed by Shobhit Yadav</p>
        </footer>
      </main>
    </div>
  );
}

export default function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white font-sans">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-slate-700 border-t-brand-500 animate-spin" />
          <p className="text-xs font-semibold text-slate-400 tracking-wider">SECURE BOOTING CLINICAL LAYERS...</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Login />} />
      <Route path="/*" element={user ? <ProtectedLayout /> : <Navigate to="/login" replace />} />
    </Routes>
  );
}
