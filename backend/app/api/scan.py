"""
scan.py  — URL-only phishing scan API router.
"""

import io
import csv
import os
import sys
import joblib
import numpy as np
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status, UploadFile, File

from bson import ObjectId

# Include project root so ml.* imports resolve
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app.database.connection import db
from app.core.config import settings
from app.schemas.scan import URLScanRequest, ScanResponse, RiskFactor, ModelResultItem
from ml.features.extractor import extract_url_features
from ml.explainability.xai_engine import XAIEngine
from ml.training.fusion_engine import FusionEngine

router = APIRouter(prefix="/scan", tags=["Scanning"])

# ── Model artifact cache (loaded once per process) ───────────────────────────
_MODEL_CACHE: dict = {}


def get_url_model_artifacts():

    """
    Lazily loads the URL best_model, scaler, and feature_names from disk.
    Returns (model, scaler, feature_names) or (None, None, None).
    """
    if "url" in _MODEL_CACHE:
        return _MODEL_CACHE["url"]

    # Try configured path, fallback to project root ml/saved_models
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    candidates = [
        os.path.join(settings.MODEL_PATH, "url"),
        os.path.join(project_root, "ml", "saved_models", "url"),
    ]

    save_dir = None
    for cand in candidates:
        if os.path.exists(os.path.join(cand, "best_model.pkl")):
            save_dir = cand
            break

    if not save_dir:
        _MODEL_CACHE["url"] = (None, None, None)
        return None, None, None

    model_path       = os.path.join(save_dir, "best_model.pkl")
    scaler_path      = os.path.join(save_dir, "scaler.pkl")
    feat_names_path  = os.path.join(save_dir, "feature_names.pkl")

    model         = joblib.load(model_path)
    scaler        = joblib.load(scaler_path)       if os.path.exists(scaler_path)     else None
    feature_names = joblib.load(feat_names_path)  if os.path.exists(feat_names_path) else None

    _MODEL_CACHE["url"] = (model, scaler, feature_names)
    return model, scaler, feature_names


# ── URL scan endpoint ────────────────────────────────────────────────────────
@router.post("/url", response_model=ScanResponse, summary="Scan a URL for phishing")
async def scan_url(req: URLScanRequest):
    """
    Analyse a URL using 35 structural/lexical/domain features and
    return a risk score, prediction, XAI risk factors, and recommendations.
    """
    model, scaler, feature_names = get_url_model_artifacts()

    # ── Model prediction ──────────────────────────────────────────────────────
    if model and scaler:
        feats_dict = extract_url_features(req.url)
        feats_arr  = np.array([list(feats_dict.values())])
        X          = scaler.transform(feats_arr)

        if hasattr(model, "predict_proba"):
            url_risk = float(model.predict_proba(X)[0][1]) * 100.0
        else:
            url_risk = float(model.predict(X)[0]) * 100.0

        selected_model_name = type(model).__name__
    else:
        # Rule-based fallback when model is not yet trained
        feats_dict = extract_url_features(req.url)
        rule_score = 0.0

        if feats_dict["is_ip"]              > 0: rule_score += 35
        if feats_dict["has_suspicious_tld"] > 0: rule_score += 25
        if feats_dict["domain_brand_mismatch"] > 0: rule_score += 30
        if feats_dict["brand_in_subdomain"] > 0: rule_score += 25
        if feats_dict["is_shortened"]       > 0: rule_score += 20
        if feats_dict["has_punycode"]       > 0: rule_score += 30
        if feats_dict["has_exec_extension"] > 0: rule_score += 35
        if feats_dict["domain_entropy"]     > 3.8: rule_score += 20
        if feats_dict["dga_vowel_signal"]   > 0: rule_score += 15
        if feats_dict["uses_https"]         == 0: rule_score += 10
        if feats_dict["is_trusted_domain"]  > 0: rule_score -= 40

        url_risk = float(min(max(rule_score, 0), 99))
        selected_model_name = "RuleBasedFallback"

    # ── Trusted Domain Calibration ────────────────────────────────────────────
    # Prevent dataset path-bias false positives for trusted domains (e.g. github.com/foo)
    if feats_dict.get("is_trusted_domain", 0) > 0:
        # Check preliminary high-risk indicators
        has_high_risk = bool(
            feats_dict.get("is_ip", 0) > 0 or
            feats_dict.get("has_punycode", 0) > 0 or
            feats_dict.get("has_suspicious_tld", 0) > 0 or
            feats_dict.get("domain_brand_mismatch", 0) > 0 or
            feats_dict.get("brand_in_subdomain", 0) > 0 or
            feats_dict.get("has_at_symbol", 0) > 0 or
            feats_dict.get("has_exec_extension", 0) > 0
        )
        if not has_high_risk:
            url_risk = min(url_risk, 5.0)

    # ── Fusion (URL-only mode: url_risk == domain_risk) ───────────────────────
    fusion = FusionEngine.combine_predictions(url_risk=url_risk, domain_risk=url_risk)

    # ── XAI analysis ─────────────────────────────────────────────────────────
    xai = XAIEngine.analyze_url(req.url, fusion["risk_score"])

    # ── Build response ────────────────────────────────────────────────────────
    response = ScanResponse(
        input_type="URL",
        prediction=fusion["prediction"],
        risk_score=fusion["risk_score"],
        confidence=fusion["confidence"],
        detected_in=xai["detected_in"],
        model_results={
            "url_model": ModelResultItem(
                model=selected_model_name,
                risk_score=round(url_risk, 1)
            )
        },
        risk_factors=[RiskFactor(**rf) for rf in xai["risk_factors"]],
        recommendations=xai["recommendations"],
        created_at=datetime.utcnow(),
    )

    # ── Persist to MongoDB (non-blocking best-effort) ─────────────────────────
    if db.db is not None:
        try:
            doc = response.model_dump()
            doc["input"] = {
                "url": req.url if settings.STORE_RAW_INPUT else "[REDACTED]"
            }
            res = await db.db.scans.insert_one(doc)
            response.id = str(res.inserted_id)
        except Exception:
            response.id = "scan_url_standalone"
    else:
        response.id = "scan_url_standalone"

    return response# ── Scan history ─────────────────────────────────────────────────────────────

@router.get("/history", response_model=List[ScanResponse], summary="Retrieve past scans")
async def get_scan_history(
    input_type: Optional[str] = Query(None, description="Filter by URL / SMS / EMAIL"),
    prediction: Optional[str] = Query(None, description="Filter by SAFE / SUSPICIOUS / PHISHING"),
    limit: int = Query(20, ge=1, le=100),
):
    if db.db is None:
        return []

    try:
        query: dict = {}
        if input_type:
            query["input_type"] = input_type.upper()
        if prediction:
            query["prediction"] = prediction.upper()

        cursor = db.db.scans.find(query).sort("created_at", -1).limit(limit)
        scans  = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            scans.append(ScanResponse(**doc))
        return scans
    except Exception:
        return []


# ── Delete a scan ─────────────────────────────────────────────────────────────
@router.delete("/{scan_id}", summary="Delete a scan record")
async def delete_scan(scan_id: str):
    if db.db is not None and ObjectId.is_valid(scan_id):
        try:
            res = await db.db.scans.delete_one({"_id": ObjectId(scan_id)})
            if res.deleted_count > 0:
                return {"message": "Scan deleted successfully"}
        except Exception:
            pass
    return {"message": "Scan not found or already deleted"}

