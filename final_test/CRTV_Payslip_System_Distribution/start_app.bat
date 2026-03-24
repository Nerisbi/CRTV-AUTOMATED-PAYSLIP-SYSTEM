@echo off
title CRTV Payslip Distribution System
color 0A
echo.
echo ========================================
echo   CRTV Automated Payslip Distribution
echo ========================================
echo.
echo Starting application...
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

REM Check if required files exist
if not exist "run_ui.py" (
    echo Error: Application files not found!
    pause
    exit /b 1
)

REM Start the application
echo Launching CRTV Payslip System...
python run_ui.py

REM Keep window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application closed with error code: %ERRORLEVEL%
    pause
)
