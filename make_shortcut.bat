@echo off
title CRTV Shortcut Creator
color 0A

echo Creating CRTV Payslip System desktop shortcut...
powershell -ExecutionPolicy Bypass -File create_simple_shortcut.ps1

echo.
echo ✅ Desktop shortcut created successfully!
echo 📍 Find it on your desktop: "CRTV Payslip System"
echo.
pause
