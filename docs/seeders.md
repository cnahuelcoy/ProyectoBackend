# Parte 5 — Seeders y datos iniciales

El archivo `scripts/seed_db.py` inserta **dos clientes, dos vehículos, dos órdenes de trabajo y dos reparaciones** en la base configurada (SQLite o PostgreSQL), enlazados como `Cliente → Vehículo → Orden de Trabajo → Reparación`. No crea migraciones nuevas ni modifica reglas de negocio, modelos o endpoints. En PostgreSQL, las migraciones existentes deben aplicarse **antes** de ejecutar este script.

## Verificación segura con PostgreSQL y Docker (base aislada)

**Advertencia:** ejecutar estas comprobaciones únicamente en una **base de pruebas nueva**, nunca en la base compartida ni de producción. El ejemplo usa otro clon, otro proyecto de Docker Compose y otro volumen; no contiene credenciales reales. **Estos comandos son un ejemplo reproducible; las comprobaciones efectivamente ejecutadas y sus resultados se documentan al final de esta guía.**

Requisitos: Git, Docker Desktop + Compose y un clon limpio del repositorio. En PowerShell, desde una carpeta distinta de la copia que utiliza el equipo:

```powershell
git clone https://github.com/cnahuelcoy/backend-2026-grupo-06.git backend-seeders-audit
cd backend-seeders-audit
Copy-Item .env.example .env
```

Editar el archivo `.env` **solo dentro del clon de pruebas**: establecer `POSTGRES_DB=seeders_audit_db` y una contraseña propia para `POSTGRES_PASSWORD`; conservar o configurar `POSTGRES_USER`. No subir `.env` ni pegar la contraseña en evidencias. La URL `DATABASE_URL` del contenedor backend se construye automáticamente desde las variables de Compose.

Usar siempre el mismo nombre de proyecto **exclusivo** para evitar utilizar contenedores o volúmenes del equipo:

```powershell
docker compose -p seeders_audit_20261029 build backend
docker compose -p seeders_audit_20261029 up -d db
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync alembic upgrade head
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync alembic current
```

Resultado **esperado**, no certificado: Alembic en revisión `0001 (head)`. **No ejecutar `alembic downgrade`, `drop_all` ni eliminar volúmenes de bases compartidas.**

### Medir antes, después de la primera ejecución y después de la segunda

Tomar una captura de las cantidades antes de insertar:

```powershell
docker compose -p seeders_audit_20261029 exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT (SELECT count(*) FROM clientes) AS clientes, (SELECT count(*) FROM vehiculos) AS vehiculos, (SELECT count(*) FROM ordenes_trabajo) AS ordenes, (SELECT count(*) FROM reparaciones) AS reparaciones;"'
```

Ejecutar una vez y repetir la consulta anterior:

```powershell
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync python scripts/seed_db.py
```

Ejecutar **exactamente el mismo comando una segunda vez**, repetir de nuevo la consulta de cantidades y comparar los IDs mediante esta consulta (también antes y después de la segunda ejecución):

```powershell
docker compose -p seeders_audit_20261029 exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT c.id AS cliente_id, v.id AS vehiculo_id, o.id AS orden_id, r.id AS reparacion_id, c.email, v.patente FROM clientes c JOIN vehiculos v ON v.cliente_id=c.id JOIN ordenes_trabajo o ON o.vehiculo_id=v.id JOIN reparaciones r ON r.orden_trabajo_id=o.id ORDER BY c.id;"'
```

En una base realmente vacía y migrada se **espera**, en orden, `0/0/0/0 → 2/2/2/2 → 2/2/2/2`. Los IDs de las dos cadenas deberían mantenerse sin cambios entre la primera y segunda ejecución. **Anotar los valores obtenidos realmente**, no copiar los valores esperados como si fueran resultados.

### Integridad y rollback

```powershell
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync python scripts/seed_db.py --verificar
docker compose -p seeders_audit_20261029 run --rm backend uv run --no-sync python scripts/seed_db.py --probar-rollback
```

`--verificar` comprueba en una sesión nueva los 8 registros de ejemplo y sus relaciones. `--probar-rollback` inserta un cliente temporal y provoca una excepción controlada: debe terminar con `ROLLBACK EXITOSO` sin conservar dicho cliente.

Las claves foráneas deben apuntar a registros existentes; la base contiene restricciones únicas para `clientes.email` y `vehiculos.patente`. Para ensayos destructivos adicionales de restricciones (violaciones de FK o unicidad), usar **solamente** la base exclusiva de pruebas y registrar el error observado y el estado final, nunca una base real compartida. El seeder recupera registros existentes por sus identificadores naturales y no sobrescribe datos ajenos.

### Qué datos registrar para la revisión

Guardar el nombre de la base de pruebas (sin credenciales), salida de Alembic, cantidades antes y después de ambas pasadas, IDs de las dos cadenas, salida de `--verificar`, salida de `--probar-rollback` y cualquier error. Comprobar opcionalmente los cuatro GET en Swagger con el backend de **este proyecto Compose aislado**, verificando que el puerto 8000 esté libre. No levantar ese backend si hay una aplicación compartida escuchando en dicho puerto.

## Preparación y ejecución local (SQLite o base configurada)

Desde la **raíz del repositorio** (donde se encuentra `pyproject.toml`), con Python 3.13 y `uv`:

```powershell
uv sync
uv run python scripts/seed_db.py
```

La inicialización existente `proyectobackend.database.init_db.init_db()` ejecuta `Base.metadata.create_all()` antes de cargar datos. Por ello, funciona tanto en una base SQLite vacía como en una base con las tablas ya creadas. La ubicación de la base de desarrollo es `./taller_mecanico.db`, relativa al directorio de ejecución según `database/session.py`.

En una primera ejecución sobre una base vacía, el resultado esperado es:

```text
Nuevos registros por entidad: {'clientes': 2, 'vehiculos': 2, 'ordenes_trabajo': 2, 'reparaciones': 2}
Cadena 1: cliente=1 -> vehículo=1 -> orden=1 -> reparación=1
Cadena 2: cliente=2 -> vehículo=2 -> orden=2 -> reparación=2
VERIFICACIÓN EXITOSA: 2 registros iniciales por entidad y relaciones correctas.
```

Los identificadores son **autoincrementales**: si la base ya tiene datos, pueden ser distintos de 1 y 2. En tal caso, se agregan únicamente las filas de ejemplo que todavía no existan.

### Segunda ejecución: idempotencia

Ejecutar exactamente el mismo comando:

```powershell
uv run python scripts/seed_db.py
```

Si no se han modificado los identificadores de las semillas, debe mostrar:

```text
Nuevos registros por entidad: {'clientes': 0, 'vehiculos': 0, 'ordenes_trabajo': 0, 'reparaciones': 0}
VERIFICACIÓN EXITOSA: 2 registros iniciales por entidad y relaciones correctas.
```

Para verificar sin insertar:

```powershell
uv run python scripts/seed_db.py --verificar
```

El seeder identifica clientes por correo electrónico (ignorando mayúsculas), vehículos por patente (ignorando mayúsculas), órdenes por la descripción con marcador `SEED_P5_OT_*` y reparaciones por la descripción con marcador `SEED_P5_REP_*`. No sobrescribe registros existentes. Si una clave ya existe pero pertenece a un padre distinto, cancela toda la transacción y muestra un error. **No cambiar ni quitar los marcadores de las descripciones** si se quiere mantener la idempotencia.

## Datos iniciales y relaciones

| Cadena | Cliente (correo) | Vehículo (patente) | Orden (marcador) | Reparación (marcador) |
|---|---|---|---|---|
| 1 | `seed.cliente01@example.com` | `SBAB12` (Toyota Yaris) | `SEED_P5_OT_01` | `SEED_P5_REP_01` (diagnóstico; $25.000) |
| 2 | `seed.cliente02@example.com` | `SBCD34` (Hyundai Accent) | `SEED_P5_OT_02` | `SEED_P5_REP_02` (mantención; $85.000) |

Se utilizan estados `en_reparacion` y `finalizada`, tipos `diagnostico` y `mantencion`, kilometrajes no negativos y fechas de 2025 (no futuras). Todos los campos se validan usando los esquemas Pydantic existentes antes de insertarse. La inserción se realiza en orden y se ejecuta con **una sola sesión y una sola transacción**; `flush()` obtiene los ID para enlazar cada registro, y el `commit` se efectúa al finalizar correctamente.

## Verificación directa de SQLite

Puedes ejecutar los comandos siguientes sin instalar una herramienta SQL adicional:

```powershell
uv run python -c "import sqlite3; c=sqlite3.connect('taller_mecanico.db'); print({t:c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('clientes','vehiculos','ordenes_trabajo','reparaciones')}); c.close()"
```

En una base inicialmente vacía: `{'clientes': 2, 'vehiculos': 2, 'ordenes_trabajo': 2, 'reparaciones': 2}`. Con datos preexistentes, las cantidades totales pueden ser superiores a dos.

Para verificar las relaciones por SQL:

```powershell
uv run python -c "import sqlite3; c=sqlite3.connect('taller_mecanico.db'); q='SELECT c.email, v.patente, o.descripcion_problema, r.descripcion FROM clientes c JOIN vehiculos v ON v.cliente_id=c.id JOIN ordenes_trabajo o ON o.vehiculo_id=v.id JOIN reparaciones r ON r.orden_trabajo_id=o.id WHERE c.email LIKE ? ORDER BY c.email'; print(*c.execute(q, ('seed.cliente%@example.com',)).fetchall(), sep='\n'); c.close()"
```

Se esperan **dos filas**, una para cada cadena. La opción `--verificar` también comprueba que cada entidad inicial exista y su clave foránea apunte al registro esperado.

## Verificación mediante la API y persistencia

En otra terminal:

```powershell
uv run uvicorn proyectobackend.main:app --reload
```

Abrir `http://127.0.0.1:8000/docs`. Los endpoints GET existentes permiten consultar:

- `GET /clientes` (respuesta paginada; campo `items`).
- `GET /vehiculos/` (lista).
- `GET /ordenes-trabajo` (respuesta paginada; campo `items`).
- `GET /reparaciones/` (lista).

Buscar los correos, patentes y marcadores anteriores en las respuestas. Para comprobar persistencia, detener Uvicorn con `Ctrl+C`, volver a iniciar y repetir `--verificar` o los GET. **No borrar `taller_mecanico.db`**, ya que es el archivo que conserva los datos entre reinicios.

## Transacciones y prueba de rollback

Para provocar un fallo controlado y confirmar que no quede una inserción parcial:

```powershell
uv run python scripts/seed_db.py --probar-rollback
```

Resultado esperado:

```text
ROLLBACK EXITOSO: se revirtió el registro temporal tras el fallo intencional.
```

Esta prueba inicia una transacción, inserta temporalmente un cliente con correo de verificación, hace `flush()`, provoca una excepción interna y comprueba mediante otra sesión que dicho cliente **no fue guardado**. No borra ni modifica los ocho registros iniciales.

Si ocurre un error de validación, duplicidad o relación durante una carga normal, el contexto `SessionLocal.begin()` efectúa automáticamente `rollback`; el proceso devuelve código de salida 1. La excepción se muestra sin URL, contraseñas ni sentencias SQL.

## Alcance de las comprobaciones de desarrollo

En una base local SQLite aislada, con copias de los modelos ORM, esquemas Pydantic y la inicialización de `main`, se ejecutó el script: primera pasada `2/2/2/2`, segunda pasada `0/0/0/0`, consulta independiente de las dos relaciones, verificación tras iniciar un segundo proceso y prueba de rollback exitosa. También se provocó una colisión de patente con un cliente diferente: el script devolvió error y no dejó el cliente insertado antes del fallo. **Las comprobaciones SQLite descritas en este párrafo corresponden a una etapa previa**. La ejecución posterior sobre PostgreSQL aislado y las pruebas HTTP de Reparaciones están registradas a continuación.

## Alcance del seeder

El seeder existente no modifica modelos, repositorios, servicios, routers, esquemas, migraciones, configuración ni dependencias. Las reparaciones se asocian a órdenes existentes, las órdenes a vehículos existentes y los vehículos a clientes existentes. Las mejoras de documentación Swagger del módulo Reparaciones se realizan aparte, sin cambiar su lógica funcional.

## Evidencias reales de las pruebas (30/10/2026)

Las siguientes pruebas se ejecutaron **en el computador del integrante** usando Docker Compose con el proyecto independiente `taller-seeders-audit`, PostgreSQL 17 y la base `taller_seeders_audit`. Las salidas se revisaron mediante capturas de su terminal de VS Code y Swagger. **No son resultados obtenidos mediante CI ni se adjuntaron las capturas a este repositorio.**

| Comprobación | Resultado observado |
|---|---|
| Docker PostgreSQL | Contenedor `taller-seeders-audit-db-1` en estado `healthy` |
| Migración Alembic | `upgrade head` exitoso; `current` devolvió `0001 (head)` |
| Conteos iniciales (cliente/vehículo/orden/reparación) | `0 / 0 / 0 / 0` |
| Primera ejecución | `2 / 2 / 2 / 2`, ocho registros nuevos |
| Segunda ejecución | `0 / 0 / 0 / 0` registros **nuevos**; mismos IDs |
| Conteos posteriores | `2 / 2 / 2 / 2` |
| Relaciones verificadas por el script | `1 → 1 → 1 → 1` y `2 → 2 → 2 → 2` |
| Rollback intencional | `ROLLBACK EXITOSO`, registro temporal no persistió |
| Correos duplicados | PostgreSQL rechazó la inserción por `clientes_email_key`; `ROLLBACK` |
| Cliente inexistente para vehículo | PostgreSQL rechazó `cliente_id=999999` por `vehiculos_cliente_id_fkey`; `ROLLBACK` |
| Consulta SQL de huérfanos | 0 vehículos, 0 órdenes y 0 reparaciones huérfanas |
| Conteos tras ambas pruebas negativas | `2 / 2 / 2 / 2`; ninguna inserción parcial |
| `--verificar` después de las pruebas negativas | `VERIFICACIÓN EXITOSA`; ambas cadenas conservadas |

### Endpoints de Reparaciones comprobados con esta PostgreSQL de prueba

| Solicitud realizada desde Swagger | Resultado |
|---|---|
| `GET /reparaciones/` | 200; dos reparaciones iniciales (IDs 1 y 2) |
| `GET /reparaciones/1` | 200, según confirmación del integrante |
| `GET /reparaciones/999999` | 404, según confirmación del integrante |
| `POST /reparaciones/` (dato temporal asociado a orden 1) | 201; nueva reparación ID 3 |
| `PATCH /reparaciones/3` | 200; descripción y costo modificados a 20000 |
| `DELETE /reparaciones/3` | 204; respuesta sin cuerpo |
| `GET /reparaciones/3` tras eliminar | 404, error `REPAIR_NOT_FOUND` |
| `GET /reparaciones/` final | 200; solo IDs 1 y 2, con los datos iniciales |

La creación, modificación y eliminación se aplicaron **solo a la reparación temporal ID 3**. Las reparaciones 1 y 2 no se alteraron.

Las comprobaciones HTTP anteriores se realizaron contra el backend Docker de esta base PostgreSQL. Los errores 400 por fecha futura y 422 por validación fueron revisados en las pruebas del contrato HTTP con servicio simulado; **no hay evidencia de ejecución de esos dos casos contra PostgreSQL real**. Tampoco se hizo una prueba adicional de reinicio del contenedor backend sobre PostgreSQL para este cierre.

### Comandos de verificación SQL usados en esta ejecución

Aparte de `alembic` y las dos ejecuciones del seeder indicadas anteriormente, se usaron:

```powershell
docker compose -p taller-seeders-audit --env-file ../seeders-audit.env exec -T db psql -U taller_audit -d taller_seeders_audit -c "SELECT (SELECT COUNT(*) FROM clientes) AS clientes, (SELECT COUNT(*) FROM vehiculos) AS vehiculos, (SELECT COUNT(*) FROM ordenes_trabajo) AS ordenes, (SELECT COUNT(*) FROM reparaciones) AS reparaciones;"
```

Para probar restricciones se realizaron transacciones controladas `BEGIN` → `INSERT` inválido → `ROLLBACK`, solamente en la base de pruebas. Ningún fallo se provocó en una base compartida.

**Conclusión de estas evidencias:** la migración, idempotencia, referencias entre semillas, restricciones FK/UNIQUE y rollback quedaron demostrados en PostgreSQL aislado. Los escenarios HTTP no comprobados en base real quedan identificados sin declararlos aprobados.
