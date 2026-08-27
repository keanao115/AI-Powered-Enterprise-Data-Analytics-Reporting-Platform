@echo off
setlocal
title AI Analytics Platform - Backend API (FastAPI)
echo ======================================================================
echo Starting AI Analytics Platform Backend API on http://localhost:8000...
echo ======================================================================
cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
