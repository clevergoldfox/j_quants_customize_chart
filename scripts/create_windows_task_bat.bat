@echo off
setlocal
cd /d "%~dp0\.."

schtasks /Create /TN "JQuants_MT4_Stock_Update_0700" /TR "\"%CD%\scripts\update_multi_stocks.bat\"" /SC DAILY /ST 07:00 /F

if errorlevel 1 (
  echo Failed to create scheduled task.
  echo Try running this BAT as Administrator.
  pause
  exit /b 1
)

echo Scheduled task created successfully.
pause
endlocal
