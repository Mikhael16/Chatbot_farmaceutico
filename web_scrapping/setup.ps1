# Script de configuración e instalación para el scraper de Inkafarma
# Ejecutar desde PowerShell: .\web_scrapping\setup.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup: Scraper Inkafarma (Prototipo)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Python no encontrado. Instala Python 3.8+ desde python.org" -ForegroundColor Red
    exit 1
}

# 2. Crear entorno virtual
Write-Host ""
Write-Host "[2/5] Creando entorno virtual (.venv)..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "✓ Entorno virtual ya existe" -ForegroundColor Green
}
else {
    python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Entorno virtual creado" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Error al crear entorno virtual" -ForegroundColor Red
        exit 1
    }
}

# 3. Activar entorno virtual
Write-Host ""
Write-Host "[3/5] Activando entorno virtual..." -ForegroundColor Yellow
try {
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "✓ Entorno virtual activado" -ForegroundColor Green
}
catch {
    Write-Host " No se pudo activar automáticamente. Ejecuta manualmente: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
}

# 4. Instalar dependencias
Write-Host ""
Write-Host "[4/5] Instalando dependencias desde requirements.txt..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
pip install -r .\web_scrapping\requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencias instaladas" -ForegroundColor Green
}
else {
    Write-Host "✗ Error al instalar dependencias" -ForegroundColor Red
    exit 1
}

# 5. Verificar instalación
Write-Host ""
Write-Host "[5/5] Verificando instalación..." -ForegroundColor Yellow
$packages = pip list | Select-String -Pattern "requests|beautifulsoup4|lxml"
if ($packages) {
    Write-Host "✓ Paquetes instalados:" -ForegroundColor Green
    $packages | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
}
else {
    Write-Host " No se pudieron verificar todos los paquetes" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup completado exitosamente" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "1. Ejecutar prueba piloto (50 productos):" -ForegroundColor White
Write-Host "   python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_sample.csv --max 50 --stop-on-limit --delay 1.5" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Ejecutar extracción completa (800 productos):" -ForegroundColor White
Write-Host "   python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_catalogue.csv --max 800 --stop-on-limit --delay 1.5" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Ejecutar tests unitarios:" -ForegroundColor White
Write-Host "   pip install pytest" -ForegroundColor Gray
Write-Host "   pytest .\web_scrapping\tests -v" -ForegroundColor Gray
Write-Host ""
