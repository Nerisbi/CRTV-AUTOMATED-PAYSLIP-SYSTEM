@echo off
title Create CRTV Desktop Shortcut
color 0A
echo.
echo ========================================
echo   CRTV Desktop Shortcut Creator
echo ========================================
echo.
echo This will create a desktop shortcut for
echo the CRTV Payslip System with animation.
echo.

cd /d "%~dp0"

REM Create PowerShell script to create shortcut
echo Creating desktop shortcut...

powershell -ExecutionPolicy Bypass -File create_shortcut.ps1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ SUCCESS: Desktop shortcut created!
    echo.
    echo You can now launch CRTV Payslip System by:
    echo 1. Double-clicking the desktop shortcut
    echo 2. Or running: launch_animated_ui.bat
    echo.
) else (
    echo.
    echo ❌ FAILED: Could not create shortcut automatically
    echo.
    echo You can create it manually:
    echo 1. Right-click on desktop
    echo 2. New > Shortcut
    echo 3. Target: "%cd%\launch_animated_ui.bat"
    echo 4. Name: CRTV Payslip System
    echo.
)

pause
