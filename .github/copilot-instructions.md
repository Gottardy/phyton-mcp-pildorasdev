# Copilot instructions for pildorasDev

Breve: este repo es un microservicio mínimo que expone herramientas (FastMCP) para gestionar empleados y persiste en PostgreSQL. Usa `uv` como runtime dentro del contenedor y `psycopg2` para acceso a la base de datos.

- **Arquitectura y por qué**: el servicio principal está en [main.py](main.py). Se registra como `FastMCP` app y publica herramientas con `@app.tool`; el proceso se lanza con `app.run(transport="sse", port=3000)` y se espera que la orquestación use `docker compose` para crear la base de datos y el servidor.
- **Componentes clave**:
  - Servicio HTTP SSE / FastMCP: [main.py](main.py)
  - Inicialización de datos SQL: [init.sql](init.sql)
  - Contenerización: [Dockerfile](Dockerfile)
  - Orquestación local: [docker-compose.yml](docker-compose.yml)
  - Metadatos / dependencias: [pyproject.toml](pyproject.toml)

- **Patrones y convenciones del proyecto (importantes para agentes)**:
  - Cada operación pública se implementa como `@app.tool` (ver [main.py](main.py)). Añadir una nueva herramienta significa crear una función, decorarla con `@app.tool` y asegurarse de gestionar la conexión a BD y los cierres en `finally`.
  - Acceso a DB: se usa `psycopg2` con `RealDictCursor` para que las filas actúen como mappings (evita reindexado por posición). Cierra `cursor` y `conn` en `finally`.
  - Manejo de errores: las funciones no devuelven objetos de error; lanzan excepciones envolviendo errores en `RuntimeError` para mantener firmas limpias. Mantén ese patrón cuando modifiques herramientas.
  - Validaciones: `add_employee` valida campos obligatorios y valores (ej.: salary > 0). Sigue la misma estrategia para nuevas entradas.
  - Imports locales: algunas importaciones (p. ej. `RealDictCursor`) aparecen dentro de funciones — respeta esto si mueves código.

- **Workflows y comandos reproducibles**:
  - Levantar todo con Docker Compose (desarrollador):

    docker compose up --build -d

  - Ejecutar localmente sin Docker (crear venv e instalar deps):

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    uv run python main.py

  - Dentro del contenedor se usa `uv` para sincronizar e iniciar (ver [Dockerfile](Dockerfile)).

- **Integraciones y puntos de atención**:
  - El archivo [docker-compose.yml](docker-compose.yml) monta `./init.sql` en `/docker-entrypoint-initdb.d/` para poblar la BD al iniciar el contenedor Postgres.
  - Variables de entorno: el código lee `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (ver [main.py](main.py)), mientras que `docker-compose.yml` configura `DB_DATABASE` para `mcp-server`. Hay una discrepancia entre `DB_NAME` y `DB_DATABASE` — confirma cuál es la variable correcta antes de cambios que toquen la configuración de despliegue o la inicialización.
  - El servicio Postgres se configura con usuario/clave `test` y base `test_db` en [docker-compose.yml](docker-compose.yml); `init.sql` crea la tabla `employees` y filas de ejemplo.

- **Qué revisar antes de editar código**:
  - Asegurarse de usar las mismas claves de entorno que el despliegue (ver la nota sobre `DB_NAME` vs `DB_DATABASE`).
  - Mantener el patrón de conexión/cleanup (obtener `conn`, crear `cursor` con `RealDictCursor`, `try/except/finally` con `close()` y `conn.commit()` donde proceda).
  - Preservar la forma de retorno: `list_employees` => `List[Dict[str, Any]]`; `add_employee` => `Dict[str, Any]` con `success` y `employee`.

- **Ejemplos útiles sacados del repo**:
  - Añadir una herramienta mínima:

    from fastmcp import FastMCP

    @app.tool
    def foo() -> str:
        return "ok"

  - Conectar a BD (usar el helper `get_db_connection()` en [main.py](main.py)).

- **Errores y riesgos detectados** (para que el agente pregunte antes de actuar):
  - Discrepancia de nombre de variable de DB (`DB_NAME` vs `DB_DATABASE`).
  - `docker-compose.yml` expone Postgres con la dirección `127.0.0.0:5432:5432` — esto parece atípico (normalmente `127.0.0.1:5432:5432` o `"5432:5432"`). Verifica antes de proponer cambios de red.

- **Dónde practicar cambios seguros**:
  - Añade nuevas herramientas en `main.py` o en módulos nuevos importados desde `main.py`. Usa la base de datos montada por `docker compose` para pruebas de integración rápidas.

Si te sirve, puedo: 1) añadir tests básicos de integración que usen la base de datos del contenedor, 2) arreglar la discrepancia de variables de entorno y actualizar `docker-compose.yml` y `main.py`. ¿Qué prefieres que haga primero?
