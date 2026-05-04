@echo off
setlocal EnableDelayedExpansion

title J-Quants MT4 Stock Importer - One Click Installer

echo ============================================================
echo  J-Quants MT4 Stock Importer - One Click Installer
echo ============================================================
echo.

cd /d "%~dp0\.."

echo [1/7] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
  echo Python was not found in PATH.
  echo Please install Python 3.10+ or add Python to PATH.
  pause
  exit /b 1
)

echo [2/7] Creating virtual environment...
if not exist ".venv" (
  python -m venv .venv
)

echo [3/7] Installing Python dependencies...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [4/7] Preparing config file...
if not exist "config\config.json" (
  if exist "config\config.multistock.example.json" (
    copy "config\config.multistock.example.json" "config\config.json" >nul
  ) else (
    copy "config\config.example.json" "config\config.json" >nul
  )
  echo.
  echo config\config.json was created.
  echo Please edit API key and MT4 terminal_data_path before running update.
  echo.
)

echo [5/7] Installing MT4 scripts if terminal_data_path is configured...
python scripts\install_mt4_mq4.py --config config\config.json

echo [6/7] Creating AM7:00 scheduled task...
schtasks /Create /TN "JQuants_MT4_Stock_Update_0700" /TR "\"%CD%\scripts\update_multi_stocks.bat\"" /SC DAILY /ST 07:00 /F >nul
if errorlevel 1 (
  echo Could not create scheduled task automatically.
  echo Please run this BAT as Administrator or create task manually.
) else (
  echo Scheduled task created: JQuants_MT4_Stock_Update_0700
)

echo [7/7] Done.
echo.
echo Next:
echo  1. Edit config\config.json
echo  2. Set J-Quants API key
echo  3. Set MT4 terminal_data_path
echo  4. Run scripts\update_multi_stocks.bat
echo  5. Compile MQ4 files in MetaEditor
echo.
pause
endlocal
