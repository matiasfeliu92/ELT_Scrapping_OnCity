# 🚀 Retail Competitive Intelligence: ELT Pipeline

Pipeline automatizado de **Web Scraping** y **Data Analytics** para el monitoreo de precios, stock y financiación en los principales retailers de Argentina: **Fravega, Megatone, Musimundo y Naldo**.

Este proyecto implementa una arquitectura **ELT** robusta, utilizando **Airflow** para la orquestación y **dbt** para la transformación siguiendo un modelo de **Arquitectura Medallón**.

---

## 🛠 Stack Tecnológico
* **Orquestación:** Apache Airflow
* **Extracción:** Python (Requests, Selenium)
* **Almacenamiento:** PostgreSQL & Docker
* **Transformación:** dbt (Data Build Tool)
* **Catálogo:** Google Sheets (Fuente original)

---

## 🏗 Etapas del Proyecto

El flujo de datos sigue un ciclo de cuatro etapas bien definidas:

### 1. Gestión del Catálogo (Seeds)
El catálogo de productos se gestiona en un **Google Sheets**. Este se exporta como `product_catalog.csv` hacia la carpeta `seeds/` del proyecto dbt.
* **Comando:** `dbt seed`
* **Resultado:** Creación de la tabla de referencia en PostgreSQL con los links activos para scrapear.

### 2. Extracción (Scraping)
Utilizando **Selenium** y **Requests**, el sistema recorre cada uno de los links presentes en la tabla `product_catalog` cargada en la etapa anterior.
* **Lógica:** Se prioriza la velocidad y el manejo de errores (logging) para asegurar que un link caído no detenga el pipeline.

### 3. Carga (Load)
Los datos extraídos se insertan directamente en la tabla `scraping_data` dentro del schema **`raw`** de PostgreSQL.
* **Formato:** Los datos se almacenan en formato **JSONB** para preservar la estructura original del scraping y permitir futuras auditorías.

### 4. Transformación (Arquitectura Medallón)
Una vez cargados los datos crudos, **dbt** toma el control para procesar la información en capas:
* **Bronze:** Datos crudos con casting básico.
* **Silver:** Limpieza de strings, normalización de precios y eliminación de duplicados.
* **Gold:** Modelos finales listos para BI (comparativas de precios, variaciones diarias, alertas de ofertas).



---

## 📂 Estructura del Repositorio
```text
├── products_scraping/ # Proyecto DBT
│   ├── models/            # Capas Bronze, Silver, Gold
│   ├── seeds/             # product_catalog.csv (Catálogo de productos)
│   └── dbt_project.yml
├── dags/                  # Orquestación en Apache Airflow
├── src/
│   ├── scripts/           # scraping.py, extract_data.py, load_data.py
│   ├── config/            # Configuración de DB, Selectores y Logger
│   └── utils/             # extract_elements.py (Selenium helpers)
├── Dockerfile
├── docker-compose.yml     # Infraestructura Postgres/Airflow
└── main.py                # Entrada principal del proceso de extracción