@echo off
title Create CRTV Payslip Distribution
color 0E

echo.
echo ========================================
echo   Creating CRTV Payslip Distribution
echo ========================================
echo.

REM Create distribution folder
set dist_name=CRTV_Payslip_System_Distribution
if exist "%dist_name%" rmdir /s /q "%dist_name%"
mkdir "%dist_name%"

echo Copying files to distribution folder...

REM Copy main files
copy "setup.bat" "%dist_name%\" >nul 2>&1
copy "start_app.bat" "%dist_name%\" >nul 2>&1
copy "create_shortcut.ps1" "%dist_name%\" >nul 2>&1
copy "run_ui.py" "%dist_name%\" >nul 2>&1
copy "main.py" "%dist_name%\" >nul 2>&1
copy "logger.py" "%dist_name%\" >nul 2>&1
copy "requirements.txt" "%dist_name%\" >nul 2>&1
copy "Installation Guide.txt" "%dist_name%\" >nul 2>&1
copy "USER_MANUAL.md" "%dist_name%\" >nul 2>&1
copy "VERSION.txt" "%dist_name%\" >nul 2>&1

REM Copy folders
xcopy /E /I /Q "ui" "%dist_name%\ui" >nul 2>&1
xcopy /E /I /Q "services" "%dist_name%\services" >nul 2>&1
xcopy /E /I /Q "input" "%dist_name%\input" >nul 2>&1
xcopy /E /I /Q "output" "%dist_name%\output" >nul 2>&1
xcopy /E /I /Q "logs" "%dist_name%\logs" >nul 2>&1
xcopy /E /I /Q "assets" "%dist_name%\assets" >nul 2>&1

REM Create version info
echo CRTV Payslip Distribution System > "%dist_name%\VERSION.txt"
echo Created: %date% %time% >> "%dist_name%\VERSION.txt"
echo Version: 1.0 >> "%dist_name%\VERSION.txt"

echo Creating ZIP file...
powershell -Command "Compress-Archive -Path '%dist_name%' -DestinationPath 'CRTV_Payslip_System.zip' -Force"

echo.
echo ✅ Distribution package created!
echo.
echo Package: CRTV_Payslip_System.zip
dir "CRTV_Payslip_System.zip" | findstr "CRTV_Payslip_System.zip"
echo.
echo Ready to share with users!
echo.

pause
