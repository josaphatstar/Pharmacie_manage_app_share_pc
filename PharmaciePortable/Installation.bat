@echo off
title Installation Pharmacie Portable
echo.
echo ========================================
echo   INSTALLATION PHARMACIE PORTABLE
echo ========================================
echo.

REM Vérifier Python
echo Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERREUR: Python n'est pas installe
    echo.
    echo Veuillez:
    echo 1. Aller sur https://www.python.org/downloads/
    echo 2. Telecharger et installer Python
    echo 3. COCHER "Add Python to PATH" lors de l'installation
    echo 4. Redemarrer votre PC
    echo 5. Relancer ce script
    echo.
    pause
    exit /b 1
)

echo Python detecte!
echo.

REM Installer les dépendances
echo Installation des dependances...
echo Cela peut prendre quelques minutes...
echo.

pip install streamlit pandas requests

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   INSTALLATION TERMINEE AVEC SUCCES!
    echo ========================================
    echo.
    echo Vous pouvez maintenant lancer l'application avec:
    echo - Lancer_Pharmacie.bat
    echo - ou python desktop_portable.py
    echo.
) else (
    echo.
    echo ERREUR lors de l'installation des dependances
    echo Essayez de relancer ce script en tant qu'administrateur
    echo.
)

pause
