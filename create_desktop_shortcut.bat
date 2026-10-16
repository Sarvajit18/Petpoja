@echo off
TITLE Create Petpooja Desktop Shortcut
cd /d "%~dp0"

echo Creating Petpooja POS Desktop Shortcut...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$WshShell = New-Object -ComObject WScript.Shell; " ^
  "$DesktopPath = [Environment]::GetFolderPath('Desktop'); " ^
  "$Shortcut = $WshShell.CreateShortcut(\"$DesktopPath\Petpooja POS.lnk\"); " ^
  "$Shortcut.TargetPath = 'wscript.exe'; " ^
  "$Shortcut.Arguments = '\"%CD%\Petpooja_POS.vbs\"'; " ^
  "$Shortcut.WorkingDirectory = '%CD%'; " ^
  "$Shortcut.Description = 'Petpooja Restaurant POS & Billing Station'; " ^
  "$Shortcut.Save(); " ^
  "Write-Host 'Petpooja POS shortcut successfully placed on your Desktop!' -ForegroundColor Green"

pause
