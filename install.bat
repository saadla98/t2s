@echo off
echo ========================================
echo   T2S Predict - Installation
echo ========================================
echo.

:: Backend dependencies
echo [1/3] Installation des dependances Python...
cd /d %~dp0backend
python -m pip install -r requirements.txt
python -m pip install openpyxl
if %errorlevel% neq 0 (
    echo ERREUR: pip a echoue. Verifiez que Python est installe avec "Add to PATH".
    pause
    exit /b 1
)

:: Init database
echo.
echo [2/3] Initialisation de la base de donnees...
python init_system.py
if %errorlevel% neq 0 (
    echo ERREUR: Initialisation de la base echouee.
    pause
    exit /b 1
)

:: Frontend dependencies
echo.
echo [3/3] Installation des dependances Node.js...
cd /d %~dp0frontend
npm install
if %errorlevel% neq 0 (
    echo ERREUR: npm install a echoue. Verifiez que Node.js est installe.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Installation terminee avec succes !
echo  Lancez start.bat pour demarrer l'app.
echo ========================================
pause
