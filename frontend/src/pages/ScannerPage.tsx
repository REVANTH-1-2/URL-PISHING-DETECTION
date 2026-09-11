import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, AlertTriangle, Cpu, HelpCircle, CornerDownRight, Zap, Globe, ExternalLink } from 'lucide-react';
import { scanURL } from '../services/api';
import { ScanResponse } from '../types';

export const ScannerPage: React.FC = () => {
  const [targetUrl, setTargetUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    if (!targetUrl.trim()) {
      setError('Please enter a target URL to scan.');
      return;
    }

    setLoading(true);

    try {
      const data = await scanURL(targetUrl.trim());
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'URL scan failed');
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (sampleType: 'PHISHING' | 'LEGIT' | 'IP_BASED') => {
    setResult(null);
    setError(null);

    if (sampleType === 'PHISHING') {
      setTargetUrl('http://chase-bank-security-update.xyz/login/verify.html');
    } else if (sampleType === 'IP_BASED') {
      setTargetUrl('http://192.168.1.1/online-banking/verify-login.php?id=9238');
    } else {
      setTargetUrl('https://github.com/fastapi/fastapi');
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Top Banner */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Zap className="w-6 h-6 text-blue-400" /> AI Phishing URL Scanner
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Detect sophisticated phishing threats across web domains using ML ensemble models (XGBoost + RF) & Explainable AI (XAI).
          </p>
        </div>
      </div>

      {/* Preset Sample Presets */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/40 p-4 rounded-xl border border-slate-800/80">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5 text-amber-400" /> Pre-fill Real Sample:
        </span>
        <div className="flex flex-wrap gap-2 text-xs font-semibold">
          <button onClick={() => loadSample('PHISHING')} className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-rose-400 hover:text-rose-300 hover:border-rose-500/40 transition cursor-pointer">
            + Phishing URL Sample
          </button>
          <button onClick={() => loadSample('IP_BASED')} className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-amber-400 hover:text-amber-300 hover:border-amber-500/40 transition cursor-pointer">
            + Suspicious / IP Sample
          </button>
          <button onClick={() => loadSample('LEGIT')} className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-emerald-400 hover:text-emerald-300 hover:border-emerald-500/40 transition cursor-pointer">
            + Safe URL Sample
          </button>
        </div>
      </div>

      {/* Input Form */}
      <div className="glass-card rounded-2xl border border-slate-800 p-6 space-y-6">
        <form onSubmit={handleScan} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Target URL to Analyze</label>
            <div className="relative">
              <input
                type="text"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="https://login-verification-security.com/update-info?id=82931"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-slate-200 focus:outline-none focus:border-blue-500 font-mono transition pr-12"
              />
              <ExternalLink className="w-5 h-5 text-slate-600 absolute right-4 top-1/2 -translate-y-1/2" />
            </div>
          </div>

          {error && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-xs font-medium flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" /> {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="px-8 py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-blue-600/30 transition flex items-center justify-center gap-2 w-full md:w-auto cursor-pointer"
          >
            {loading ? <Cpu className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            {loading ? 'Analyzing URL with ML Inference...' : 'ANALYZE URL NOW'}
          </button>
        </form>
      </div>

      {/* Detailed Analysis Output */}
      {result && (
        <div className="glass-card rounded-2xl border border-slate-800 p-8 space-y-8 animate-fadeIn">
          {/* Top Threat Classification Card */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
            <div className="flex items-center gap-4">
              <div className={`p-4 rounded-2xl ${
                result.prediction === 'PHISHING' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                result.prediction === 'SUSPICIOUS' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
              }`}>
                {result.prediction === 'PHISHING' ? <ShieldAlert className="w-10 h-10" /> :
                 result.prediction === 'SUSPICIOUS' ? <AlertTriangle className="w-10 h-10" /> :
                 <CheckCircle className="w-10 h-10" />}
              </div>
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Classification</span>
                <h3 className={`text-3xl font-extrabold tracking-tight ${
                  result.prediction === 'PHISHING' ? 'text-rose-400' :
                  result.prediction === 'SUSPICIOUS' ? 'text-amber-400' :
                  'text-emerald-400'
                }`}>
                  {result.prediction}
                </h3>
                <span className="text-xs text-slate-400">Type: <strong className="text-blue-400">{result.input_type}</strong></span>
              </div>
            </div>

            <div className="flex items-center gap-6 bg-slate-950 p-4 rounded-xl border border-slate-800 self-stretch justify-around md:justify-end">
              <div className="text-center">
                <span className="text-[10px] text-slate-400 font-bold uppercase block">Risk Score</span>
                <span className="text-2xl font-black text-white">{result.risk_score}%</span>
              </div>
              <div className="w-px h-8 bg-slate-800" />
              <div className="text-center">
                <span className="text-[10px] text-slate-400 font-bold uppercase block">Confidence</span>
                <span className="text-2xl font-black text-blue-400">{result.confidence}%</span>
              </div>
            </div>
          </div>

          {/* Model Breakdown */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">MODEL INFERENCE BREAKDOWN</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(result.model_results).map(([key, val]) => (
                <div key={key} className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl space-y-1">
                  <span className="text-xs font-semibold text-slate-400 uppercase">{key.replace('_', ' ')}</span>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">{val.model}</span>
                    <span className="text-xs font-bold text-blue-400">{val.risk_score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Explainable AI (XAI) Risk Factors */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">EXPLAINABLE AI (XAI) ANOMALY FACTORS</h4>
            {result.risk_factors.length === 0 ? (
              <div className="bg-slate-900/50 border border-slate-800 p-4 rounded-xl text-xs text-slate-400">
                No high or medium risk structural anomalies detected in this input.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.risk_factors.map((rf, idx) => (
                  <div key={idx} className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-white">{rf.factor}</span>
                      <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-md ${
                        rf.severity === 'HIGH' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                        rf.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        rf.severity === 'INFO' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {rf.severity}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">{rf.explanation}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Safety Recommendations */}
          <div className="space-y-3 pt-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">SAFETY RECOMMENDATIONS</h4>
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 space-y-2">
              {result.recommendations.map((rec, idx) => (
                <div key={idx} className="text-xs text-slate-300 flex items-center gap-2">
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
