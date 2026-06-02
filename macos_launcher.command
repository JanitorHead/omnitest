#!/bin/bash
# Omnitest - Launcher para macOS
# Doble clic sobre este archivo para arrancar la aplicacion.
# La primera vez puede que macOS pida permiso: ve a
# Preferencias > Privacidad y Seguridad > Permitir de todas formas.

clear
echo "========================================================"
echo "                OMNITEST - Iniciando..."
echo "========================================================"
echo ""

cd "$(dirname "$0")"

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 no encontrado en el sistema."
    echo ""
    echo "Instala Python desde: https://www.python.org/downloads/"
    echo ""
    read -p "Pulsa Enter para salir..."
    exit 1
fi

echo "[OK] Python3 encontrado: $(python3 --version)"
echo ""
echo "Instalando / verificando dependencias..."
pip3 install -r requirements.txt -q --disable-pip-version-check

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
echo " Abriendo Omnitest en tu navegador..."
echo " No cierres esta ventana mientras uses la aplicacion."
echo "========================================================"
echo ""

python3 -m streamlit run app.py --server.headless false

read -p "Pulsa Enter para salir..."
