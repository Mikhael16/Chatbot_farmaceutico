# Web Scraping - Inkafarma (Prototipo)

Este directorio contiene el prototipo del scraper para el catálogo de Inkafarma, parte del proyecto **Chatbot IA Farmacéutico** de la unidad de Innovación Digital.

## Estructura del Proyecto

```
web_scrapping/
├── scraper_inkafarma.py    # Script principal del scraper
├── requirements.txt         # Dependencias Python
├── setup.ps1               # Script de instalación automática
├── run_scraper.ps1         # Script helper para ejecutar con presets
├── tests/                  # Tests unitarios
│   ├── __init__.py
│   └── test_normalize.py
├── .gitignore
└── README.md               # Este archivo
```

## Instalación Rápida

### Opción 1: Setup Automático (Recomendado)

Desde la raíz del proyecto en PowerShell:

```powershell
.\web_scrapping\setup.ps1
```

Este script:
- ✓ Verifica Python 3.8+
- ✓ Crea entorno virtual `.venv`
- ✓ Instala todas las dependencias
- ✓ Verifica la instalación

### Opción 2: Setup Manual

```powershell
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 3. Actualizar pip
python -m pip install --upgrade pip

# 4. Instalar dependencias
pip install -r .\web_scrapping\requirements.txt
```

## Uso del Scraper

### Método 1: Scripts Helper (Más Fácil)

```powershell
# Prueba rápida (10 productos)
.\web_scrapping\run_scraper.ps1 test

# Prueba piloto (50 productos)
.\web_scrapping\run_scraper.ps1 pilot

# Extracción completa (800 productos)
.\web_scrapping\run_scraper.ps1 full
```

### Método 2: Ejecución Directa

```powershell
# Activar entorno virtual primero
.\.venv\Scripts\Activate.ps1

# Prueba con 10 productos
python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_test.csv --max 10 --stop-on-limit --delay 0.5

# Prueba piloto con 50 productos
python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_pilot.csv --max 50 --stop-on-limit --delay 1.5

# Extracción objetivo de 800 productos
python .\web_scrapping\scraper_inkafarma.py --output .\inkafarma_catalogue.csv --max 800 --stop-on-limit --delay 1.5
```

## Parámetros de Configuración

| Parámetro | Descripción | Valor por defecto |
|-----------|-------------|-------------------|
| `--output` | Archivo CSV de salida | `inkafarma_catalogue.csv` |
| `--max` | Número máximo de productos | `800` |
| `--stop-on-limit` | Detener al alcanzar límite | `False` |
| `--delay` | Segundos entre peticiones | `1.5` |
| `--categories` | URLs de categorías custom | Ver `START_CATEGORY_URLS` |

## Campos Extraídos (CSV)

El scraper extrae los siguientes campos para cada producto:

| Campo | Descripción |
|-------|-------------|
| `sku` | Código único del producto |
| `nombre_comercial` | Nombre del producto |
| `dci` | Denominación Común Internacional |
| `forma` | Forma farmacéutica (tabletas, jarabe, etc.) |
| `concentracion` | Concentración del principio activo |
| `presentacion` | Presentación comercial |
| `condicion_venta` | OTC, receta médica, etc. |
| `registro_sanitario` | Número de registro DIGEMID |
| `precio_lista` | Precio regular |
| `precio_promocion` | Precio en oferta (si aplica) |
| `categoria` | Categoría principal |
| `subcategoria` | Subcategoría |
| `stock_disponible` | Estado de disponibilidad |
| `url_producto` | URL del producto |
| `fecha_extraccion` | Timestamp ISO 8601 |

## Ejecutar Tests

```powershell
# Instalar pytest si no lo tienes
pip install pytest

# Ejecutar tests
pytest .\web_scrapping\tests -v

# Con coverage
pip install pytest-cov
pytest .\web_scrapping\tests --cov=web_scrapping --cov-report=html
```

## Notas Importantes

### Ajuste de Selectores CSS
**IMPORTANTE**: Los selectores CSS en el script son heurísticos y **deben ajustarse** según el DOM real de inkafarma.pe:

1. Abre el navegador y navega a https://inkafarma.pe
2. Usa DevTools (F12) para inspeccionar:
   - Páginas de categoría (enlaces de productos)
   - Páginas de producto (SKU, precio, specs)
   - Enlaces de paginación
3. Ajusta los selectores en:
   - `extract_product_links_from_category_soup()` - línea ~155
   - `parse_product_page()` - línea ~185
   - `find_next_page_url()` - línea ~173

### Contenido Dinámico (JavaScript)
Si el sitio carga productos vía AJAX/JavaScript:
- El scraper actual usa `requests` + `BeautifulSoup` (HTML estático)
- Para contenido JS, se necesita **Playwright** o **Selenium**
- Contacta al equipo para habilitar soporte JS

### Cumplimiento y Buenas Prácticas
✓ User-Agent customizado incluido  
✓ Delay configurable entre peticiones  
✓ Manejo de errores y retries  
✓ Logging detallado  
✓ Prevención de duplicados  

**Uso autorizado**: Este scraper es para uso interno de Inkafarma bajo el proyecto corporativo del chatbot IA.

## Workflow Recomendado

1. **Primera ejecución** (prueba con 10 productos):
   ```powershell
   .\web_scrapping\run_scraper.ps1 test
   ```
   → Verifica que los selectores funcionen

2. **Ajustar selectores** si es necesario:
   - Edita `scraper_inkafarma.py`
   - Prueba de nuevo con `test`

3. **Prueba piloto** (50 productos):
   ```powershell
   .\web_scrapping\run_scraper.ps1 pilot
   ```
   → Valida calidad de datos

4. **Extracción completa** (800 productos):
   ```powershell
   .\web_scrapping\run_scraper.ps1 full
   ```
   → Genera `inkafarma_catalogue.csv`

5. **Validación**:
   - Abre el CSV en Excel/LibreOffice
   - Verifica campos regulatorios: `registro_sanitario`, `condicion_venta`
   - Valida precios numéricos

6. **Carga al backend**:
   - Prepara ETL para PostgreSQL
   - Integra con FastAPI

## Próximos Pasos (Roadmap)

- [ ] Ajustar selectores según DOM real de Inkafarma
- [ ] Validar extracción piloto (50 productos)
- [ ] Ejecutar extracción objetivo (800 productos)
- [ ] Implementar soporte Playwright (si se requiere JS)
- [ ] Crear modelo SQLAlchemy para PostgreSQL
- [ ] Desarrollar endpoints FastAPI para consulta
- [ ] Integrar con sistema VSM (S1.2 Plataforma Digital)

## Troubleshooting

**Error: "No module named 'requests'"**
→ Activa el entorno virtual: `.\.venv\Scripts\Activate.ps1`

**Error: "No se encontraron productos"**
→ Ajusta selectores en `extract_product_links_from_category_soup()`

**CSV vacío o con pocos campos**
→ Ajusta selectores en `parse_product_page()`

**Error 403/429**
→ Aumenta `--delay` a 2-3 segundos

## Contacto

Para dudas o soporte técnico, contacta al equipo de Innovación Digital - Inkafarma.
