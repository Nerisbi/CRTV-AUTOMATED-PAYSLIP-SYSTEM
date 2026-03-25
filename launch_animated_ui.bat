@echo off
title CRTV Payslip System - Animated Launch
color 0A
echo.
echo ========================================
echo   CRTV Payslip System - Animated UI
echo ========================================
echo.
echo Starting with professional animation...
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the animated UI
echo Launching CRTV System with Animation...
python run_animated_ui.py

REM Keep window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application closed with error code: %ERRORLEVEL%
    pause
)
