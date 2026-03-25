@echo off
title CRTV Distribution Package Creator
color 0A
echo.
echo ========================================
echo   CRTV Distribution Package Creator
echo ========================================
echo.
echo This will create a portable package for
echo sharing with other users.
echo.

cd /d "%~dp0"

REM Create distribution directory
set DIST_DIR=CRTV_Payslip_System_Portable
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
mkdir "%DIST_DIR%"

echo Creating distribution package...

REM Copy essential files
echo [1/8] Copying main application files...
copy "main.py" "%DIST_DIR%\" >nul
copy "run_animated_ui.py" "%DIST_DIR%\" >nul
copy "run_professional_ui.py" "%DIST_DIR%\" >nul
copy "launch_animated_ui.bat" "%DIST_DIR%\" >nul
copy "make_shortcut.bat" "%DIST_DIR%\" >nul

REM Copy UI files
echo [2/8] Copying UI files...
xcopy "ui" "%DIST_DIR%\ui\" /E /I /Q >nul

REM Copy input folder structure
echo [3/8] Creating input folders...
mkdir "%DIST_DIR%\input" >nul
mkdir "%DIST_DIR%\output" >nul
mkdir "%DIST_DIR%\output\sent_payslips" >nul

REM Copy sample files if they exist
echo [4/8] Copying sample files...
if exist "input\payslips.pdf" copy "input\payslips.pdf" "%DIST_DIR%\input\" >nul
if exist "input\employees.xlsx" copy "input\employees.xlsx" "%DIST_DIR%\input\" >nul
if exist "input\Stamp.png" copy "input\Stamp.png" "%DIST_DIR%\input\" >nul

REM Copy requirements
echo [5/8] Copying requirements...
copy "requirements.txt" "%DIST_DIR%\" >nul

REM Copy documentation
echo [6/8] Copying documentation...
copy "README-USER.txt" "%DIST_DIR%\" >nul
copy "Installation Guide.txt" "%DIST_DIR%\" >nul

REM Create setup script for users
echo [7/8] Creating user setup script...
echo @echo off > "%DIST_DIR%\setup_for_users.bat"
echo title CRTV Payslip System - Setup >> "%DIST_DIR%\setup_for_users.bat"
echo color 0A >> "%DIST_DIR%\setup_for_users.bat"
echo echo. >> "%DIST_DIR%\setup_for_users.bat"
echo echo ======================================== >> "%DIST_DIR%\setup_for_users.bat"
echo echo   CRTV Payslip System - User Setup >> "%DIST_DIR%\setup_for_users.bat"
echo echo ======================================== >> "%DIST_DIR%\setup_for_users.bat"
echo echo. >> "%DIST_DIR%\setup_for_users.bat"
echo echo Setting up CRTV Payslip System... >> "%DIST_DIR%\setup_for_users.bat"
echo echo. >> "%DIST_DIR%\setup_for_users.bat"
echo. >> "%DIST_DIR%\setup_for_users.bat"
echo REM Check if Python is installed >> "%DIST_DIR%\setup_for_users.bat"
echo python --version ^>nul 2^>^&1 >> "%DIST_DIR%\setup_for_users.bat"
echo if %%ERRORLEVEL%% NEQ 0 ( >> "%DIST_DIR%\setup_for_users.bat"
echo     echo ERROR: Python is not installed! >> "%DIST_DIR%\setup_for_users.bat"
echo     echo Please install Python 3.8 or higher from: >> "%DIST_DIR%\setup_for_users.bat"
echo     echo https://www.python.org/downloads/ >> "%DIST_DIR%\setup_for_users.bat"
echo     echo. >> "%DIST_DIR%\setup_for_users.bat"
echo     pause >> "%DIST_DIR%\setup_for_users.bat"
echo     exit /b 1 >> "%DIST_DIR%\setup_for_users.bat"
echo ^) >> "%DIST_DIR%\setup_for_users.bat"
echo. >> "%DIST_DIR%\setup_for_users.bat"
echo echo Installing required packages... >> "%DIST_DIR%\setup_for_users.bat"
echo pip install pandas openpyxl PyPDF2 reportlab pillow >> "%DIST_DIR%\setup_for_users.bat"
echo if %%ERRORLEVEL%% NEQ 0 ( >> "%DIST_DIR%\setup_for_users.bat"
echo     echo ERROR: Failed to install dependencies >> "%DIST_DIR%\setup_for_users.bat"
echo     pause >> "%DIST_DIR%\setup_for_users.bat"
echo     exit /b 1 >> "%DIST_DIR%\setup_for_users.bat"
echo ^) >> "%DIST_DIR%\setup_for_users.bat"
echo. >> "%DIST_DIR%\setup_for_users.bat"
echo echo Creating desktop shortcut... >> "%DIST_DIR%\setup_for_users.bat"
echo powershell -ExecutionPolicy Bypass -File create_simple_shortcut.ps1 >> "%DIST_DIR%\setup_for_users.bat"
echo. >> "%DIST_DIR%\setup_for_users.bat"
echo echo ======================================== >> "%DIST_DIR%\setup_for_users.bat"
echo echo   Setup Complete! >> "%DIST_DIR%\setup_for_users.bat"
echo echo ======================================== >> "%DIST_DIR%\setup_for_users.bat"
echo echo. >> "%DIST_DIR%\setup_for_users.bat"
echo echo CRTV Payslip System is now installed! >> "%DIST_DIR%\setup_for_users.bat"
echo echo. >> "%DIST_DIR%\setup_for_users.bat"
echo echo To launch the app: >> "%DIST_DIR%\setup_for_users.bat"
echo echo   1. Double-click desktop shortcut >> "%DIST_DIR%\setup_for_users.bat"
echo echo   2. Or run launch_animated_ui.bat >> "%DIST_DIR%\setup_for_users.bat"
echo echo. >> "%DIST_DIR%\setup_for_users.bat"
echo echo IMPORTANT: >> "%DIST_DIR%\setup_for_users.bat"
echo echo   - Place payslip PDF in: input\payslips.pdf >> "%DIST_DIR%\setup_for_users.bat"
echo echo   - Place employee Excel in: input\employees.xlsx >> "%DIST_DIR%\setup_for_users.bat"
echo echo   - Place stamp image in: input\Stamp.png >> "%DIST_DIR%\setup_for_users.bat"
echo echo. >> "%DIST_DIR%\setup_for_users.bat"
echo pause >> "%DIST_DIR%\setup_for_users.bat"

REM Copy shortcut creator
echo [8/8] Copying shortcut creator...
copy "create_simple_shortcut.ps1" "%DIST_DIR%\" >nul

REM Create user guide
echo # CRTV Payslip System - User Guide > "%DIST_DIR%\USER_GUIDE.txt"
echo. >> "%DIST_DIR%\USER_GUIDE.txt"
echo ## Quick Start Guide >> "%DIST_DIR%\USER_GUIDE.txt"
echo. >> "%DIST_DIR%\USER_GUIDE.txt"
echo 1. Run setup_for_users.bat to install dependencies >> "%DIST_DIR%\USER_GUIDE.txt"
echo 2. Place your files in the input folder: >> "%DIST_DIR%\USER_GUIDE.txt"
echo    - payslips.pdf (combined payslip PDF) >> "%DIST_DIR%\USER_GUIDE.txt"
echo    - employees.xlsx (employee list with Name and Email columns) >> "%DIST_DIR%\USER_GUIDE.txt"
echo    - Stamp.png (company stamp image) >> "%DIST_DIR%\USER_GUIDE.txt"
echo 3. Launch the app using the desktop shortcut >> "%DIST_DIR%\USER_GUIDE.txt"
echo 4. Use the interface to process and send payslips >> "%DIST_DIR%\USER_GUIDE.txt"
echo. >> "%DIST_DIR%\USER_GUIDE.txt"
echo ## Features >> "%DIST_DIR%\USER_GUIDE.txt"
echo - Professional animated loading screen >> "%DIST_DIR%\USER_GUIDE.txt"
echo - Modern user interface for directors >> "%DIST_DIR%\USER_GUIDE.txt"
echo - Automatic email sending via Gmail >> "%DIST_DIR%\USER_GUIDE.txt"
echo - Simulation mode for testing >> "%DIST_DIR%\USER_GUIDE.txt"
echo - Progress tracking and error handling >> "%DIST_DIR%\USER_GUIDE.txt"
echo. >> "%DIST_DIR%\USER_GUIDE.txt"
echo ## Support >> "%DIST_DIR%\USER_GUIDE.txt"
echo For technical support, contact CRTV IT Department. >> "%DIST_DIR%\USER_GUIDE.txt"

echo.
echo ✅ Distribution package created successfully!
echo.
echo 📁 Package location: %DIST_DIR%
echo 📦 Ready to share with other users!
echo.
echo Package contains:
echo   - Complete application files
echo   - Automatic setup script
echo   - User documentation
echo   - Desktop shortcut creator
echo.

REM Ask if user wants to open the folder
set /p choice="Open distribution folder? (Y/N): "
if /i "%choice%"=="Y" start "" "%DIST_DIR%"

pause
