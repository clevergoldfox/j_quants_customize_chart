@echo off
setlocal

cd /d "%~dp0\.."

if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
)

python scripts\update_multi_stocks.py --config config\config.json --install

if errorlevel 1 (
  echo.
  echo Update failed. Please check logs.
  pause
  exit /b 1
)

echo.
echo Multi-stock update completed successfully.
endlocal
