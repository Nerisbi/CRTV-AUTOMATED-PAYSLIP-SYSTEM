@echo off
title CRTV Professional Payslip System
color 0A
echo.
echo ========================================
echo   CRTV Professional Payslip System
echo ========================================
echo.
echo Starting Professional UI for Directors...
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

REM Start the professional UI
echo Launching CRTV Professional Interface...
python run_professional_ui.py

REM Keep window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application closed with error code: %ERRORLEVEL%
    pause
)
