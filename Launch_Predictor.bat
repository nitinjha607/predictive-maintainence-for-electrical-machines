@echo off
title AI Motor Predictor Launcher
color 0B
echo ======================================================
echo    AI MOTOR STATE PREDICTOR - SYSTEM LAUNCHER
echo ======================================================
echo.
echo [1/2] Verifying Python Environment...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. 
    echo Please install Python from python.org
    pause
    exit
)
echo.
echo [2/2] Launching AI Predictor Application...
start "" python "Python Software\AI_Predictor.py"
echo.
echo [Done] Application started. This window will close.
timeout /t 3 >nul
exit
