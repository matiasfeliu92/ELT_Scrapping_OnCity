# 🚀 Retail Competitive Intelligence: ELT Pipeline

Pipeline automatizado de **Web Scraping** y **Data Analytics** para el monitoreo de precios, stock y financiación en los principales retailers de Argentina: **Fravega, Megatone, Musimundo y Naldo**.

Este proyecto implementa una arquitectura **ELT** robusta, utilizando **Airflow** para la orquestación y **dbt** para la transformación siguiendo un modelo de **Arquitectura Medallón**.

---

## 📑 Menú de Navegación
* [🛠 Stack Tecnológico](#-stack-tecnológico)
* [🏗 Arquitectura y Etapas](#-arquitectura-y-etapas)
* [📂 Estructura del Repositorio](#-estructura-del-repositorio)
* [📋 Catálogo de Productos](#-catálogo-de-productos)
* [✅ Calidad de Datos y Logs](#-calidad-de-datos-y-logs)
* [🚀 Instalación y Uso](#-instalación-y-uso)

---

## 🛠 Stack Tecnológico
* **Orquestación:** Apache Airflow
* **Extracción:** Python (Requests, Selenium)
* **Almacenamiento:** PostgreSQL & Docker
* **Transformación:** dbt (Data Build Tool)
* **Catálogo:** Google Sheets (Fuente original)

---

## 🏗 Arquitectura y Etapas
El flujo de datos está diseñado para ser escalable y resiliente, dividiéndose en cuatro etapas clave:

1. **Gestión del Catálogo (dbt seeds):** Los productos se definen originalmente en un Google Sheets y se exportan a `products_scraping/seeds/product_catalog.csv`. Al ejecutar `dbt seed`, se crea la tabla de referencia en PostgreSQL que sirve como origen para el scraper.
2. **Extracción (Scraping):** El motor de scraping lee los links activos de la tabla cargada en el paso anterior y extrae información mediante Selenium y Requests.
3. **Carga (Raw Data):** Los datos obtenidos se insertan en la tabla `scraping_data` (esquema `raw`) en formato **JSONB**, preservando la estructura original de cuotas y metadatos.
4. **Transformación (Medallion Architecture):** dbt procesa los datos en tres capas:
    * **Bronze:** Casting básico y limpieza inicial.
    * **Silver:** Normalización de precios, eliminación de caracteres especiales y deduplicación.
    * **Gold:** Modelos finales listos para BI y análisis comparativo.



---

## 📂 Estructura del Repositorio
```text
ELT_SCRAPPING_ONCITY/
├── products_scraping/      # Proyecto dbt
│   ├── models/             # Transformaciones (Bronze, Silver, Gold)
│   ├── seeds/              # product_catalog.csv (Origen de la verdad)
│   └── dbt_project.yml
├── dags/                   # Orquestación en Apache Airflow
├── data/                   # Almacenamiento local de archivos JSON procesados
├── logs/                   # Registros de ejecución de scripts y dbt
├── src/
│   ├── config/             # Configuración de DB, Logger y selectores
│   ├── scripts/            # extract_data.py, load_data.py, scraping.py
│   └── utils/              # extract_elements.py, get_last_timestamp.py
├── Dockerfile              # Configuración de imagen del entorno
├── docker-compose.yml      # Orquestación de servicios
├── main.py                 # Punto de entrada para el proceso de extracción
└── requirements.txt        # Dependencias de Python
```

---

## 📋 Catálogo de Productos

El catálogo monitorea productos estratégicos con alta sensibilidad de precio:
* **Línea Blanca**: Heladeras (Samsung, Whirlpool, Electrolux) y Lavarropas (Drean, Samsung).
* **Tecnología**: Smart TVs (Samsung, Philips) y Smartphones (Motorola G56/G15, Galaxy A06).
* **Pequeños Electrodomésticos**: Microondas y Depiladoras.

---


## ✅ Calidad de Datos y Logs
* **Logging técnico**: Captura fallos de selectores HTML y errores de navegación en extract_elements.py.
* **Auditoría de Carga**: Registro de registros procesados vs. fallidos en cada ciclo de scraping.
* **dbt Tests**: Validación de integridad, unicidad y valores no nulos en las capas Silver y Gold.

---


## 🚀 Instalación y Uso
### 1. Clonar el repositorio de GitHub
```bash
git clone [https://github.com/matiasfeliu92/ELT_Scrapping_OnCity.git](https://github.com/matiasfeliu92/ELT_Scrapping_OnCity.git)
cd ELT_Scrapping_OnCity

2. **Acceder a la carpeta ELT_Scrapping_OnCity y crear entorno virtual de Python:**
PARA WINDOWS:
pip install virtualenv
virtualenv scraping
scraping/Scripts/activate

PARA LINUX:
python3 -m pip install virtualenv
virtualenv scraping
source scraping/bin/activate

3. **instalar modulos de Python:**
PARA WINDOWS:
pip install -r requirements.txt

PARA LINUX:
python3 -m pip install -r requirements.txt