@echo off
setlocal
cd /d "%~dp0"
python run.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [Error] Failed to run with python. Please make sure Python is installed.
    pause
)
