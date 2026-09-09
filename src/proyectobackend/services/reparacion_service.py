from datetime import date
from proyectobackend.domain.reparacion import Reparacion
from proyectobackend.repositories.orden_trabajo_repositorio import OrdenTrabajoRepository
from proyectobackend.repositories.reparacion_repository import ReparacionRepository
from proyectobackend.schemas.reparacion import ReparacionCreate, ReparacionUpdate


class ReparacionService:

    def __init__(
        self,
        repository: ReparacionRepository,
        orden_repository: OrdenTrabajoRepository,
    ):
        self._repository = repository
        self._orden_repository = orden_repository

    def crear_reparacion(self, dto: ReparacionCreate) -> Reparacion:
        if dto.fecha > date.today():
            raise ValueError("INVALID_REPAIR_DATE:La fecha de la reparación no puede ser futura")

        orden = self._orden_repository.buscar_por_id(dto.orden_trabajo_id)
        if orden is None:
            raise LookupError(
                f"WORK_ORDER_NOT_FOUND:No se encontró la orden de trabajo con ID {dto.orden_trabajo_id}"
            )

        return self._repository.crear(dto)

    def listar_reparaciones(self) -> list[Reparacion]:
        return self._repository.listar()

    def obtener_reparacion_por_id(self, reparacion_id: int) -> Reparacion:
        reparacion = self._repository.buscar_por_id(reparacion_id)
        if reparacion is None:
            raise LookupError(
                f"REPAIR_NOT_FOUND:No se encontró la reparación con ID {reparacion_id}"
            )
        return reparacion

    def actualizar_reparacion(
        self, reparacion_id: int, dto: ReparacionUpdate
    ) -> Reparacion:
        reparacion = self._repository.buscar_por_id(reparacion_id)
        if reparacion is None:
            raise LookupError(
                f"REPAIR_NOT_FOUND:No se encontró la reparación con ID {reparacion_id}"
            )

        datos_actualizar = dto.model_dump(exclude_unset=True, exclude_none=True)

        if "fecha" in datos_actualizar and datos_actualizar["fecha"] > date.today():
            raise ValueError("INVALID_REPAIR_DATE:La fecha de la reparación no puede ser futura")

        return self._repository.actualizar(reparacion_id, datos_actualizar)

    def eliminar_reparacion(self, reparacion_id: int) -> None:
        reparacion = self._repository.buscar_por_id(reparacion_id)
        if reparacion is None:
            raise LookupError(
                f"REPAIR_NOT_FOUND:No se encontró la reparación con ID {reparacion_id}"
            )
        self._repository.eliminar(reparacion_id)