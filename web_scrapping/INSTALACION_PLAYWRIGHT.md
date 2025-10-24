#  Instalación de Playwright

## ¿Por qué Playwright?

**Inkafarma usa Angular** para cargar los productos dinámicamente con JavaScript. Los scrapers tradicionales (`requests + BeautifulSoup`) solo ven el HTML estático (esqueleto vacío), pero **Playwright renderiza JavaScript** como un navegador real.

##  Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```powershell
# Activa el entorno virtual primero
.\.venv\Scripts\Activate.ps1

# Ejecuta el script de instalación
.\web_scrapping\setup_playwright.ps1
```

### Opción 2: Manual

```powershell
# 1. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 2. Instalar Playwright
pip install playwright

# 3. Descargar navegador Chromium (puede tardar 3-5 minutos)
playwright install chromium
```

##  Verificar Instalación

```powershell
# Verificar que Playwright está instalado
python -c "from playwright.sync_api import sync_playwright; print('✓ Playwright OK')"
```

##  Usar el Scraper con Playwright

### Test Rápido (10 productos)

```powershell
.\web_scrapping\run_scraper.ps1 test
```

### Pilot (50 productos)

```powershell
.\web_scrapping\run_scraper.ps1 pilot
```

### Completo (800 productos)

```powershell
.\web_scrapping\run_scraper.ps1 full
```

### Comando Manual

```powershell
python .\web_scrapping\scraper_inkafarma.py --use-playwright --output test.csv --max 10 --stop-on-limit
```

##  Solución de Problemas

### Error: "playwright not found"

```powershell
pip install playwright
playwright install chromium
```

### Error: "Chromium not found"

```powershell
playwright install chromium
```

### El scraper sigue dando 0 productos

Verifica que estés usando `--use-playwright`:

```powershell
python .\web_scrapping\scraper_inkafarma.py --use-playwright --output test.csv --max 10
```

##  Diferencias

| Método | Velocidad | Productos encontrados | Uso de memoria |
|--------|-----------|----------------------|----------------|
| **requests** (sin Playwright) |  Rápido | 0 (HTML vacío) |  Bajo |
| **Playwright**  |  Más lento |  Todos |  Medio-Alto |

##  Notas

- Playwright descarga ~150-200 MB de Chromium la primera vez
- Cada request tarda ~3-5 segundos (vs 0.5s con requests)
- **Es necesario para Inkafarma** porque usa Angular
- El navegador se ejecuta en modo `headless` (sin ventana visible)

---

**¿Listo?** Ejecuta: `.\web_scrapping\setup_playwright.ps1` 
