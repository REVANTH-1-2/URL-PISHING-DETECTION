import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def run_stages_2_6_tests():
    print("==================================================")
    print("TESTING STAGES 2-6: AUTH, SCANS, HISTORY, ANALYTICS & METRICS")
    print("==================================================")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. User Registration
        res_reg = await client.post("/api/auth/register", json={
            "name": "Security Analyst",
            "email": "analyst@deepshield.ai",
            "password": "SecurePassword2026!"
        })
        print(f"1. Register: Status {res_reg.status_code}")
        assert res_reg.status_code in [200, 201]
        token = res_reg.json()["access_token"]
        
        # 2. Get Me
        res_me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        print(f"2. Auth Me: Status {res_me.status_code} | Name: {res_me.json()['name']}")
        assert res_me.status_code == 200

        # 3. Scan URL
        res_url = await client.post("/api/scan/url", json={
            "url": "http://192.168.1.1/banking/login.php?verify=1"
        })
        print(f"3. URL Scan: Status {res_url.status_code} | Prediction: {res_url.json()['prediction']}")
        assert res_url.status_code == 200

        # 4. Analytics Overview
        res_analytics = await client.get("/api/analytics/overview")
        print(f"4. Analytics Overview: Status {res_analytics.status_code} | Total Scans: {res_analytics.json()['total_scans']}")
        assert res_analytics.status_code == 200

        # 5. Model Performance Metrics
        res_models = await client.get("/api/models")
        print(f"5. Model Performance Metrics: Status {res_models.status_code} | Datasets: {list(res_models.json().keys())}")
        assert res_models.status_code == 200

    print("==================================================")
    print("STAGES 2-6 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

def test_stages2_6():
    asyncio.run(run_stages_2_6_tests())

if __name__ == "__main__":
    asyncio.run(run_stages_2_6_tests())
