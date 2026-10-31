# Pruebas de la API — Taller Mecánico

En esta etapa comprobamos los principales flujos de Clientes, Vehículos, Órdenes de Trabajo y Reparaciones. Las pruebas usan `unittest`, levantan una API de prueba y trabajan con una base SQLite temporal para no alterar los datos de PostgreSQL.

## Estado de la revisión

| Verificación | Resultado |
|---|---|
| Pruebas originales | 9 de 9 correctas |
| Pruebas nuevas de revisión final | 33 de 33 correctas |
| **Total en Windows** | **42 de 42 correctas** |
| Tiempo de ejecución en Windows | 54,947 segundos |
| Errores y fallos en esa ejecución | 0 |
| Solicitudes de `docs/solicitudes.http` | 60 de 60 correctas, según la ejecución informada por Salinas |

La ejecución local en Windows terminó con:

```text
Ran 42 tests in 54.947s

OK
```

El resultado de las 60 solicitudes corresponde a la comprobación informada por el integrante a cargo. No se ejecutó de nuevo el archivo completo mediante REST Client en el computador de Windows durante esta revisión.

## Cómo ejecutar las pruebas

Desde la raíz del repositorio, con las dependencias instaladas mediante `uv`:

```powershell
uv sync --frozen
uv run --no-sync python -B -W error::ResourceWarning -m unittest discover -s tests -t . -v
```

En Linux, con el entorno virtual creado:

```bash
.venv/bin/python -B -W error::ResourceWarning -m unittest discover -s tests -t . -v
```

Los tests están distribuidos en `tests/test_clientes.py` (6), `tests/test_integracion.py` (3) y `tests/test_revision_final.py` (33). El soporte para iniciar y detener la API está en `tests/soporte_api.py`.

## Qué comprobamos

| Área | Casos revisados | Respuesta esperada |
|---|---|---|
| Clientes | Crear, consultar, actualizar y eliminar; correo duplicado; datos inválidos | `201`, `200`, `204`, `409`, `422` |
| Vehículos | CRUD, patente duplicada, cliente inexistente, eliminación con órdenes relacionadas | `201`, `200`, `204`, `404`, `409`, `422` |
| Órdenes de Trabajo | Creación y actualización, consultas, filtros, ordenamiento, paginación, reapertura de una orden finalizada | `201`, `200`, `404`, `409`, `422` |
| Reparaciones | Creación, consultas, actualización, eliminación, fechas futuras y datos inválidos | `201`, `200`, `204`, `400`, `404`, `422` |
| Integración | Relaciones Cliente → Vehículo → Orden → Reparación y persistencia tras reiniciar la API | Datos y relaciones conservados |
| Aislamiento | Uso de SQLite temporal, claves foráneas activas, separación de bases y limpieza de archivos | Sin modificar PostgreSQL |

También se comprueban respuestas JSON para los errores y cuerpos vacíos en los `DELETE` exitosos con HTTP `204`. Los métodos individuales y sus aserciones pueden revisarse directamente en `tests/test_revision_final.py`.

**Nota:** Órdenes de Trabajo no implementa `DELETE`; por eso no se inventó ese endpoint para completar la cobertura.

## Incidencias encontradas y corregidas

### 1. Eliminación de vehículos con órdenes asociadas

Durante la revisión inicial, `DELETE /vehiculos/{id}` devolvía `500 Internal Server Error` al intentar eliminar un vehículo que tenía una orden asociada. La causa fue una excepción `IntegrityError` de SQLAlchemy sin manejo específico.

La corrección incorporada mediante el [PR #36](https://github.com/cnahuelcoy/backend-2026-grupo-06/pull/36) modificó:

- `src/proyectobackend/repositories/vehiculo_repository.py`: comprueba las órdenes asociadas y ejecuta `rollback` si se produce un conflicto de integridad.
- `src/proyectobackend/routers/vehiculos.py`: devuelve HTTP `409` con el código `VEHICLE_HAS_WORK_ORDERS` y una respuesta JSON controlada.

Después de la corrección, la prueba `test_delete_vehiculo_con_ordenes_409_json_conserva_cadena` terminó con `ok` en Windows. Se comprobó que permanecieran el cliente, el vehículo, la orden y la reparación.

### 2. Limpieza de archivos temporales en Windows

La primera ejecución de la suite ampliada en Windows realizó **42 pruebas, con 9 errores de limpieza**. Los errores fueron `PermissionError: [WinError 32]`: Windows mantenía abiertos archivos como `api.log` o `taller_mecanico.db` durante la eliminación de carpetas temporales.

Se corrigió `tests/soporte_api.py` para esperar el cierre del proceso y reintentar la limpieza cuando Windows informa ese bloqueo. Los errores persistentes siguen notificándose en lugar de ocultarse. La siguiente ejecución terminó con **42 pruebas correctas y 0 errores**.

Estos dos problemas se conservan aquí como parte de la revisión; **no están pendientes en la ejecución de Windows informada arriba**.

## Archivo de solicitudes HTTP

`docs/solicitudes.http` incluye **60 solicitudes** para los cuatro módulos, con operaciones exitosas y errores esperados. Se pueden ejecutar con la extensión [REST Client para Visual Studio Code](https://github.com/Huachao/vscode-restclient).

1. Iniciar la API temporal con el soporte de pruebas, desde la raíz del repositorio:

   ```powershell
   @'
   from threading import Event
   from tests.soporte_api import ApiDePrueba

   with ApiDePrueba() as api:
       print(f"@baseUrl = {api.url}", flush=True)
       try:
           Event().wait()
       except KeyboardInterrupt:
           pass
   '@ | uv run --no-sync python -B -
   ```

2. Copiar la URL local que aparezca en la terminal y reemplazar `@baseUrl` al inicio de `docs/solicitudes.http`. El puerto `1` es solo un marcador.
3. Ejecutar las solicitudes en el orden indicado mediante **Send Request**. Las variables `{{clienteId}}`, `{{vehiculoId}}`, `{{ordenId}}` y `{{reparacionId}}` toman los identificadores de respuestas anteriores.
4. Detener la API temporal con `Ctrl+C` y volver a iniciarla desde una base vacía antes de repetir toda la secuencia.

**Importante:** usar únicamente la API temporal. Las solicitudes incluyen altas, cambios y eliminaciones; no deben ejecutarse contra PostgreSQL compartido ni contra el contenedor Docker que tenga datos del equipo.

## Base de datos utilizada

Las pruebas automatizadas crean bases SQLite independientes en directorios temporales. El soporte comprueba la ruta de la base y habilita las claves foráneas; no utiliza las credenciales de PostgreSQL. También se probaron los reinicios de la API para verificar que los registros y las relaciones persistan dentro de la misma base temporal.

Esto permite afirmar que la **suite de pruebas automatizadas se ejecutó aislada de PostgreSQL**. No equivale a una auditoría completa de PostgreSQL o Docker: esas comprobaciones se documentan por separado en [`docs/seeders.md`](seeders.md).

## Resultado

**APROBADO en los escenarios ejecutados.** Las 42 pruebas automatizadas pasaron en Windows. La ejecución de las 60 solicitudes fue informada como satisfactoria por Salinas. La documentación conserva los fallos iniciales y sus correcciones para dejar trazabilidad del trabajo.
