@echo off
echo ========================================
echo   AntigravityDL - Video Downloader
echo ========================================
echo.

REM Kill any existing instances on port 8000
echo Checking for existing instances...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping existing instance (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Starting AntigravityDL...
echo.
echo The application will open in your browser.
echo Close this window to stop the application.
echo.

python main.py

pause
