# Seeders — Taller Mecánico

El proyecto tiene **un seeder**: `scripts/seed_db.py`. Inserta, si aún no existen, 2 clientes, 2 vehículos, 2 órdenes de trabajo y 2 reparaciones relacionadas en este orden:

`Cliente → Vehículo → Orden de Trabajo → Reparación`

Utiliza los modelos SQLAlchemy y los esquemas Pydantic del proyecto. La base utilizada depende de `DATABASE_URL`: PostgreSQL con Docker o SQLite local. No modifica registros ya existentes.

## Datos de ejemplo

| Cliente (correo) | Vehículo (patente) | Orden (marcador) | Reparación (marcador) |
|---|---|---|---|
| `seed.cliente01@example.com` | `SBAB12` (Toyota Yaris) | `SEED_P5_OT_01` | `SEED_P5_REP_01` (diagnóstico, 25000) |
| `seed.cliente02@example.com` | `SBCD34` (Hyundai Accent) | `SEED_P5_OT_02` | `SEED_P5_REP_02` (mantención, 85000) |

El script busca clientes por correo (sin distinguir mayúsculas), vehículos por patente (sin distinguir mayúsculas) y órdenes/reparaciones por su descripción identificable. Reutiliza los IDs reales para las claves foráneas; **no depende de IDs fijos**. Si un dato identificado ya existe asociado a otro padre, interrumpe la carga. No cambies los marcadores de las descripciones si quieres conservar la idempotencia.

Utiliza `SessionLocal.begin()` para una sola transacción de inserción: hace `commit` al completar las cuatro entidades, o `rollback` si una operación falla. `session.flush()` permite obtener los IDs sin confirmar parcialmente los registros.

## A. Prueba segura con PostgreSQL en Docker (base aislada)

**No ejecutes pruebas de errores, rollback ni inserciones de demostración sobre una base compartida o de producción.** Usa un proyecto Docker Compose con nombre exclusivo, su propio volumen y variables de entorno independientes.

Requisitos: Docker Desktop con Compose, Git y la imagen del backend construible. Desde la raíz del repositorio, en PowerShell:

```powershell
Copy-Item .env.example ../seeders-audit.env
```

Edita `../seeders-audit.env` (fuera del repositorio) con **credenciales propias de prueba** y un nombre de base exclusivo, por ejemplo `POSTGRES_DB=taller_seeders_audit`. Nunca subas ese archivo a GitHub. El `compose.yaml` usa `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB`; el backend recibe `DATABASE_URL` construido para el servicio `db`.

Todos los comandos siguientes usan el proyecto aislado `taller-seeders-audit`:

```powershell
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env build backend
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env up -d db
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env run --rm backend uv run --no-sync alembic upgrade head
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env run --rm backend uv run --no-sync alembic current
```

**Migra primero y ejecuta el seeder después.** `seed_db.py` llama a `init_db()` y, si se lanza antes que Alembic sobre una base completamente vacía, `create_all()` puede crear tablas sin registrar la versión de migraciones. En una base nueva correctamente migrada, `current` debe mostrar `0001 (head)`.

### Conteos antes y después

Ejecuta este comando en cada uno de los tres momentos: **antes de la carga**, **después de la primera carga** y **después de la segunda carga**:

```powershell
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "SELECT (SELECT COUNT(*) FROM clientes), (SELECT COUNT(*) FROM vehiculos), (SELECT COUNT(*) FROM ordenes_trabajo), (SELECT COUNT(*) FROM reparaciones)"'
```

La salida es una fila en orden `clientes|vehiculos|ordenes_trabajo|reparaciones`. En una base nueva, se esperan los siguientes valores; **son expectativas, no resultados de una ejecución de PostgreSQL en esta revisión**:

| Momento | Conteos esperados |
|---|---|
| Antes de ejecutar | `0|0|0|0` |
| Primera ejecución | `2|2|2|2` |
| Segunda ejecución | `2|2|2|2` |

Para insertar y volver a insertar:

```powershell
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env run --rm backend uv run --no-sync python scripts/seed_db.py
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env run --rm backend uv run --no-sync python scripts/seed_db.py
```

La primera ejecución debería indicar 2 registros nuevos por entidad y la segunda, **0 nuevos**. Conserva las líneas `Cadena 1` y `Cadena 2` con sus IDs para verificar que no cambiaron.

### Integridad de las relaciones y rollback

```powershell
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env run --rm backend uv run --no-sync python scripts/seed_db.py --verificar
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env run --rm backend uv run --no-sync python scripts/seed_db.py --probar-rollback
```

`--verificar` consulta en otra sesión los ocho registros y comprueba que cada ID de cliente, vehículo y orden coincida con la clave foránea del siguiente nivel. `--probar-rollback` inserta temporalmente un cliente, provoca un error antes del commit y verifica en una nueva sesión que dicho cliente no exista.

Para una comprobación SQL adicional de las relaciones:

```powershell
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT c.email, v.patente, o.id AS orden_id, r.id AS reparacion_id FROM clientes c JOIN vehiculos v ON v.cliente_id=c.id JOIN ordenes_trabajo o ON o.vehiculo_id=v.id JOIN reparaciones r ON r.orden_trabajo_id=o.id ORDER BY c.email"'
```

El resultado esperado son **2 filas**. Registra los conteos, los IDs de las dos pasadas y los mensajes reales en el informe; no los sustituyas por los valores esperados.

### API y persistencia

Después de aplicar migraciones:

```powershell
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env up -d backend
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env ps
```

Abre `http://localhost:8000/docs` y consulta `GET /clientes`, `GET /vehiculos/`, `GET /ordenes-trabajo` y `GET /reparaciones/`. Los clientes y las órdenes usan `items` en sus listados paginados.

Para comprobar persistencia, reinicia solamente la API:

```powershell
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env restart backend
```

Repite los GET y `--verificar`. No borres el volumen. Para detener los contenedores sin borrar datos:

```powershell
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env down
```

No añadas `-v` a `down` si quieres conservar los datos de la prueba.

## B. Ejecución local con SQLite

Si no se define `DATABASE_URL`, `database/session.py` utiliza `sqlite:///./taller_mecanico.db`. Desde la raíz:

```powershell
uv sync
uv run python scripts/seed_db.py
uv run python scripts/seed_db.py
uv run python scripts/seed_db.py --verificar
uv run python scripts/seed_db.py --probar-rollback
uv run uvicorn proyectobackend.main:app --reload
```

El seeder puede crear tablas mediante `init_db()` para desarrollo SQLite. No uses ese comportamiento como sustituto de `alembic upgrade head` al comprobar PostgreSQL. En SQLite las FK no se imponen por defecto si no está activado `PRAGMA foreign_keys=ON`; por eso `--verificar` comprueba explícitamente las relaciones de las semillas.

### Comprobación SQL local

```powershell
uv run python -c "import sqlite3; c=sqlite3.connect('taller_mecanico.db'); print({t:c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('clientes','vehiculos','ordenes_trabajo','reparaciones')}); c.close()"
```

En una base nueva se esperan 2 registros de cada entidad. En una base con registros previos, los totales pueden ser mayores; la segunda ejecución debe conservar los conteos y los IDs de las semillas.

## Estado de las evidencias

El 28 de octubre de 2026 se comprobaron en SQLite local los dos registros por entidad, sus relaciones con Swagger, el rollback de prueba y la persistencia después de reiniciar Uvicorn.

**La comprobación requerida en PostgreSQL aislado (migración, doble ejecución, conteos, IDs, errores de unicidad e integridad) necesita evidencia de una ejecución real.** No se considera aprobada únicamente por el funcionamiento anterior con SQLite.
