from fastapi import HTTPException, status
from proyectobackend.domain.reparacion import Reparacion
from proyectobackend.repositories.reparacion_repository import ReparacionRepository
from proyectobackend.repositories.orden_trabajo_repository import OrdenTrabajoRepository
from proyectobackend.schemas.reparacion import ReparacionCreate


class ReparacionService:

    def __init__(
        self,
        repository: ReparacionRepository,
        orden_repository: OrdenTrabajoRepository,
    ) -> None:
        self._repository = repository
        self._orden_repository = orden_repository

    def crear_reparacion(self, dto: ReparacionCreate) -> Reparacion:
        # Check if the related work order exists in memory
        orden = self._orden_repository.buscar_por_id(dto.orden_trabajo_id)
        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Work order {dto.orden_trabajo_id} not found",
            )

        # Transform the input DTO into a domain entity
        reparacion = Reparacion(
            orden_trabajo_id=dto.orden_trabajo_id,
            descripcion=dto.descripcion,
            tipo=dto.tipo,
            costo=dto.costo,
            fecha=dto.fecha,
        )
        return self._repository.crear(reparacion)

    def listar_reparaciones(self) -> list[Reparacion]:
        return self._repository.listar()

    def obtener_reparacion_por_id(self, reparacion_id: int) -> Reparacion | None:
        return self._repository.buscar_por_id(reparacion_id)