# Create Safe Desktop Shortcut for CRTV Payslip System

$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = $WshShell.SpecialFolders("Desktop")
$ShortcutPath = "$DesktopPath\CRTV Payslip System.lnk"
$BatchFilePath = "$PSScriptRoot\Launch CRTV Payslip System.bat"

# Remove existing shortcut if it exists
if (Test-Path $ShortcutPath) {
    Remove-Item $ShortcutPath -Force
}

# Create shortcut
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $BatchFilePath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "CRTV Automated Payslip Distribution System"
$Shortcut.IconLocation = "shell32.dll,25"
$Shortcut.WindowStyle = 1
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Shortcut: $ShortcutPath" -ForegroundColor Yellow
