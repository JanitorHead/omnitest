@echo off
chcp 65001 > nul
title Omnitest

echo ========================================================
echo                 OMNITEST - Iniciando...
echo ========================================================
echo.

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado en el sistema.
    echo.
    echo Instala Python desde: https://www.python.org/downloads/
    echo IMPORTANTE: marca "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado.
echo.
echo Instalando / verificando dependencias...
cd /d "%~dp0"
pip install -r requirements.txt -q --disable-pip-version-check

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Fallo al instalar las dependencias.
    echo Comprueba tu conexion a internet e intentalo de nuevo.
    pause
    exit /b 1
)

echo [OK] Dependencias listas.
echo.
echo ========================================================
echo  Abriendo Omnitest en tu navegador...
echo  No cierres esta ventana mientras uses la aplicacion.
echo ========================================================
echo.

streamlit run app.py --server.headless false

pause
