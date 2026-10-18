@echo off
TITLE Create Shansara Desktop Shortcut
cd /d "%~dp0"

echo Creating Shansara POS Desktop Shortcut...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$WshShell = New-Object -ComObject WScript.Shell; " ^
  "$DesktopPath = [Environment]::GetFolderPath('Desktop'); " ^
  "$Shortcut = $WshShell.CreateShortcut(\"$DesktopPath\Shansara POS.lnk\"); " ^
  "$Shortcut.TargetPath = 'wscript.exe'; " ^
  "$Shortcut.Arguments = '\"%CD%\Petpooja_POS.vbs\"'; " ^
  "$Shortcut.WorkingDirectory = '%CD%'; " ^
  "$Shortcut.Description = 'Shansara Restaurant POS & Billing Station'; " ^
  "$Shortcut.Save(); " ^
  "Write-Host 'Shansara POS shortcut successfully placed on your Desktop!' -ForegroundColor Green"

pause
