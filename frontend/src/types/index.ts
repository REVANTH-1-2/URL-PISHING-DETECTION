export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  created_at?: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RiskFactor {
  factor: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  explanation: string;
}

export interface ModelResultItem {
  model: string;
  risk_score: number;
}

export interface ScanResponse {
  id?: string;
  input_type: 'URL';
  prediction: 'SAFE' | 'SUSPICIOUS' | 'PHISHING';
  risk_score: number;
  confidence: number;
  detected_in: string[];
  model_results: Record<string, ModelResultItem>;
  risk_factors: RiskFactor[];
  recommendations: string[];
  created_at: string;
}

export interface AnalyticsOverview {
  total_scans: number;
  safe_scans: number;
  suspicious_scans: number;
  phishing_scans: number;
  average_risk_score: number;
  distribution: {
    URL: number;
  };


  recent_threats?: Array<{
    type: string;
    prediction: string;
    risk_score: number;
    time: string;
  }>;
}

export interface ModelMetricsValues {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  specificity: number;
  false_positive_rate: number;
  false_negative_rate: number;
}

export interface OverfittingCheck {
  train_f1: number;
  val_f1: number;
  test_f1: number;
  is_overfitting: boolean;
  warning?: string;
}

export interface ModelMetricDoc {
  model: string;
  evaluation_type: string;
  metrics: ModelMetricsValues;
  overfitting: OverfittingCheck;
}
