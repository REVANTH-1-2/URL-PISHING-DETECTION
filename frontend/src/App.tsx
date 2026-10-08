import React, { useState, useEffect } from 'react';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { ScannerPage } from './pages/ScannerPage';
import { ScanHistoryPage } from './pages/ScanHistoryPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { AboutPage } from './pages/AboutPage';
import { fetchHealth } from './services/api';

export type ThemeMode = 'CYBER_BLUE' | 'PURPLE_NEBULA' | 'EMERALD_MATRIX' | 'STEALTH_DARK';

export default function App() {
  const [currentPage, setCurrentPage] = useState<string>('scanner');
  const [serverStatus, setServerStatus] = useState<boolean>(false);
  const [theme, setTheme] = useState<ThemeMode>('CYBER_BLUE');

  useEffect(() => {
    fetchHealth()
      .then(() => setServerStatus(true))
      .catch(() => setServerStatus(false));
  }, []);

  return (
    <AuthProvider>
      <div className="relative min-h-screen text-slate-100 flex flex-col font-sans overflow-hidden bg-slate-950">
        
        {/* ── Dynamic Background Theme Engine ─────────────────────────────────── */}
        <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
          {/* Cyber Grid Layer */}
          <div className="absolute inset-0 cyber-bg-grid opacity-40" />
          <div className="absolute inset-0 cyber-bg-dots opacity-30" />
          <div className="absolute inset-0 scanline opacity-20" />

          {/* Theme-Specific Glowing Gradient Ambient Orbs */}
          {theme === 'CYBER_BLUE' && (
            <>
              <div className="glow-orb-blue -top-40 -left-20" />
              <div className="glow-orb-cyan top-1/3 -right-40" />
              <div className="glow-orb-purple -bottom-40 left-1/4" />
            </>
          )}

          {theme === 'PURPLE_NEBULA' && (
            <>
              <div className="glow-orb-purple -top-40 -left-20 opacity-90" />
              <div className="glow-orb-blue top-1/2 -right-40 opacity-70" />
              <div className="glow-orb-cyan -bottom-20 left-1/3 opacity-50" />
            </>
          )}

          {theme === 'EMERALD_MATRIX' && (
            <>
              <div className="absolute -top-40 -left-20 w-[600px] h-[600px] bg-emerald-500/10 rounded-full blur-[90px] animate-pulse" />
              <div className="absolute top-1/2 -right-40 w-[500px] h-[500px] bg-teal-500/10 rounded-full blur-[80px]" />
            </>
          )}

          {theme === 'STEALTH_DARK' && (
            <>
              <div className="absolute top-10 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-slate-800/20 rounded-full blur-[100px]" />
            </>
          )}
        </div>

        {/* ── Foreground Navigation & Pages ───────────────────────────────────── */}
        <div className="relative z-10 flex flex-col min-h-screen">
          <Navbar 
            currentPage={currentPage} 
            onNavigate={(page) => setCurrentPage(page)} 
            serverStatus={serverStatus}
            theme={theme}
            onThemeChange={setTheme}
          />

          <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
            {currentPage === 'scanner' && <ScannerPage />}
            {currentPage === 'history' && <ScanHistoryPage />}
            {currentPage === 'analytics' && <AnalyticsPage />}
            {currentPage === 'models' && <ModelPerformancePage />}
            {currentPage === 'login' && <LoginPage onNavigate={setCurrentPage} />}
            {currentPage === 'register' && <RegisterPage onNavigate={setCurrentPage} />}
            {currentPage === 'about' && <AboutPage />}
          </main>

          <footer className="border-t border-slate-900/80 py-6 px-6 text-center text-xs text-slate-500 glass-nav backdrop-blur-md">
            AI-Enhanced Multi-Modal Phishing Detection System — DeepShield AI Engine
          </footer>
        </div>
      </div>
    </AuthProvider>
  );
}
