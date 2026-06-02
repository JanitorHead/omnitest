# Omnitest - Instalador automatico para Windows
# Uso: abre PowerShell y ejecuta:
#   irm https://raw.githubusercontent.com/JanitorHead/omnitest/main/install.ps1 | iex

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ZIP = "https://github.com/JanitorHead/omnitest/archive/refs/heads/main.zip"
$DIR = "$env:USERPROFILE\Omnitest"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "            OMNITEST - Instalacion automatica" -ForegroundColor Cyan
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
        Write-Host "  https://www.python.org/downloads/  (marca 'Add Python to PATH')" -ForegroundColor Red
        Read-Host "Pulsa Enter para salir"; exit 1
    }
    try { if ((python --version 2>&1) -match "Python 3") { $pyOk = $true } } catch {}
    if (-not $pyOk) {
        Write-Host "  [ERROR] Python no disponible. Abre una nueva sesion de PowerShell." -ForegroundColor Red
        Read-Host "Pulsa Enter para salir"; exit 1
    }
}
Write-Host "      OK - $(python --version)" -ForegroundColor Green

# 2. Descargar y extraer el repositorio
Write-Host ""
Write-Host "[2/3] Descargando Omnitest en: $DIR" -ForegroundColor Yellow
$tmp = "$env:TEMP\omnitest.zip"
Invoke-WebRequest -Uri $ZIP -OutFile $tmp -UseBasicParsing
if (Test-Path $DIR) { Remove-Item $DIR -Recurse -Force }
Expand-Archive -Path $tmp -DestinationPath "$env:TEMP\omnitest_extract" -Force
Move-Item "$env:TEMP\omnitest_extract\omnitest-main" $DIR -Force
Remove-Item $tmp -Force
Remove-Item "$env:TEMP\omnitest_extract" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "      OK - Archivos descargados." -ForegroundColor Green

# 3. Dependencias
Write-Host ""
Write-Host "[3/3] Instalando dependencias de Python..." -ForegroundColor Yellow
try { python -m pip install -r "$DIR\requirements.txt" -q --disable-pip-version-check }
catch { Write-Host "  [ERROR] Fallo al instalar dependencias." -ForegroundColor Red; Read-Host "Pulsa Enter para salir"; exit 1 }
Write-Host "      OK - Dependencias listas." -ForegroundColor Green

# 4. Arrancar
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Listo. Abriendo Omnitest en tu navegador..." -ForegroundColor Cyan
Write-Host "  Carpeta instalada en: $DIR" -ForegroundColor White
Write-Host "  No cierres esta ventana mientras uses la app." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Set-Location $DIR
python -m streamlit run app.py --server.headless false
