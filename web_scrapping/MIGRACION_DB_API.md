#  Notas de Migración: PostgreSQL + FastAPI

Este documento contiene notas técnicas para la futura migración del catálogo extraído hacia PostgreSQL y la implementación de una API REST con FastAPI.

##  Modelo de Datos Propuesto

### Tabla: `productos`

```sql
CREATE TABLE productos (
    -- Identificadores
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    
    -- Información básica
    nombre_comercial VARCHAR(500) NOT NULL,
    dci VARCHAR(500),  -- Denominación Común Internacional
    
    -- Características farmacéuticas
    forma VARCHAR(200),  -- tabletas, jarabe, crema, etc.
    concentracion VARCHAR(200),
    presentacion VARCHAR(500),
    
    -- Regulatorio
    condicion_venta VARCHAR(100),  -- OTC, receta, receta retenida
    registro_sanitario VARCHAR(200),
    
    -- Comercial
    precio_lista DECIMAL(10, 2),
    precio_promocion DECIMAL(10, 2),
    stock_disponible VARCHAR(50),
    
    -- Clasificación
    categoria VARCHAR(200),
    subcategoria VARCHAR(200),
    
    -- Metadata
    url_producto TEXT,
    fecha_extraccion TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    
    -- Índices
    CONSTRAINT chk_precio_lista CHECK (precio_lista >= 0),
    CONSTRAINT chk_precio_promocion CHECK (precio_promocion >= 0)
);

-- Índices para búsquedas frecuentes
CREATE INDEX idx_productos_sku ON productos(sku);
CREATE INDEX idx_productos_nombre ON productos USING gin(to_tsvector('spanish', nombre_comercial));
CREATE INDEX idx_productos_dci ON productos USING gin(to_tsvector('spanish', dci));
CREATE INDEX idx_productos_categoria ON productos(categoria);
CREATE INDEX idx_productos_activo ON productos(activo);
```

### Tablas Relacionadas (Futuras)

```sql
-- Tabla de categorías
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) UNIQUE NOT NULL,
    descripcion TEXT,
    parent_id INTEGER REFERENCES categorias(id),
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla de historial de precios
CREATE TABLE historial_precios (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER REFERENCES productos(id),
    precio_lista DECIMAL(10, 2),
    precio_promocion DECIMAL(10, 2),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de stock por tienda (si aplica)
CREATE TABLE stock_tienda (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER REFERENCES productos(id),
    tienda_id INTEGER,
    cantidad INTEGER,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

##  Script de Carga CSV → PostgreSQL

```python
# load_to_db.py
import csv
import psycopg2
from datetime import datetime

def load_csv_to_postgres(csv_path, db_config):
    """
    Carga el CSV generado por el scraper a PostgreSQL
    """
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            cursor.execute("""
                INSERT INTO productos (
                    sku, nombre_comercial, dci, forma, concentracion,
                    presentacion, condicion_venta, registro_sanitario,
                    precio_lista, precio_promocion, categoria, subcategoria,
                    stock_disponible, url_producto, fecha_extraccion
                ) VALUES (
                    %(sku)s, %(nombre_comercial)s, %(dci)s, %(forma)s, 
                    %(concentracion)s, %(presentacion)s, %(condicion_venta)s,
                    %(registro_sanitario)s, %(precio_lista)s, %(precio_promocion)s,
                    %(categoria)s, %(subcategoria)s, %(stock_disponible)s,
                    %(url_producto)s, %(fecha_extraccion)s
                )
                ON CONFLICT (sku) DO UPDATE SET
                    nombre_comercial = EXCLUDED.nombre_comercial,
                    precio_lista = EXCLUDED.precio_lista,
                    precio_promocion = EXCLUDED.precio_promocion,
                    stock_disponible = EXCLUDED.stock_disponible,
                    fecha_actualizacion = CURRENT_TIMESTAMP
            """, row)
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'database': 'inkafarma_db',
        'user': 'postgres',
        'password': 'your_password'
    }
    load_csv_to_postgres('inkafarma_catalogue.csv', db_config)
```

##  API REST con FastAPI

### Modelo Pydantic

```python
# models.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductoBase(BaseModel):
    sku: str
    nombre_comercial: str
    dci: Optional[str]
    forma: Optional[str]
    concentracion: Optional[str]
    presentacion: Optional[str]
    condicion_venta: Optional[str]
    registro_sanitario: Optional[str]
    precio_lista: Optional[float]
    precio_promocion: Optional[float]
    categoria: Optional[str]
    subcategoria: Optional[str]
    stock_disponible: Optional[str]
    url_producto: Optional[str]

class Producto(ProductoBase):
    id: int
    fecha_extraccion: Optional[datetime]
    fecha_actualizacion: datetime
    activo: bool
    
    class Config:
        orm_mode = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    precio_lista: Optional[float]
    precio_promocion: Optional[float]
    stock_disponible: Optional[str]
```

### Endpoints Principales

```python
# main.py
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import databases
import sqlalchemy

app = FastAPI(title="API Catálogo Inkafarma")

# Configuración de base de datos
DATABASE_URL = "postgresql://user:password@localhost/inkafarma_db"
database = databases.Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Endpoints

@app.get("/productos", response_model=List[Producto])
async def listar_productos(
    skip: int = 0,
    limit: int = 100,
    categoria: Optional[str] = None,
    busqueda: Optional[str] = None
):
    """Listar productos con filtros y paginación"""
    query = "SELECT * FROM productos WHERE activo = true"
    
    if categoria:
        query += f" AND categoria = '{categoria}'"
    
    if busqueda:
        query += f" AND (nombre_comercial ILIKE '%{busqueda}%' OR dci ILIKE '%{busqueda}%')"
    
    query += f" OFFSET {skip} LIMIT {limit}"
    
    return await database.fetch_all(query)

@app.get("/productos/{sku}", response_model=Producto)
async def obtener_producto(sku: str):
    """Obtener producto por SKU"""
    query = "SELECT * FROM productos WHERE sku = :sku AND activo = true"
    producto = await database.fetch_one(query, values={"sku": sku})
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto

@app.get("/productos/categoria/{categoria}", response_model=List[Producto])
async def productos_por_categoria(categoria: str, limit: int = 50):
    """Obtener productos de una categoría"""
    query = """
        SELECT * FROM productos 
        WHERE categoria = :categoria AND activo = true 
        LIMIT :limit
    """
    return await database.fetch_all(
        query, 
        values={"categoria": categoria, "limit": limit}
    )

@app.get("/buscar", response_model=List[Producto])
async def buscar_productos(
    q: str = Query(..., min_length=3),
    limit: int = 20
):
    """Búsqueda full-text en nombre y DCI"""
    query = """
        SELECT *, 
               ts_rank(to_tsvector('spanish', nombre_comercial || ' ' || COALESCE(dci, '')), 
                       plainto_tsquery('spanish', :busqueda)) AS rank
        FROM productos
        WHERE to_tsvector('spanish', nombre_comercial || ' ' || COALESCE(dci, '')) 
              @@ plainto_tsquery('spanish', :busqueda)
              AND activo = true
        ORDER BY rank DESC
        LIMIT :limit
    """
    return await database.fetch_all(
        query,
        values={"busqueda": q, "limit": limit}
    )

@app.get("/stats")
async def estadisticas():
    """Estadísticas del catálogo"""
    query_total = "SELECT COUNT(*) as total FROM productos WHERE activo = true"
    query_categorias = "SELECT categoria, COUNT(*) as count FROM productos WHERE activo = true GROUP BY categoria"
    
    total = await database.fetch_one(query_total)
    categorias = await database.fetch_all(query_categorias)
    
    return {
        "total_productos": total["total"],
        "por_categoria": categorias
    }
```

##  Consideraciones de Seguridad

1. **Autenticación/Autorización**
   - Implementar OAuth2 o JWT para endpoints privados
   - Rate limiting para prevenir abuso
   - CORS configurado según frontend

2. **Validación de Datos**
   - Validar SKUs únicos
   - Sanitizar inputs de búsqueda
   - Prevenir SQL injection (usar parametrized queries)

3. **Cumplimiento Regulatorio**
   - Logs de acceso a datos sensibles
   - Encriptación de datos en tránsito (HTTPS)
   - Backup regular de base de datos

##  Integración con Chatbot

```python
# chatbot_integration.py
from langchain.tools import Tool
from typing import List

class InkafarmaProductSearch:
    """Herramienta para que el chatbot consulte productos"""
    
    def __init__(self, api_client):
        self.api = api_client
    
    def search_products(self, query: str) -> List[dict]:
        """Buscar productos para recomendación"""
        response = self.api.get(f"/buscar?q={query}&limit=5")
        return response.json()
    
    def get_product_details(self, sku: str) -> dict:
        """Obtener detalles de un producto"""
        response = self.api.get(f"/productos/{sku}")
        return response.json()

# Uso con LangChain
product_search_tool = Tool(
    name="BuscarProducto",
    func=InkafarmaProductSearch().search_products,
    description="Busca productos farmacéuticos en el catálogo de Inkafarma"
)
```

##  Pipeline de Actualización

```python
# update_pipeline.py
"""
Pipeline para actualizar catálogo periódicamente
"""

def update_catalog_pipeline():
    """
    1. Ejecutar scraper
    2. Validar CSV
    3. Comparar con DB (detectar cambios)
    4. Actualizar precios y stock
    5. Registrar en historial
    6. Notificar cambios significativos
    """
    pass

# Programar con cron o Celery
from celery import Celery
from celery.schedules import crontab

app = Celery('inkafarma_tasks')

@app.task
def scheduled_catalog_update():
    """Actualización diaria del catálogo"""
    update_catalog_pipeline()

# Beat schedule
app.conf.beat_schedule = {
    'update-catalog-daily': {
        'task': 'scheduled_catalog_update',
        'schedule': crontab(hour=2, minute=0),  # 2 AM diario
    },
}
```

##  Próximos Pasos Técnicos

1.  CSV generado por scraper
2.  Setup PostgreSQL local
3.  Crear schema y tablas
4.  Implementar script de carga
5.  Desarrollar API básica con FastAPI
6.  Agregar búsqueda full-text
7.  Integrar con chatbot (LangChain)
8.  Deploy en producción

##  Dependencias Adicionales

```txt
# requirements_backend.txt
fastapi==0.104.0
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
databases==0.8.0
pydantic==2.5.0
python-dotenv==1.0.0

# Para chatbot
langchain==0.1.0
openai==1.3.0
```

---

**Autor**: Equipo Innovación Digital - Inkafarma  
**Fecha**: Octubre 2025  
**Versión**: 1.0 (Prototipo)
