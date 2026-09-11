import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def run_locked_model_integration_test():
    print("==================================================")
    print("TESTING FASTAPI INTEGRATION WITH LOCKED ML MODELS")
    print("==================================================")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test URL Scan endpoint with real model inference
        res_url = await client.post("/api/scan/url", json={
            "url": "http://192.168.1.1/online-banking/login.php?id=9231"
        })
        print(f"\nURL Scan Response: Status {res_url.status_code}")
        data_url = res_url.json()
        print(f"   Prediction: {data_url['prediction']} | Risk Score: {data_url['risk_score']}%")
        assert res_url.status_code == 200
        assert data_url["prediction"] in ["SUSPICIOUS", "PHISHING"]

    print("\n==================================================")
    print("FASTAPI LOCKED MODEL INTEGRATION TEST PASSED SUCCESSFULLY!")
    print("==================================================")

def test_locked_model_integration():
    asyncio.run(run_locked_model_integration_test())

if __name__ == "__main__":
    asyncio.run(run_locked_model_integration_test())
