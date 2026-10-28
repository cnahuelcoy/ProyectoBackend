# Parte 5 — Seeders y datos iniciales

El archivo `scripts/seed_db.py` inserta **dos clientes, dos vehículos, dos órdenes de trabajo y dos reparaciones** en SQLite, enlazados como `Cliente → Vehículo → Orden de Trabajo → Reparación`. No requiere migraciones nuevas ni modifica reglas de negocio, modelos o endpoints.

## Preparación y ejecución

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

En una base local SQLite aislada, con copias de los modelos ORM, esquemas Pydantic y la inicialización de `main`, se ejecutó el script: primera pasada `2/2/2/2`, segunda pasada `0/0/0/0`, consulta independiente de las dos relaciones, verificación tras iniciar un segundo proceso y prueba de rollback exitosa. También se provocó una colisión de patente con un cliente diferente: el script devolvió error y no dejó el cliente insertado antes del fallo. **Esas ejecuciones no son evidencia de pruebas ejecutadas en el entorno del usuario ni de los endpoints del repositorio completo**. Deben repetirse los comandos anteriores en un clon actualizado del repositorio antes del merge definitivo.

## Restricciones respetadas

Solo se agregan `scripts/seed_db.py` y `docs/seeders.md`. No se modifican modelos, repositorios, servicios, routers, esquemas, migraciones, configuración ni dependencias. Las reparaciones se asocian a órdenes existentes, las órdenes a vehículos existentes y los vehículos a clientes existentes.
