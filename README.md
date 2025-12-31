# pildorasDev

Proyecto `pildorasDev` — un microservicio ligero para gestionar empleados usando FastMCP y PostgreSQL.

Características principales
- Endpoints/Tools para listar y añadir empleados.
- Persistencia en PostgreSQL (script de inicialización `init.sql`).
- Contenerizado con `Dockerfile` y orquestación con `docker-compose.yml`.

Contenido del repositorio
- `main.py`: implementación de las herramientas `list_employees` y `add_employee`.
- `init.sql`: script para crear la tabla `employees` y datos de ejemplo.
- `pyproject.toml`, `uv.lock`: dependencias y bloqueo para reproducibilidad.
- `Dockerfile`, `docker-compose.yml`: configuración para desplegar el servicio y la base de datos.

Requisitos
- Python >= 3.12
- PostgreSQL (si no usa Docker)

Uso rápido (con Docker)
1. Construir y levantar servicios:

```bash
docker compose up --build -d
```

2. El servicio queda expuesto en el puerto `3000`.

Variables de entorno (ejemplo para `mcp-server`)
- `DB_HOST` (por defecto en `docker-compose` está configurado a `localhost` dentro del contenedor)
- `DB_PORT` (5432)
- `DB_USER` (test)
- `DB_PASSWORD` (test)
- `DB_DATABASE` (test_db)

Notas de desarrollo
- Antes de ejecutar localmente sin Docker, asegúrate de crear un entorno virtual e instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # o usa uv/uv.lock según tu flujo
```

- El fichero `uv.lock` contiene el bloqueo de paquetes; el proyecto usa `fastmcp` y `psycopg2`.

Licencia
Este proyecto se publica bajo la licencia MIT — ver `LICENSE`.

Contacto
Autor: Gottardy Melo — https://github.com/Gottardy
