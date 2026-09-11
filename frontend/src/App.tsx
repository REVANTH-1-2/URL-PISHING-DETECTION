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

export default function App() {
  const [currentPage, setCurrentPage] = useState<string>('scanner');
  const [serverStatus, setServerStatus] = useState<boolean>(false);

  useEffect(() => {
    fetchHealth()
      .then(() => setServerStatus(true))
      .catch(() => setServerStatus(false));
  }, []);

  return (
    <AuthProvider>
      <div className="min-h-screen bg-black text-slate-100 flex flex-col font-sans">
        <Navbar 
          currentPage={currentPage} 
          onNavigate={(page) => setCurrentPage(page)} 
          serverStatus={serverStatus} 
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

        <footer className="border-t border-zinc-900 py-6 px-6 text-center text-xs text-zinc-500">
          AI-Enhanced Sophisticated Phishing Detection System — DeepShield AI
        </footer>
      </div>
    </AuthProvider>
  );
}
