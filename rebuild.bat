@echo off
REM Quick Rebuild Script for main.exe
REM Run this after making changes to main.py

echo ===============================================
echo   Invoice/POS System - EXE Rebuild Script
echo ===============================================
echo.

echo [1/3] Cleaning previous build...
if exist dist\main.exe del /F /Q dist\main.exe
if exist build rmdir /S /Q build

echo [2/3] Building new executable...
pyinstaller --noconfirm --clean main.spec

if %ERRORLEVEL% neq 0 (
  echo.
  echo [ERROR] Build failed! Check the error messages above.
  pause
  exit /b %ERRORLEVEL%
)

echo [3/3] Verifying build...
if exist dist\main.exe (
  echo.
  echo ===============================================
  echo   SUCCESS! Your new main.exe is ready!
  echo ===============================================
  echo.
  echo Location: dist\main.exe
  for %%A in (dist\main.exe) do echo Size: %%~zA bytes
  echo.
  echo You can now distribute dist\main.exe
  echo.
) else (
  echo.
  echo [ERROR] main.exe was not created!
  echo.
)

pause

