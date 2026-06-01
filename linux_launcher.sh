#!/bin/bash
# Daypo Extractor - Launcher para Linux
# Ejecuta este script desde la terminal o desde tu gestor de archivos
# (puede que necesites darle permiso de ejecucion la primera vez con:
#   chmod +x linux_launcher.sh )

clear
echo "========================================================"
echo "           DAYPO EXTRACTOR - Iniciando..."
echo "========================================================"
echo ""

# Cambiar al directorio donde esta este script
cd "$(dirname "$(readlink -f "$0")")"

# Verificar que Python3 esta disponible
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
pip3 install streamlit requests python-docx -q --disable-pip-version-check

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Fallo al instalar las dependencias."
    echo "Prueba con: pip3 install --user streamlit requests python-docx"
    echo "O comprueba tu conexion a internet."
    read -p "Pulsa Enter para salir..."
    exit 1
fi

echo "[OK] Dependencias listas."
echo ""
echo "========================================================"
echo " Abriendo Daypo Extractor en tu navegador..."
echo " No cierres esta terminal mientras uses la aplicacion."
echo "========================================================"
echo ""

python3 -m streamlit run daypo_extractor.py --server.headless false
