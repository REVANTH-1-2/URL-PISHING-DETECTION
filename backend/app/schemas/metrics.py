from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class MetricsValues(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    specificity: float
    false_positive_rate: float
    false_negative_rate: float

class OverfittingCheck(BaseModel):
    train_f1: float
    val_f1: float
    test_f1: float
    is_overfitting: bool
    warning: Optional[str] = None

class ModelMetricDoc(BaseModel):
    dataset: str  # SMS, EMAIL, URL
    model: str  # DistilBERT, Logistic Regression, SVM, Random Forest, XGBoost
    evaluation_type: str  # TRAIN, VALIDATION, TEST
    metrics: MetricsValues
    test_samples: int
    evaluation_date: datetime = Field(default_factory=datetime.utcnow)
    overfitting: Optional[OverfittingCheck] = None
