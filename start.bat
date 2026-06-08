@echo off
echo ========================================
echo     T2S Predict - Demarrage serveurs
echo ========================================
echo.

:: Backend
echo [1/2] Demarrage Backend (port 8000)...
start "T2S Backend" cmd /k "cd /d %~dp0backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

:: Frontend
echo [2/2] Demarrage Frontend (port 3000)...
start "T2S Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo  Application disponible sur :
echo  http://localhost:3000
echo ========================================
echo.
start http://localhost:3000
