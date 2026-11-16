@echo off
title GestureOS Launcher
color 0b
echo ============================================================
echo           GestureOS - Touchless Desktop Control
echo           Windows 11 One-Click Launcher
echo ============================================================
echo.

:: Move to script directory
cd /d "%~dp0"

echo [1/2] Opening Dashboard in your Web Browser...
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000

echo [2/2] Starting GestureOS Backend Server...
echo.
echo Press Ctrl + C in this window anytime to stop the application.
echo ============================================================
echo.

venv\Scripts\python.exe backend\main.py

pause
