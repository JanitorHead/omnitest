#!/usr/bin/env bash
# Daypo Extractor - Instalador automatico para macOS y Linux
#
# macOS - pega esto en la Terminal:
#   curl -fsSL https://raw.githubusercontent.com/JanitorHead/extractor-daypo/main/install.sh | bash
#
# Linux - pega esto en la terminal:
#   curl -fsSL https://raw.githubusercontent.com/JanitorHead/extractor-daypo/main/install.sh | bash

set -euo pipefail

REPO="https://raw.githubusercontent.com/JanitorHead/extractor-daypo/main"
DIR="$HOME/DaypoExtractor"
FILES=("daypo_extractor.py")

echo ''
echo '========================================================'
echo '       DAYPO EXTRACTOR - Instalacion automatica'
echo '========================================================'
echo ''

# 1. Comprobar / instalar Python3
echo '[1/3] Comprobando Python3...'

install_python_macos() {
    if command -v brew &>/dev/null; then
        echo '      Instalando Python via Homebrew...'
        brew install python3
    else
        echo '  [INFO] Homebrew no encontrado. Instalando Homebrew primero...'
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(brew shellenv 2>/dev/null || true)"
        brew install python3
    fi
}

install_python_linux() {
    if command -v apt-get &>/dev/null; then
        echo '      Detectado: Debian/Ubuntu. Instalando python3...'
        sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip
    elif command -v dnf &>/dev/null; then
        echo '      Detectado: Fedora/RHEL. Instalando python3...'
        sudo dnf install -y python3 python3-pip
    elif command -v pacman &>/dev/null; then
        echo '      Detectado: Arch. Instalando python...'
        sudo pacman -Sy --noconfirm python python-pip
    else
        echo '  [ERROR] No se pudo detectar tu gestor de paquetes.'
        echo '  Instala Python3 manualmente y vuelve a ejecutar este script.'
        exit 1
    fi
}

if ! command -v python3 &>/dev/null; then
    echo '      Python3 no encontrado. Instalando...'
    OS="$(uname -s)"
    if [ "$OS" = "Darwin" ]; then install_python_macos; else install_python_linux; fi
fi

if ! command -v python3 &>/dev/null; then
    echo '  [ERROR] Python3 no disponible. Instala desde: https://www.python.org/downloads/'
    exit 1
fi
echo "      OK - $(python3 --version)"

# 2. Descargar archivos
echo ''
echo "[2/3] Descargando archivos a: $DIR"
mkdir -p "$DIR"

for f in "${FILES[@]}"; do
    echo "      -> $f"
    if command -v curl &>/dev/null; then
        curl -fsSL "$REPO/$f" -o "$DIR/$f"
    elif command -v wget &>/dev/null; then
        wget -q "$REPO/$f" -O "$DIR/$f"
    else
        echo '  [ERROR] Se necesita curl o wget.'
        exit 1
    fi
done
echo '      OK - Archivos descargados.'

# 3. Dependencias de Python
echo ''
echo '[3/3] Instalando dependencias de Python...'
python3 -m pip install streamlit requests python-docx -q --disable-pip-version-check 2>/dev/null || \
python3 -m pip install streamlit requests python-docx -q --user --disable-pip-version-check
echo '      OK - Dependencias listas.'

# 4. Arrancar
echo ''
echo '========================================================'
echo '  Listo. Abriendo Daypo Extractor en tu navegador...'
echo "  Carpeta instalada en: $DIR"
echo '  No cierres esta terminal mientras uses la app.'
echo '========================================================'
echo ''
cd "$DIR"
python3 -m streamlit run daypo_extractor.py --server.headless false
