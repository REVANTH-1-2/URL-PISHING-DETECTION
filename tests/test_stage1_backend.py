import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def run_stage1_backend_tests():
    print("==================================================")
    print("STAGE 1 BACKEND VERIFICATION & HEALTH CHECKS")
    print("==================================================")
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test Root Endpoint
        res_root = await client.get("/")
        print(f"[GET /] Status: {res_root.status_code} | Body: {res_root.json()}")
        assert res_root.status_code == 200
        
        # Test Health Endpoint
        res_health = await client.get("/api/health")
        print(f"[GET /api/health] Status: {res_health.status_code} | Body: {res_health.json()}")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"
        
        # Test Auth Endpoint Stub
        res_auth = await client.post("/api/auth/register", json={
            "name": "Test Security Admin",
            "email": "admin@deepshield.ai",
            "password": "SecurePassword2026!"
        })
        print(f"[POST /api/auth/register] Status: {res_auth.status_code} | Body: {res_auth.json()}")
        assert res_auth.status_code in [200, 201]
        

        
        # Test Scan URL Endpoint Stub
        res_scan_url = await client.post("/api/scan/url", json={
            "url": "http://fake-bank-login.com"
        })
        print(f"[POST /api/scan/url] Status: {res_scan_url.status_code} | Body: {res_scan_url.json()}")
        assert res_scan_url.status_code == 200

    print("==================================================")
    print("ALL STAGE 1 BACKEND VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

def test_stage1_backend():
    asyncio.run(run_stage1_backend_tests())

if __name__ == "__main__":
    asyncio.run(run_stage1_backend_tests())

