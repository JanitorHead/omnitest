#!/bin/bash
# Omnitest - Launcher para Linux
# Dale permiso de ejecucion la primera vez:  chmod +x linux_launcher.sh

clear
echo "========================================================"
echo "                OMNITEST - Iniciando..."
echo "========================================================"
echo ""

cd "$(dirname "$(readlink -f "$0")")"

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 no encontrado en el sistema."
    echo ""
    echo "Instala Python3 con el gestor de paquetes de tu distribucion."
    echo "  Debian/Ubuntu:  sudo apt install python3 python3-pip"
    echo "  Fedora/RHEL:    sudo dnf install python3 python3-pip"
    echo "  Arch:           sudo pacman -S python python-pip"
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
    echo "Prueba con: pip3 install --user -r requirements.txt"
    read -p "Pulsa Enter para salir..."
    exit 1
fi

echo "[OK] Dependencias listas."
echo ""
echo "========================================================"
echo " Abriendo Omnitest en tu navegador..."
echo " No cierres esta terminal mientras uses la aplicacion."
echo "========================================================"
echo ""

python3 -m streamlit run app.py --server.headless false
