import React from 'react';
import { Shield, Cpu, Database, FileCheck2, Lock } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="glass-card p-8 rounded-2xl border border-slate-800 space-y-4">
        <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
          <Shield className="w-6 h-6 text-blue-400" /> About DeepShield AI Architecture
        </h2>
        <p className="text-slate-300 text-sm leading-relaxed">
          AI-Enhanced URL Phishing Detection System using 35-Feature Machine Learning Ensembles and Explainable AI (XAI).
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-2">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-purple-400" /> 35-Feature ML Architecture
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Combines Random Forest, XGBoost, and Voting Ensembles trained on 235,795 URLs using structural, domain entropy, punycode, and brand impersonation features.
          </p>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-2">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <FileCheck2 className="w-4 h-4 text-emerald-400" /> Explainable AI (XAI)
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Extracts exact URL risk factors, highlights DGA entropy signals, brand impersonation, and IP-based URLs to explain "Why?" a link was flagged.
          </p>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-2">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Lock className="w-4 h-4 text-amber-400" /> Data Leakage Prevention
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            StandardScaler pipelines and feature extraction are fitted strictly on the Training split to guarantee unseen test evaluation integrity.
          </p>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-2">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-400" /> MongoDB Audit Logging
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Powered by Motor async driver with Pydantic schema validation. Respects <code className="text-blue-300">STORE_RAW_INPUT=false</code> for user privacy.
          </p>
        </div>
      </div>
    </div>
  );
};
