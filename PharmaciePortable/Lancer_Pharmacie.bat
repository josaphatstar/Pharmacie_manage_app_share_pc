@echo off
title Application Pharmacie
echo.
echo ========================================
echo   APPLICATION PHARMACIE PORTABLE
echo ========================================
echo.
echo Lancement de l'application...
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installe sur ce PC
    echo.
    echo Veuillez installer Python depuis: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Installer les dépendances si nécessaire
echo Verification des dependances...
pip install streamlit pandas requests >nul 2>&1

REM Lancer l'application
echo Demarrage de l'application...
python desktop_portable.py

pause
