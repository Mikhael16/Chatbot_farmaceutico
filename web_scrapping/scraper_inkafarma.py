#!/usr/bin/env python3
"""
Scraper prototipo para catálogo de Inkafarma

Características:
- Recorre categorías predefinidas
- Extrae campos mínimos y escribe `inkafarma_catalogue.csv`
- Retries, delay configurable, User-Agent custom
- Límite de extracción configurable (por defecto 800)
- Módulos: fetch_page, parse_category, parse_product_page, write_csv, main

Notas:
- Ajustar selectores en parse_product_page() y parse_category() según inspección del DOM.
- Si el sitio carga contenido dinámicamente vía JS, habilitar `USE_PLAYWRIGHT` o usar Selenium.
"""

import argparse
import csv
import json
import logging
import re
import time
from collections import OrderedDict
from datetime import datetime
from typing import Dict, Optional, Set, Tuple

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Playwright imports (opcionales)
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# --------------------- Configurables ---------------------
BASE_URL = "https://inkafarma.pe"
START_CATEGORY_URLS = [
    f"{BASE_URL}/categoria/farmacia",
    f"{BASE_URL}/categoria/cuidado-personal",
    f"{BASE_URL}/categoria/bienestar",
    # Añadir otras categorías importantes si se desea
]
OUTPUT_CSV = "inkafarma_catalogue.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; InkafarmaScraper/1.0; +https://yourcompany.com/bot)"
}
REQUEST_DELAY = 1.5  # segundos entre peticiones para respetar servidores
MAX_PRODUCTS = 800
STOP_ON_LIMIT = True  # si True detiene cuando alcanza MAX_PRODUCTS
REQUEST_TIMEOUT = 15  # segundos
MAX_RETRIES = 3

CSV_FIELDS = [
    "sku",
    "nombre_comercial",
    "dci",
    "forma",
    "concentracion",
    "presentacion",
    "condicion_venta",
    "registro_sanitario",
    "precio_lista",
    "precio_promocion",
    "categoria",
    "subcategoria",
    "stock_disponible",
    "url_producto",
    "fecha_extraccion",
]

# --------------------- Helpers ---------------------

def make_session(headers: Dict[str, str] = None) -> requests.Session:
    session = requests.Session()
    hdrs = headers.copy() if headers else {}
    hdrs.setdefault("User-Agent", HEADERS["User-Agent"]) if headers is None else None
    session.headers.update(hdrs)
    retries = Retry(total=MAX_RETRIES, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))
    return session


def parse_price(text: str) -> Tuple[Optional[float], str]:
    """Intentar normalizar un texto de precio a float (en moneda local). Devuelve (float_or_None, raw_str).

    Ejemplos de entradas: 'S/ 12.50', '12,50', 'S/12', '12.000,50' etc.
    """
    if not text:
        return None, ""
    raw = text.strip()
    # Remover etiquetas no numéricas salvo . y , y -
    cleaned = re.sub(r"[^0-9,\.\-]", "", raw)
    # Si hay ambos '.' y ',' asumir que '.' es thousand separator y ',' es decimal
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace('.', '')
        cleaned = cleaned.replace(',', '.')
    else:
        # Si solo tiene comas, transformar coma->dot
        if "," in cleaned and "." not in cleaned:
            cleaned = cleaned.replace(',', '.')
    try:
        value = float(cleaned)
    except Exception:
        value = None
    return value, raw


def safe_get_text(el) -> str:
    return el.get_text(strip=True) if el else ""


def normalize_record(rec: Dict[str, any]) -> Dict[str, any]:
    """Garantiza todas las claves CSV y normaliza precios y fecha.
    Devuelve un OrderedDict con el mismo orden que CSV_FIELDS.
    """
    out = OrderedDict()
    for k in CSV_FIELDS:
        out[k] = rec.get(k, "") if rec.get(k, None) is not None else ""

    # Normalizar precios
    pl_val, pl_raw = parse_price(str(out.get("precio_lista", "")))
    pp_val, pp_raw = parse_price(str(out.get("precio_promocion", "")))
    out["precio_lista"] = pl_val if pl_val is not None else (pl_raw or "")
    out["precio_promocion"] = pp_val if pp_val is not None else (pp_raw or "")

    # Fecha en ISO
    if not out.get("fecha_extraccion"):
        out["fecha_extraccion"] = datetime.utcnow().isoformat()

    return out


# --------------------- Fetching ---------------------

def fetch_page(session: requests.Session, url: str) -> str:
    """Pide una URL con sesión, maneja errores básicos y devuelve HTML.
    Lanza excepción si falla tras reintentos.
    """
    logging.info(f"Solicitando URL: {url}")
    resp = session.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


def fetch_page_playwright(url: str, wait_selector: str = "a.link[href*='/producto/']", timeout: int = 60000) -> Optional[str]:
    """
    Obtiene HTML renderizado usando Playwright (espera a que se cargue JavaScript).
    
    Args:
        url: URL a cargar
        wait_selector: Selector CSS para esperar antes de extraer HTML
        timeout: Tiempo máximo de espera en milisegundos
    
    Returns:
        HTML renderizado o None si falla
    """
    if not PLAYWRIGHT_AVAILABLE:
        logging.error("Playwright no está instalado. Instala con: pip install playwright && playwright install chromium")
        return None
    
    try:
        logging.info(f"Solicitando URL con Playwright: {url}")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Configurar timeout más largo
            page.set_default_timeout(timeout)
            
            # Navegar sin esperar networkidle (más rápido y confiable)
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                logging.info(f"Página cargada (DOM ready), esperando productos...")
            except Exception as e:
                logging.error(f"Error al navegar a {url}: {e}")
                browser.close()
                return None
            
            # Esperar a que aparezcan los productos (más tiempo)
            try:
                page.wait_for_selector(wait_selector, timeout=20000, state="visible")
                logging.info(f"✓ Productos encontrados, extrayendo HTML")
                # Esperar un poco más para asegurar que todo se cargue
                time.sleep(2)
            except PlaywrightTimeout:
                logging.warning(f"No se encontró selector '{wait_selector}' en 20s, extrayendo HTML de todas formas")
            
            html = page.content()
            browser.close()
            return html
            
    except Exception as e:
        logging.error(f"Error con Playwright en {url}: {e}")
        return None


# --------------------- Parsing ---------------------

def extract_product_links_from_category_soup(soup: BeautifulSoup) -> list:
    """Intentar extraer enlaces de producto con múltiples selectores de respaldo."""
    links = set()
    # Selectores ajustados para Inkafarma (sitio Angular)
    selectors = [
        "a.link[href*='/producto/']",  # Selector principal de Inkafarma
        "fp-link a[href*='/producto/']",  # Componente Angular
        "div.card.product a[href*='/producto/']",  # Card de producto
        "a[href*='/producto/']",  # Fallback general
    ]
    for sel in selectors:
        for a in soup.select(sel):
            href = a.get("href")
            if href and '/producto/' in href:
                full = href if href.startswith("http") else BASE_URL + href
                links.add(full)
    return list(links)


def find_next_page_url(soup: BeautifulSoup) -> Optional[str]:
    # Buscar enlaces de paginación
    candidates = ["a.next", "a.next-page", "a[rel='next']", "a.pagination__next"]
    for sel in candidates:
        el = soup.select_one(sel)
        if el and el.get("href"):
            href = el["href"]
            return href if href.startswith("http") else BASE_URL + href
    # Try look for link text 'Siguiente' or '»'
    for a in soup.find_all("a"):
        if a.string and a.string.strip().lower() in ("siguiente", "siguientes", "»", ">"):
            href = a.get("href")
            if href:
                return href if href.startswith("http") else BASE_URL + href
    return None


def parse_product_page(html: str, url: str, categoria: str, subcategoria: str) -> Dict[str, any]:
    """Extrae los campos del HTML de la página de producto. Los selectores son heurísticos y deben ajustarse."""
    soup = BeautifulSoup(html, "html.parser")

    # SKU - extraer del section.product-detail-container (el producto principal, no complementarios)
    sku = ""
    product_container = soup.select_one("section.product-detail-container")
    
    if product_container and product_container.get("data-product"):
        try:
            product_data = json.loads(product_container.get("data-product", "{}"))
            sku = str(product_data.get("id", ""))
            
            # Extraer todos los datos del JSON principal
            nombre = product_data.get("name", "")
            
            # DCI/Composición
            dci = product_data.get("compositionContent", "")
            
            # Condición de venta
            condicion = product_data.get("prescription", "")
            if condicion:
                condicion_map = {
                    "RM": "Receta Médica",
                    "VL": "Venta Libre",
                    "0": "Venta Libre"
                }
                condicion = condicion_map.get(str(condicion), condicion)
            
            # Presentación de la presentación por defecto
            presentations = product_data.get("presentations", [])
            presentacion = ""
            precio_lista = ""
            precio_prom = ""
            stock = ""
            
            if presentations:
                # Buscar presentación por defecto
                default_pres_id = product_data.get("defaultPresentation", None)
                default_pres = None
                
                for pres in presentations:
                    if pres.get("id") == default_pres_id:
                        default_pres = pres
                        break
                
                # Si no encontramos la por defecto, usar la primera
                if not default_pres and presentations:
                    default_pres = presentations[0]
                
                if default_pres:
                    presentacion = default_pres.get("description", "")
                    
                    # Precios: intentar múltiples campos
                    # 1. price (precio actual)
                    precio = default_pres.get("price", 0)
                    
                    # 2. offerPrice (precio de oferta)
                    if not precio:
                        precio = default_pres.get("offerPrice", 0)
                    
                    # 3. regularPrice (precio regular)
                    precio_regular = default_pres.get("regularPrice", 0)
                    
                    # Asignar precios
                    if precio and precio > 0:
                        precio_prom = str(precio)
                    elif precio_regular and precio_regular > 0:
                        precio_prom = str(precio_regular)
                    
                    # Precio lista (si hay descuento)
                    old_price = default_pres.get("oldPrice", 0)
                    if old_price and old_price > 0:
                        precio_lista = str(old_price)
                    elif precio_regular and precio_regular > 0 and precio and precio > 0 and precio < precio_regular:
                        # Si regularPrice es mayor que price, regularPrice es el precio lista
                        precio_lista = str(precio_regular)
                        precio_prom = str(precio)
                    
                    # Stock
                    stock_val = default_pres.get("stock", 0)
                    if not stock_val:
                        stock_val = default_pres.get("stockRet", 0)
                    
                    if stock_val and stock_val > 0:
                        stock = "Disponible"
                    else:
                        stock = "Agotado"
            
            # Registro sanitario y forma/concentración - buscar en HTML
            registro = ""
            forma = ""
            concentracion = ""
            
            # Si no tenemos precios del JSON, buscar en HTML
            if not precio_prom:
                # Buscar precio en fp-product-detail-price
                price_container = soup.select_one("fp-product-detail-price")
                if price_container:
                    # Buscar precio regular o precio de oferta
                    price_text = price_container.get_text(strip=True)
                    # Extraer números del texto "S/ 1.50" o "Precio Regular S/ 1.50"
                    import re
                    price_match = re.search(r'S/\s*([0-9,.]+)', price_text)
                    if price_match:
                        precio_prom = price_match.group(1).replace(',', '.')
            
            # Construir registro
            rec = {
                "sku": sku,
                "nombre_comercial": nombre,
                "dci": dci,
                "forma": forma,
                "concentracion": concentracion,
                "presentacion": presentacion,
                "condicion_venta": condicion,
                "registro_sanitario": registro,
                "precio_lista": precio_lista,
                "precio_promocion": precio_prom,
                "categoria": categoria,
                "subcategoria": subcategoria,
                "stock_disponible": stock,
                "url_producto": url,
                "fecha_extraccion": datetime.now().isoformat(),
            }
            return rec
            
        except Exception as e:
            logging.error(f"Error parseando JSON de producto: {e}")
    
    # Fallback si no se pudo parsear JSON
    return {
        "sku": "",
        "nombre_comercial": "",
        "dci": "",
        "forma": "",
        "concentracion": "",
        "presentacion": "",
        "condicion_venta": "",
        "registro_sanitario": "",
        "precio_lista": "",
        "precio_promocion": "",
        "categoria": categoria,
        "subcategoria": subcategoria,
        "stock_disponible": "",
        "url_producto": url,
        "fecha_extraccion": datetime.now().isoformat(),
    }


def parse_category(session: requests.Session, url: str, categoria: str, subcategoria: str, writer: csv.DictWriter, visited: Set[str], counter: Dict[str, int], max_products: int, use_playwright: bool = False) -> None:
    """Recorre una categoría: extrae enlaces de producto y los procesa.
    Usa paginación si existe. Mantiene visited para evitar duplicados.
    
    Args:
        use_playwright: Si True, usa Playwright para renderizar JavaScript
    """
    try:
        if use_playwright:
            html = fetch_page_playwright(url)
            if html is None:
                logging.error(f"No se pudo obtener HTML con Playwright para {url}")
                return
        else:
            html = fetch_page(session, url)
    except Exception as e:
        logging.error(f"Error al solicitar categoría {url}: {e}")
        return

    soup = BeautifulSoup(html, "html.parser")
    product_links = extract_product_links_from_category_soup(soup)
    logging.info(f"{len(product_links)} enlaces de producto encontrados en categoría {url}")

    for link in product_links:
        if STOP_ON_LIMIT and counter["count"] >= max_products:
            logging.info(f"Objetivo alcanzado: {counter['count']} productos — deteniendo extracción.")
            return
        if link in visited:
            continue
        visited.add(link)
        try:
            if use_playwright:
                prod_html = fetch_page_playwright(link)
                if prod_html is None:
                    continue
            else:
                prod_html = fetch_page(session, link)
            
            rec = parse_product_page(prod_html, link, categoria, subcategoria)
            rec_norm = normalize_record(rec)
            writer.writerow(rec_norm)
            counter["count"] += 1
            logging.info(f"[{counter['count']}] Extraído: {rec_norm.get('sku') or 'SKU?' } - {rec_norm.get('nombre_comercial','(sin nombre)')}")
        except Exception as e:
            logging.error(f"Error extrayendo producto {link}: {e}")
        time.sleep(REQUEST_DELAY)

    # Paginación: continuar si no alcanzamos el límite
    if STOP_ON_LIMIT and counter["count"] >= max_products:
        return
    next_url = find_next_page_url(soup)
    if next_url:
        logging.info(f"Paginación: siguiente página {next_url}")
        # llamar recursivamente o iterativamente
        parse_category(session, next_url, categoria, subcategoria, writer, visited, counter, max_products, use_playwright)


def main(argv=None):
    global REQUEST_DELAY, MAX_PRODUCTS, STOP_ON_LIMIT
    
    parser = argparse.ArgumentParser(description="Scraper prototipo para Inkafarma - genera inkafarma_catalogue.csv")
    parser.add_argument("--output", default=OUTPUT_CSV, help="Archivo CSV de salida")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY, help="Segundos entre peticiones")
    parser.add_argument("--max", type=int, default=MAX_PRODUCTS, help="Numero objetivo de productos (0 = completo)")
    parser.add_argument("--stop-on-limit", action="store_true", help="Detener cuando se alcanza --max")
    parser.add_argument("--categories", nargs="*", help="Lista de URLs de categoría para procesar (sobrescribe START_CATEGORY_URLS)")
    parser.add_argument("--use-playwright", action="store_true", help="Usar Playwright para renderizar JavaScript (requerido para sitios Angular)")
    args = parser.parse_args(argv)

    # Actualizar configurables runtime
    REQUEST_DELAY = args.delay
    MAX_PRODUCTS = args.max if args.max and args.max > 0 else MAX_PRODUCTS
    STOP_ON_LIMIT = args.stop_on_limit
    use_playwright = args.use_playwright

    # Verificar disponibilidad de Playwright
    if use_playwright and not PLAYWRIGHT_AVAILABLE:
        logging.error("ERROR: --use-playwright especificado pero Playwright no está instalado.")
        logging.error("Instala con: pip install playwright")
        logging.error("Luego ejecuta: playwright install chromium")
        return

    category_urls = args.categories if args.categories else START_CATEGORY_URLS

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    if use_playwright:
        logging.info("Iniciando scraper Inkafarma con Playwright (renderizado JavaScript)")
    else:
        logging.info("Iniciando scraper Inkafarma (prototipo)")

    session = make_session()

    visited: Set[str] = set()
    counter = {"count": 0}

    with open(args.output, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for cat_url in category_urls:
            if STOP_ON_LIMIT and counter["count"] >= MAX_PRODUCTS:
                break
            categoria = cat_url.rstrip("/").split("/")[-1]
            subcategoria = ""
            try:
                parse_category(session, cat_url, categoria, subcategoria, writer, visited, counter, MAX_PRODUCTS, use_playwright)
            except Exception as e:
                logging.error(f"Error procesando categoría {cat_url}: {e}")

    logging.info(f"Extracción finalizada. Productos extraídos: {counter['count']}")
    logging.info(f"Archivo de salida: {args.output}")


if __name__ == "__main__":
    main()
