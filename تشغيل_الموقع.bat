@echo off
chcp 65001 >nul
set PYTHONUTF8=1
title Hussein Atheer Store

echo ================================================================
echo   متجر حسين اثير ^| @ttbbegbot
echo   Bot + Web Server
echo ================================================================
echo.

REM اقتل أي Python قديم على المنفذ 8080
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8080" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [OK] Starting...
echo.

REM شغّل البوت والسيرفر
python -X utf8 bot_backend.py

echo.
echo [!] Server stopped. Press any key to restart...
pause >nul
goto :EOF
