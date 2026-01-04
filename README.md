# pildorasDev

Proyecto `pildorasDev` — un microservicio ligero para gestionar empleados usando `FastMCP` y PostgreSQL.

Características principales
- Tools (FastMCP) para CRUD completo de empleados: `list_employees`, `add_employee`, `get_employee`, `update_employee`, `delete_employee`.
- Persistencia en PostgreSQL (script de inicialización `init.sql`).
- Contenerizado con `Dockerfile` y orquestación con `docker-compose.yml`.

Contenido del repositorio
- `main.py`: implementación de las tools mencionadas.
- `init.sql`: script para crear la tabla `employees` y datos de ejemplo.
- `pyproject.toml`, `uv.lock`: dependencias y bloqueo para reproducibilidad.
- `Dockerfile`, `docker-compose.yml`: configuración para desplegar el servicio y la base de datos.

Requisitos
- Python >= 3.12
- PostgreSQL (si no usas Docker)

Uso rápido (con Docker)
1. Construir y levantar servicios:

```bash
docker compose up --build -d
```

2. El servicio queda expuesto en el puerto `3000`.

Variables de entorno (ejemplo para `mcp-server`)
- `DB_HOST` (en `docker-compose.yml` se conecta al servicio de la BD usando el host `postgres`)
- `DB_PORT` (5432)
- `DB_USER`
- `DB_PASSWORD`
- `DB_DATABASE`

Nota: `docker-compose.yml` monta `init.sql` en la inicialización de la BD; revisa las variables en el propio fichero.

Ejecución local (desarrollo) — usando `uv` (recomendado para reproducir el entorno de contenedores):

1. Crear y activar un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar `uv` y sincronizar dependencias desde `uv.lock`:

```bash
pip install uv
uv sync --frozen --no-dev --no-cache
```

3. Ejecutar el servicio (espera tener la BD disponible y variables de entorno configuradas):

```bash
uv run python main.py
```

Alternativa rápida: usar `docker compose up --build -d` para arrancar la BD y el servicio juntos.

Cómo usar las tools
- `list_employees(limit=10, offset=0)` — lista con paginación.
- `add_employee(name, position, department, salary, hire_date?)` — inserta un empleado.
- `get_employee(employee_id)` — obtiene un empleado por `id`.
- `update_employee(employee_id, ...)` — permite actualizaciones parciales de campos.
- `delete_employee(employee_id)` — borra un empleado por `id`.

Notas de desarrollo
- `main.py` usa `psycopg2.extras.RealDictCursor` para devolver filas como diccionarios (accesibles por nombre de columna).
- Las funciones propagan errores envolviéndolos en `RuntimeError` para mantener consistencia con el runner del servicio.

Licencia
Este proyecto se publica bajo la licencia MIT — ver [LICENSE](LICENSE).

Contacto
Autor: Gottardy Melo — https://github.com/Gottardy
