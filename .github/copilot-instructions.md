# Copilot / AI Agent instructions for pildorasDev

Resumen rápido
- Proyecto: `pildorasDev` — microservicio Python que expone herramientas (`tools`) con FastMCP para gestionar empleados.
- Ejecuta en puerto `3000`. Persistencia: PostgreSQL inicializada vía `init.sql`.

Arquitectura y propósito
- `main.py` implementa las herramientas principales: `list_employees(limit, offset)` y `add_employee(...)` decoradas con `@app.tool` de FastMCP. Mantener la semántica de `tool` (firmas y tipos) al modificar.
- Base de datos: PostgreSQL. La inicialización de esquema y datos de ejemplo se hace en `init.sql` (montado en `docker-compose`).
- Contenerización: `Dockerfile` + `docker-compose.yml`. El servicio `mcp-server` depende del servicio `postgres` (nombre de host `postgres` en redes Docker).

Puntos críticos y convenciones del proyecto
- Conexión DB: función `get_db_connection()` en `main.py`. Usa `DB_DATABASE` por defecto y cae a `DB_NAME` si existe. No renombrar variables sin actualizar `docker-compose.yml`.
- Cursores: se usa `psycopg2.extras.RealDictCursor` para devolver filas como dicts; el código asume claves por nombre (por ejemplo `row["name"]`).
- Manejo de errores: las funciones propagan errores envolviéndolos en `RuntimeError` (no devolver estructuras mixtas). Mantener esta convención para consistencia con clientes.
- Validaciones: `add_employee` valida campos obligatorios y valores (p.ej. salary > 0). Mantener validaciones en la capa de tool.
- Tipos y formatos: `salary` se convierte a `float` al construir el JSON de salida; `hire_date` se devuelve en ISO (`YYYY-MM-DD`).
- Import patterns: hay importaciones inline para tipos (`from typing import cast`) y para `RealDictCursor` en la función; mantener ese patrón si la importación debe estar dentro de la función.

Comandos y flujos de desarrollo
- Levantar todo con Docker (recomendado):

```bash
docker compose up --build -d
```

- Servicio expuesto en `http://localhost:3000` (puerto mapeado en `docker-compose.yml`).
- Construcción local sin Docker (dev):

```bash
python -m venv .venv
source .venv/bin/activate
# El proyecto usa `uv` en Docker; para instalar dependencias localmente usar pip o replicar uv workflow
pip install -r requirements.txt  # si existe; alternativamente actualizar uv.lock y usar uv
```

- En `Dockerfile` se usa la imagen `ghcr.io/astral-sh/uv` y `uv sync --frozen --no-dev --no-cache` para instalar dependencias. Si cambias dependencias, actualiza `uv.lock` y prueba el `uv sync`.

Integraciones y puntos de atención
- `docker-compose.yml` monta `./init.sql` en `/docker-entrypoint-initdb.d/` para poblar la BD al arranque. Si modificas el esquema, actualiza `init.sql` y recrea los volúmenes.
- Variables de entorno relevantes (ver `docker-compose.yml`): `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_DATABASE`.
- No depends_on explícito en código: el servicio asume que la DB estará disponible; `docker-compose` usa `depends_on` con `condition: service_healthy`.

Guías para editar y probar código AI-driven
- Cuando implementes nuevas `@app.tool`:
  - Mantén firmas tipadas y devuelve tipos JSON-serializables (listas/dict). Ejemplo: `list_employees(...) -> List[Dict[str, Any]]`.
  - Usa `RealDictCursor` si vas a mapear columnas a claves.
  - Nunca silencies excepciones: propaga con `RuntimeError` para que el runner del servicio lo capture.
- Si tocas la persistencia:
  - Actualiza `init.sql` para infraestructura reproducible.
  - Si la modificación requiere migraciones, documenta el paso en `README.md`.
- Dependencias:
  - Cambios en paquetes deben reflejarse en `pyproject.toml` y en `uv.lock` (si se usa `uv`).

Archivos clave (referencias)
- `main.py` — implementa las herramientas y la lógica DB.
- `init.sql` — esquema y datos de ejemplo.
- `docker-compose.yml` — despliegue local: servicios, redes, volúmenes y variables DB.
- `Dockerfile` — build image, uso de `uv` y comando de ejecución (`uv run python main.py`).
- `pyproject.toml` — dependencias declaradas (`fastmcp`, `psycopg2`).

Preguntas al autor / puntos por confirmar
- ¿Existe un endpoint HTTP públicamente documentado para invocar las `tools` de FastMCP además de SSE? (útil para ejemplos concretos).
- ¿Prefieres instrucciones en inglés para la audiencia internacional? Actualmente este archivo está en español.

Feedback
- Revisa estas instrucciones y dime qué agregar o aclarar: ejemplos de input/output para las `tools`, flujos de testing automatizado, o convenciones de commit.
