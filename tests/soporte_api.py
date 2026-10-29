import json
import os 
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import ProxyHandler, Request, build_opener


_ARRANQUE_API = """
from pathlib import Path
import socket
import uvicorn

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexion:
    conexion.bind(("127.0.0.1", 0))

    Path("puerto.txt").write_text(
        str(conexion.getsockname()[1]),
        encoding="utf-8",
    )

    configuracion = uvicorn.Config(
        "proyectobackend.main:app",
        log_level="warning",
        access_log=False,
    )

    uvicorn.Server(configuracion).run(sockets=[conexion])
"""


class ApiDePrueba:
    def __init__(self) -> None:
        self._temporal = TemporaryDirectory(prefix="parte5-api")
        self.directorio = Path(self._temporal.name)
        self.base_de_datos = self.directorio / "taller_mecanico.db"
       
        self._proceso: subprocess.Popen | None = None
        self._url: str | None = None
        self._cerrada = False

        self._http = build_opener(ProxyHandler({}))

    @property
    def pid(self) -> int | None:
        if self._proceso is None:
            return None

        return self._proceso.pid

    def iniciar(self, tiempo_espera: float = 15) -> None:
        if self._cerrada:
            raise RuntimeError("Esta APi de prueba ya fue limpiada")

        if self._proceso is not None:
            raise RuntimeError("Detén la API antes de volver a iniciarla")
        
        raiz = Path(__file__).resolve().parents[1]

        entorno = os.environ.copy()
        entorno["DATABASE_URL"] = "sqlite:///./taller_mecanico.db"
        rutas = [str(raiz / "src")]

        if entorno.get("PYTHONPATH"):
            rutas.append(entorno["PYTHONPATH"])

        entorno["PYTHONPATH"] = os.pathsep.join(rutas)
        entorno["PYTHONDONTWRITEBYTECODE"] = "1"

        archivo_puerto = self.directorio / "puerto.txt"
        archivo_puerto.unlink(missing_ok=True)

        registro = self.directorio / "api.log"

        with registro.open("ab") as salida:
            self._proceso = subprocess.Popen(
                [sys.executable, "-B", "-c", _ARRANQUE_API],
                cwd=self.directorio,
                env=entorno,
                stdin=subprocess.DEVNULL,
                stdout=salida,
                stderr=subprocess.STDOUT,
            )

        try:
            vencimiento = time.monotonic() + tiempo_espera

            while time.monotonic() < vencimiento:
                if self._proceso.poll() is not None:
                    break

                try:
                    puerto = int(
                        archivo_puerto.read_text(encoding="utf-8")
                    )

                    self._url = f"http://127.0.0.1:{puerto}"

                    estado, cuerpo = self.solicitar(
                        "GET",
                        "/",
                        timeout=0.5,
                    )

                    if estado == 200 and cuerpo == {
                        "mensaje": "API Taller Mecánico funcionando"
                    }:
                        return

                except (OSError, ValueError):
                    # El servidor puede no estar listo todavía.
                    pass

                time.sleep(0.05)

            detalle = registro.read_text(
                encoding="utf-8",
                errors="replace",
            )

            raise RuntimeError(
                f"La API no pudo arrancar. Registro:\n{detalle}"
            )

        except BaseException:
            self.detener()
            raise

    def solicitar(
        self,
        metodo: str,
        ruta: str,
        datos: dict[str, Any] | None = None,
        parametros: dict[str, str | int] | None = None,
        timeout: float = 5,
    ) -> tuple[int, Any]:
        if self._url is None or self._proceso is None:
            raise RuntimeError("primero debes iniciar a la API de prueba")

        if self._proceso.poll() is not None:
            raise RuntimeError(
                "El proceso de la API de prueba se ha detenido"
            )

        if not ruta.startswith("/"):
            raise ValueError("La ruta debe comenzar con /")

        url = self._url + ruta

        if parametros:
            separador = "&" if "?" in ruta else "?"
            url += separador + urlencode(parametros)

        contenido = (
            None
            if datos is None
            else json.dumps(datos).encode("utf-8")
        )

        cabeceras = {"Accept": "application/json"}

        if contenido is not None:
            cabeceras["Content-Type"] = "application/json"

        peticion = Request(
            url,
            data=contenido,
            headers=cabeceras,
            method=metodo,
        )

        try:
            respuesta = self._http.open(
                peticion,
                timeout=timeout,
            )

        except HTTPError as error:
            # Los estados 404, 409 y 422 también deben comprobarse.
            respuesta = error

        with respuesta:
            estado = respuesta.code
            cuerpo = respuesta.read().decode("utf-8")

        if not cuerpo:
            return estado, None

        try:
            return estado, json.loads(cuerpo)

        except json.JSONDecodeError:
            return estado, cuerpo

    def detener(self) -> None:
        """Cierra la API y conserva la base para poder reiniciarla."""
        if self._proceso is not None:
            if self._proceso.poll() is None:
                self._proceso.terminate()

                try:
                    self._proceso.wait(timeout=5)

                except subprocess.TimeoutExpired:
                    self._proceso.kill()
                    self._proceso.wait(timeout=5)

            self._proceso = None

        self._url = None

    def reiniciar(self) -> None:
        """Abre otro proceso usando la misma SQLite temporal."""
        self.detener()
        self.iniciar()

    def cerrar(self) -> None:
        """Cierra la API y elimina todos los archivos temporales."""
        if not self._cerrada:
            self.detener()
            self._temporal.cleanup()
            self._cerrada = True

    def __enter__(self) -> "ApiDePrueba":
        try:
            self.iniciar()

        except BaseException:
            self.cerrar()
            raise

        return self

    def __exit__(self, tipo, valor, traza) -> None:
        self.cerrar()
        


    
        

