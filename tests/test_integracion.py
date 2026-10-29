import unittest

from tests.soporte_api import ApiDePrueba


class TestIntegracion(unittest.TestCase):
    def setUp(self) -> None:
        self.api = ApiDePrueba()
        self.addCleanup(self.api.cerrar)
        self.api.iniciar()

    def _crear(self, ruta: str, datos: dict) -> dict:
        estado, cuerpo = self.api.solicitar(
            metodo="POST",
            ruta=ruta,
            datos=datos,
        )

        self.assertEqual(estado, 201, msg=cuerpo)
        self.assertIsInstance(cuerpo, dict)
        self.assertIn("id", cuerpo)
        self.assertIsInstance(cuerpo["id"], int)
        self.assertGreater(cuerpo["id"], 0)

        for campo, valor in datos.items():
            self.assertIn(campo, cuerpo)
            self.assertEqual(cuerpo[campo], valor)

        return cuerpo

    def _crear_cadena(self) -> list[tuple[str, dict]]:
        cliente = self._crear(
            "/clientes",
            {
                "nombre": "Marta",
                "apellido": "Torres",
                "telefono": "978901234",
                "email": "marta.integracion@example.com",
                "direccion": "Calle Integracion 303",
            },
        )

        vehiculo = self._crear(
            "/vehiculos/",
            {
                "patente": "TEST01",
                "marca": "Toyota",
                "modelo": "Yaris",
                "anio": 2020,
                "kilometraje": 120000,
                "cliente_id": cliente["id"],
            },
        )

        orden = self._crear(
            "/ordenes-trabajo",
            {
                "vehiculo_id": vehiculo["id"],
                "fecha_ingreso": "2024-01-10",
                "descripcion_problema": "Revisar frenos del vehiculo",
                "estado": "pendiente",
                "kilometraje_ingreso": 120000,
            },
        )

        reparacion = self._crear(
            "/reparaciones/",
            {
                "orden_trabajo_id": orden["id"],
                "descripcion": "Cambio de pastillas de freno",
                "tipo": "mantencion",
                "costo": 45000.0,
                "fecha": "2024-01-11",
            },
        )

        return [
            (f"/clientes/{cliente['id']}", cliente),
            (f"/vehiculos/{vehiculo['id']}", vehiculo),
            (f"/ordenes-trabajo/{orden['id']}", orden),
            (f"/reparaciones/{reparacion['id']}", reparacion),
        ]

    def test_listado_con_filtro_orden_y_paginacion(self) -> None:
        entradas = [
            ("Ana", "Zulu", "ana.zulu@example.com"),
            ("Luis", "Perez", "luis.perez@example.com"),
            ("Ana", "Bravo", "ana.bravo@example.com"),
            ("ANA", "Alba", "ana.alba@example.com"),
            ("Ana", "Mora", "ana.mora@example.com"),
            ("Anabel", "Abarca", "anabel.abarca@example.com"),
        ]

        creados = {}

        for nombre, apellido, email in entradas:
            creados[apellido] = self._crear(
                "/clientes",
                {
                    "nombre": nombre,
                    "apellido": apellido,
                    "telefono": "972345678",
                    "email": email,
                    "direccion": "Calle Listado 100",
                },
            )

        for pagina, apellidos in [
            (1, ["Zulu", "Mora"]),
            (2, ["Bravo", "Alba"]),
        ]:
            with self.subTest(pagina=pagina):
                estado, cuerpo = self.api.solicitar(
                    metodo="GET",
                    ruta="/clientes",
                    parametros={
                        "nombre": "ana",
                        "ordenar_por": "apellido",
                        "direccion": "desc",
                        "pagina": pagina,
                        "limite": 2,
                    },
                )

                self.assertEqual(estado, 200, msg=cuerpo)

                self.assertEqual(
                    cuerpo,
                    {
                        "items": [
                            creados[apellido]
                            for apellido in apellidos
                        ],
                        "total": 4,
                        "pagina": pagina,
                        "limite": 2,
                        "total_paginas": 2,
                    },
                )

    def test_persistencia_de_los_cuatro_modulos_tras_reinicio(self) -> None:
        registros = self._crear_cadena()
        pid_anterior = self.api.pid
        base_anterior = self.api.base_de_datos

        self.assertIsNotNone(pid_anterior)
        self.assertTrue(base_anterior.is_file())

        self.api.reiniciar()

        self.assertIsNotNone(self.api.pid)
        self.assertNotEqual(self.api.pid, pid_anterior)
        self.assertEqual(self.api.base_de_datos, base_anterior)
        self.assertTrue(self.api.base_de_datos.is_file())

        for ruta, esperado in registros:
            with self.subTest(ruta=ruta):
                estado, cuerpo = self.api.solicitar(
                    metodo="GET",
                    ruta=ruta,
                )

                self.assertEqual(estado, 200, msg=cuerpo)
                self.assertEqual(cuerpo, esperado)

    def test_relacion_cliente_vehiculo_orden_reparacion(self) -> None:
        registros = self._crear_cadena()
        consultados = []

        for ruta, esperado in registros:
            estado, cuerpo = self.api.solicitar(
                metodo="GET",
                ruta=ruta,
            )

            self.assertEqual(estado, 200, msg=cuerpo)
            self.assertEqual(cuerpo, esperado)

            consultados.append(cuerpo)

        cliente, vehiculo, orden, reparacion = consultados

        self.assertEqual(
            vehiculo["cliente_id"],
            cliente["id"],
        )

        self.assertEqual(
            orden["vehiculo_id"],
            vehiculo["id"],
        )

        self.assertEqual(
            reparacion["orden_trabajo_id"],
            orden["id"],
        )