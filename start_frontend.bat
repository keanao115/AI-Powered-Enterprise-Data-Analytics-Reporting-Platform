@echo off
setlocal
title AI Analytics Platform - Frontend (Next.js)
echo ======================================================================
echo Starting AI Analytics Platform Frontend on http://localhost:3000...
echo ======================================================================
cd /d "%~dp0frontend"
npm run dev
pause
