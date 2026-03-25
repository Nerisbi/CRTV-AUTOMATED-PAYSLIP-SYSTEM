' CRTV Payslip System - Desktop Shortcut Creator
Set objShell = CreateObject("WScript.Shell")

' Get current directory
strCurrentDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Desktop path
strDesktop = objShell.SpecialFolders("Desktop")

' Create shortcut
Set objShortcut = objShell.CreateShortcut(strDesktop & "\CRTV Payslip System.lnk")

' Set shortcut properties
objShortcut.TargetPath = strCurrentDir & "\launch_animated_ui.bat"
objShortcut.WorkingDirectory = strCurrentDir
objShortcut.Description = "CRTV Automated Payslip Distribution System"
objShortcut.Save()

' Show success message
MsgBox "CRTV Payslip System desktop shortcut created successfully!" & vbCrLf & vbCrLf & "Find it on your desktop: CRTV Payslip System", 64, "Success"
