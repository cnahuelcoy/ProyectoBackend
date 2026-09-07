from datetime import date
from fastapi import HTTPException, status
from proyectobackend.domain.reparacion import Reparacion
from proyectobackend.repositories.orden_trabajo_repository import OrdenTrabajoRepository
from proyectobackend.repositories.reparacion_repository import ReparacionRepository
from proyectobackend.schemas.reparacion import ReparacionCreate, ReparacionUpdate


class ReparacionService:

    def __init__(
        self,
        repository: ReparacionRepository,
        orden_repository: OrdenTrabajoRepository,
    ) -> None:
        self._repository = repository
        self._orden_repository = orden_repository

    def crear_reparacion(self, dto: ReparacionCreate) -> Reparacion:
        # 1. Validar existencia de la Orden de Trabajo
        orden = self._orden_repository.buscar_por_id(dto.orden_trabajo_id)
        if not orden:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Work order {dto.orden_trabajo_id} not found",
            )

        # 2. REGLA DE NEGOCIO: No permitir reparaciones con fecha futura
        if dto.fecha > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Repair date cannot be in the future",
            )

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

    def actualizar_reparacion(
        self, reparacion_id: int, dto: ReparacionUpdate
    ) -> Reparacion:
        reparacion = self._repository.buscar_por_id(reparacion_id)
        if not reparacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repair with ID {reparacion_id} not found",
            )

        # REGLA DE NEGOCIO: Si se actualiza la fecha, no puede ser futura
        if dto.fecha and dto.fecha > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Repair date cannot be in the future",
            )

        datos = dto.model_dump(exclude_unset=True)
        actualizada = self._repository.actualizar(reparacion_id, datos)
        if not actualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repair with ID {reparacion_id} not found",
            )
        return actualizada

    def eliminar_reparacion(self, reparacion_id: int) -> None:
        eliminado = self._repository.eliminar(reparacion_id)
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repair with ID {reparacion_id} not found",
            )