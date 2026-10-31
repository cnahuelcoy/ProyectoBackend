"""Regresiones HTTP sobre una SQLite temporal por prueba, con FK activas."""

from contextlib import closing
from datetime import date, timedelta
import json
import os
import sqlite3
import unittest
from unittest.mock import patch

from tests.soporte_api import ApiDePrueba


class TestRevisionFinal(unittest.TestCase):
    def setUp(self) -> None:
        self.api = ApiDePrueba()
        self.addCleanup(self.api.cerrar)
        self.api.iniciar()

    def _crear(self, ruta: str, datos: dict) -> dict:
        estado, cuerpo = self.api.solicitar("POST", ruta, datos)
        self.assertEqual(estado, 201, msg={"ruta": ruta, "respuesta": cuerpo})
        self.assertIsInstance(cuerpo, dict)
        return cuerpo

    def _cliente(self, **cambios) -> dict:
        return self._crear("/clientes", {
            "nombre": "Ana", "apellido": "Pruebas", "telefono": "912345678",
            "email": "ana.revision@example.com", "direccion": "Calle QA 123",
            **cambios,
        })

    def _vehiculo(self, cliente_id: int, **cambios) -> dict:
        return self._crear("/vehiculos/", {
            "patente": "QA0001", "marca": "Toyota", "modelo": "Yaris",
            "anio": 2020, "kilometraje": 120000, "cliente_id": cliente_id,
            **cambios,
        })

    def _orden(self, vehiculo_id: int, **cambios) -> dict:
        return self._crear("/ordenes-trabajo", {
            "vehiculo_id": vehiculo_id, "fecha_ingreso": "2024-01-10",
            "descripcion_problema": "Revisar los frenos", "estado": "pendiente",
            "kilometraje_ingreso": 120000, **cambios,
        })

    def _reparacion(self, orden_id: int, **cambios) -> dict:
        return self._crear("/reparaciones/", {
            "orden_trabajo_id": orden_id, "descripcion": "Cambio de pastillas",
            "tipo": "mantencion", "costo": 45000.0, "fecha": "2024-01-11",
            **cambios,
        })

    def _cadena(self) -> tuple[dict, dict, dict, dict]:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        orden = self._orden(vehiculo["id"])
        reparacion = self._reparacion(orden["id"])
        return cliente, vehiculo, orden, reparacion

    def _consultar(self, ruta: str, esperado: dict) -> None:
        estado, cuerpo = self.api.solicitar("GET", ruta)
        self.assertEqual(estado, 200, msg={"ruta": ruta, "respuesta": cuerpo})
        self.assertEqual(cuerpo, esperado)

    def _error(self, resultado: tuple, esperado: int, codigo: str | None,
               *, ruta: str, datos=None, content_type=None) -> dict:
        estado, cuerpo = resultado
        tipo = content_type or self.api.ultimo_content_type
        evidencia = {
            "endpoint": ruta, "entrada": datos, "HTTP_esperado": esperado,
            "HTTP_obtenido": estado, "content_type": tipo, "respuesta": cuerpo,
        }
        self.assertEqual(estado, esperado, msg=evidencia)
        self.assertEqual(tipo, "application/json", msg=evidencia)
        self.assertIsInstance(cuerpo, dict, msg=evidencia)
        self.assertIsInstance(cuerpo.get("error"), dict, msg=evidencia)
        error = cuerpo["error"]
        self.assertIsInstance(error.get("code"), str, msg=evidencia)
        self.assertTrue(error["code"], msg=evidencia)
        if codigo is not None:
            self.assertEqual(error["code"], codigo, msg=evidencia)
        self.assertIsInstance(error.get("message"), str)
        self.assertTrue(error["message"])
        self.assertIsInstance(error.get("details"), list)
        return error

    def _eliminar_y_consultar(self, ruta: str, codigo: str) -> None:
        estado, cuerpo = self.api.solicitar("DELETE", ruta)
        self.assertEqual(estado, 204, msg={"ruta": ruta, "respuesta": cuerpo})
        self.assertIsNone(cuerpo, msg="Un DELETE 204 debe responder sin cuerpo")
        self._error(self.api.solicitar("GET", ruta), 404, codigo, ruta=ruta)
        self._error(self.api.solicitar("DELETE", ruta), 404, codigo, ruta=ruta)

    def test_delete_cliente_existente_204_sin_cuerpo(self) -> None:
        cliente = self._cliente()
        self._eliminar_y_consultar(f"/clientes/{cliente['id']}", "CLIENT_NOT_FOUND")

    def test_delete_vehiculo_sin_ordenes_204_sin_cuerpo(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        self._eliminar_y_consultar(f"/vehiculos/{vehiculo['id']}", "VEHICLE_NOT_FOUND")
        self._consultar(f"/clientes/{cliente['id']}", cliente)

    def test_delete_reparacion_existente_204_conserva_orden(self) -> None:
        _, _, orden, reparacion = self._cadena()
        self._eliminar_y_consultar(f"/reparaciones/{reparacion['id']}", "REPAIR_NOT_FOUND")
        self._consultar(f"/ordenes-trabajo/{orden['id']}", orden)

    def test_delete_cliente_inexistente_404_json(self) -> None:
        ruta = "/clientes/999999"
        self._error(self.api.solicitar("DELETE", ruta), 404, "CLIENT_NOT_FOUND", ruta=ruta)

    def test_delete_vehiculo_inexistente_404_json(self) -> None:
        ruta = "/vehiculos/999999"
        self._error(self.api.solicitar("DELETE", ruta), 404, "VEHICLE_NOT_FOUND", ruta=ruta)

    def test_delete_reparacion_inexistente_404_json(self) -> None:
        ruta = "/reparaciones/999999"
        self._error(self.api.solicitar("DELETE", ruta), 404, "REPAIR_NOT_FOUND", ruta=ruta)

    def test_delete_cliente_con_vehiculos_409_conserva_relacion(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        ruta = f"/clientes/{cliente['id']}"
        self._error(self.api.solicitar("DELETE", ruta), 409, "CLIENT_HAS_VEHICLES", ruta=ruta)
        self._consultar(ruta, cliente)
        self._consultar(f"/vehiculos/{vehiculo['id']}", vehiculo)

    def test_delete_vehiculo_con_ordenes_409_json_conserva_cadena(self) -> None:
        cliente, vehiculo, orden, reparacion = self._cadena()
        ruta = f"/vehiculos/{vehiculo['id']}"
        resultado = self.api.solicitar("DELETE", ruta)
        tipo = self.api.ultimo_content_type
        # Comprobar la integridad incluso cuando falle el contrato HTTP.
        for prefijo, registro in (("clientes", cliente), ("vehiculos", vehiculo),
                                 ("ordenes-trabajo", orden), ("reparaciones", reparacion)):
            self._consultar(f"/{prefijo}/{registro['id']}", registro)
        self._error(resultado, 409, None, ruta=ruta, content_type=tipo)

    def _rechazar_reapertura(self, estado_nuevo: str) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        orden = self._orden(vehiculo["id"])
        ruta = f"/ordenes-trabajo/{orden['id']}"
        for estado_nuevo_valido in ("en_reparacion", "finalizada"):
            estado, finalizada = self.api.solicitar("PATCH", ruta, {"estado": estado_nuevo_valido})
            self.assertEqual(estado, 200, msg=finalizada)
            self.assertEqual(finalizada["estado"], estado_nuevo_valido)
        datos = {"estado": estado_nuevo, "descripcion_problema": "No debe guardarse"}
        self._error(self.api.solicitar("PATCH", ruta, datos), 409,
                    "INVALID_WORK_ORDER_STATE", ruta=ruta, datos=datos)
        self._consultar(ruta, finalizada)

    def test_reabrir_orden_finalizada_a_pendiente_409(self) -> None:
        self._rechazar_reapertura("pendiente")

    def test_reabrir_orden_finalizada_a_en_reparacion_409(self) -> None:
        self._rechazar_reapertura("en_reparacion")

    def test_patch_orden_valido_persiste_y_conserva_campos(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        orden = self._orden(vehiculo["id"])
        ruta = f"/ordenes-trabajo/{orden['id']}"
        cambios = {"descripcion_problema": "Revisar frenos y suspension", "kilometraje_ingreso": 120001}
        estado, cuerpo = self.api.solicitar("PATCH", ruta, cambios)
        self.assertEqual(estado, 200, msg=cuerpo)
        self.assertEqual(cuerpo, {**orden, **cambios})
        self._consultar(ruta, cuerpo)

    def test_listado_ordenes_filtra_ordena_y_pagina(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        ordenes = [self._orden(vehiculo["id"], fecha_ingreso=fecha, estado=estado)
                   for fecha, estado in (("2024-01-10", "pendiente"),
                                          ("2024-01-12", "en_reparacion"),
                                          ("2024-01-11", "pendiente"))]
        for pagina, registro in ((1, ordenes[2]), (2, ordenes[0])):
            with self.subTest(pagina=pagina):
                estado, cuerpo = self.api.solicitar("GET", "/ordenes-trabajo", parametros={
                    "estado": "pendiente", "ordenar_por": "fecha_ingreso",
                    "direccion": "desc", "pagina": pagina, "limite": 1,
                })
                self.assertEqual(estado, 200, msg=cuerpo)
                self.assertEqual(cuerpo, {"items": [registro], "total": 2,
                                         "pagina": pagina, "limite": 1, "total_paginas": 2})

    def test_orden_inexistente_get_y_patch_404_json(self) -> None:
        ruta = "/ordenes-trabajo/999999"
        for metodo, datos in (("GET", None), ("PATCH", {"estado": "en_reparacion"})):
            with self.subTest(metodo=metodo):
                self._error(self.api.solicitar(metodo, ruta, datos), 404,
                            "WORK_ORDER_NOT_FOUND", ruta=ruta, datos=datos)

    def test_crear_vehiculo_cliente_inexistente_404_json(self) -> None:
        datos = {"patente": "QA0001", "marca": "Toyota", "modelo": "Yaris",
                 "anio": 2020, "kilometraje": 0, "cliente_id": 999999}
        ruta = "/vehiculos/"
        self._error(self.api.solicitar("POST", ruta, datos), 404, "CLIENT_NOT_FOUND", ruta=ruta, datos=datos)

    def test_crear_orden_vehiculo_inexistente_404_json(self) -> None:
        datos = {"vehiculo_id": 999999, "fecha_ingreso": "2024-01-10",
                 "descripcion_problema": "Revisar frenos", "kilometraje_ingreso": 0}
        ruta = "/ordenes-trabajo"
        self._error(self.api.solicitar("POST", ruta, datos), 404, "VEHICLE_NOT_FOUND", ruta=ruta, datos=datos)

    def test_crear_reparacion_orden_inexistente_404_json(self) -> None:
        datos = {"orden_trabajo_id": 999999, "descripcion": "Revisar frenos",
                 "tipo": "diagnostico", "costo": 0, "fecha": "2024-01-11"}
        ruta = "/reparaciones/"
        self._error(self.api.solicitar("POST", ruta, datos), 404, "WORK_ORDER_NOT_FOUND", ruta=ruta, datos=datos)

    def test_patch_orden_vehiculo_inexistente_404_sin_mutacion(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        orden = self._orden(vehiculo["id"])
        ruta = f"/ordenes-trabajo/{orden['id']}"
        datos = {"vehiculo_id": 999999, "estado": "finalizada"}
        self._error(self.api.solicitar("PATCH", ruta, datos), 404, "VEHICLE_NOT_FOUND", ruta=ruta, datos=datos)
        self._consultar(ruta, orden)

    def test_patente_duplicada_409_json(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        ruta = "/vehiculos/"
        datos = {campo: valor for campo, valor in vehiculo.items() if campo != "id"}
        self._error(self.api.solicitar("POST", ruta, datos), 409,
                    "VEHICLE_LICENSE_PLATE_ALREADY_EXISTS", ruta=ruta, datos=datos)
        estado, cuerpo = self.api.solicitar("GET", ruta)
        self.assertEqual(estado, 200, msg=cuerpo)
        self.assertEqual(cuerpo, [vehiculo])

    def _validar_post(self, ruta: str, datos_validos: dict, casos: tuple) -> None:
        for campo, valor in casos:
            with self.subTest(campo=campo, valor=valor):
                datos = {**datos_validos, campo: valor}
                error = self._error(self.api.solicitar("POST", ruta, datos), 422,
                                    "VALIDATION_ERROR", ruta=ruta, datos=datos)
                self.assertTrue(any(detalle.get("loc") == ["body", campo]
                                    for detalle in error["details"]), msg=error)
                estado, listado = self.api.solicitar("GET", ruta)
                self.assertEqual(estado, 200, msg=listado)
                self.assertEqual(listado["items"] if isinstance(listado, dict) else listado, [])

    def test_post_cliente_datos_invalidos_422_sin_insertar(self) -> None:
        datos = {"nombre": "Ana", "apellido": "Pruebas", "telefono": "912345678",
                 "email": "ana.revision@example.com", "direccion": "Calle QA 123"}
        self._validar_post("/clientes", datos, (("nombre", "A"), ("apellido", "P"),
                          ("telefono", "123"), ("email", "sin-arroba"), ("direccion", "A")))

    def test_post_vehiculo_datos_invalidos_422_sin_insertar(self) -> None:
        cliente = self._cliente()
        datos = {"patente": "QA0001", "marca": "Toyota", "modelo": "Yaris",
                 "anio": 2020, "kilometraje": 0, "cliente_id": cliente["id"]}
        self._validar_post("/vehiculos/", datos, (("patente", "ABC"), ("marca", ""),
                          ("modelo", ""), ("anio", 1885), ("anio", 2028),
                          ("kilometraje", -1), ("cliente_id", 0)))

    def test_post_orden_datos_invalidos_422_sin_insertar(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        datos = {"vehiculo_id": vehiculo["id"], "fecha_ingreso": "2024-01-10",
                 "descripcion_problema": "Revisar frenos", "estado": "pendiente",
                 "kilometraje_ingreso": 0}
        self._validar_post("/ordenes-trabajo", datos, (("vehiculo_id", 0),
                          ("fecha_ingreso", "2024-02-30"), ("descripcion_problema", "abc"),
                          ("descripcion_problema", "     "), ("estado", "abierta"),
                          ("kilometraje_ingreso", -1)))

    def test_post_reparacion_datos_invalidos_422_sin_insertar(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        orden = self._orden(vehiculo["id"])
        datos = {"orden_trabajo_id": orden["id"], "descripcion": "Revisar frenos",
                 "tipo": "diagnostico", "costo": 0, "fecha": "2024-01-11"}
        self._validar_post("/reparaciones/", datos, (("orden_trabajo_id", 0),
                          ("descripcion", "abc"), ("tipo", "otro"),
                          ("costo", -1), ("fecha", "fecha-invalida")))

    def _validar_patch(self, ruta: str, registro: dict, casos: tuple) -> None:
        for campo, valor in casos:
            with self.subTest(campo=campo, valor=valor):
                datos = {campo: valor}
                self._error(self.api.solicitar("PATCH", ruta, datos), 422,
                            "VALIDATION_ERROR", ruta=ruta, datos=datos)
                self._consultar(ruta, registro)

    def test_patch_cliente_invalido_422_sin_mutacion(self) -> None:
        cliente = self._cliente()
        self._validar_patch(f"/clientes/{cliente['id']}", cliente,
                            (("email", "invalido"), ("telefono", "1"), ("nombre", "A")))

    def test_patch_vehiculo_invalido_422_sin_mutacion(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        self._validar_patch(f"/vehiculos/{vehiculo['id']}", vehiculo,
                            (("kilometraje", -1), ("cliente_id", 0), ("patente", "ABC")))

    def test_patch_orden_invalida_422_sin_mutacion(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        orden = self._orden(vehiculo["id"])
        self._validar_patch(f"/ordenes-trabajo/{orden['id']}", orden,
                            (("kilometraje_ingreso", -1), ("vehiculo_id", 0),
                             ("estado", "abierta"), ("fecha_ingreso", "invalida"),
                             ("descripcion_problema", "     ")))

    def test_patch_reparacion_invalida_422_sin_mutacion(self) -> None:
        _, _, _, reparacion = self._cadena()
        self._validar_patch(f"/reparaciones/{reparacion['id']}", reparacion,
                            (("costo", -1), ("tipo", "otro"), ("descripcion", "abc")))

    def test_campos_obligatorios_faltantes_422_en_cuatro_modulos(self) -> None:
        for ruta in ("/clientes", "/vehiculos/", "/ordenes-trabajo", "/reparaciones/"):
            with self.subTest(ruta=ruta):
                self._error(self.api.solicitar("POST", ruta, {}), 422,
                            "VALIDATION_ERROR", ruta=ruta, datos={})

    def test_id_no_numerico_422_en_cuatro_modulos(self) -> None:
        for prefijo in ("clientes", "vehiculos", "ordenes-trabajo", "reparaciones"):
            with self.subTest(modulo=prefijo):
                ruta = f"/{prefijo}/no-es-un-id"
                self._error(self.api.solicitar("GET", ruta), 422,
                            "VALIDATION_ERROR", ruta=ruta)

    def test_parametros_listado_invalidos_422_json(self) -> None:
        for ruta in ("/clientes", "/ordenes-trabajo"):
            for parametros in ({"pagina": 0}, {"limite": 101},
                               {"ordenar_por": "inexistente"}, {"direccion": "invalida"}):
                with self.subTest(ruta=ruta, parametros=parametros):
                    self._error(self.api.solicitar("GET", ruta, parametros=parametros),
                                422, "VALIDATION_ERROR", ruta=ruta, datos=parametros)

    def test_crear_reparacion_fecha_futura_400_json(self) -> None:
        cliente = self._cliente()
        vehiculo = self._vehiculo(cliente["id"])
        orden = self._orden(vehiculo["id"])
        datos = {"orden_trabajo_id": orden["id"], "descripcion": "Revision futura",
                 "tipo": "diagnostico", "costo": 0,
                 "fecha": (date.today() + timedelta(days=1)).isoformat()}
        ruta = "/reparaciones/"
        self._error(self.api.solicitar("POST", ruta, datos), 400,
                    "INVALID_REPAIR_DATE", ruta=ruta, datos=datos)

    def test_patch_reparacion_fecha_futura_400_sin_mutacion(self) -> None:
        _, _, _, reparacion = self._cadena()
        datos = {"fecha": (date.today() + timedelta(days=1)).isoformat()}
        ruta = f"/reparaciones/{reparacion['id']}"
        self._error(self.api.solicitar("PATCH", ruta, datos), 400,
                    "INVALID_REPAIR_DATE", ruta=ruta, datos=datos)
        self._consultar(ruta, reparacion)

    def test_actualizaciones_y_relaciones_persisten_tras_reinicio(self) -> None:
        cliente, vehiculo, orden, reparacion = self._cadena()
        registros = (("clientes", cliente, {"telefono": "987654321"}),
                     ("vehiculos", vehiculo, {"kilometraje": 120001}),
                     ("ordenes-trabajo", orden, {"estado": "en_reparacion"}),
                     ("reparaciones", reparacion, {"costo": 50000.0}))
        esperados = []
        for prefijo, registro, cambios in registros:
            ruta = f"/{prefijo}/{registro['id']}"
            estado, cuerpo = self.api.solicitar("PATCH", ruta, cambios)
            self.assertEqual(estado, 200, msg=cuerpo)
            self.assertEqual(cuerpo, {**registro, **cambios})
            esperados.append((ruta, cuerpo))
        pid_anterior = self.api.pid
        self.api.reiniciar()
        self.assertNotEqual(self.api.pid, pid_anterior)
        for ruta, esperado in esperados:
            self._consultar(ruta, esperado)
        with closing(sqlite3.connect(self.api.base_de_datos.as_uri() + "?mode=ro", uri=True)) as conexion:
            relaciones = conexion.execute(
                "SELECT c.id, v.id, o.id, r.id FROM clientes c "
                "JOIN vehiculos v ON v.cliente_id = c.id "
                "JOIN ordenes_trabajo o ON o.vehiculo_id = v.id "
                "JOIN reparaciones r ON r.orden_trabajo_id = o.id"
            ).fetchall()
            self.assertEqual(relaciones, [(cliente["id"], vehiculo["id"], orden["id"], reparacion["id"])])
            self.assertEqual(conexion.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_base_temporal_ignora_url_postgresql_heredada(self) -> None:
        # URL ficticia sin credenciales: nunca debe abrirse esta conexión.
        with patch.dict(os.environ, {
            "DATABASE_URL": "postgresql+psycopg://127.0.0.1:1/no_conectar",
            "PYTHONPATH": "/ruta/qa/inexistente",
        }):
            with ApiDePrueba() as otra_api:
                evidencia = json.loads((otra_api.directorio / "aislamiento.json").read_text(encoding="utf-8"))
                self.assertEqual(evidencia, {"dialecto": "sqlite",
                    "base_de_datos": str(otra_api.base_de_datos.resolve()), "claves_foraneas": 1})
                self.assertNotEqual(otra_api.base_de_datos, self.api.base_de_datos)
                directorio = otra_api.directorio
                estado_creacion, creado = otra_api.solicitar("POST", "/clientes", {
                    "nombre": "Otra", "apellido": "Base", "telefono": "912345678",
                    "email": "otra.base@example.com", "direccion": "Calle QA 999",
                })
                self.assertEqual(estado_creacion, 201, msg=creado)
                estado, cuerpo = self.api.solicitar("GET", "/clientes")
                self.assertEqual(estado, 200, msg=cuerpo)
                self.assertEqual(cuerpo["items"], [])
        self.assertFalse(directorio.exists(), msg="La carpeta temporal debe limpiarse")
