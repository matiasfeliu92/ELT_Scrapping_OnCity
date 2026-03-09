# ELT_Scrapping_OnCity

## 1. Descripcion General
`ELT_Scrapping_OnCity` es una aplicacion de data engineering y backend API enfocada en scraping de productos, carga ELT en PostgreSQL y exposicion de informacion por API REST.

Objetivos principales:
- Ingestar catalogo y URLs de productos.
- Scrapear datos comerciales (precio, stock, retailer, etc.).
- Persistir en base de datos para analitica y consumo API.
- Gestionar usuarios y autenticacion con JWT.

## 2. Stack Tecnologico
- Python 3.10
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker y Docker Compose
- Alembic (recomendado para migraciones de esquema)
- Apache Airflow
- dbt (`dbt-core`, `dbt-postgres`)
- Pydantic
- bcrypt
- PyJWT
- Selenium, Requests y BeautifulSoup

## 3. Arquitectura (Clean Architecture)
La API esta organizada por contexto de negocio (`products`, `users`, `auth`) y por capas:

- `domain`: entidades y reglas de negocio puras.
- `application`: casos de uso que orquestan la logica del dominio.
- `infrastructure`: adaptadores externos (DB, API, esquemas, repositorios concretos).

Estructura general:

```text
API/src/
    products/
        domain/
        application/
        infrastructure/
    users/
        domain/
        application/
        infrastructure/
    auth/
        domain/
        application/
        infrastructure/
    shared/
        common/
        infrastructure/db/
```

## 4. Capas Principales
### Domain
- Contiene entidades de negocio y contratos de repositorios.
- Ejemplo: `AuthCredentials` valida politica de password.
- Ejemplo: `AuthUser` encapsula reglas de autenticacion y generacion de `jti` seguro.

### Application
- Implementa casos de uso del sistema.
- Ejemplo: `register_user` y `login_user` validan credenciales y devuelven JWT.
- Ejemplo: en users, la logica de `update_user` restringe campos sensibles.

### Infrastructure
- Implementa persistencia, transporte HTTP y componentes externos.
- Ejemplo: repositorios SQLAlchemy para `users`, `products`, `auth_tokens`.
- Ejemplo: hashing con `bcrypt` y firma/verificacion JWT con `PyJWT`.

## 5. Documentacion de Carpetas y Modulos
### `API/src/products`
- Responsabilidad: lectura de productos scrapeados almacenados en `raw.products`.
- Incluye entidad de dominio, casos de uso (`get_all_products`, `get_product_by_id`), repositorio SQLAlchemy y rutas FastAPI.

### `API/src/users`
- Responsabilidad: lectura de usuarios y gestion de actualizacion de datos de usuario.
- Contiene reglas para proteger campos sensibles en update (`password`, `email`, `id`).

### `API/src/auth`
- Responsabilidad: registro, login y seguridad.
- Incluye validacion de credenciales, hashing de passwords, emision/verificacion JWT y persistencia de tokens.

### `API/src/shared/common`
- Responsabilidad: piezas compartidas del dominio.
- Incluye excepciones comunes y utilidades transversales para la API.

### `API/src/shared/infrastructure/db`
- Responsabilidad: definicion de `Base` de SQLAlchemy y configuracion de sesion/conexion a PostgreSQL.

### `products_scraping`
- Responsabilidad: ingesta de catalogo via `dbt seed`, transformaciones dbt y soporte al scraping de URLs.

### `src/config`, `src/scripts`, `src/utils`
- Responsabilidad: configuracion de entorno, scripts auxiliares para scraping/extraccion/carga y utilidades de procesamiento.

### `dags`, `plugins`, `data`
- Responsabilidad: procesos ETL, orquestacion con Airflow y almacenamiento intermedio de artefactos (por ejemplo JSON).

## 6. Endpoints Principales
### Products
- `GET /v1/products/`
- `GET /v1/products/{product_id}`

### Users
- `GET /v1/users/`
- `PUT /v1/users/{id}` (logica de actualizacion implementada en capa de aplicacion/repositorio; exponer ruta en API segun necesidad)

### Auth
- `POST /v1/auth/register`
- `POST /v1/auth/login`

## 7. Ejemplos de Requests y Responses
### Registrar usuario
```bash
curl -X POST "http://127.0.0.1:8000/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Matias",
        "email": "matias@example.com",
        "password": "StrongPass1!",
        "location": "Buenos Aires",
        "phone": "+54-11-1234-5678"
    }'
```

Response:
```json
{
    "access_token": "<jwt>",
    "token_type": "bearer"
}
```

### Login
```bash
curl -X POST "http://127.0.0.1:8000/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "matias@example.com",
        "password": "StrongPass1!"
    }'
```

### Obtener productos
```bash
curl -X GET "http://127.0.0.1:8000/v1/products/"
```

Response:
```json
[
    {
        "id": 1,
        "product_id": "SKU-001",
        "name": "Smart TV 50",
        "brand": "Samsung",
        "cash_price": 799999.99,
        "retailer": "Fravega",
        "link": "https://..."
    }
]
```

### Obtener usuarios
```bash
curl -X GET "http://127.0.0.1:8000/v1/users/"
```

## 8. Flujo Completo del Sistema
1. Se define/actualiza el catalogo de productos.
2. `dbt seed` ingesta el catalogo a PostgreSQL.
3. Scripts de scraping consumen URLs y extraen datos.
4. Datos scrapeados se guardan en tablas raw (ejemplo `raw.products`) y/o archivos intermedios.
5. Airflow orquesta ejecuciones periodicas de scraping y transformaciones.
6. dbt transforma datos para uso analitico.
7. La API FastAPI expone productos y usuarios.
8. `auth` protege el acceso emitiendo tokens JWT a usuarios registrados/autenticados.

## 9. Instrucciones de Ejecucion
### 9.1 Instalar dependencias
```bash
python -m venv scraping
```

Windows:
```powershell
.\scraping\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS:
```bash
source scraping/bin/activate
pip install -r requirements.txt
```

### 9.2 Configurar entorno
Crear archivo `.env` con al menos:
- `DB_USER`
- `DB_PASS`
- `DB_HOST`
- `DB_HOST_DOCKER`
- `DB_NAME`
- `DB_NAME_USE`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM` (opcional)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (opcional)

### 9.3 Migraciones
Opciones de migracion segun entorno:
- Airflow metadata DB: `airflow db migrate`
- SQLAlchemy auto-create (actual en API): al iniciar `API.src.main` se ejecuta `Config().create_tables()`
- Alembic (recomendado para control de versiones de esquema):

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

### 9.4 Correr API
```bash
uvicorn API.src.main:app --reload
```

### 9.5 Levantar entorno con Docker Compose
```bash
docker compose up --build
```

## 10. Validaciones Implementadas
- Email unico en registro de usuario.
- Hashing de contrasenas con `bcrypt`.
- JWT con claims (`sub`, `email`, `jti`, `iat`, `exp`) y expiracion.
- Persistencia de hash de token en `auth_tokens` para control de validez/revocacion.
- Reglas de negocio en `domain` (fortaleza de password, usuario activo para login).
- Validaciones de payload en schemas Pydantic para requests/responses.
- Reglas de actualizacion de usuario para bloquear campos sensibles.

## 11. Documentacion API
Con la API en ejecucion:
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## 12. Notas de Evolucion
- Se recomienda exponer formalmente `PUT /v1/users/{id}` en `user_routes.py` para completar la funcionalidad de update ya disponible en capas internas.
- Se recomienda formalizar Alembic como flujo principal de migraciones de esquema de la API.