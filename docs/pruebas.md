# Revisión final de pruebas: Taller Mecánico

Fecha: 30 de octubre de 2026, America/Santiago.

## Estado de la entrega

**REQUIERE CORRECCIONES.** La suite final ejecutó 42 pruebas: 41 exitosas,
1 fallida y 0 errores de ejecución. El fallo es el borrado de un vehículo con
órdenes asociadas: devuelve HTTP 500 en texto plano en lugar de un rechazo JSON.

Los cuatro archivos autorizados ya están incorporados al repositorio, siguiendo
la instrucción del usuario de aplicar los cambios. La rama observada es
`Matias-Salinas`. Git corresponde exclusivamente al usuario: no se ejecutaron
comandos Git, commits, push, creación de PR ni merge. La creación de una rama
nueva desde `main` y la publicación del trabajo quedan pendientes a su cargo.

## Archivos creados o modificados

- `tests/test_revision_final.py`: 33 pruebas nuevas con `unittest`.
- `tests/soporte_api.py`: URL SQLite absoluta, comprobación del motor y su ruta,
  claves foráneas activas en cada conexión, evidencia temporal del aislamiento,
  tipo de contenido de las respuestas y acceso a la URL de la API temporal.
- `docs/solicitudes.http`: 60 solicitudes encadenadas para los cuatro módulos.
- `docs/pruebas.md`: resultados, incidencia, instrucciones y límites de la revisión.

Las nueve pruebas originales permanecen sin cambios. No se modifica código de
Clientes, Vehículos, Reparaciones u Órdenes de Trabajo, configuración de
producción, migraciones ni reglas de negocio. No se agregan dependencias,
credenciales, archivos `.env` ni bases de datos.

## Ejecuciones y resultados reales

La primera ejecución se realizó en el repositorio con el soporte original:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m unittest discover -s tests -t . -v
```

El entorno restringido bloqueó la creación de sockets; ningún endpoint llegó
a ejecutarse en ese intento:

```text
PermissionError: [Errno 1] Operation not permitted
Ran 9 tests in 1.078s
FAILED (errors=9)
```

Se repitió el mismo comando con acceso a sockets de `127.0.0.1`:

```text
Ran 9 tests in 6.871s
OK
```

Primera ejecución ampliada, desde `/tmp/taller-qa-yskVcd`:

```bash
env PYTHONDONTWRITEBYTECODE=1 /home/matias/Documentos/GitHub/ProyectoBackend/.venv/bin/python -B -m unittest discover -s tests -t . -v
```

```text
Ran 42 tests in 30.500s
FAILED (failures=1)
```

En esa ejecución apareció un `ResourceWarning` por una conexión SQLite de la
prueba SQL que no se cerraba. Se corrigió usando `contextlib.closing` en las
pruebas. La verificación final ya no presenta esa advertencia.

Verificación final, desde la misma carpeta temporal:

```bash
env PYTHONDONTWRITEBYTECODE=1 /home/matias/Documentos/GitHub/ProyectoBackend/.venv/bin/python -B -W error::ResourceWarning -m unittest discover -s tests -t . -v > /tmp/taller-qa-yskVcd/resultados_unittest.log 2>&1
```

Salida real relevante:

```text
AssertionError: 500 != 409 : {'endpoint': '/vehiculos/1', 'entrada': None, 'HTTP_esperado': 409, 'HTTP_obtenido': 500, 'content_type': 'text/plain', 'respuesta': 'Internal Server Error'}
Ran 42 tests in 30.818s
FAILED (failures=1)
```

El código de salida es 1 por el fallo real detectado. No se marca como
`expectedFailure` ni se cambia la expectativa para ocultarlo. Las nueve pruebas
originales también pasan con las claves foráneas activas. Los `subTest` verifican
variantes adicionales; no se cuentan como pruebas independientes.

Para ejecutar la suite desde la raíz del repositorio:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -W error::ResourceWarning -m unittest discover -s tests -t . -v
```

En Windows, con las dependencias instaladas:

```powershell
uv run --no-sync python -B -W error::ResourceWarning -m unittest discover -s tests -t . -v
```

### Verificación definitiva en el repositorio

Después de incorporar los cuatro archivos se ejecutó, desde
`/home/matias/Documentos/GitHub/ProyectoBackend`:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -W error::ResourceWarning -m unittest discover -s tests -t . -v > /tmp/taller-qa-yskVcd/resultados_unittest_repositorio.log 2>&1
```

Resultado real:

```text
FAIL: test_delete_vehiculo_con_ordenes_409_json_conserva_cadena
AssertionError: 500 != 409 : {'endpoint': '/vehiculos/1', 'entrada': None, 'HTTP_esperado': 409, 'HTTP_obtenido': 500, 'content_type': 'text/plain', 'respuesta': 'Internal Server Error'}
Ran 42 tests in 47.562s
FAILED (failures=1)
```

Resumen de esta ejecución: 9 pruebas originales exitosas y 32 de las 33 nuevas
exitosas; total 41 exitosas, 1 fallida y 0 errores de ejecución. Sin advertencias
`ResourceWarning`. Código de salida: 1. Los intentos y repeticiones anteriores
no representan casos adicionales; la suite contiene 42 pruebas distintas.

## Las 33 pruebas nuevas

Todos los casos de esta tabla pasaron salvo QA08. Los nombres completos de
los métodos están en `tests/test_revision_final.py` y en el registro de ejecución.

| Caso | Qué verifica |
|---|---|
| QA01 | DELETE de cliente existente: 204 sin cuerpo; GET y segundo DELETE: 404. |
| QA02 | DELETE de vehículo sin órdenes: 204; el cliente permanece. |
| QA03 | DELETE de reparación existente: 204; la orden permanece. |
| QA04 | DELETE de cliente inexistente: 404 con JSON controlado. |
| QA05 | DELETE de vehículo inexistente: 404 con JSON controlado. |
| QA06 | DELETE de reparación inexistente: 404 con JSON controlado. |
| QA07 | DELETE de cliente con vehículo: 409 y relación conservada. |
| QA08 | DELETE de vehículo con orden: se espera 409 JSON y cadena conservada. FALLA: devuelve 500, text/plain. |
| QA09 | Reabrir orden finalizada a pendiente: 409, sin guardar otros campos enviados. |
| QA10 | Reabrir orden finalizada a en_reparacion: 409 y estado conservado. |
| QA11 | PATCH válido de orden: 200, cambios persistidos y otros campos conservados. |
| QA12 | Listado de órdenes: filtro por estado, orden por fecha y dos páginas con metadatos. |
| QA13 | GET y PATCH de orden inexistente: 404 con WORK_ORDER_NOT_FOUND. |
| QA14 | POST de vehículo con cliente inexistente: 404 JSON. |
| QA15 | POST de orden con vehículo inexistente: 404 JSON. |
| QA16 | POST de reparación con orden inexistente: 404 JSON. |
| QA17 | PATCH de orden con vehículo inexistente: 404 sin modificar estado ni relación. |
| QA18 | Patente duplicada: 409 y un único vehículo guardado. |
| QA19 | POST de cliente: nombre, apellido, teléfono, email y dirección inválidos: 422 sin insertar. |
| QA20 | POST de vehículo: patente, marca, modelo, año, kilometraje e ID inválidos: 422 sin insertar. |
| QA21 | POST de orden: ID, fecha, descripción corta o en blanco, estado y kilometraje inválidos: 422 sin insertar. |
| QA22 | POST de reparación: ID, descripción, tipo, costo y fecha inválidos: 422 sin insertar. |
| QA23 | PATCH inválido de cliente: 422 sin modificar el registro. |
| QA24 | PATCH inválido de vehículo: 422 sin modificar el registro. |
| QA25 | PATCH inválido de orden: 422 sin modificar el registro. |
| QA26 | PATCH inválido de reparación: 422 sin modificar el registro. |
| QA27 | POST sin campos obligatorios: 422 en los cuatro módulos. |
| QA28 | GET con ID no numérico: 422 en los cuatro módulos. |
| QA29 | Listados de Clientes y Órdenes: página, límite, ordenamiento y dirección inválidos: 422. |
| QA30 | POST de reparación con fecha futura: 400 JSON, conservando la regla existente. |
| QA31 | PATCH de reparación con fecha futura: 400 JSON sin modificar el registro. |
| QA32 | Actualizar las cuatro entidades, reiniciar la API y comprobar datos, JOIN SQL y ausencia de referencias huérfanas. |
| QA33 | Sobrescribir URL PostgreSQL ficticia, comprobar SQLite con FK activas, aislamiento entre APIs y limpieza temporal. |

## Endpoints comprobados

Estos resultados describen exclusivamente los escenarios ejecutados:

| Módulo | Resultados observados |
|---|---|
| Clientes | POST 201; GET y PATCH 200; DELETE sin vehículos 204; inexistentes 404; duplicado y borrado con vehículos 409; entradas inválidas 422. |
| Vehículos | POST 201; GET y PATCH 200; DELETE sin órdenes 204; inexistentes 404; patente duplicada 409; entradas inválidas 422. DELETE con órdenes: 500 en texto plano. |
| Órdenes | POST 201; GET, listado y PATCH 200; referencias inexistentes 404; reapertura de finalizada a pendiente o en_reparacion 409; entradas inválidas 422. No ofrece DELETE. |
| Reparaciones | POST 201; GET y PATCH 200; DELETE 204; inexistentes o referencia inexistente 404; fecha futura 400; entradas inválidas 422. |

Los errores esperados que pasaron incluyen `Content-Type: application/json` y un
objeto `error` con `code`, `message` y `details`. Los DELETE 204 no incluyen cuerpo.
El fallo de Vehículos devuelve `text/plain` y `Internal Server Error`.

## Incidencia para el responsable de Vehículos

- Endpoint: `DELETE /vehiculos/1` en una base temporal recién creada.
- Entrada del DELETE: sin cuerpo; el ID procede de la respuesta de creación.
- Preparación: cliente Ana Pruebas, teléfono `912345678`, email
  `ana.revision@example.com`, dirección `Calle QA 123`; vehículo `QA0001`, Toyota
  Yaris, año 2020, kilometraje 120000, asociado al cliente; orden pendiente del
  vehículo con fecha `2024-01-10`, descripción `Revisar los frenos` y kilometraje
  de ingreso 120000; reparación `Cambio de pastillas`, tipo `mantencion`, costo
  45000 y fecha `2024-01-11`, asociada a la orden.
- Esperado: HTTP 409 con JSON controlado y conservación de los registros.
- Obtenido: HTTP 500, `Content-Type: text/plain`, cuerpo `Internal Server Error`.
- Integridad: los GET de cliente, vehículo, orden y reparación conservan los
  mismos registros después del intento y responden 200.
- Evidencia del servidor: `sqlite3.IntegrityError: FOREIGN KEY constraint failed`,
  propagado como `sqlalchemy.exc.IntegrityError` al ejecutar
  `DELETE FROM vehiculos WHERE vehiculos.id = ?`.
- Causa: el repositorio elimina y confirma sin comprobar órdenes; el servicio
  tampoco las comprueba y el router solo captura `LookupError`. La excepción de
  integridad no se transforma en una respuesta HTTP de negocio.
- El contrato esperado es 409; no se inventa un código de error nuevo.
- Alcance: reproducido con SQLite temporal y FK activas. PostgreSQL no se ejecutó.
- Corrección propuesta al responsable: impedir el borrado con órdenes y devolver
  un conflicto JSON controlado. Este módulo permanece sin modificaciones.

## Ejecutar el archivo HTTP sin tocar datos reales

El archivo contiene 60 solicitudes para los cuatro módulos, con éxitos, errores
400, 404, 409 y 422, y el caso de regresión que devuelve 500. Los comentarios
`Esperado` expresan expectativas, no resultados aprobados.

Desde la raíz del repositorio, iniciar la API aislada:

```bash
.venv/bin/python -B - <<'PY'
from threading import Event
from tests.soporte_api import ApiDePrueba

with ApiDePrueba() as api:
    print(f"@baseUrl = {api.url}", flush=True)
    print("API temporal lista. Ctrl+C para detener y eliminar sus datos.", flush=True)
    try:
        Event().wait()
    except KeyboardInterrupt:
        pass
PY
```

Abrir `docs/solicitudes.http` con [REST Client de VS Code](https://github.com/Huachao/vscode-restclient#usage).
Copiar la línea `@baseUrl` impresa por ese proceso temporal. Enviar las solicitudes
01 a 60 en orden con `Send Request`. Los IDs se extraen de las respuestas de
creación mediante [variables de solicitud](https://github.com/Huachao/vscode-restclient#request-variables).
El puerto 1 inicial es un marcador; no reemplazarlo por la API Docker con datos
reales. Reiniciar la API temporal antes de repetir el archivo completo.

Se reprodujeron las 60 solicitudes con un verificador temporal que lee el archivo,
resuelve las variables y llama a la API aislada. Se verificó primero la copia
temporal y después el archivo incorporado al repositorio. Comando de esta última
verificación, ejecutado desde la raíz del repositorio:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B /tmp/taller-qa-yskVcd/verificar_http.py /home/matias/Documentos/GitHub/ProyectoBackend > /tmp/taller-qa-yskVcd/resultados_http_repositorio.log 2>&1
```

```text
vehiculoConOrden: esperado=409 obtenido=500 FALLO
Solicitudes: 60; correctas: 59; fallidas: 1
```

También se comprobó JSON de errores, cuerpo vacío en 204 y conservación del
estado finalizada tras los rechazos. No se ejecutó la interfaz gráfica de la
extensión. El verificador y sus resultados permanecen en `/tmp`; la reproducción
entregada en el repositorio es el archivo `.http` y las instrucciones anteriores.
Código de salida: 1 por la misma incidencia de Vehículos. Estas 60 solicitudes
no se suman a los 42 casos de `unittest`.

## Aislamiento y PostgreSQL

Cada prueba crea su carpeta con `TemporaryDirectory`, fija una URL SQLite
absoluta y reemplaza `PYTHONPATH` por el `src` correspondiente. Antes de abrir la
base, el subproceso verifica el motor y la ruta. Un listener activa y comprueba
las claves foráneas en cada conexión. `aislamiento.json` registra el motor, la
ruta y `claves_foraneas=1` dentro de esa carpeta temporal.

QA33 parte con una URL PostgreSQL ficticia sin credenciales y comprueba su
sustitución por SQLite, la independencia entre dos APIs y la eliminación de la
carpeta al cerrar. QA32 abre SQLite con `mode=ro`, verifica las relaciones por
JOIN y ejecuta `PRAGMA foreign_key_check` sin encontrar referencias huérfanas.

No se leen `.env`, no se conecta a PostgreSQL, no se arrancan contenedores ni se
ejecutan migraciones o seeders. Se verificó el aislamiento de las pruebas; no se
hizo una comparación antes/después de los datos reales de PostgreSQL. Esta
revisión no acredita compatibilidad completa con PostgreSQL o Docker.

Además, se compararon huellas SHA-256 antes y después de la ejecución: el archivo
SQLite local preexistente permaneció idéntico. El código de todos los módulos de
la API, las nueve pruebas originales, `pyproject.toml` y `uv.lock` también
conservan sus huellas originales. Los únicos archivos existentes modificados
son `tests/soporte_api.py` y `docs/pruebas.md`; los otros dos son nuevos.

## Pendientes de Git

Git corresponde exclusivamente al usuario. La rama observada al aplicar los
archivos es `Matias-Salinas`. Queda pendiente gestionar la rama nueva desde
`main`, realizar commits claros, publicar la rama y crear el Pull Request hacia
`main`. La base de la rama no se verificó mediante Git. No se han creado commits
durante esta revisión y no existe un enlace de PR para informar.

Mensajes sugeridos, todavía no ejecutados:

- `test: ampliar regresiones HTTP y reforzar aislamiento SQLite`
- `docs: agregar solicitudes reproducibles e informe QA final`

No se debe hacer merge automático.

**REQUIERE CORRECCIONES:** el borrado de un vehículo con órdenes devuelve un 500
inesperado sin JSON controlado. Las nueve pruebas originales y las otras 32
pruebas nuevas pasan, pero ese fallo impide aprobar la revisión.
