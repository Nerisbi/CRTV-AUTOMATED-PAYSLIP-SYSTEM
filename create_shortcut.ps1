# CRTV Payslip System - Desktop Shortcut Creator
# This script creates a desktop shortcut for the animated UI

Write-Host "Creating CRTV Payslip System desktop shortcut..." -ForegroundColor Green

# Get current directory
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ShortcutPath = "$env:USERPROFILE\Desktop\CRTV Payslip System.lnk"

# Target script
$TargetPath = Join-Path $ScriptPath "launch_animated_ui.bat"

# Create Shell Object
$Shell = New-Object -ComObject WScript.Shell

# Create Shortcut
$Shortcut = $Shell.CreateShortcut($ShortcutPath)

# Set shortcut properties
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $ScriptPath
$Shortcut.Description = "CRTV Automated Payslip Distribution System"
$Shortcut.IconLocation = "shell32.dll,25"  # Folder icon
$Shortcut.WindowStyle = 1  # Normal window

# Save shortcut
$Shortcut.Save()

Write-Host "✅ Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "📍 Location: $ShortcutPath" -ForegroundColor Cyan
Write-Host "🚀 You can now launch the app from your desktop!" -ForegroundColor Yellow

# Pause to see output
Write-Host "Press Enter to exit" -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
