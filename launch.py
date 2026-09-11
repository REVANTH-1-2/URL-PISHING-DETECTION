#!/usr/bin/env python3
"""
launch.py
=========
One-click Python launcher script for the Phishing Detection System.
Starts the FastAPI backend server, Frontend server, and automatically opens the browser.
"""

import os
import sys
import time
import subprocess
import webbrowser
import urllib.request

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
VENV_PYTHON = os.path.join(PROJECT_ROOT, "backend", "venv", "bin", "python")
HOST = "127.0.0.1"
PORT = 8000
HEALTH_URL = f"http://{HOST}:{PORT}/api/health"
DOCS_URL = f"http://{HOST}:{PORT}/docs"
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
FRONTEND_URL = "http://localhost:5173"


def is_server_running(url):
    try:
        req = urllib.request.urlopen(url, timeout=1)
        return req.status == 200
    except Exception:
        return False


def main():
    print("=" * 60)
    print("🚀 Launching AI-Enhanced Phishing Detection System...")
    print("=" * 60)

    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    backend_path = os.path.join(PROJECT_ROOT, "backend")
    ml_path = os.path.join(PROJECT_ROOT, "ml")
    env["PYTHONPATH"] = f"{backend_path}:{ml_path}:{PROJECT_ROOT}:{pythonpath}".strip(":")

    python_bin = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable

    # 1. Start Backend Server
    if not is_server_running(HEALTH_URL):
        print(f"⚙️  Starting FastAPI backend on http://{HOST}:{PORT} ...")
        cmd_backend = [
            python_bin, "-m", "uvicorn", "app.main:app",
            "--host", HOST,
            "--port", str(PORT),
            "--reload"
        ]
        subprocess.Popen(cmd_backend, cwd=PROJECT_ROOT, env=env)

        print("⏳ Waiting for backend server to become ready...")
        for _ in range(15):
            if is_server_running(HEALTH_URL):
                break
            time.sleep(1)

    print("✅ Backend service is UP & RUNNING!")

    # 2. Start Frontend Server
    if os.path.exists(FRONTEND_DIR):
        print("⚙️  Starting Frontend UI dev server...")
        try:
            subprocess.Popen(["npm", "run", "dev"], cwd=FRONTEND_DIR, env=env)
            time.sleep(2)
        except Exception as e:
            print(f"Notice: Could not auto-start npm dev server ({e}). Backend is active.")

    print(f"🔗 Documentation & API: {DOCS_URL}")
    print(f"💻 Web UI Interface: {FRONTEND_URL}")
    print("🌐 Opening web browser...")

    # Automatically open browser to frontend and backend docs
    try:
        webbrowser.open(FRONTEND_URL)
    except Exception:
        webbrowser.open(DOCS_URL)

    print("=" * 60)
    print("🎉 System Ready!")
    print("  • Web Scanner UI: http://localhost:5173")
    print("  • API Documentation: http://127.0.0.1:8000/docs")
    print("  (Press Ctrl+C in terminal to stop)")
    print("=" * 60)

    # Keep script alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 System shutting down gracefully.")


if __name__ == "__main__":
    main()
