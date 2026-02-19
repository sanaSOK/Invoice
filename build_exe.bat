@echo off
REM Build one-file executable using the venv Python
SET PYTHON_EXEC="%~dp0.venv\Scripts\python.exe"
if not exist %PYTHON_EXEC% (
  echo Python executable not found at %PYTHON_EXEC%
  echo Activate your venv or edit this script to point to your python.
  exit /b 1
)

%PYTHON_EXEC% -m PyInstaller --noconfirm --onefile --add-data "invoices;invoices" main.py
if %ERRORLEVEL% neq 0 (
  echo Build failed
  exit /b %ERRORLEVEL%
)
echo Build completed. See dist\main.exe
