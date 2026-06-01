@echo off
chcp 65001 > nul
title Daypo Extractor

echo.
echo  Comprobando e instalando dependencias...
echo.
pip install streamlit requests python-docx -q

if %errorlevel% neq 0 (
    echo [ERROR] Instala Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo  Arrancando la aplicacion. No cierres esta ventana.
echo.
streamlit run daypo_extractor.py
pause
