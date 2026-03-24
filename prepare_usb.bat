@echo off
title Prepare USB Distribution
color 0B

echo.
echo ========================================
echo   Preparing USB Distribution Package
echo ========================================
echo.

REM Check if distribution package exists
if not exist "CRTV_Payslip_System.zip" (
    echo ❌ Distribution package not found!
    echo Please run simple_distribution.bat first.
    pause
    exit /b 1
)
echo.

REM Ask for USB drive letter
set /p usb_drive="Enter USB drive letter (e.g., E): "

if not exist "%usb_drive%:\" (
    echo ❌ Drive %usb_drive%: not found!
    pause
    exit /b 1
)

echo.
echo Copying files to USB drive %usb_drive%: ...
echo.

REM Create folder structure on USB
mkdir "%usb_drive%:\CRTV_Payslip_System" 2>nul
mkdir "%usb_drive%:\Python Installer" 2>nul

REM Copy distribution package
echo Copying application package...
copy "CRTV_Payslip_System.zip" "%usb_drive%:\CRTV_Payslip_System\"

REM Copy installation guide
echo Copying installation guide...
copy "Installation Guide.txt" "%usb_drive%:\CRTV_Payslip_System\"

REM Check if Python installer exists
if exist "python-3.11.8-amd64.exe" (
    echo Copying Python installer...
    copy "python-3.11.8-amd64.exe" "%usb_drive%:\Python Installer\"
) else (
    echo ⚠️  Python installer not found. Please download from python.org
    echo    and copy to USB drive manually.
)

echo.
echo ✅ USB preparation complete!
echo.
echo USB Drive Contents:
dir "%usb_drive%:\CRTV_Payslip_System"
echo.
echo The USB is ready for distribution to users.
echo.
pause
