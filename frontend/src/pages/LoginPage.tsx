import React, { useState } from 'react';
import { Shield, User, Lock, ArrowRight } from 'lucide-react';
import { loginUser } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const LoginPage: React.FC<{ onNavigate: (page: string) => void }> = ({ onNavigate }) => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await loginUser(email, password);
      login(res.access_token, res.user);
      onNavigate('scanner');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 glass-card p-8 rounded-2xl border border-slate-800 space-y-6">
      <div className="text-center space-y-2">
        <div className="inline-p-3 bg-blue-600/20 border border-blue-500/40 rounded-xl text-blue-400 p-3 glow-blue">
          <Shield className="w-8 h-8 mx-auto" />
        </div>
        <h2 className="text-xl font-extrabold text-white">Sign In to DeepShield</h2>
        <p className="text-xs text-slate-400">Access full phishing scan history & analytics</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-xs font-semibold text-slate-400 block mb-1">Email Address</label>
          <div className="relative">
            <User className="w-4 h-4 text-slate-500 absolute left-3 top-3.5" />
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@example.com"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-400 block mb-1">Password</label>
          <div className="relative">
            <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3.5" />
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {error && <div className="text-xs text-rose-400 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl">{error}</div>}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-blue-600/30 transition flex items-center justify-center gap-2"
        >
          {loading ? 'Authenticating...' : 'Sign In'} <ArrowRight className="w-4 h-4" />
        </button>
      </form>

      <div className="text-center text-xs text-slate-400">
        Don't have an account?{' '}
        <button onClick={() => onNavigate('register')} className="text-blue-400 hover:underline font-semibold">
          Register now
        </button>
      </div>
    </div>
  );
};
