from sqlalchemy import select

from proyectobackend.database.session import SessionLocal
from proyectobackend.domain.orden_trabajo import OrdenTrabajo
from proyectobackend.models.orden_trabajo import OrdenTrabajoModel


class OrdenTrabajoRepository:
    @staticmethod
    def _to_domain(model: OrdenTrabajoModel) -> OrdenTrabajo:
        return OrdenTrabajo(
            id=model.id,
            vehiculo_id=model.vehiculo_id,
            fecha_ingreso=model.fecha_ingreso,
            descripcion_problema=model.descripcion_problema,
            kilometraje_ingreso=model.kilometraje_ingreso,
            estado=model.estado,
        )

    def crear(self, orden: OrdenTrabajo) -> OrdenTrabajo:
        with SessionLocal() as session:
            model = OrdenTrabajoModel(
                vehiculo_id=orden.vehiculo_id,
                fecha_ingreso=orden.fecha_ingreso,
                descripcion_problema=orden.descripcion_problema,
                kilometraje_ingreso=orden.kilometraje_ingreso,
                estado=orden.estado,
            )

            session.add(model)
            session.commit()
            session.refresh(model)

            orden.id = model.id
            return orden

    def listar(self) -> list[OrdenTrabajo]:
        with SessionLocal() as session:
            statement = select(OrdenTrabajoModel).order_by(
                OrdenTrabajoModel.id.asc()
            )

            modelos = session.scalars(statement).all()

            return [
                self._to_domain(model)
                for model in modelos
            ]

    def buscar_por_id(self, orden_id: int) -> OrdenTrabajo | None:
        with SessionLocal() as session:
            model = session.get(OrdenTrabajoModel, orden_id)

            if model is None:
                return None

            return self._to_domain(model)

    def actualizar(
        self,
        orden_id: int,
        orden_actualizada: OrdenTrabajo,
    ) -> OrdenTrabajo | None:
        with SessionLocal() as session:
            model = session.get(OrdenTrabajoModel, orden_id)

            if model is None:
                return None

            model.vehiculo_id = orden_actualizada.vehiculo_id
            model.fecha_ingreso = orden_actualizada.fecha_ingreso
            model.descripcion_problema = (
                orden_actualizada.descripcion_problema
            )
            model.kilometraje_ingreso = (
                orden_actualizada.kilometraje_ingreso
            )
            model.estado = orden_actualizada.estado

            session.commit()
            session.refresh(model)

            orden_actualizada.id = model.id
            return orden_actualizada


orden_trabajo_repository_instance = OrdenTrabajoRepository()
