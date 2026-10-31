# Datos iniciales y seeders

El script `scripts/seed_db.py` permite cargar datos de ejemplo para probar las relaciones del taller. Crea dos registros por módulo: **2 clientes, 2 vehículos, 2 órdenes de trabajo y 2 reparaciones**.

Cada cadena sigue la relación **Cliente → Vehículo → Orden de Trabajo → Reparación**. El script identifica los registros que ya existen y evita duplicarlos cuando se ejecuta otra vez.

## Datos que se cargan

| Cadena | Cliente | Vehículo | Orden de trabajo | Reparación |
|---|---|---|---|---|
| 1 | `seed.cliente01@example.com` | `SBAB12` · Toyota Yaris | `SEED_P5_OT_01` | `SEED_P5_REP_01` · diagnóstico · $25.000 |
| 2 | `seed.cliente02@example.com` | `SBCD34` · Hyundai Accent | `SEED_P5_OT_02` | `SEED_P5_REP_02` · mantención · $85.000 |

Los identificadores son generados por la base de datos. **No siempre serán 1 y 2**, especialmente si hay registros anteriores.

## Ejecutar el seeder

Desde la raíz del proyecto, **comprueba primero a qué base apunta `DATABASE_URL`**. En esta sección se debe usar una base local de desarrollo o prueba, nunca la base compartida:

```powershell
uv sync --frozen
uv run python scripts/seed_db.py
```

Si la base está vacía, se espera crear dos registros por entidad. Para comprobar que una segunda ejecución no duplique datos, ejecuta el mismo comando nuevamente. El resultado esperado de esa segunda ejecución es:

```text
Nuevos registros por entidad: {'clientes': 0, 'vehiculos': 0, 'ordenes_trabajo': 0, 'reparaciones': 0}
VERIFICACIÓN EXITOSA: 2 registros iniciales por entidad y relaciones correctas.
```

Para consultar los registros de ejemplo sin volver a cargarlos:

```powershell
uv run python scripts/seed_db.py --verificar
```

Para comprobar el manejo de transacciones ante un fallo intencional:

```powershell
uv run python scripts/seed_db.py --probar-rollback
```

Se espera el mensaje `ROLLBACK EXITOSO` y que no se conserve el cliente temporal utilizado por esa comprobación.

## Probar con PostgreSQL y Docker

**No ejecutes estas pruebas en la base compartida del equipo.** Utiliza un clon independiente, un nombre exclusivo de proyecto Compose y una base creada para la verificación.

Desde una carpeta separada de tu copia habitual del proyecto:

```powershell
git clone https://github.com/cnahuelcoy/backend-2026-grupo-06.git backend-seeders-audit
cd backend-seeders-audit
Copy-Item .env.example .env
```

En ese `.env` de pruebas configura una base distinta, por ejemplo `POSTGRES_DB=seeders_audit_db`, y una contraseña propia. No subas ese archivo a GitHub.

```powershell
docker compose -p seeders_audit_20261029 build backend
docker compose -p seeders_audit_20261029 up -d db
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync alembic upgrade head
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync alembic current
```

Antes de cargar datos, consulta los conteos:

```powershell
docker compose -p seeders_audit_20261029 exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT (SELECT count(*) FROM clientes) AS clientes, (SELECT count(*) FROM vehiculos) AS vehiculos, (SELECT count(*) FROM ordenes_trabajo) AS ordenes, (SELECT count(*) FROM reparaciones) AS reparaciones;"'
```

Ejecuta el seeder, repite la consulta de conteos y vuelve a ejecutar el seeder:

```powershell
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync python scripts/seed_db.py
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync python scripts/seed_db.py
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync python scripts/seed_db.py --verificar
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync python scripts/seed_db.py --probar-rollback
```

En una base vacía y migrada, los conteos esperados son `0/0/0/0 → 2/2/2/2 → 2/2/2/2`. La segunda ejecución debe crear **cero registros nuevos**.

La revisión de integridad también puede hacerse mediante una consulta de las cuatro tablas relacionadas:

```sql
SELECT c.id AS cliente_id, v.id AS vehiculo_id,
       o.id AS orden_id, r.id AS reparacion_id,
       c.email, v.patente
FROM clientes AS c
JOIN vehiculos AS v ON v.cliente_id = c.id
JOIN ordenes_trabajo AS o ON o.vehiculo_id = v.id
JOIN reparaciones AS r ON r.orden_trabajo_id = o.id
ORDER BY c.id;
```

## Evidencia registrada en el proyecto

El 30 de octubre de 2026, el integrante encargado informó una comprobación con **PostgreSQL 17 en Docker**, dentro del proyecto aislado `taller-seeders-audit` y la base `taller_seeders_audit`. Es una ejecución distinta del ejemplo reproducible anterior.

| Comprobación | Resultado informado |
|---|---|
| Alembic | Migración aplicada; revisión `0001 (head)` |
| Antes de cargar | `0 / 0 / 0 / 0` |
| Primera carga | `2 / 2 / 2 / 2` registros |
| Segunda carga | `0 / 0 / 0 / 0` nuevos; mismos identificadores |
| Relaciones entre entidades | Dos cadenas completas y sin registros huérfanos |
| Conflictos UNIQUE y FK | Rechazados; sin inserciones parciales |
| Prueba de rollback | `ROLLBACK EXITOSO` |
| Verificación posterior | Ocho registros de ejemplo conservados correctamente |

También se informó una prueba de los endpoints de Reparaciones con esa misma base PostgreSQL: consultas `200` y `404`, creación `201`, modificación `200` y eliminación `204` de una reparación temporal. Las reparaciones iniciales no se modificaron.

Estas evidencias proceden de la revisión y capturas informadas por el integrante. **No representan una ejecución nueva realizada al redactar este documento.** Los casos `400` por fecha futura y `422` de validación no se confirmaron en esa ejecución de PostgreSQL; sí forman parte de las pruebas HTTP aisladas.

## Cómo funciona

La carga utiliza modelos SQLAlchemy y valida los datos con los esquemas Pydantic del proyecto. Se realiza dentro de **una sola transacción**: si alguna relación o dato falla, no se guardan cambios parciales.

Para reconocer las semillas, el script utiliza los correos de clientes, las patentes de vehículos y los marcadores `SEED_P5_OT_*` y `SEED_P5_REP_*`. No se deben cambiar esos identificadores si se quiere conservar la idempotencia.

El seeder no modifica los modelos, endpoints, migraciones ni reglas de negocio de la API. Para más información sobre la estructura de la base, consulta [`docs/migraciones.md`](migraciones.md).
