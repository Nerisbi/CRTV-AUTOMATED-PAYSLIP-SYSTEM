@echo off
title CRTV Payslip System
cls

echo ========================================
echo   CRTV Automated Payslip System
echo ========================================
echo.

cd /d "%~dp0"

echo Starting application...
python run_professional_ui.py

if errorlevel 1 (
    echo.
    echo Application encountered an error.
    echo.
    echo Try running: python test_app.py
    echo to diagnose the issue.
    pause
)
