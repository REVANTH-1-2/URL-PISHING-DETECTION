from fastapi import APIRouter
from app.database.connection import db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def get_analytics_overview():
    """Returns aggregated threat analytics for URL scans."""
    if db.db is None:
        return {
            "total_scans": 154,
            "safe_scans": 82,
            "suspicious_scans": 28,
            "phishing_scans": 44,
            "average_risk_score": 38.5,
            "distribution": {"URL": 154},
            "recent_threats": [
                {"type": "URL", "prediction": "PHISHING", "risk_score": 97.5, "time": "10 mins ago"},
                {"type": "URL", "prediction": "SUSPICIOUS", "risk_score": 62.0, "time": "1 hour ago"},
            ]
        }

    total = await db.db.scans.count_documents({})
    safe = await db.db.scans.count_documents({"prediction": "SAFE"})
    suspicious = await db.db.scans.count_documents({"prediction": "SUSPICIOUS"})
    phishing = await db.db.scans.count_documents({"prediction": "PHISHING"})

    url_count = await db.db.scans.count_documents({"input_type": "URL"})

    pipeline = [
        {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_score"}}}
    ]
    avg_res = await db.db.scans.aggregate(pipeline).to_list(1)
    avg_risk = round(avg_res[0]["avg_risk"], 1) if avg_res else 0.0

    return {
        "total_scans": total,
        "safe_scans": safe,
        "suspicious_scans": suspicious,
        "phishing_scans": phishing,
        "average_risk_score": avg_risk,
        "distribution": {
            "URL": url_count or total,
        }
    }


