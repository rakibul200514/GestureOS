@echo off
title GestureOS Native Desktop
color 0b
echo ============================================================
echo          GestureOS - Native Windows Desktop Controller
echo                   (NO BROWSER REQUIRED)
echo ============================================================
echo.
cd /d "%~dp0"
echo [INFO] Starting GestureOS Desktop Window...
echo Press 's' to activate mouse control.
echo Press 'q' or 'ESC' to quit.
echo ============================================================
echo.
venv\Scripts\python.exe backend\desktop_app.py
pause
