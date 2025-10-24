# Script completo: Extraccion + Conversion a Excel
# Ejecuta el scraper y convierte automaticamente a Excel

param(
    [Parameter(Position=0)]
    [ValidateSet('test', 'pilot', 'full')]
    [string]$Mode = 'test'
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Extraccion Completa Inkafarma" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$csvFile = ""
$excelFile = ""
$maxProducts = 0
$delay = 1.5

switch ($Mode) {
    'test' {
        Write-Host "Modo: TEST (10 productos)" -ForegroundColor Green
        $csvFile = ".\inkafarma_test.csv"
        $excelFile = ".\inkafarma_test.xlsx"
        $maxProducts = 10
        $delay = 0.5
    }
    'pilot' {
        Write-Host "Modo: PILOT (50 productos)" -ForegroundColor Green
        $csvFile = ".\inkafarma_pilot.csv"
        $excelFile = ".\inkafarma_pilot.xlsx"
        $maxProducts = 50
        $delay = 1.5
    }
    'full' {
        Write-Host "Modo: FULL (800 productos)" -ForegroundColor Green
        $csvFile = ".\inkafarma_catalogue.csv"
        $excelFile = ".\inkafarma_productos.xlsx"
        $maxProducts = 800
        $delay = 1.5
    }
}

Write-Host ""
Write-Host "Configuracion:" -ForegroundColor Yellow
Write-Host "  - Productos: $maxProducts" -ForegroundColor Gray
Write-Host "  - Delay: $delay segundos" -ForegroundColor Gray
Write-Host "  - CSV: $csvFile" -ForegroundColor Gray
Write-Host "  - Excel: $excelFile" -ForegroundColor Gray
Write-Host ""

# Paso 1: Ejecutar scraper
Write-Host "[1/2] Ejecutando scraper..." -ForegroundColor Cyan
python .\web_scrapping\scraper_inkafarma.py --output $csvFile --max $maxProducts --stop-on-limit --delay $delay --use-playwright

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] El scraper fallo" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/2] Convirtiendo a Excel..." -ForegroundColor Cyan
python .\web_scrapping\csv_to_excel.py $csvFile $excelFile

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] La conversion a Excel fallo" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  PROCESO COMPLETADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Archivos generados:" -ForegroundColor Cyan
Write-Host "  - CSV:   $csvFile" -ForegroundColor White
Write-Host "  - Excel: $excelFile" -ForegroundColor White
Write-Host ""
Write-Host "Puedes abrir el Excel para ver:" -ForegroundColor Yellow
Write-Host "  - Hoja 1: Productos (datos completos)" -ForegroundColor Gray
Write-Host "  - Hoja 2: Estadisticas (metricas)" -ForegroundColor Gray
Write-Host "  - Hoja 3: Documentacion (diccionario)" -ForegroundColor Gray
Write-Host "  - Hoja 4: Metadatos (proyecto)" -ForegroundColor Gray
Write-Host ""
