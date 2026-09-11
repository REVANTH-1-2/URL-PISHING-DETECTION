import React from 'react';
import { Shield, LayoutDashboard, History, BarChart3, Cpu, User as UserIcon, LogOut, Info } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface NavbarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  serverStatus: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ currentPage, onNavigate, serverStatus }) => {
  const { user, logout, isAuthenticated } = useAuth();

  const navItems = [
    { id: 'scanner', label: 'Scanner', icon: Shield },
    { id: 'history', label: 'Scan History', icon: History },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'models', label: 'Model Performance', icon: Cpu },
    { id: 'about', label: 'About', icon: Info },
  ];

  return (
    <header className="glass-nav sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between border-b border-slate-800">
      {/* Brand */}
      <div 
        onClick={() => onNavigate('scanner')} 
        className="flex items-center space-x-3 cursor-pointer group"
      >
        <div className="p-2 bg-blue-600/20 border border-blue-500/40 rounded-xl text-blue-400 group-hover:scale-105 transition-transform glow-blue">
          <Shield className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-2">
            DeepShield AI <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">v1.0</span>
          </h1>
          <p className="text-xs text-slate-400">Sophisticated Phishing Detection</p>
        </div>
      </div>

      {/* Nav items */}
      <nav className="hidden md:flex items-center space-x-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* User Actions */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 bg-slate-900/80 px-3 py-1.5 rounded-full border border-slate-800 text-xs">
          <span className={`w-2 h-2 rounded-full ${serverStatus ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`} />
          <span className="text-slate-400">{serverStatus ? 'FastAPI Online' : 'Backend Offline'}</span>
        </div>

        {isAuthenticated ? (
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-300 hidden sm:inline">{user?.name}</span>
            <button
              onClick={logout}
              className="p-2 bg-slate-900 hover:bg-rose-500/20 hover:text-rose-400 border border-slate-800 rounded-xl text-slate-400 transition"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => onNavigate('login')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold transition shadow-md shadow-blue-600/20"
          >
            <UserIcon className="w-4 h-4" /> Sign In
          </button>
        )}
      </div>
    </header>
  );
};
