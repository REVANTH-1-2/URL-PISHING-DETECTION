import { ScanResponse, AnalyticsOverview, ModelMetricDoc, AuthToken, User } from '../types';

const getApiBase = () => {
  const metaEnv = (import.meta as any).env;
  if (metaEnv && metaEnv.VITE_API_URL) {
    const base = metaEnv.VITE_API_URL.replace(/\/+$/, '');
    return base.endsWith('/api') ? base : `${base}/api`;
  }
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host === 'localhost' || host === '127.0.0.1') {
      return 'http://127.0.0.1:8000/api';
    }
    if (host.includes('onrender.com')) {
      const backendHost = host.replace('frontend', 'backend');
      return `https://${backendHost}/api`;
    }
  }
  return '/api';
};

const API_BASE = getApiBase();

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function scanURL(url: string): Promise<ScanResponse> {
  const res = await fetch(`${API_BASE}/scan/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  if (!res.ok) throw new Error('URL analysis failed');
  return res.json();
}







export async function getScanHistory(inputType?: string, prediction?: string): Promise<ScanResponse[]> {
  const params = new URLSearchParams();
  if (inputType) params.append('input_type', inputType);
  if (prediction) params.append('prediction', prediction);
  
  const res = await fetch(`${API_BASE}/scan/history?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch scan history');
  return res.json();
}

export async function deleteScan(scanId: string): Promise<void> {
  await fetch(`${API_BASE}/scan/${scanId}`, { method: 'DELETE' });
}

export async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  const res = await fetch(`${API_BASE}/analytics/overview`);
  if (!res.ok) throw new Error('Failed to fetch analytics overview');
  return res.json();
}

export async function getModelMetrics(): Promise<Record<string, ModelMetricDoc[]>> {
  const res = await fetch(`${API_BASE}/models`);
  if (!res.ok) throw new Error('Failed to fetch model performance metrics');
  return res.json();
}

export async function loginUser(email: string, password: string): Promise<AuthToken> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) {
    let detail = 'Login failed';
    try {
      const err = await res.json();
      detail = err.detail || err.message || detail;
    } catch {
      detail = `Server error (${res.status})`;
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function registerUser(name: string, email: string, password: string): Promise<AuthToken> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password })
  });
  if (!res.ok) {
    let detail = 'Registration failed';
    try {
      const err = await res.json();
      detail = err.detail || err.message || detail;
    } catch {
      detail = `Server error (${res.status})`;
    }
    throw new Error(detail);
  }
  return res.json();
}
