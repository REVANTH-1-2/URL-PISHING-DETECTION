

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class URLScanRequest(BaseModel):
    url: str = Field(..., min_length=3, description="Target URL to analyse for phishing")



class RiskFactor(BaseModel):
    factor: str
    severity: str  # HIGH, MEDIUM, LOW, INFO
    explanation: str


class ModelResultItem(BaseModel):
    model: str
    risk_score: float


class ScanResponse(BaseModel):
    id: Optional[str] = None
    input_type: str       # URL
    prediction: str       # SAFE, SUSPICIOUS, PHISHING
    risk_score: float     # 0–100
    confidence: float     # 0–100
    detected_in: List[str]
    model_results: Dict[str, ModelResultItem]
    risk_factors: List[RiskFactor]
    recommendations: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
