from fastapi import APIRouter, HTTPException, status
from proyectobackend.repositories.reparacion_repository import ReparacionRepository
from proyectobackend.schemas.reparacion import ReparacionCreate, ReparacionResponse
from proyectobackend.services.reparacion_service import ReparacionService

router = APIRouter(prefix="/reparaciones", tags=["Reparaciones"])

# Shared in-memory instance to preserve state
_repository = ReparacionRepository()
_service = ReparacionService(_repository)


@router.post(
    "",
    response_model=ReparacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva reparación",
    description="Crea una nueva reparación asociada a una orden de trabajo.",
)
def crear_reparacion(dto: ReparacionCreate):
    return _service.crear_reparacion(dto)


@router.get(
    "",
    response_model=list[ReparacionResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener todas las reparaciones",
    description="Retorna una lista con todas las reparaciones registradas en el sistema.",
)
def listar_reparaciones():
    return _service.listar_reparaciones()


@router.get(
    "/{reparacion_id}",
    response_model=ReparacionResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener una reparación por ID",
    description="Busca y retorna una reparación específica mediante su identificador único.",
)
def obtener_reparacion(reparacion_id: int):
    reparacion = _service.obtener_reparacion_por_id(reparacion_id)
    if not reparacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reparación con ID {reparacion_id} no encontrada",
        )
    return reparacion