"""Carga reproducible de datos iniciales del taller mecánico.

Desde la raíz del proyecto: uv run python scripts/seed_db.py
"""

import argparse
import sys
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from proyectobackend.database.init_db import init_db
from proyectobackend.database.session import SessionLocal
from proyectobackend.domain.orden_trabajo import EstadoOrdenTrabajo
from proyectobackend.domain.reparacion import TipoReparacion
from proyectobackend.models.cliente import ClienteModel
from proyectobackend.models.orden_trabajo import OrdenTrabajoModel
from proyectobackend.models.reparacion import ReparacionModel
from proyectobackend.models.vehiculo import VehiculoModel
from proyectobackend.schemas.cliente import ClienteCreate
from proyectobackend.schemas.orden_trabajo_schemas import OrdenTrabajoCreate
from proyectobackend.schemas.reparacion import ReparacionCreate
from proyectobackend.schemas.vehiculo import VehiculoCreate


class ErrorSeeder(Exception):
    """Inconsistencia entre datos existentes y relaciones esperadas."""


CLIENTES = (
    dict(nombre="Valentina", apellido="Pérez", telefono="+56951234567",
         email="seed.cliente01@example.com", direccion="Av. Alemania 120, Temuco"),
    dict(nombre="Diego", apellido="Soto", telefono="+56958765432",
         email="seed.cliente02@example.com", direccion="Av. Prieto Norte 430, Temuco"),
)
VEHICULOS = (
    dict(patente="SBAB12", marca="Toyota", modelo="Yaris", anio=2021, kilometraje=28600),
    dict(patente="SBCD34", marca="Hyundai", modelo="Accent", anio=2018, kilometraje=71350),
)
ORDENES = (
    dict(fecha_ingreso=date(2025, 10, 6),
         descripcion_problema="SEED_P5_OT_01 | Ruido al frenar en baja velocidad",
         kilometraje_ingreso=28600, estado=EstadoOrdenTrabajo.EN_REPARACION),
    dict(fecha_ingreso=date(2025, 10, 8),
         descripcion_problema="SEED_P5_OT_02 | Mantención preventiva programada",
         kilometraje_ingreso=71350, estado=EstadoOrdenTrabajo.FINALIZADA),
)
REPARACIONES = (
    dict(descripcion="SEED_P5_REP_01 | Diagnóstico y revisión de pastillas de freno",
         tipo=TipoReparacion.DIAGNOSTICO, costo=25000.0,
         fecha=date(2025, 10, 7)),
    dict(descripcion="SEED_P5_REP_02 | Cambio de aceite y filtro de motor",
         tipo=TipoReparacion.MANTENCION, costo=85000.0,
         fecha=date(2025, 10, 9)),
)


def buscar_unico(session: Session, modelo: type, criterio, etiqueta: str):
    encontrados = session.scalars(select(modelo).where(criterio).limit(2)).all()
    if len(encontrados) > 1:
        raise ErrorSeeder(f"Se encontraron varios registros con el identificador de {etiqueta}.")
    return encontrados[0] if encontrados else None


def obtener_o_crear(session: Session, modelo: type, criterio, campos: dict,
                    etiqueta: str, *, padre: str | None = None):
    existente = buscar_unico(session, modelo, criterio, etiqueta)
    if existente is not None:
        if padre is not None and getattr(existente, padre) != campos[padre]:
            raise ErrorSeeder(f"El registro de {etiqueta} existe, pero pertenece a otro padre.")
        return existente, False
    nuevo = modelo(**campos)
    session.add(nuevo)
    session.flush()  # Obtiene ID para el siguiente nivel sin hacer commit individual.
    return nuevo, True


def cargar_semillas() -> dict[str, int]:
    creados = {"clientes": 0, "vehiculos": 0, "ordenes_trabajo": 0, "reparaciones": 0}
    # Una sola transacción: commit al terminar, rollback ante cualquier excepción.
    with SessionLocal.begin() as session:
        for indice in range(2):
            datos_cliente = ClienteCreate.model_validate(CLIENTES[indice]).model_dump()
            cliente, nuevo = obtener_o_crear(
                session, ClienteModel,
                func.lower(ClienteModel.email) == datos_cliente["email"].lower(),
                datos_cliente, "cliente",
            )
            creados["clientes"] += int(nuevo)

            datos_vehiculo = VehiculoCreate.model_validate({
                **VEHICULOS[indice], "cliente_id": cliente.id,
            }).model_dump()
            vehiculo, nuevo = obtener_o_crear(
                session, VehiculoModel,
                func.upper(VehiculoModel.patente) == datos_vehiculo["patente"].upper(),
                datos_vehiculo, "vehiculo", padre="cliente_id",
            )
            creados["vehiculos"] += int(nuevo)

            datos_orden = OrdenTrabajoCreate.model_validate({
                **ORDENES[indice], "vehiculo_id": vehiculo.id,
            }).model_dump()
            orden, nuevo = obtener_o_crear(
                session, OrdenTrabajoModel,
                OrdenTrabajoModel.descripcion_problema == datos_orden["descripcion_problema"],
                datos_orden, "orden de trabajo", padre="vehiculo_id",
            )
            creados["ordenes_trabajo"] += int(nuevo)

            datos_reparacion = ReparacionCreate.model_validate({
                **REPARACIONES[indice], "orden_trabajo_id": orden.id,
            }).model_dump()
            if datos_reparacion["fecha"] > date.today():
                raise ErrorSeeder("La fecha de reparación no puede ser futura.")
            _, nuevo = obtener_o_crear(
                session, ReparacionModel,
                ReparacionModel.descripcion == datos_reparacion["descripcion"],
                datos_reparacion, "reparacion", padre="orden_trabajo_id",
            )
            creados["reparaciones"] += int(nuevo)
    return creados


def verificar() -> None:
    """Consulta en sesión nueva los ocho datos y sus FK, sin escribir registros."""
    with SessionLocal() as session:
        for i in range(2):
            cliente = buscar_unico(session, ClienteModel,
                func.lower(ClienteModel.email) == CLIENTES[i]["email"].lower(), "cliente")
            if cliente is None:
                raise ErrorSeeder(f"Falta cliente inicial {i + 1}.")
            vehiculo = buscar_unico(session, VehiculoModel,
                func.upper(VehiculoModel.patente) == VEHICULOS[i]["patente"].upper(), "vehiculo")
            if vehiculo is None or vehiculo.cliente_id != cliente.id:
                raise ErrorSeeder(f"Vehículo inicial {i + 1} no asociado al cliente.")
            orden = buscar_unico(session, OrdenTrabajoModel,
                OrdenTrabajoModel.descripcion_problema == ORDENES[i]["descripcion_problema"], "orden")
            if orden is None or orden.vehiculo_id != vehiculo.id:
                raise ErrorSeeder(f"Orden inicial {i + 1} no asociada al vehículo.")
            reparacion = buscar_unico(session, ReparacionModel,
                ReparacionModel.descripcion == REPARACIONES[i]["descripcion"], "reparacion")
            if reparacion is None or reparacion.orden_trabajo_id != orden.id:
                raise ErrorSeeder(f"Reparación inicial {i + 1} no asociada a la orden.")
            print(f"Cadena {i + 1}: cliente={cliente.id} -> vehículo={vehiculo.id} "
                  f"-> orden={orden.id} -> reparación={reparacion.id}")
    print("VERIFICACIÓN EXITOSA: 2 registros iniciales por entidad y relaciones correctas.")


class _RollbackDePrueba(Exception):
    pass


def comprobar_rollback() -> None:
    """Fuerza un fallo antes del commit y verifica ausencia del registro temporal."""
    correo = "seed.rollback.verificacion@example.com"
    with SessionLocal() as session:
        if session.scalar(select(ClienteModel.id).where(ClienteModel.email == correo)) is not None:
            raise ErrorSeeder("El correo de prueba de rollback ya existe; no se modificó.")
    try:
        with SessionLocal.begin() as session:
            session.add(ClienteModel(nombre="Prueba", apellido="Rollback",
                telefono="+56950000000", email=correo, direccion="Solo transacción temporal"))
            session.flush()
            raise _RollbackDePrueba("Fallo intencional antes del commit")
    except _RollbackDePrueba:
        pass
    with SessionLocal() as session:
        persistio = session.scalar(
            select(ClienteModel.id).where(ClienteModel.email == correo))
        if persistio is not None:
            raise ErrorSeeder("FALLÓ el rollback: se conservó el registro temporal.")
    print("ROLLBACK EXITOSO: se revirtió el registro temporal tras el fallo intencional.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    opciones = parser.add_mutually_exclusive_group()
    opciones.add_argument("--verificar", action="store_true", help="Solo comprueba datos y relaciones.")
    opciones.add_argument("--probar-rollback", action="store_true", help="Simula un fallo y comprueba rollback.")
    args = parser.parse_args()
    try:
        init_db()  # Inicialización existente, también válida sin migraciones.
        if args.probar_rollback:
            comprobar_rollback()
        elif args.verificar:
            verificar()
        else:
            creados = cargar_semillas()
            print("Nuevos registros por entidad:", creados)
            verificar()
        return 0
    except (ErrorSeeder, SQLAlchemyError, ValueError) as exc:
        # Nunca publicar URL de conexión ni SQL con credenciales.
        detalle = str(exc) if isinstance(exc, ErrorSeeder) else type(exc).__name__
        print(f"ERROR: carga no completada ({detalle}). Transacción revertida.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
