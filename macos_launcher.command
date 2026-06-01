#!/bin/bash
# Daypo Extractor - Launcher para macOS
# Doble clic sobre este archivo para arrancar la aplicacion.
# La primera vez puede que macOS pida permiso: ve a
# Preferencias > Privacidad y Seguridad > Permitir de todas formas.

clear
echo "========================================================"
echo "           DAYPO EXTRACTOR - Iniciando..."
echo "========================================================"
echo ""

# Cambiar al directorio donde esta este script
cd "$(dirname "$0")"

# Verificar que Python3 esta disponible
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 no encontrado en el sistema."
    echo ""
    echo "Por favor, instala Python desde:"
    echo "  https://www.python.org/downloads/"
    echo ""
    read -p "Pulsa Enter para salir..."
    exit 1
fi

echo "[OK] Python3 encontrado: $(python3 --version)"
echo ""
echo "Instalando / verificando dependencias..."
pip3 install streamlit requests python-docx -q --disable-pip-version-check

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Fallo al instalar las dependencias."
    echo "Comprueba tu conexion a internet e intentalo de nuevo."
    read -p "Pulsa Enter para salir..."
    exit 1
fi

echo "[OK] Dependencias listas."
echo ""
echo "========================================================"
echo " Abriendo Daypo Extractor en tu navegador..."
echo " No cierres esta ventana mientras uses la aplicacion."
echo "========================================================"
echo ""

python3 -m streamlit run daypo_extractor.py --server.headless false

read -p "Pulsa Enter para salir..."
