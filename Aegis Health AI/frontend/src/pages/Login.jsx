import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { ShieldAlert, Activity, Heart, ArrowRight } from 'lucide-react';

export default function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (isRegister) {
      const res = await register(username, email, password);
      if (res.success) {
        // Toggle to login and prefill
        setIsRegister(false);
        setError('Registration successful! Please login.');
      } else {
        setError(res.error || 'Failed to register');
      }
    } else {
      const res = await login(email, password);
      if (!res.success) {
        setError(res.error || 'Invalid credentials');
      }
    }
    setLoading(false);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 transition-colors duration-300 overflow-hidden font-sans">
      {/* Background visual gradients */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-brand-500/10 blur-[120px] dark:bg-brand-500/5" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-accent-teal/10 blur-[100px] dark:bg-accent-teal/5" />
      <div className="absolute top-[30%] right-[10%] w-[30%] h-[30%] rounded-full bg-accent-indigo/10 blur-[90px] dark:bg-accent-indigo/5" />

      <div className="w-full max-w-md p-8 m-4 rounded-3xl glass-panel relative z-10 animate-fade-in border border-slate-200/50 dark:border-slate-800/80">
        {/* Branding header */}
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-gradient-to-tr from-brand-500 to-accent-teal rounded-2xl shadow-lg mb-3">
            <Activity className="w-8 h-8 text-white animate-pulse" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-800 dark:text-white flex items-center gap-1.5">
            Aegis <span className="text-brand-500">Health</span>
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {isRegister ? 'Create your platform account' : 'Production-Ready AI Healthcare Platform'}
          </p>
        </div>

        {error && (
          <div className={`p-4 rounded-xl mb-6 flex items-start gap-2 text-sm ${error.includes('successful') ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400' : 'bg-rose-500/15 text-rose-600 dark:text-rose-400'}`}>
            <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Username</label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Dr. John Doe"
                className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100/50 dark:bg-slate-900/50 text-slate-800 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500/50"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="john@hospital.org"
              className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100/50 dark:bg-slate-900/50 text-slate-800 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500/50"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100/50 dark:bg-slate-900/50 text-slate-800 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500/50"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl gradient-btn-primary flex items-center justify-center gap-2 font-medium mt-6 shadow-xl cursor-pointer"
          >
            {loading ? 'Processing...' : isRegister ? 'Register Account' : 'Authenticate Credentials'}
            {!loading && <ArrowRight className="w-5 h-5" />}
          </button>
        </form>

        <div className="mt-8 text-center border-t border-slate-200 dark:border-slate-800 pt-6">
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setError('');
            }}
            className="text-sm font-semibold text-brand-500 hover:text-brand-600 dark:hover:text-brand-400 transition-colors cursor-pointer"
          >
            {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Sign Up"}
          </button>
        </div>
      </div>
    </div>
  );
}
