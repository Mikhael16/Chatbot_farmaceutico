# Script de setup simplificado para el scraper de Inkafarma
# Ejecutar desde PowerShell: .\web_scrapping\setup_simple.ps1

Write-Host "`n========== SETUP INKAFARMA SCRAPER ==========" -ForegroundColor Cyan

# 1. Verificar Python
Write-Host "`n[1/5] Verificando Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python no encontrado" -ForegroundColor Red
    exit 1
}
Write-Host "OK" -ForegroundColor Green

# 2. Crear entorno virtual
Write-Host "`n[2/5] Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "Entorno virtual ya existe" -ForegroundColor Gray
} else {
    python -m venv .venv
    Write-Host "OK" -ForegroundColor Green
}

# 3. Activar entorno virtual
Write-Host "`n[3/5] Activando entorno virtual..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1
Write-Host "OK" -ForegroundColor Green

# 4. Instalar dependencias
Write-Host "`n[4/5] Instalando dependencias..." -ForegroundColor Yellow
Write-Host "Actualizando pip..." -ForegroundColor Gray
python -m pip install --upgrade pip
Write-Host "Instalando paquetes..." -ForegroundColor Gray
pip install -r .\web_scrapping\requirements.txt
Write-Host "OK" -ForegroundColor Green

# 5. Verificar
Write-Host "`n[5/5] Verificando instalacion..." -ForegroundColor Yellow
pip list | Select-String -Pattern "requests|beautifulsoup4|lxml"
Write-Host "OK" -ForegroundColor Green

Write-Host "`n========== SETUP COMPLETADO ==========" -ForegroundColor Green
Write-Host "`nProximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Prueba: .\web_scrapping\run_scraper.ps1 test" -ForegroundColor White
Write-Host "  2. Pilot:  .\web_scrapping\run_scraper.ps1 pilot" -ForegroundColor White
Write-Host "  3. Full:   .\web_scrapping\run_scraper.ps1 full`n" -ForegroundColor White
