@echo off
title CRTV Payslip System - Setup
color 0B

echo.
echo ========================================
echo   CRTV Payslip System - First Time Setup
echo ========================================
echo.
echo This will set up the CRTV Payslip Distribution System
echo on this computer.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Python is not installed!
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing required packages...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  WARNING: Could not create desktop shortcut
    echo You can still run the app by double-clicking start_app.bat
) else (
    echo ✅ Desktop shortcut created
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo The CRTV Payslip System is now installed.
echo.
echo To launch the app:
echo   1. Double-click "CRTV Payslip System" on desktop
echo   2. Or double-click start_app.bat in this folder
echo.
echo IMPORTANT:
echo   - Place your payslip PDF in: input\payslip.pdf
echo   - Place employee Excel in: input\employees.xlsx
echo   - Place stamp image in: input\Stamp.png
echo.
echo For support, check the README files.
echo.
pause
