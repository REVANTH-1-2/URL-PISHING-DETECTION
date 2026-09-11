import React, { useState, useEffect } from 'react';
import { Cpu, AlertTriangle, CheckCircle } from 'lucide-react';
import { getModelMetrics } from '../services/api';
import { ModelMetricDoc } from '../types';

export const ModelPerformancePage: React.FC = () => {
  const [metricsData, setMetricsData] = useState<Record<string, ModelMetricDoc[]> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getModelMetrics()
      .then(setMetricsData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !metricsData) {
    return <div className="p-12 text-center text-slate-400 text-sm">Loading model performance metrics...</div>;
  }

  const currentModels = metricsData['url'] || [];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <div>
        <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
          <Cpu className="w-6 h-6 text-purple-400" /> URL Phishing Model Evaluation & Performance
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Final test set metrics evaluated on locked 35-feature models trained on the PhiUSIIL Phishing URL Dataset (235,795 URLs).
        </p>
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
                <th className="p-3">Features</th>
                <th className="p-3">Train F1</th>
                <th className="p-3">Validation F1</th>
                <th className="p-3">Test F1</th>
                <th className="p-3">Overfitting Warning</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {currentModels.map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40">
                  <td className="p-3 font-bold text-white">{item.model}</td>
                  <td className="p-3 font-mono text-purple-400 font-bold">35 Features</td>
                  <td className="p-3 font-mono">{item.overfitting?.train_f1}</td>
                  <td className="p-3 font-mono text-blue-400">{item.overfitting?.val_f1}</td>
                  <td className="p-3 font-mono text-emerald-400">{item.overfitting?.test_f1}</td>
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
        <h3 className="text-sm font-bold text-slate-200">Unseen Test Set Evaluation Metrics (35,370 Test URLs)</h3>
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
