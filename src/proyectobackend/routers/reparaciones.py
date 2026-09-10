from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from proyectobackend.schemas.error import ErrorDetail, ErrorResponse

from proyectobackend.repositories.orden_trabajo_repositorio import (
    orden_trabajo_repository_instance,
)
from proyectobackend.repositories.reparacion_repository import (
    reparacion_repository_instance,
)
from proyectobackend.schemas.reparacion import (
    ReparacionCreate,
    ReparacionResponse,
    ReparacionUpdate,
)
from proyectobackend.services.reparacion_service import ReparacionService

router = APIRouter(prefix="/reparaciones", tags=["Reparaciones"])

RESPUESTAS_ERROR = {
    400: {"description": "Datos de entrada inválidos o regla de negocio violada"},
    404: {"description": "Recurso no encontrado en el sistema"},
}


def get_reparacion_service() -> ReparacionService:
    return ReparacionService(
        repository=reparacion_repository_instance,
        orden_repository=orden_trabajo_repository_instance,
    )


def parse_error_message(e: Exception) -> tuple[str, str]:
    parts = str(e).split(":", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return "ERROR", str(e)


def error_json_response(code: str, message: str, status_code: int) -> JSONResponse:
    respuesta = ErrorResponse(error=ErrorDetail(code=code, message=message))
    return JSONResponse(
        status_code=status_code,
        content=respuesta.model_dump(),
    )


@router.post(
    "/",
    response_model=ReparacionResponse,
    status_code=status.HTTP_201_CREATED,
    responses=RESPUESTAS_ERROR,
)
def crear_reparacion(
    dto: ReparacionCreate,
    service: ReparacionService = Depends(get_reparacion_service),
):
    try:
        return service.crear_reparacion(dto)
    except LookupError as e:
        code, msg = parse_error_message(e)
        return error_json_response(code, msg, status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        code, msg = parse_error_message(e)
        return error_json_response(code, msg, status.HTTP_400_BAD_REQUEST)


@router.get("/", response_model=list[ReparacionResponse], status_code=status.HTTP_200_OK)
def listar_reparaciones(
    service: ReparacionService = Depends(get_reparacion_service),
):
    return service.listar_reparaciones()


@router.get(
    "/{reparacion_id}",
    response_model=ReparacionResponse,
    status_code=status.HTTP_200_OK,
    responses={404: RESPUESTAS_ERROR[404]},
)
def obtener_reparacion(
    reparacion_id: int,
    service: ReparacionService = Depends(get_reparacion_service),
):
    try:
        return service.obtener_reparacion_por_id(reparacion_id)
    except LookupError as e:
        code, msg = parse_error_message(e)
        return error_json_response(code, msg, status.HTTP_404_NOT_FOUND)


@router.patch(
    "/{reparacion_id}",
    response_model=ReparacionResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPUESTAS_ERROR,
)
def actualizar_reparacion(
    reparacion_id: int,
    dto: ReparacionUpdate,
    service: ReparacionService = Depends(get_reparacion_service),
):
    try:
        return service.actualizar_reparacion(reparacion_id, dto)
    except LookupError as e:
        code, msg = parse_error_message(e)
        return error_json_response(code, msg, status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        code, msg = parse_error_message(e)
        return error_json_response(code, msg, status.HTTP_400_BAD_REQUEST)


@router.delete(
    "/{reparacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: RESPUESTAS_ERROR[404]},
)
def eliminar_reparacion(
    reparacion_id: int,
    service: ReparacionService = Depends(get_reparacion_service),
):
    try:
        service.eliminar_reparacion(reparacion_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LookupError as e:
        code, msg = parse_error_message(e)
        return error_json_response(code, msg, status.HTTP_404_NOT_FOUND)