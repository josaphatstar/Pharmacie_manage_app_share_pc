@echo off
title Test Pharmacie Portable
echo.
echo ========================================
echo   TEST DE L'ENVIRONNEMENT
echo ========================================
echo.

echo Test de Python...
python --version
if %errorlevel% neq 0 (
    echo ERREUR: Python non detecte
    pause
    exit /b 1
)

echo.
echo Test des modules...
python -c "import streamlit; print('Streamlit: OK')" 2>nul || echo Streamlit: MANQUANT
python -c "import pandas; print('Pandas: OK')" 2>nul || echo Pandas: MANQUANT  
python -c "import sqlite3; print('SQLite: OK')" 2>nul || echo SQLite: MANQUANT
python -c "import requests; print('Requests: OK')" 2>nul || echo Requests: MANQUANT

echo.
echo Test des fichiers...
if exist "app.py" (echo app.py: OK) else (echo app.py: MANQUANT)
if exist "db.py" (echo db.py: OK) else (echo db.py: MANQUANT)
if exist "utils.py" (echo utils.py: OK) else (echo utils.py: MANQUANT)
if exist "desktop_portable.py" (echo desktop_portable.py: OK) else (echo desktop_portable.py: MANQUANT)

echo.
echo ========================================
echo   FIN DU TEST
echo ========================================
pause
