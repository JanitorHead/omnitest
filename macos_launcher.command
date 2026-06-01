#!/bin/bash
# Daypo Extractor - Lanzador para macOS
clear
echo "========================================================"
echo "   Daypo Extractor — Iniciando..."
echo "========================================================"
echo ""

# Posicionarse en la carpeta donde está este script
cd "$(dirname "$0")"

echo " Comprobando e instalando dependencias (solo la primera vez)..."
pip3 install streamlit requests python-docx -q 2>/dev/null || pip install streamlit requests python-docx -q

if [ $? -ne 0 ]; then
    echo ""
    echo " [ERROR] No se pudo instalar las dependencias."
    echo " Instala Python desde: https://www.python.org/downloads/"
    read -p " Pulsa Enter para cerrar..."
    exit 1
fi

echo ""
echo " Arrancando la aplicacion. No cierres esta ventana."
echo ""
python3 -m streamlit run daypo_extractor.py || python -m streamlit run daypo_extractor.py

echo ""
read -p " La aplicacion se ha cerrado. Pulsa Enter para salir..."
