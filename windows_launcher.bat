@echo off
chcp 65001 > nul
title Daypo Extractor

echo ========================================================
echo           DAYPO EXTRACTOR - Iniciando...
echo ========================================================
echo.

:: Verificar que Python esta instalado
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado en el sistema.
    echo.
    echo Por favor, instala Python desde:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante la instalacion, marca la casilla
    echo "Add Python to PATH" antes de hacer clic en Install.
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado.
echo.
echo Instalando / verificando dependencias...
pip install streamlit requests python-docx -q --disable-pip-version-check

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
echo  Abriendo Daypo Extractor en tu navegador...
echo  No cierres esta ventana mientras uses la aplicacion.
echo ========================================================
echo.

:: Cambiar al directorio donde esta el script
cd /d "%~dp0"
streamlit run daypo_extractor.py --server.headless false

pause
