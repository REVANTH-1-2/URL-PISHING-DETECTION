import React, { useState, useEffect } from 'react';
import { Cpu, AlertTriangle, CheckCircle, Globe, MessageSquare, Mail } from 'lucide-react';
import { getModelMetrics } from '../services/api';
import { ModelMetricDoc } from '../types';

export const ModelPerformancePage: React.FC = () => {
  const [metricsData, setMetricsData] = useState<Record<string, ModelMetricDoc[]> | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'url' | 'sms' | 'email'>('url');

  useEffect(() => {
    getModelMetrics()
      .then(setMetricsData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !metricsData) {
    return <div className="p-12 text-center text-slate-400 text-sm">Loading model performance metrics...</div>;
  }

  const currentModels = metricsData[activeTab] || [];

  const tabConfig = {
    url: {
      title: 'URL Phishing Detection Models',
      subtitle: 'Evaluated on 35 lexical, structural, and domain features against real phishing URLs.',
      featureDesc: '35 Lexical / Structural Features',
      icon: Globe,
    },
    sms: {
      title: 'SMS Smishing Detection Models',
      subtitle: 'Evaluated on TF-IDF n-grams + 12 handcrafted auxiliary indicators on authentic SMS datasets.',
      featureDesc: 'TF-IDF + 12 Auxiliary Features',
      icon: MessageSquare,
    },
    email: {
      title: 'Email Phishing Detection Models',
      subtitle: 'Evaluated across sender, subject, and body components against real phishing and business emails.',
      featureDesc: 'Multi-component TF-IDF + Indicators',
      icon: Mail,
    },
  };

  const currentConfig = tabConfig[activeTab];
  const Icon = currentConfig.icon;

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Cpu className="w-6 h-6 text-purple-400" /> Multi-Modal Model Evaluation & Performance
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Comparative performance, overfitting analysis, and test set evaluations across URL, SMS, and Email phishing models.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-xl">
          <button
            onClick={() => setActiveTab('url')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
              activeTab === 'url'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Globe className="w-3.5 h-3.5" /> URL Models
          </button>
          <button
            onClick={() => setActiveTab('sms')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
              activeTab === 'sms'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" /> SMS Models
          </button>
          <button
            onClick={() => setActiveTab('email')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
              activeTab === 'email'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            <Mail className="w-3.5 h-3.5" /> Email Models
          </button>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/80 flex items-center gap-3">
        <Icon className="w-5 h-5 text-purple-400 flex-shrink-0" />
        <div>
          <h4 className="text-sm font-bold text-white">{currentConfig.title}</h4>
          <p className="text-xs text-slate-400">{currentConfig.subtitle}</p>
        </div>
      </div>

      {/* Overfitting Analysis Table */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-400" /> Overfitting Analysis Check (Train F1 vs Val F1 vs Test F1)
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3">Model</th>
                <th className="p-3">Feature Space</th>
                <th className="p-3">Train F1</th>
                <th className="p-3">Validation F1</th>
                <th className="p-3">Test F1</th>
                <th className="p-3">Generalization Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {currentModels.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40">
                  <td className="p-3 font-bold text-white flex items-center gap-2">
                    {item.model}
                  </td>
                  <td className="p-3 font-mono text-purple-400 font-bold">
                    {currentConfig.featureDesc}
                  </td>
                  <td className="p-3 font-mono">{item.overfitting?.train_f1 != null ? (item.overfitting.train_f1 * 100).toFixed(1) + '%' : '-'}</td>
                  <td className="p-3 font-mono text-blue-400">{item.overfitting?.val_f1 != null ? (item.overfitting.val_f1 * 100).toFixed(1) + '%' : '-'}</td>
                  <td className="p-3 font-mono text-emerald-400">{item.overfitting?.test_f1 != null ? (item.overfitting.test_f1 * 100).toFixed(1) + '%' : '-'}</td>
                  <td className="p-3">
                    {item.overfitting?.is_overfitting ? (
                      <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center gap-1 w-max">
                        <AlertTriangle className="w-3 h-3" /> {item.overfitting.warning || 'Potential Overfitting'}
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1 w-max">
                        <CheckCircle className="w-3 h-3" /> Well Generalized
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Main Model Metrics Comparison Table */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-slate-200">Unseen Held-Out Test Set Metrics</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-slate-400 uppercase font-semibold border-b border-slate-800">
              <tr>
                <th className="p-3">Model</th>
                <th className="p-3">Accuracy</th>
                <th className="p-3">Precision</th>
                <th className="p-3 text-emerald-400">Recall</th>
                <th className="p-3 text-blue-400">F1-Score</th>
                <th className="p-3">ROC-AUC</th>
                <th className="p-3">Specificity</th>
                <th className="p-3 text-rose-400">False Neg Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {currentModels.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40">
                  <td className="p-3 font-bold text-white font-sans">{item.model}</td>
                  <td className="p-3">{(item.metrics.accuracy * 100).toFixed(1)}%</td>
                  <td className="p-3">{(item.metrics.precision * 100).toFixed(1)}%</td>
                  <td className="p-3 text-emerald-400 font-bold">{(item.metrics.recall * 100).toFixed(1)}%</td>
                  <td className="p-3 text-blue-400 font-bold">{(item.metrics.f1_score * 100).toFixed(1)}%</td>
                  <td className="p-3">{(item.metrics.roc_auc * 100).toFixed(1)}%</td>
                  <td className="p-3">{(item.metrics.specificity * 100).toFixed(1)}%</td>
                  <td className="p-3 text-rose-400 font-bold">{(item.metrics.false_negative_rate * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
