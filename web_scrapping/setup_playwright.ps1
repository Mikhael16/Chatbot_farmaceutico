# Script para instalar Playwright y navegadores
# Para usar con sitios que requieren renderizado JavaScript (como Inkafarma)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Instalación de Playwright" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si el entorno virtual está activado
if (-not $env:VIRTUAL_ENV) {
    Write-Host "[ERROR] El entorno virtual no está activado." -ForegroundColor Red
    Write-Host "Por favor, ejecuta primero: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/2] Instalando Playwright..." -ForegroundColor Green
python -m pip install playwright

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Falló la instalación de Playwright" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/2] Descargando navegador Chromium..." -ForegroundColor Green
Write-Host "Esto puede tardar varios minutos..." -ForegroundColor Yellow
playwright install chromium

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Falló la instalación de Chromium" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ¡Instalación completada!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Ahora puedes ejecutar el scraper con:" -ForegroundColor Cyan
Write-Host "  python .\web_scrapping\scraper_inkafarma.py --use-playwright --output test.csv --max 10 --stop-on-limit" -ForegroundColor White
Write-Host ""
