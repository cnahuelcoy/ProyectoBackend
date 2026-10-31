Revisión final de pruebas: Taller Mecánico
Fecha: 30 de octubre de 2026, America/Santiago.
Estado de la entrega
APROBADO según los resultados posteriores a la corrección comunicados para el PR #36: 42/42 pruebas automatizadas y 60/60 solicitudes HTTP aprobadas, sin casos fallidos reportados en la verificación posterior.

Alcance de la evidencia: las cifras finales fueron comunicadas por el responsable de la corrección. Los registros de consola conservados más abajo corresponden a ejecuciones anteriores al arreglo y no deben presentarse como la situación actual. Para una trazabilidad completa, adjuntar al PR los logs de las ejecuciones finales si están disponibles; aquí no se inventan salidas, tiempos ni rutas de archivos.

La incidencia HTTP 500 al borrar un vehículo con órdenes asociadas quedó resuelta en el PR #36. Se conserva su diagnóstico y evidencia original como historial de regresión.

Rama de trabajo informada: Matias-Salinas. PR: #36 (actualizar su descripción; sin merge). No se ejecutaron comandos Git ni se modificó código durante esta actualización documental.
Archivos creados o modificados
Archivos de la revisión QA original:
- tests/test_revision_final.py: 33 pruebas nuevas con unittest.
- tests/soporte_api.py: aislamiento con SQLite temporal, verificación de claves foráneas y respuestas HTTP.
- docs/solicitudes.http: 60 solicitudes para los cuatro módulos.
- docs/pruebas.md: resultados, comandos, evidencias e historial de incidencias (actualizado en esta revisión documental).
Corrección posterior del PR #36: se informa que fueron modificados dos archivos del módulo Vehículos para resolver el HTTP 500. Sus rutas exactas no constan en este documento original; deben incorporarse desde la pestaña Files changed del PR #36, sin adivinarlas.

Esta actualización no cambia código, pruebas, dependencias, migraciones ni reglas de negocio. Las nueve pruebas originales y las 33 nuevas integran los 42 casos totales.
Historial de ejecuciones anteriores a la corrección
La primera ejecución se realizó en el repositorio con el soporte original:

env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -m unittest discover -s tests -t . -v

El entorno restringido bloqueó la creación de sockets; ningún endpoint llegó

a ejecutarse en ese intento:

PermissionError: [Errno 1] Operation not permitted

Ran 9 tests in 1.078s

FAILED (errors=9)

Se repitió el mismo comando con acceso a sockets de 127.0.0.1:

Ran 9 tests in 6.871s

OK

Primera ejecución ampliada, desde /tmp/taller-qa-yskVcd:

env PYTHONDONTWRITEBYTECODE=1 /home/matias/Documentos/GitHub/ProyectoBackend/.venv/bin/python -B -m unittest discover -s tests -t . -v


Ran 42 tests in 30.500s

FAILED (failures=1)

En esa ejecución apareció un ResourceWarning por una conexión SQLite de la

prueba SQL que no se cerraba. Se corrigió usando contextlib.closing en las

pruebas. La verificación final ya no presenta esa advertencia.

Verificación previa a la corrección, desde la misma carpeta temporal:

env PYTHONDONTWRITEBYTECODE=1 /home/matias/Documentos/GitHub/ProyectoBackend/.venv/bin/python -B -W error::ResourceWarning -m unittest discover -s tests -t . -v > /tmp/taller-qa-yskVcd/resultados_unittest.log 2>&1

Salida histórica real de esa ejecución previa:

AssertionError: 500 != 409 : {'endpoint': '/vehiculos/1', 'entrada': None, 'HTTP_esperado': 409, 'HTTP_obtenido': 500, 'content_type': 'text/plain', 'respuesta': 'Internal Server Error'}

Ran 42 tests in 30.818s

FAILED (failures=1)

El código de salida de aquella ejecución anterior fue 1 por el fallo entonces detectado. No se marca como

expectedFailure ni se cambia la expectativa para ocultarlo. Las nueve pruebas

originales también pasan con las claves foráneas activas. Los subTest verifican

variantes adicionales; no se cuentan como pruebas independientes.

Para ejecutar la suite desde la raíz del repositorio:

env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -W error::ResourceWarning -m unittest discover -s tests -t . -v

En Windows, con las dependencias instaladas:

uv run --no-sync python -B -W error::ResourceWarning -m unittest discover -s tests -t . -v

### Verificación histórica en el repositorio (previa al arreglo)

Después de incorporar los cuatro archivos se ejecutó, desde

/home/matias/Documentos/GitHub/ProyectoBackend:

env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B -W error::ResourceWarning -m unittest discover -s tests -t . -v > /tmp/taller-qa-yskVcd/resultados_unittest_repositorio.log 2>&1

Resultado registrado antes de corregir el HTTP 500:

FAIL: test_delete_vehiculo_con_ordenes_409_json_conserva_cadena

AssertionError: 500 != 409 : {'endpoint': '/vehiculos/1', 'entrada': None, 'HTTP_esperado': 409, 'HTTP_obtenido': 500, 'content_type': 'text/plain', 'respuesta': 'Internal Server Error'}

Ran 42 tests in 47.562s

FAILED (failures=1)

Resumen histórico de esta ejecución previa: 9 pruebas originales exitosas y 32 de las 33 nuevas

exitosas; total 41 exitosas, 1 fallida y 0 errores de ejecución. Sin advertencias

ResourceWarning. Código de salida: 1. Los intentos y repeticiones anteriores

no representan casos adicionales; la suite contiene 42 pruebas distintas.
Las 33 pruebas nuevas
En la ejecución histórica todos estos casos pasaron salvo QA08. Tras la corrección se reportaron 42/42 aprobados, incluido QA08. Los nombres completos de

los métodos están en tests/test_revision_final.py y en el registro de ejecución.

| Caso | Qué verifica |

|---|---|

| QA01 | DELETE de cliente existente: 204 sin cuerpo; GET y segundo DELETE: 404. |

| QA02 | DELETE de vehículo sin órdenes: 204; el cliente permanece. |

| QA03 | DELETE de reparación existente: 204; la orden permanece. |

| QA04 | DELETE de cliente inexistente: 404 con JSON controlado. |

| QA05 | DELETE de vehículo inexistente: 404 con JSON controlado. |

| QA06 | DELETE de reparación inexistente: 404 con JSON controlado. |

| QA07 | DELETE de cliente con vehículo: 409 y relación conservada. |

| QA08 | DELETE de vehículo con orden: se espera 409 JSON y cadena conservada. antes fallaba con 500/text/plain; incidencia resuelta posteriormente (409 JSON esperado). |

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
Endpoints comprobados
Las respuestas siguientes describen los escenarios cubiertos. El HTTP 500 mencionado en la evidencia histórica ya fue corregido según los resultados posteriores reportados:

| Módulo | Resultados observados |

|---|---|

| Clientes | POST 201; GET y PATCH 200; DELETE sin vehículos 204; inexistentes 404; duplicado y borrado con vehículos 409; entradas inválidas 422. |

| Vehículos | POST 201; GET y PATCH 200; DELETE sin órdenes 204; inexistentes 404; patente duplicada 409; entradas inválidas 422. DELETE con órdenes: 409 JSON esperado (antes 500/text/plain; corregido). |

| Órdenes | POST 201; GET, listado y PATCH 200; referencias inexistentes 404; reapertura de finalizada a pendiente o en_reparacion 409; entradas inválidas 422. No ofrece DELETE. |

| Reparaciones | POST 201; GET y PATCH 200; DELETE 204; inexistentes o referencia inexistente 404; fecha futura 400; entradas inválidas 422. |

Los errores esperados que pasaron incluyen Content-Type: application/json y un

objeto error con code, message y details. Los DELETE 204 no incluyen cuerpo.

Antes de la corrección, Vehículos devolvía text/plain y Internal Server Error; esa salida queda documentada solo como evidencia histórica.
Incidencia de Vehículos — RESUELTA (historial)
- Endpoint: DELETE /vehiculos/1 en una base temporal recién creada.
- Entrada del DELETE: sin cuerpo; el ID procede de la respuesta de creación.
- Preparación: cliente Ana Pruebas, teléfono 912345678, email
  ana.revision@example.com, dirección Calle QA 123; vehículo QA0001, Toyota
  Yaris, año 2020, kilometraje 120000, asociado al cliente; orden pendiente del
  vehículo con fecha 2024-01-10, descripción Revisar los frenos y kilometraje
  de ingreso 120000; reparación Cambio de pastillas, tipo mantencion, costo
  45000 y fecha 2024-01-11, asociada a la orden.
- Esperado: HTTP 409 con JSON controlado y conservación de los registros.
- Obtenido antes de corregir: HTTP 500, Content-Type: text/plain, cuerpo Internal Server Error.
- Integridad: los GET de cliente, vehículo, orden y reparación conservan los
  mismos registros después del intento y responden 200.
- Evidencia del servidor: sqlite3.IntegrityError: FOREIGN KEY constraint failed,
  propagado como sqlalchemy.exc.IntegrityError al ejecutar
  DELETE FROM vehiculos WHERE vehiculos.id = ?.
- Causa: el repositorio elimina y confirma sin comprobar órdenes; el servicio
  tampoco las comprueba y el router solo captura LookupError. La excepción de
  integridad no se transforma en una respuesta HTTP de negocio.
- El contrato esperado es 409; no se inventa un código de error nuevo.
- Alcance: reproducido con SQLite temporal y FK activas. PostgreSQL no se ejecutó.
- Corrección propuesta al responsable: impedir el borrado con órdenes y devolver
  un conflicto JSON controlado. Este módulo permanece sin modificaciones.
Ejecutar el archivo HTTP sin tocar datos reales
El archivo contiene 60 solicitudes para los cuatro módulos, con éxitos, errores

400, 404, 409 y 422, y el caso de regresión del antiguo HTTP 500, ahora resuelto. Los comentarios

Esperado expresan expectativas, no resultados aprobados.

Desde la raíz del repositorio, iniciar la API aislada:

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

Abrir docs/solicitudes.http con REST Client de VS Code.

Copiar la línea @baseUrl impresa por ese proceso temporal. Enviar las solicitudes

01 a 60 en orden con Send Request. Los IDs se extraen de las respuestas de

creación mediante variables de solicitud.

El puerto 1 inicial es un marcador; no reemplazarlo por la API Docker con datos

reales. Reiniciar la API temporal antes de repetir el archivo completo.

Antes del arreglo se reprodujeron las 60 solicitudes con un verificador temporal que lee el archivo,

resuelve las variables y llama a la API aislada. Se verificó primero la copia

temporal y después el archivo incorporado al repositorio. Comando de esta última

verificación, ejecutado desde la raíz del repositorio:

env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B /tmp/taller-qa-yskVcd/verificar_http.py /home/matias/Documentos/GitHub/ProyectoBackend > /tmp/taller-qa-yskVcd/resultados_http_repositorio.log 2>&1


vehiculoConOrden: esperado=409 obtenido=500 FALLO

Solicitudes: 60; correctas: 59; fallidas: 1

También se comprobó JSON de errores, cuerpo vacío en 204 y conservación del

estado finalizada tras los rechazos. No se ejecutó la interfaz gráfica de la

extensión. El verificador y sus resultados permanecen en /tmp; la reproducción

entregada en el repositorio es el archivo .http y las instrucciones anteriores.

Código de salida de aquella ejecución anterior: 1 por la incidencia de Vehículos, posteriormente resuelta. Estas 60 solicitudes

no se suman a los 42 casos de unittest.
Aislamiento y PostgreSQL
Cada prueba crea su carpeta con TemporaryDirectory, fija una URL SQLite

absoluta y reemplaza PYTHONPATH por el src correspondiente. Antes de abrir la

base, el subproceso verifica el motor y la ruta. Un listener activa y comprueba

las claves foráneas en cada conexión. aislamiento.json registra el motor, la

ruta y claves_foraneas=1 dentro de esa carpeta temporal.

QA33 parte con una URL PostgreSQL ficticia sin credenciales y comprueba su

sustitución por SQLite, la independencia entre dos APIs y la eliminación de la

carpeta al cerrar. QA32 abre SQLite con mode=ro, verifica las relaciones por

JOIN y ejecuta PRAGMA foreign_key_check sin encontrar referencias huérfanas.

No se leen .env, no se conecta a PostgreSQL, no se arrancan contenedores ni se

ejecutan migraciones o seeders. Se verificó el aislamiento de las pruebas; no se

hizo una comparación antes/después de los datos reales de PostgreSQL. Esta

revisión no acredita compatibilidad completa con PostgreSQL o Docker.

Además, se compararon huellas SHA-256 antes y después de la ejecución: el archivo

SQLite local preexistente permaneció idéntico. El código de todos los módulos de

la API, las nueve pruebas originales, pyproject.toml y uv.lock también

conservan sus huellas originales. Los únicos archivos existentes modificados

son tests/soporte_api.py y docs/pruebas.md; los otros dos son nuevos.
PR #36 y cierre documental
PR #36: la corrección del HTTP 500 de Vehículos fue revisada y se informa que afecta a dos archivos del módulo. La descripción del PR debe reflejar expresamente ambos archivos (con sus rutas reales), el comportamiento anterior y corregido, y los resultados posteriores:
- Suite automatizada: 42 ejecutadas, 42 aprobadas, 0 fallidas (resultado comunicado).
- Archivo HTTP: 60 ejecutadas, 60 aprobadas, 0 fallidas (resultado comunicado).
- Incidencia anterior: DELETE /vehiculos/{id} con órdenes relacionadas devolvía HTTP 500, text/plain; resuelta tras la corrección, con rechazo HTTP 409 en JSON según contrato esperado.
- Evidencias históricas: comandos, salidas y diagnóstico registrados en las secciones anteriores.
- Evidencia final pendiente de adjuntar: salida o log de la corrida 42/42 y del verificador HTTP 60/60, con sus comandos exactos si difieren de los ya documentados. No se dispone aquí de la salida de esas corridas posteriores.
Sin merge. Actualización limitada a documentación; no cambiar código ni tests. El PR queda para nueva revisión del responsable.

Resultado final comunicado: APROBADO (42/42 y 60/60).