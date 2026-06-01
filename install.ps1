                                                      # Daypo Extractor - Instalador automatico para Windows
# Uso: Abre PowerShell y ejecuta:
#   irm https://raw.githubusercontent.com/JanitorHead/extractor-daypo/main/install.ps1 | iex

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$REPO = "https://raw.githubusercontent.com/JanitorHead/extractor-daypo/main"
$DIR  = "$env:USERPROFILE\DaypoExtractor"
$FILES = @("daypo_extractor.py")

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "        DAYPO EXTRACTOR - Instalacion automatica" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Python
Write-Host "[1/3] Comprobando Python..." -ForegroundColor Yellow
$pyOk = $false
try { if ((python --version 2>&1) -match "Python 3") { $pyOk = $true } } catch {}

if (-not $pyOk) {
    Write-Host "      Python no encontrado. Instalando via winget..." -ForegroundColor Yellow
    $wgOk = $false
    try { winget --version 2>&1 | Out-Null; $wgOk = $true } catch {}

    if ($wgOk) {
        winget install --id Python.Python.3.12 --source winget --accept-package-agreements --accept-source-agreements --silent
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Host "  [ERROR] winget no disponible. Instala Python manualmente:" -ForegroundColor Red
        Write-Host "  https://www.python.org/downloads/" -ForegroundColor Red
        Write-Host "  IMPORTANTE: marca 'Add Python to PATH' durante la instalacion." -ForegroundColor Red
        Read-Host "Pulsa Enter para salir"; exit 1
    }
    try { if ((python --version 2>&1) -match "Python 3") { $pyOk = $true } } catch {}
    if (-not $pyOk) {
        Write-Host "  [ERROR] Python no disponible tras instalacion. Abre una nueva sesion de PowerShell." -ForegroundColor Red
        Read-Host "Pulsa Enter para salir"; exit 1
    }
}
Write-Host "      OK - $(python --version)" -ForegroundColor Green

# 2. Descargar archivos
Write-Host ""
Write-Host "[2/3] Descargando archivos a: $DIR" -ForegroundColor Yellow
if (-not (Test-Path $DIR)) { New-Item -ItemType Directory -Path $DIR | Out-Null }
foreach ($f in $FILES) {
    Write-Host "      -> $f" -ForegroundColor Gray
    try { Invoke-WebRequest -Uri "$REPO/$f" -OutFile "$DIR\$f" -UseBasicParsing }
    catch { Write-Host "  [ERROR] No se pudo descargar $f. Comprueba tu conexion." -ForegroundColor Red; Read-Host "Pulsa Enter para salir"; exit 1 }
}
Write-Host "      OK - Archivos descargados." -ForegroundColor Green

# 3. Dependencias
Write-Host ""
Write-Host "[3/3] Instalando dependencias de Python..." -ForegroundColor Yellow
try { python -m pip install streamlit requests python-docx -q --disable-pip-version-check }
catch { Write-Host "  [ERROR] Fallo al instalar dependencias." -ForegroundColor Red; Read-Host "Pulsa Enter para salir"; exit 1 }
Write-Host "      OK - Dependencias listas." -ForegroundColor Green

# 4. Arrancar
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Listo. Abriendo Daypo Extractor en tu navegador..." -ForegroundColor Cyan
Write-Host "  Carpeta instalada en: $DIR" -ForegroundColor White
Write-Host "  No cierres esta ventana mientras uses la app." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Set-Location $DIR
python -m streamlit run daypo_extractor.py --server.headless false
