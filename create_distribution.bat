@echo off
title CRTV Payslip System - Create Distribution Package
color 0E

echo.
echo ========================================
echo   Creating Distribution Package
echo ========================================
echo.

REM Get current date for version
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /format:list') do set datetime=%%I
set version_date=%datetime:~0,8%

REM Create distribution folder name
set dist_name=CRTV_Payslip_System_v%version_date%

echo Creating distribution package: %dist_name%
echo.

REM Create distribution folder
if exist "%dist_name%" rmdir /s /q "%dist_name%"
mkdir "%dist_name%"

REM Copy essential files (excluding venv and temporary files)
echo Copying application files...
xcopy /E /I /Q /EXCLUDE:exclude_files.txt . "%dist_name%"

REM Create version info file
echo Creating version information...
echo CRTV Payslip Distribution System > "%dist_name%\VERSION.txt"
echo Created: %date% %time% >> "%dist_name%\VERSION.txt"
echo Version: 1.0 >> "%dist_name%\VERSION.txt"

REM Create the distribution ZIP
echo Creating ZIP file...
powershell -Command "Compress-Archive -Path '%dist_name%' -DestinationPath '%dist_name%.zip' -Force"

echo.
echo ✅ Distribution package created!
echo.
echo Package: %dist_name%.zip
echo Size: 
dir "%dist_name%.zip" | findstr "%dist_name%.zip"
echo.
echo You can now share this ZIP file with other users.
echo.
echo Users will need to:
echo 1. Extract the ZIP file
echo 2. Run setup.bat
echo 3. Follow the installation instructions
echo.

pause
