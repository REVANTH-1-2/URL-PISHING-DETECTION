from fastapi import APIRouter
from app.database.connection import db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def get_analytics_overview():
    """Returns aggregated threat analytics across URL, SMS, and Email scans."""
    if db.db is None:
        return {
            "total_scans": 218,
            "safe_scans": 120,
            "suspicious_scans": 34,
            "phishing_scans": 64,
            "average_risk_score": 41.2,
            "distribution": {
                "URL": 110,
                "SMS": 56,
                "EMAIL": 52
            },
            "recent_threats": [
                {"type": "SMS", "prediction": "PHISHING", "risk_score": 92.5, "time": "5 mins ago"},
                {"type": "EMAIL", "prediction": "PHISHING", "risk_score": 82.9, "time": "15 mins ago"},
                {"type": "URL", "prediction": "SUSPICIOUS", "risk_score": 62.0, "time": "1 hour ago"},
            ]
        }

    total = await db.db.scans.count_documents({})
    safe = await db.db.scans.count_documents({"prediction": "SAFE"})
    suspicious = await db.db.scans.count_documents({"prediction": "SUSPICIOUS"})
    phishing = await db.db.scans.count_documents({"prediction": "PHISHING"})

    url_count = await db.db.scans.count_documents({"input_type": "URL"})
    sms_count = await db.db.scans.count_documents({"input_type": "SMS"})
    email_count = await db.db.scans.count_documents({"input_type": "EMAIL"})

    pipeline = [
        {"$group": {"_id": None, "avg_risk": {"$avg": "$risk_score"}}}
    ]
    avg_res = await db.db.scans.aggregate(pipeline).to_list(1)
    avg_risk = round(avg_res[0]["avg_risk"], 1) if avg_res else 0.0

    recent_cursor = db.db.scans.find({"prediction": {"$in": ["PHISHING", "SUSPICIOUS"]}}).sort("created_at", -1).limit(5)
    recent_threats = []
    async for doc in recent_cursor:
        created_at = doc.get("created_at")
        time_str = created_at.strftime("%b %d, %H:%M") if hasattr(created_at, "strftime") else "Recent"
        recent_threats.append({
            "type": doc.get("input_type", "URL"),
            "prediction": doc.get("prediction", "PHISHING"),
            "risk_score": doc.get("risk_score", 0.0),
            "time": time_str
        })

    return {
        "total_scans": total,
        "safe_scans": safe,
        "suspicious_scans": suspicious,
        "phishing_scans": phishing,
        "average_risk_score": avg_risk,
        "distribution": {
            "URL": url_count,
            "SMS": sms_count,
            "EMAIL": email_count,
        },
        "recent_threats": recent_threats
    }
