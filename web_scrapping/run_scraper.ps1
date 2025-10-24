# Script helper para ejecutar el scraper con configuraciones predefinidas
# Uso: .\web_scrapping\run_scraper.ps1 [test|pilot|full]

param(
    [Parameter(Position=0)]
    [ValidateSet('test', 'pilot', 'full', 'custom')]
    [string]$Mode = 'pilot'
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ejecutando Scraper Inkafarma" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que el entorno virtual esté activado
if (-not $env:VIRTUAL_ENV) {
    Write-Host " Activando entorno virtual..." -ForegroundColor Yellow
    & ".\.venv\Scripts\Activate.ps1"
}

switch ($Mode) {
    'test' {
        Write-Host "Modo: TEST (10 productos, delay corto, con Playwright)" -ForegroundColor Green
        Write-Host "Comando: python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_test.csv --max 10 --stop-on-limit --delay 0.5 --use-playwright" -ForegroundColor Gray
        Write-Host ""
        python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_test.csv --max 10 --stop-on-limit --delay 0.5 --use-playwright
    }
    'pilot' {
        Write-Host "Modo: PILOT (50 productos, delay normal, con Playwright)" -ForegroundColor Green
        Write-Host "Comando: python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_pilot.csv --max 50 --stop-on-limit --delay 1.5 --use-playwright" -ForegroundColor Gray
        Write-Host ""
        python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_pilot.csv --max 50 --stop-on-limit --delay 1.5 --use-playwright
    }
    'full' {
        Write-Host "Modo: FULL (800 productos, delay normal, con Playwright)" -ForegroundColor Green
        Write-Host "Comando: python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_catalogue.csv --max 800 --stop-on-limit --delay 1.5 --use-playwright" -ForegroundColor Gray
        Write-Host ""
        python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_catalogue.csv --max 800 --stop-on-limit --delay 1.5 --use-playwright
    }
    'custom' {
        Write-Host "Modo: CUSTOM - Ejecuta con tus propios parámetros" -ForegroundColor Green
        Write-Host "Ejemplo: python .\web_scrapping\scraper_inkafarma.py --output .\mi_archivo.csv --max 100 --delay 2 --use-playwright" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ejecución finalizada" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
