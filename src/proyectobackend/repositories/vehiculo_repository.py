from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from proyectobackend.database.session import SessionLocal
from proyectobackend.domain.vehiculo import Vehiculo
from proyectobackend.models.orden_trabajo import OrdenTrabajoModel
from proyectobackend.models.vehiculo import VehiculoModel


class VehiculoRepository:
    @staticmethod
    def _to_domain(model: VehiculoModel) -> Vehiculo:
        return Vehiculo(
            id=model.id,
            patente=model.patente,
            marca=model.marca,
            modelo=model.modelo,
            anio=model.anio,
            kilometraje=model.kilometraje,
            cliente_id=model.cliente_id,
        )

    def crear(self, vehiculo: Vehiculo) -> Vehiculo:
        with SessionLocal() as session:
            model = VehiculoModel(
                patente=vehiculo.patente,
                marca=vehiculo.marca,
                modelo=vehiculo.modelo,
                anio=vehiculo.anio,
                kilometraje=vehiculo.kilometraje,
                cliente_id=vehiculo.cliente_id,
            )

            session.add(model)
            session.commit()
            session.refresh(model)

            return self._to_domain(model)

    def listar(self) -> list[Vehiculo]:
        with SessionLocal() as session:
            # Keep insertion order, as the previous in-memory dict did
            statement = select(VehiculoModel).order_by(VehiculoModel.id)
            modelos = session.scalars(statement).all()

            return [
                self._to_domain(model)
                for model in modelos
            ]

    def buscar_por_id(self, vehiculo_id: int) -> Vehiculo | None:
        with SessionLocal() as session:
            model = session.get(VehiculoModel, vehiculo_id)

            if model is None:
                return None

            return self._to_domain(model)

    def buscar_por_patente(self, patente: str) -> Vehiculo | None:
        with SessionLocal() as session:
            statement = select(VehiculoModel).where(
                VehiculoModel.patente == patente
            )

            model = session.scalar(statement)

            if model is None:
                return None

            return self._to_domain(model)

    def actualizar(self, vehiculo: Vehiculo) -> Vehiculo | None:
        with SessionLocal() as session:
            model = session.get(VehiculoModel, vehiculo.id)

            if model is None:
                return None

            model.patente = vehiculo.patente
            model.marca = vehiculo.marca
            model.modelo = vehiculo.modelo
            model.anio = vehiculo.anio
            model.kilometraje = vehiculo.kilometraje
            model.cliente_id = vehiculo.cliente_id

            session.commit()
            session.refresh(model)

            return self._to_domain(model)

    def eliminar(self, vehiculo_id: int) -> bool:
        with SessionLocal() as session:
            model = session.get(VehiculoModel, vehiculo_id)

            if model is None:
                return False

            orden_asociada = session.scalar(
                select(OrdenTrabajoModel.id)
                .where(OrdenTrabajoModel.vehiculo_id == vehiculo_id)
                .limit(1)
            )

            mensaje_conflicto = (
                "VEHICLE_HAS_WORK_ORDERS:"
                "No se puede eliminar un vehículo con órdenes de trabajo asociadas"
            )

            if orden_asociada is not None:
                raise ValueError(mensaje_conflicto)

            try:
                session.delete(model)
                session.commit()
            except IntegrityError as error:
                session.rollback()
                raise ValueError(mensaje_conflicto) from error

            return True


# Shared single instance used by the routers
vehiculo_repository_instance = VehiculoRepository()
