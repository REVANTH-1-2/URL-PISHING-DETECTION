import React, { useState, useEffect } from 'react';
import { BarChart3, ShieldAlert, MessageSquare, Mail, Globe, Zap } from 'lucide-react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
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

  const threatPieData = [
    { name: 'Safe Inputs', value: data.safe_scans, color: '#10b981' },
    { name: 'Suspicious Inputs', value: data.suspicious_scans, color: '#f59e0b' },
    { name: 'Phishing Attacks', value: data.phishing_scans, color: '#ef4444' },
  ];

  const modalityDistributionData = [
    { name: 'URL Scans', count: data.distribution?.URL || 0, fill: '#3b82f6' },
    { name: 'SMS Scans', count: data.distribution?.SMS || 0, fill: '#a855f7' },
    { name: 'Email Scans', count: data.distribution?.EMAIL || 0, fill: '#06b6d4' },
  ];

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-400" /> Multi-Modal Threat Intelligence Analytics
          </h2>
          <p className="text-xs text-slate-400 mt-1">Real-time cross-channel metrics across URL, SMS (Smishing), and Email threat vectors.</p>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-slate-400 font-semibold uppercase">Total Scans Conducted</span>
          <div className="text-3xl font-black text-white">{data.total_scans}</div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-rose-400 font-semibold uppercase flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4" /> Phishing Attacks Blocked
          </span>
          <div className="text-3xl font-black text-rose-400">{data.phishing_scans}</div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-amber-400 font-semibold uppercase">Suspicious Inputs Flagged</span>
          <div className="text-3xl font-black text-amber-400">{data.suspicious_scans}</div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-1">
          <span className="text-xs text-blue-400 font-semibold uppercase">Average Phishing Risk</span>
          <div className="text-3xl font-black text-blue-400">{data.average_risk_score}%</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Severity Pie Chart */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-slate-200 text-center flex items-center justify-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" /> Overall Threat Severity Breakdown
          </h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={threatPieData} cx="50%" cy="50%" innerRadius={65} outerRadius={90} paddingAngle={5} dataKey="value">
                  {threatPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff' }} />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Modality Distribution Bar Chart */}
        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-slate-200 text-center flex items-center justify-center gap-2">
            <BarChart3 className="w-4 h-4 text-blue-400" /> Scan Volume by Modality (URL vs SMS vs Email)
          </h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={modalityDistributionData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff' }} />
                <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                  {modalityDistributionData.map((entry, index) => (
                    <Cell key={`bar-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Modality Breakdown Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center gap-4">
          <div className="p-3 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-xl">
            <Globe className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-bold text-slate-400 uppercase">URL Scans</span>
            <div className="text-2xl font-black text-white">{data.distribution?.URL || 0}</div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center gap-4">
          <div className="p-3 bg-purple-500/20 text-purple-400 border border-purple-500/30 rounded-xl">
            <MessageSquare className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-bold text-slate-400 uppercase">SMS Smishing Scans</span>
            <div className="text-2xl font-black text-white">{data.distribution?.SMS || 0}</div>
          </div>
        </div>

        <div className="glass-card p-5 rounded-2xl border border-slate-800 flex items-center gap-4">
          <div className="p-3 bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 rounded-xl">
            <Mail className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-bold text-slate-400 uppercase">Email Phishing Scans</span>
            <div className="text-2xl font-black text-white">{data.distribution?.EMAIL || 0}</div>
          </div>
        </div>
      </div>
    </div>
  );
};
