@echo off
REM OneDrive Removal Script
echo WARNING: This will remove OneDrive completely!
pause
echo Stopping OneDrive...
taskkill /f /im OneDrive.exe
timeout /t 3
echo Uninstalling OneDrive...
%LOCALAPPDATA%\Microsoft\OneDrive\OneDriveSetup.exe /uninstall
timeout /t 5
echo Removing OneDrive folder...
rd "C:\Users\fonat\OneDrive" /s /q
echo Preventing OneDrive from auto-starting...
reg add "HKLM\Software\Policies\Microsoft\Windows\OneDrive" /v "DisableFileSyncNGSC" /t REG_DWORD /d 1 /f
echo Done!
pause
