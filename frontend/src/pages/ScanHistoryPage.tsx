import React, { useState, useEffect } from 'react';
import { History, Trash2 } from 'lucide-react';
import { getScanHistory, deleteScan } from '../services/api';
import { ScanResponse } from '../types';

export const ScanHistoryPage: React.FC = () => {
  const [history, setHistory] = useState<ScanResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterPrediction, setFilterPrediction] = useState<string>('ALL');

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await getScanHistory(
        'URL',
        filterPrediction !== 'ALL' ? filterPrediction : undefined
      );
      setHistory(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [filterPrediction]);

  const handleDelete = async (id?: string) => {
    if (!id) return;
    await deleteScan(id);
    setHistory(history.filter((item) => item.id !== id));
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <History className="w-6 h-6 text-blue-400" /> URL Scan Audit History
          </h2>
          <p className="text-xs text-slate-400 mt-1">Review past URL scan results stored in MongoDB database.</p>
        </div>

        {/* Filter controls */}
        <div className="flex items-center gap-3">
          <select
            value={filterPrediction}
            onChange={(e) => setFilterPrediction(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs font-semibold text-slate-300 focus:outline-none"
          >
            <option value="ALL">All Classifications</option>
            <option value="PHISHING">Phishing</option>
            <option value="SUSPICIOUS">Suspicious</option>
            <option value="SAFE">Safe</option>
          </select>
        </div>
      </div>

      {/* History table */}
      <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading URL scan history...</div>
        ) : history.length === 0 ? (
          <div className="p-12 text-center space-y-2">
            <History className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-slate-400 text-sm">No URL scan records found in database.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-4">Type</th>
                  <th className="p-4">Prediction</th>
                  <th className="p-4">Risk Score</th>
                  <th className="p-4">Confidence</th>
                  <th className="p-4">Detected In</th>
                  <th className="p-4">Date</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {history.map((scan) => (
                  <tr key={scan.id} className="hover:bg-slate-900/40 transition">
                    <td className="p-4 font-bold text-white">{scan.input_type}</td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-md text-[10px] uppercase font-bold ${
                        scan.prediction === 'PHISHING' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                        scan.prediction === 'SUSPICIOUS' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}>
                        {scan.prediction}
                      </span>
                    </td>
                    <td className="p-4 font-mono font-bold text-white">{scan.risk_score}%</td>
                    <td className="p-4 font-mono text-blue-400">{scan.confidence}%</td>
                    <td className="p-4">
                      <div className="flex flex-wrap gap-1">
                        {scan.detected_in.map((d) => (
                          <span key={d} className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] font-mono text-slate-400">
                            {d}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="p-4 text-slate-400">{new Date(scan.created_at).toLocaleString()}</td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => handleDelete(scan.id)}
                        className="p-1.5 bg-slate-900 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 rounded-lg transition"
                        title="Delete Scan Record"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
