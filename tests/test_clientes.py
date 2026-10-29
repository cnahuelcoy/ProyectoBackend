import unittest
from tests.soporte_api import ApiDePrueba

class TestClientes(unittest.TestCase):

    def setUp(self) -> None:
        self.api = ApiDePrueba()

        
        self.addCleanup(self.api.cerrar)

        self.api.iniciar()

    def test_crear_cliente_exitosamente(self) -> None:
        datos = {
            "nombre": "Ana",
            "apellido": "Perez",
            "telefono": "912345678",
            "email": "ana.pruebas@example.com",
            "direccion": "Calle Pruebas 123",
        }

        estado, cuerpo = self.api.solicitar(
            metodo="POST",
            ruta="/clientes",
            datos=datos,
        )

        
        self.assertEqual(estado, 201, msg=cuerpo)

        
        self.assertIsInstance(cuerpo, dict)
        self.assertIn("id", cuerpo)
        self.assertIsInstance(cuerpo["id"], int)
        self.assertGreater(cuerpo["id"], 0)

        
        for campo, valor_esperado in datos.items():
            with self.subTest(campo=campo):
                self.assertIn(campo, cuerpo)
                self.assertEqual(cuerpo[campo], valor_esperado)

    def test_obtener_cliente_existente(self) -> None:
        datos = {
            "nombre": "Luis",
            "apellido": "Soto",
            "telefono": "923456789",
            "email": "luis.pruebas@example.com",
            "direccion": "Calle Pruebas 456",
        } 

        
        estado_creacion, cliente_creado = self.api.solicitar(
            metodo="POST",
            ruta="/clientes",
            datos=datos,
        )

        self.assertEqual(
            estado_creacion,
            201,
            msg=cliente_creado,
        )

        cliente_id = cliente_creado["id"]

       
        estado, cuerpo = self.api.solicitar(
            metodo="GET",
            ruta=f"/clientes/{cliente_id}",
        )

        self.assertEqual(estado, 200, msg=cuerpo)
        self.assertEqual(cuerpo, cliente_creado)

    def test_actualizar_cliente_existente(self) -> None:
        datos = {
            "nombre": "Carla",
            "apellido": "Rojas",
            "telefono": "934567890",
            "email": "carla.pruebas@example.com",
            "direccion": "Calle Pruebas 789",
        }

        
        estado_creacion, cliente_creado = self.api.solicitar(
            metodo="POST",
            ruta="/clientes",
            datos=datos,
        )

        self.assertEqual(
            estado_creacion,
            201,
            msg=cliente_creado,
        )

        cliente_id = cliente_creado["id"]

        cambios = {
            "telefono": "945678901",
            "direccion": "Avenida Taller 100",
        }

        
        estado_actualizacion, cliente_actualizado = self.api.solicitar(
            metodo="PATCH",
            ruta=f"/clientes/{cliente_id}",
            datos=cambios,
        )

        self.assertEqual(
            estado_actualizacion,
            200,
            msg=cliente_actualizado,
        )

        esperado = {**cliente_creado, **cambios}

        self.assertEqual(cliente_actualizado, esperado)

        
        estado_consulta, cliente_consultado = self.api.solicitar(
            metodo="GET",
            ruta=f"/clientes/{cliente_id}",
        )

        self.assertEqual(
            estado_consulta,
            200,
            msg=cliente_consultado,
        )

        self.assertEqual(cliente_consultado, esperado)

    def test_obtener_cliente_inexistente_devuelve_404(self) -> None:
        estado, cuerpo = self.api.solicitar(
            metodo="GET",
            ruta="/clientes/999999",
        )

        self.assertEqual(estado, 404, msg=cuerpo)

        self.assertEqual(
            cuerpo["error"]["code"],
            "CLIENT_NOT_FOUND",
        )

        self.assertEqual(
            cuerpo["error"]["message"],
            "Cliente no encontrado",
        )


    def test_crear_cliente_con_email_duplicado_devuelve_409(self) -> None:
        datos = {
            "nombre": "Pedro",
            "apellido": "Munoz",
            "telefono": "956789012",
            "email": "pedro.pruebas@example.com",
            "direccion": "Calle Pruebas 101",
        }

        
        estado_creacion, cliente_creado = self.api.solicitar(
            metodo="POST",
            ruta="/clientes",
            datos=datos,
        )

        self.assertEqual(
            estado_creacion,
            201,
            msg=cliente_creado,
        )

        
        estado, cuerpo = self.api.solicitar(
            metodo="POST",
            ruta="/clientes",
            datos=datos,
        )

        self.assertEqual(estado, 409, msg=cuerpo)

        self.assertEqual(
            cuerpo["error"]["code"],
            "CLIENT_EMAIL_ALREADY_EXISTS",
        )

        self.assertEqual(
            cuerpo["error"]["message"],
            "Ya existe un cliente registrado con este correo",
        )

       
        estado_listado, listado = self.api.solicitar(
            metodo="GET",
            ruta="/clientes",
        )

        self.assertEqual(estado_listado, 200, msg=listado)
        self.assertEqual(listado["total"], 1)
        self.assertEqual(listado["items"], [cliente_creado])

    def test_crear_cliente_con_email_invalido_devuelve_422(self) -> None:
        datos = {
            "nombre": "Elena",
            "apellido": "Diaz",
            "telefono": "967890123",
            "email": "correo-invalido",
            "direccion": "Calle Pruebas 202",
        }

        estado, cuerpo = self.api.solicitar(
            metodo="POST",
            ruta="/clientes",
            datos=datos,
        )

        self.assertEqual(estado, 422, msg=cuerpo)

        self.assertEqual(
            cuerpo["error"]["code"],
            "VALIDATION_ERROR",
        )

        self.assertEqual(
            cuerpo["error"]["message"],
            "Los datos de la solicitud no son válidos",
        )

        detalles = cuerpo["error"]["details"]

        self.assertIsInstance(detalles, list)

        self.assertTrue(
            any(
                detalle.get("loc") == ["body", "email"]
                for detalle in detalles
            ),
            msg=detalles,
        )

        estado_listado, listado = self.api.solicitar(
            metodo="GET",
            ruta="/clientes",
        )

        self.assertEqual(estado_listado, 200, msg=listado)
        self.assertEqual(listado["total"], 0)
        self.assertEqual(listado["items"], [])
