# Simple CRTV Desktop Shortcut Creator

$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ShortcutPath = "$env:USERPROFILE\Desktop\CRTV Payslip System.lnk"
$TargetPath = Join-Path $ScriptPath "launch_animated_ui.bat"

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $ScriptPath
$Shortcut.Description = "CRTV Automated Payslip Distribution System"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!"
