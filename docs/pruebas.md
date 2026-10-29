# Parte 5: Pruebas de la API

Para esta parte preparé nueve pruebas con `unittest`. Cubren clientes y el flujo
Cliente → Vehículo → Orden de Trabajo → Reparación. Cada prueba usa una SQLite
temporal y crea los datos que necesita mediante la API.

Los archivos son [test_clientes.py](../tests/test_clientes.py),
[test_integracion.py](../tests/test_integracion.py) y
[soporte_api.py](../tests/soporte_api.py). No se agregaron dependencias ni se
cambiaron los módulos de otros integrantes.

## Reglas que se revisaron

Los casos se basan en los routers, schemas y services actuales:

| Módulo | Validaciones y reglas |
|---|---|
| Clientes | Nombre y apellido de 2 a 50 caracteres, teléfono de 8 a 15, dirección de 3 a 100 y email válido. El correo debe ser único; su búsqueda ignora mayúsculas. |
| Vehículos | Patente única de 6 caracteres, marca y modelo no vacíos, año entre 1886 y 2027, kilometraje no negativo y cliente_id positivo de un cliente existente. |
| Órdenes | vehiculo_id positivo de un vehículo existente, fecha válida, descripción de al menos 5 caracteres y kilometraje no negativo. Los estados son pendiente, en_reparacion y finalizada. Una orden finalizada no puede volver a un estado anterior. |
| Reparaciones | orden_trabajo_id positivo de una orden existente, descripción de al menos 5 caracteres y costo no negativo. Los tipos son reparacion, mantencion y diagnostico. La fecha no puede ser futura. |

El listado de clientes filtra por nombre completo sin distinguir mayúsculas.
Permite ordenar por id, nombre, apellido o email, en dirección asc o desc.
La página parte en 1 y el límite permitido va de 1 a 100.

Las rutas usadas son `/clientes`, `/vehiculos/`, `/ordenes-trabajo` y
`/reparaciones/`. Para consultar un registro se agrega su ID a la ruta.
También se usa `PATCH /clientes/{id}` para la actualización.

## Cómo ejecutar las pruebas

Se necesita Python 3.13 o superior y las dependencias del proyecto.
Si aún no está preparado el entorno, ejecutar desde la raíz:

```bash
uv sync --frozen
```

Para correr las nueve pruebas:

```bash
.venv/bin/python -B -m unittest discover -s tests -t . -v
```

En Windows, usando uv:

```powershell
uv run python -B -m unittest discover -s tests -t . -v
```

El 28 de octubre de 2026 la ejecución local terminó con este resultado,
mostrado en la captura de la terminal:

```text
Ran 9 tests in 12.780s

OK
```

Después de fijar `DATABASE_URL`, se repitieron las nueve pruebas en Linux:
terminaron con `OK` en 12.692 segundos.

Los nueve casos pasaron. La tabla siguiente resume lo comprobado por sus
aserciones. Los IDs se toman de las respuestas de la API; no se usan IDs fijos
para los registros creados. El tiempo puede cambiar en otra ejecución.

## Resultados

| Caso y objetivo | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|
| P01: crear un cliente | POST 201, ID entero positivo y datos iguales a los enviados. | HTTP 201; el cliente Ana Perez recibió un ID positivo y conservó sus datos. | Aprobado |
| P02: consultar un cliente | GET 200 y el mismo registro creado para el caso. | HTTP 200; la respuesta coincidió con el cliente Luis Soto creado antes de consultar. | Aprobado |
| P03: actualizar un cliente | PATCH 200 y GET 200, con teléfono y dirección nuevos y los demás campos iguales. | Ambos respondieron 200; se guardaron los cambios de Carla Rojas y se conservaron los demás campos. | Aprobado |
| P04: consultar un ID inexistente | GET 404, código CLIENT_NOT_FOUND y mensaje Cliente no encontrado. | HTTP 404; coincidieron el código y el mensaje. | Aprobado |
| P05: repetir un correo | Segundo POST 409, código CLIENT_EMAIL_ALREADY_EXISTS y un solo cliente guardado. | HTTP 409; el GET posterior respondió 200 y mostró únicamente el cliente original. | Aprobado |
| P06: enviar un email inválido | POST 422, código VALIDATION_ERROR con detalle en email y ningún registro guardado. | HTTP 422; coincidieron el mensaje y el campo del error. El GET respondió 200 con total=0 e items=[]. | Aprobado |
| P07: filtrar, ordenar y paginar | Dos GET 200, apellidos en el orden indicado y metadatos correctos en ambas páginas. | Ambos respondieron 200; coincidieron todos los registros, total=4, pagina, limite=2 y total_paginas=2. | Aprobado |
| P08: comprobar persistencia | Un proceso nuevo sobre la misma SQLite y cuatro GET 200 con los registros anteriores al reinicio. | Cambió el PID, se conservó el archivo y los cuatro GET respondieron 200 con los mismos datos e IDs. | Aprobado |
| P09: comprobar las relaciones | Cuatro GET 200 y coincidencia de los IDs de cliente, vehículo y orden asociados. | Los cuatro GET respondieron 200 y las tres relaciones coincidieron. | Aprobado |

Todas las creaciones válidas de preparación comprueban HTTP 201. P07 crea seis
clientes; P08 y P09 crean un registro de cada módulo. La última ejecución no
presentó fallos.

## Datos usados en cada caso

Para P01, P02, P03, P05 y P06 se envían estos cuerpos a `POST /clientes`:

| Caso | nombre | apellido | telefono | email | direccion |
|---|---|---|---|---|---|
| P01 | Ana | Perez | 912345678 | ana.pruebas@example.com | Calle Pruebas 123 |
| P02 | Luis | Soto | 923456789 | luis.pruebas@example.com | Calle Pruebas 456 |
| P03 | Carla | Rojas | 934567890 | carla.pruebas@example.com | Calle Pruebas 789 |
| P05 | Pedro | Munoz | 956789012 | pedro.pruebas@example.com | Calle Pruebas 101 |
| P06 | Elena | Diaz | 967890123 | correo-invalido | Calle Pruebas 202 |

P01 revisa la respuesta de creación. P02 consulta `GET /clientes/{id}`.
P03 envía este cambio a `PATCH /clientes/{id}` y luego consulta el cliente:

```json
{
  "telefono": "945678901",
  "direccion": "Avenida Taller 100"
}
```

P04 consulta `GET /clientes/999999` en una base vacía.

P05 repite exactamente el mismo POST de Pedro Munoz. El mensaje esperado y
obtenido es `Ya existe un cliente registrado con este correo`. Después consulta
el listado y comprueba que solo esté el cliente original.

P06 usa `correo-invalido`. El mensaje esperado y obtenido es
`Los datos de la solicitud no son válidos`, con un detalle cuya `loc` sea
`["body", "email"]`. Después consulta el listado para comprobar que siga vacío.

### P07: listado

Se crean estos seis clientes. Todos usan teléfono `972345678` y dirección
`Calle Listado 100`:

| nombre | apellido | email |
|---|---|---|
| Ana | Zulu | ana.zulu@example.com |
| Luis | Perez | luis.perez@example.com |
| Ana | Bravo | ana.bravo@example.com |
| ANA | Alba | ana.alba@example.com |
| Ana | Mora | ana.mora@example.com |
| Anabel | Abarca | anabel.abarca@example.com |

Se hacen las dos consultas:

```text
GET /clientes?nombre=ana&ordenar_por=apellido&direccion=desc&pagina=1&limite=2
GET /clientes?nombre=ana&ordenar_por=apellido&direccion=desc&pagina=2&limite=2
```

El filtro debe incluir Ana y ANA, y dejar fuera a Luis y Anabel. Estos fueron
los valores esperados y obtenidos:

| Página | Apellidos, en orden | total | pagina | limite | total_paginas |
|---|---|---|---|---|---|
| 1 | Zulu, Mora | 4 | 1 | 2 | 2 |
| 2 | Bravo, Alba | 4 | 2 | 2 | 2 |

La prueba compara la respuesta completa, incluidos todos los campos de cada
cliente y los metadatos.

### P08 y P09: persistencia y relaciones

Cada caso crea su propia cadena con estos datos:

| Recurso | POST | Datos |
|---|---|---|
| Cliente | /clientes | nombre=Marta; apellido=Torres; telefono=978901234; email=marta.integracion@example.com; direccion=Calle Integracion 303 |
| Vehículo | /vehiculos/ | patente=TEST01; marca=Toyota; modelo=Yaris; anio=2020; kilometraje=120000; cliente_id=ID recibido al crear el cliente |
| Orden | /ordenes-trabajo | vehiculo_id=ID recibido al crear el vehículo; fecha_ingreso=2024-01-10; descripcion_problema=Revisar frenos del vehiculo; estado=pendiente; kilometraje_ingreso=120000 |
| Reparación | /reparaciones/ | orden_trabajo_id=ID recibido al crear la orden; descripcion=Cambio de pastillas de freno; tipo=mantencion; costo=45000.0; fecha=2024-01-11 |

P08 guarda el PID y la ruta de la base. Después detiene la API, espera su salida
y la vuelve a iniciar en la misma carpeta. Comprueba que el PID cambie y consulta
los cuatro registros por ID. Todos deben responder 200 y conservar sus datos,
sin volver a crearlos después del reinicio.

P09 consulta los cuatro registros por ID y compara sus datos con los creados.
También comprueba estas relaciones en las respuestas:

```text
vehiculo.cliente_id == cliente.id
orden.vehiculo_id == vehiculo.id
reparacion.orden_trabajo_id == orden.id
```

## Cómo repetir un solo caso

Desde la raíz del proyecto, usar el comando correspondiente:

| Caso | Comando |
|---|---|
| P01 | `.venv/bin/python -B -m unittest tests.test_clientes.TestClientes.test_crear_cliente_exitosamente -v` |
| P02 | `.venv/bin/python -B -m unittest tests.test_clientes.TestClientes.test_obtener_cliente_existente -v` |
| P03 | `.venv/bin/python -B -m unittest tests.test_clientes.TestClientes.test_actualizar_cliente_existente -v` |
| P04 | `.venv/bin/python -B -m unittest tests.test_clientes.TestClientes.test_obtener_cliente_inexistente_devuelve_404 -v` |
| P05 | `.venv/bin/python -B -m unittest tests.test_clientes.TestClientes.test_crear_cliente_con_email_duplicado_devuelve_409 -v` |
| P06 | `.venv/bin/python -B -m unittest tests.test_clientes.TestClientes.test_crear_cliente_con_email_invalido_devuelve_422 -v` |
| P07 | `.venv/bin/python -B -m unittest tests.test_integracion.TestIntegracion.test_listado_con_filtro_orden_y_paginacion -v` |
| P08 | `.venv/bin/python -B -m unittest tests.test_integracion.TestIntegracion.test_persistencia_de_los_cuatro_modulos_tras_reinicio -v` |
| P09 | `.venv/bin/python -B -m unittest tests.test_integracion.TestIntegracion.test_relacion_cliente_vehiculo_orden_reparacion -v` |

En cada ejecución individual se espera una prueba y `OK`.

## Preparación y limpieza de los datos

Antes de cada prueba, `setUp()` crea una carpeta temporal y arranca allí la API.
La ruta `sqlite:///./taller_mecanico.db` hace que SQLite se guarde dentro de esa
carpeta. El arranque normal crea las tablas y cada caso prepara sus registros
mediante POST. No se usan seeders ni migraciones pendientes.

Cada caso empieza con su propia base vacía. `addCleanup(self.api.cerrar)` cierra
el proceso y elimina la carpeta con la base y sus archivos, aunque falle una
aserción. No hay que borrar registros de la base real.

En P08 la carpeta se conserva durante el reinicio y se elimina al terminar la
prueba.

Si una prueba futura falla, se debe guardar la salida y anotar la entrada, el
resultado esperado, el obtenido, el estado HTTP y el archivo responsable. Si el
problema está en otro módulo, se propone la corrección para revisarla con su
integrante.
