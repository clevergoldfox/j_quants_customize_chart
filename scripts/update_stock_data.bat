@echo off
setlocal

REM Move to project root
cd /d "%~dp0\.."

REM Activate venv if it exists
if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
)

python scripts\update_stock_data.py --config config\config.json --install

endlocal
