#!/usr/bin/env bash
# Omnitest - Instalador automatico para macOS y Linux
# Pega esto en la terminal:
#   curl -fsSL https://raw.githubusercontent.com/JanitorHead/omnitest/main/install.sh | bash

set -euo pipefail

TARBALL="https://github.com/JanitorHead/omnitest/archive/refs/heads/main.tar.gz"
DIR="$HOME/Omnitest"

echo ''
echo '========================================================'
echo '            OMNITEST - Instalacion automatica'
echo '========================================================'
echo ''

# 1. Comprobar / instalar Python3
echo '[1/3] Comprobando Python3...'
install_python_macos() {
    if command -v brew &>/dev/null; then
        brew install python3
    else
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(brew shellenv 2>/dev/null || true)"
        brew install python3
    fi
}
install_python_linux() {
    if command -v apt-get &>/dev/null; then sudo apt-get update -qq && sudo apt-get install -y python3 python3-pip
    elif command -v dnf &>/dev/null; then sudo dnf install -y python3 python3-pip
    elif command -v pacman &>/dev/null; then sudo pacman -Sy --noconfirm python python-pip
    else echo '  [ERROR] Instala Python3 manualmente y vuelve a ejecutar.'; exit 1; fi
}
if ! command -v python3 &>/dev/null; then
    OS="$(uname -s)"
    if [ "$OS" = "Darwin" ]; then install_python_macos; else install_python_linux; fi
fi
if ! command -v python3 &>/dev/null; then
    echo '  [ERROR] Python3 no disponible. Instala desde https://www.python.org/downloads/'
    exit 1
fi
echo "      OK - $(python3 --version)"

# 2. Descargar y extraer el repositorio
echo ''
echo "[2/3] Descargando Omnitest en: $DIR"
rm -rf "$DIR"
mkdir -p "$DIR"
curl -fsSL "$TARBALL" | tar -xz -C "$DIR" --strip-components=1
echo '      OK - Archivos descargados.'

# 3. Dependencias
echo ''
echo '[3/3] Instalando dependencias de Python...'
python3 -m pip install -r "$DIR/requirements.txt" -q --disable-pip-version-check 2>/dev/null || \
python3 -m pip install -r "$DIR/requirements.txt" -q --user --disable-pip-version-check
echo '      OK - Dependencias listas.'

# 4. Arrancar
echo ''
echo '========================================================'
echo '  Listo. Abriendo Omnitest en tu navegador...'
echo "  Carpeta instalada en: $DIR"
echo '  No cierres esta terminal mientras uses la app.'
echo '========================================================'
echo ''
cd "$DIR"
python3 -m streamlit run app.py --server.headless false
