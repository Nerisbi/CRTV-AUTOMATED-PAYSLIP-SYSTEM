@echo off 
title CRTV Payslip System - Setup 
color 0A 
echo. 
echo ======================================== 
echo   CRTV Payslip System - User Setup 
echo ======================================== 
echo. 
echo Setting up CRTV Payslip System... 
echo. 
 
REM Check if Python is installed 
python --version >nul 2>&1 
if %ERRORLEVEL% NEQ 0 ( 
    echo ERROR: Python is not installed! 
    echo Please install Python 3.8 or higher from: 
    echo https://www.python.org/downloads/ 
    echo. 
    pause 
    exit /b 1 
) 
 
echo Installing required packages... 
pip install pandas openpyxl PyPDF2 reportlab pillow 
if %ERRORLEVEL% NEQ 0 ( 
    echo ERROR: Failed to install dependencies 
    pause 
    exit /b 1 
) 
 
echo Creating desktop shortcut... 
powershell -ExecutionPolicy Bypass -File create_simple_shortcut.ps1 
 
echo ======================================== 
echo   Setup Complete! 
echo ======================================== 
echo. 
echo CRTV Payslip System is now installed! 
echo. 
echo To launch the app: 
echo   1. Double-click desktop shortcut 
echo   2. Or run launch_animated_ui.bat 
echo. 
echo IMPORTANT: 
echo   - Place payslip PDF in: input\payslips.pdf 
echo   - Place employee Excel in: input\employees.xlsx 
echo   - Place stamp image in: input\Stamp.png 
echo. 
pause 
