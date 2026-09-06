from proyectobackend.domain.reparacion import Reparacion
from proyectobackend.repositories.reparacion_repository import ReparacionRepository
from proyectobackend.schemas.reparacion import ReparacionCreate


class ReparacionService:

    def __init__(self, repository: ReparacionRepository) -> None:
        self._repository = repository

    def crear_reparacion(self, dto: ReparacionCreate) -> Reparacion:
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