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
import json
from pathlib import Path
import socket
import uvicorn
from sqlalchemy import event

from proyectobackend.database.session import engine

base_esperada = Path("taller_mecanico.db").resolve()
if engine.dialect.name != "sqlite":
    raise RuntimeError("Las pruebas solo pueden usar SQLite temporal")
if Path(engine.url.database).resolve() != base_esperada:
    raise RuntimeError("La base de pruebas debe estar en la carpeta temporal")


@event.listens_for(engine, "connect")
def activar_claves_foraneas(conexion_dbapi, registro):
    cursor = conexion_dbapi.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA foreign_keys")
        if cursor.fetchone()[0] != 1:
            raise RuntimeError("No se pudieron activar las claves foráneas")
    finally:
        cursor.close()


with engine.connect() as conexion_bd:
    claves_foraneas = conexion_bd.exec_driver_sql("PRAGMA foreign_keys").scalar()
    if claves_foraneas != 1:
        raise RuntimeError("Las claves foráneas deben estar activas")

Path("aislamiento.json").write_text(
    json.dumps({
        "dialecto": engine.dialect.name,
        "base_de_datos": str(base_esperada),
        "claves_foraneas": claves_foraneas,
    }),
    encoding="utf-8",
)

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
        self.ultimo_content_type: str | None = None

        self._http = build_opener(ProxyHandler({}))

    @property
    def url(self) -> str:
        if self._url is None:
            raise RuntimeError("Primero debes iniciar la API de prueba")
        return self._url

    @property
    def pid(self) -> int | None:
        if self._proceso is None:
            return None
        return self._proceso.pid

    def iniciar(self, tiempo_espera: float = 15) -> None:
        if self._cerrada:
            raise RuntimeError("Esta API de prueba ya fue limpiada")
        if self._proceso is not None:
            raise RuntimeError("Detén la API antes de volver a iniciarla")

        raiz = Path(__file__).resolve().parents[1]
        entorno = os.environ.copy()
        entorno["DATABASE_URL"] = f"sqlite:///{self.base_de_datos.resolve()}"
        entorno["PYTHONPATH"] = str(raiz / "src")
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
                    puerto = int(archivo_puerto.read_text(encoding="utf-8"))
                    self._url = f"http://127.0.0.1:{puerto}"

                    estado, cuerpo = self.solicitar(
                        "GET", "/", timeout=0.5
                    )
                    if estado == 200 and cuerpo == {
                        "mensaje": "API Taller Mecánico funcionando"
                    }:
                        return
                except (OSError, ValueError):
                    pass

                time.sleep(0.05)

            detalle = registro.read_text(encoding="utf-8", errors="replace")
            raise RuntimeError(f"La API no pudo arrancar. Registro:\n{detalle}")

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
            raise RuntimeError("Primero debes iniciar la API de prueba")
        if self._proceso.poll() is not None:
            raise RuntimeError("El proceso de la API de prueba se ha detenido")
        if not ruta.startswith("/"):
            raise ValueError("La ruta debe comenzar con /")

        url = self._url + ruta
        if parametros:
            separador = "&" if "?" in ruta else "?"
            url += separador + urlencode(parametros)

        contenido = None if datos is None else json.dumps(datos).encode("utf-8")
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
            respuesta = self._http.open(peticion, timeout=timeout)
        except HTTPError as error:
            respuesta = error

        with respuesta:
            estado = respuesta.code
            self.ultimo_content_type = respuesta.headers.get_content_type()
            cuerpo = respuesta.read().decode("utf-8")

        if not cuerpo:
            return estado, None

        try:
            return estado, json.loads(cuerpo)
        except json.JSONDecodeError:
            return estado, cuerpo

    def detener(self) -> None:
        """Detiene el servidor y conserva la SQLite para poder reiniciar."""
        if self._proceso is not None:
            proceso = self._proceso
            if proceso.poll() is None:
                proceso.terminate()
                try:
                    proceso.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proceso.kill()
                    proceso.wait(timeout=5)
            else:
                proceso.wait()

            self._proceso = None

        self._url = None

    def reiniciar(self) -> None:
        """Inicia otro proceso usando la misma SQLite temporal."""
        self.detener()
        self.iniciar()

    def cerrar(self) -> None:
        """Detiene la API y elimina sus archivos, reintentando bloqueos de Windows.

        No ignora errores persistentes: si otro proceso conserva abierto
        api.log o taller_mecanico.db, la limpieza finalmente falla de forma
        visible para que la prueba no se marque como exitosa por error.
        """
        if self._cerrada:
            return

        self.detener()

        intentos = 20
        for intento in range(intentos):
            try:
                self._temporal.cleanup()
                self._cerrada = True
                return
            except PermissionError as error:
                if (
                    os.name != "nt"
                    or getattr(error, "winerror", None) != 32
                    or intento == intentos - 1
                ):
                    raise

                time.sleep(0.25)

    def __enter__(self) -> "ApiDePrueba":
        try:
            self.iniciar()
        except BaseException:
            self.cerrar()
            raise
        return self

    def __exit__(self, tipo, valor, traza) -> None:
        self.cerrar()
