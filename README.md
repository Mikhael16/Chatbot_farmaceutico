# Chatbot Farmacéutico - Inkafarma

Proyecto de Innovación Digital: Asistente de farmacia virtual con IA para recomendaciones de productos OTC.

**Contexto**: Chatbot para realizar un diagnóstico inicial con productos de Inkafarma, desarrollado como parte del curso Modelo del Sistema Viable (VSM).

##  Estructura del Proyecto

```
inkafarma/
├── web_scrapping/                    #  Módulo Web Scraping
│   ├── scraper_inkafarma.py         #  Script principal del scraper
│   ├── requirements.txt              #  Dependencias Python
│   ├── setup.ps1                     #  Setup automático
│   ├── run_scraper.ps1               #   Helper de ejecución
│   ├── .gitignore                    #  Archivos a ignorar
│   ├── __init__.py                   #  Package marker
│   ├── tests/                        #  Tests unitarios
│   │   ├── __init__.py
│   │   └── test_normalize.py
│   ├── README.md                     #  Documentación completa
│   ├── GUIA_RAPIDA.md               #  Comandos rápidos
│   ├── EJEMPLOS_USO.md              #  Ejemplos prácticos
│   ├── MIGRACION_DB_API.md          #   Notas técnicas backend
│   └── RESUMEN_EJECUTIVO.md         #  Resumen del proyecto
├── README.md                         #  Este archivo
└── (otros módulos próximamente)
```

##  Inicio Rápido

### 1. Web Scraping (Extracción de Catálogo)

El módulo `web_scrapping` permite extraer productos del sitio de Inkafarma.

**Setup automático:**
```powershell
.\web_scrapping\setup.ps1
```

**Ejecutar scraper:**
```powershell
# Prueba rápida (10 productos)
.\web_scrapping\run_scraper.ps1 test

# Prueba piloto (50 productos)
.\web_scrapping\run_scraper.ps1 pilot

# Extracción completa (800 productos)
.\web_scrapping\run_scraper.ps1 full
```

Ver documentación completa en: [`web_scrapping/README.md`](web_scrapping/README.md)

##  Componentes del Sistema

###  Web Scraping
- **Estado**: Implementado (prototipo)
- **Tecnología**: Python, requests, BeautifulSoup
- **Output**: CSV con 15 campos (SKU, nombre, DCI, precios, stock, etc.)
- **Objetivo**: 800 productos mínimo

###  Backend (Próximamente)
- **Tecnología**: Python + FastAPI
- **Base de datos**: PostgreSQL
- **Features**: API REST, gestión de stock, integración con chatbot

###  Chatbot IA (Próximamente)
- **Tecnología**: LangChain / OpenAI
- **Features**: Recomendaciones OTC, consulta de precios, disponibilidad

##  Objetivos del Proyecto

1.  Extracción automatizada de catálogo (~800 productos)
2.  Backend con API REST (FastAPI + PostgreSQL)
3.  Chatbot conversacional con IA
4.  Integración con sistema de stock en tiempo real
5.  Cumplimiento regulatorio (DIGEMID, NTS 162)

##  Tecnologías

- **Python 3.8+**
- **BeautifulSoup4** - Web scraping
- **Requests** - HTTP client
- **FastAPI** - Backend API (próximamente)
- **PostgreSQL** - Base de datos (próximamente)
- **LangChain** - Framework IA (próximamente)

##  Próximos Pasos

1. Ejecutar y validar scraper con 50 productos
2. Ajustar selectores según DOM real de inkafarma.pe
3. Ejecutar extracción completa (800 productos)
4. Diseñar modelo de datos PostgreSQL
5. Implementar API REST con FastAPI
6. Desarrollar lógica del chatbot IA

##  Contacto

**Equipo**: Innovación Digital - Inkafarma (Intercorp)  
**Proyecto**: Chatbot IA Farmacéutico (S1.2 Plataforma Digital - VSM)

---

*Última actualización: Octubre 2025*
