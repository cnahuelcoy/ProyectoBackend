from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from proyectobackend.schemas.error import ErrorDetail, ErrorResponse
from proyectobackend.repositories.orden_trabajo_repositorio import orden_trabajo_repository_instance
from proyectobackend.repositories.reparacion_repository import ReparacionRepository
from proyectobackend.schemas.reparacion import ReparacionCreate, ReparacionResponse
from proyectobackend.services.reparacion_service import ReparacionService

router = APIRouter(prefix="/reparaciones", tags=["Reparaciones"])

# Shared in-memory instance to preserve state
_repository = ReparacionRepository()
_service = ReparacionService(_repository, orden_trabajo_repository_instance)


@router.post(
    "",
    response_model=ReparacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva reparación",
    description="Crea una nueva reparación asociada a una orden de trabajo.",
)
def crear_reparacion(dto: ReparacionCreate):
    try:
        return _service.crear_reparacion(dto)
    except LookupError as error:
        respuesta = ErrorResponse(error=ErrorDetail(
            code="WORK_ORDER_NOT_FOUND", message=str(error),
        ))
        return JSONResponse(status_code=404, content=respuesta.model_dump())


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