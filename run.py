#!/usr/bin/env python
"""
AI Job & Internship Automation Platform - One-Click Launcher
Usage:
  python run.py
"""
import sys
import subprocess
import os

def check_dependencies():
    required_packages = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "jose", "passlib", "pypdf", "docx"]
    missing = []
    for pkg in required_packages:
        try:
            if pkg == "jose":
                __import__("jose")
            elif pkg == "docx":
                __import__("docx")
            else:
                __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"[!] Installing required dependencies: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    print("=" * 70)
    print("   AI Job & Internship Automation Platform (CareerAgent AI)")
    print("=" * 70)
    print("[*] Verifying environment & dependencies...")
    check_dependencies()

    print("\n[*] Starting FastAPI Backend & Single-Page Application...")
    print("    - Web App URL:      http://127.0.0.1:8000")
    print("    - Interactive API:  http://127.0.0.1:8000/docs")
    print("    - Demo Candidate:   student@example.com (pass: password123)\n")
    print("Press Ctrl+C to stop the server.\n")

    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
