
from sqlalchemy import select

from proyectobackend.database.session import SessionLocal
from proyectobackend.domain.reparacion import Reparacion
from proyectobackend.models.reparacion import ReparacionModel


class ReparacionRepository:

    @staticmethod
    def _to_domain(model: ReparacionModel) -> Reparacion:
        return Reparacion(
            id=model.id,
            orden_trabajo_id=model.orden_trabajo_id,
            descripcion=model.descripcion,
            tipo=model.tipo,
            costo=model.costo,
            fecha=model.fecha,
        )

    def crear(self, reparacion: Reparacion) -> Reparacion:
        with SessionLocal() as session:
            model = ReparacionModel(
                orden_trabajo_id=reparacion.orden_trabajo_id,
                descripcion=reparacion.descripcion,
                tipo=reparacion.tipo,
                costo=reparacion.costo,
                fecha=reparacion.fecha,
            )

            session.add(model)
            session.commit()
            session.refresh(model)

            reparacion.id = model.id
            return reparacion

    def listar(self) -> list[Reparacion]:
        with SessionLocal() as session:
            statement = select(ReparacionModel).order_by(
                ReparacionModel.id
            )
            modelos = session.scalars(statement).all()

            return [self._to_domain(model) for model in modelos]

    def buscar_por_id(self, reparacion_id: int) -> Reparacion | None:
        with SessionLocal() as session:
            model = session.get(ReparacionModel, reparacion_id)

            if model is None:
                return None

            return self._to_domain(model)

    def actualizar(
        self, reparacion_id: int, datos: dict
    ) -> Reparacion | None:
        with SessionLocal() as session:
            model = session.get(ReparacionModel, reparacion_id)

            if model is None:
                return None

            for campo, valor in datos.items():
                setattr(model, campo, valor)

            session.commit()
            session.refresh(model)

            return self._to_domain(model)

    def eliminar(self, reparacion_id: int) -> bool:
        with SessionLocal() as session:
            model = session.get(ReparacionModel, reparacion_id)

            if model is None:
                return False

            session.delete(model)
            session.commit()

            return True


# Shared instance for dependency injection
reparacion_repository_instance = ReparacionRepository()
