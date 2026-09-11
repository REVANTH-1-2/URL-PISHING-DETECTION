import React, { useState, useEffect } from 'react';
import { BarChart3 } from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { getAnalyticsOverview } from '../services/api';
import { AnalyticsOverview } from '../types';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalyticsOverview()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return <div className="p-12 text-center text-slate-400 text-sm">Loading analytics pipeline...</div>;
  }

  const pieData = [
    { name: 'Safe URLs', value: data.safe_scans, color: '#10b981' },
    { name: 'Suspicious URLs', value: data.suspicious_scans, color: '#f59e0b' },
    { name: 'Phishing URLs', value: data.phishing_scans, color: '#ef4444' },
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <div>
        <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-blue-400" /> URL Phishing Threat Intelligence Analytics
        </h2>
        <p className="text-xs text-slate-400 mt-1">Real-time URL threat metrics computed via MongoDB aggregation pipelines.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-semibold uppercase">Total URLs Analyzed</span>
          <div className="text-3xl font-black text-white">{data.total_scans}</div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-rose-400 font-semibold uppercase">Phishing Attacks Blocked</span>
          <div className="text-3xl font-black text-rose-400">{data.phishing_scans}</div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-amber-400 font-semibold uppercase">Suspicious URLs Flagged</span>
          <div className="text-3xl font-black text-amber-400">{data.suspicious_scans}</div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-blue-400 font-semibold uppercase">Average Phishing Risk</span>
          <div className="text-3xl font-black text-blue-400">{data.average_risk_score}%</div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4 max-w-2xl mx-auto">
        <h3 className="text-sm font-bold text-slate-200 text-center">URL Threat Severity Distribution</h3>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={70} outerRadius={95} paddingAngle={5} dataKey="value">
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff' }} />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
