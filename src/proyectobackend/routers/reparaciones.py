from fastapi import APIRouter, Depends, HTTPException, status
from proyectobackend.domain.reparacion import Reparacion
from proyectobackend.schemas.reparacion import ReparacionCreate
from proyectobackend.services.reparacion_service import ReparacionService
from proyectobackend.repositories.reparacion_repository import (
    reparacion_repository_instance,
)
from proyectobackend.routers.orden_trabajo_routers import (
    repository as orden_trabajo_repository_instance,
)

router = APIRouter(prefix="/reparaciones", tags=["Reparaciones"])


def get_reparacion_service() -> ReparacionService:
    return ReparacionService(
        repository=reparacion_repository_instance,
        orden_repository=orden_trabajo_repository_instance,
    )


@router.post("/", response_model=Reparacion, status_code=status.HTTP_201_CREATED)
def crear_reparacion(
    dto: ReparacionCreate,
    service: ReparacionService = Depends(get_reparacion_service),
) -> Reparacion:
    # Service validates that orden_trabajo_id exists before creating
    return service.crear_reparacion(dto)


@router.get("/", response_model=list[Reparacion], status_code=status.HTTP_200_OK)
def listar_reparaciones(
    service: ReparacionService = Depends(get_reparacion_service),
) -> list[Reparacion]:
    return service.listar_reparaciones()


@router.get(
    "/{reparacion_id}", response_model=Reparacion, status_code=status.HTTP_200_OK
)
def obtener_reparacion(
    reparacion_id: int,
    service: ReparacionService = Depends(get_reparacion_service),
) -> Reparacion:
    reparacion = service.obtener_reparacion_por_id(reparacion_id)
    if not reparacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repair with ID {reparacion_id} not found",
        )
    return reparacion