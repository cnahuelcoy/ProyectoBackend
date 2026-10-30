from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse

from proyectobackend.repositories.orden_trabajo_repositorio import (
    orden_trabajo_repository_instance,
)
from proyectobackend.repositories.reparacion_repository import (
    reparacion_repository_instance,
)
from proyectobackend.schemas.error import ErrorDetail, ErrorResponse
from proyectobackend.schemas.reparacion import (
    ReparacionCreate,
    ReparacionResponse,
    ReparacionUpdate,
)
from proyectobackend.services.reparacion_service import ReparacionService


router = APIRouter(
    prefix="/reparaciones",
    tags=["Reparaciones"],
)

# Documentamos solo los errores que realmente maneja cada endpoint.
ERROR_422 = {
    "model": ErrorResponse,
    "description": "Datos de entrada inválidos (validación Pydantic).",
}
ERROR_400_FECHA = {
    "model": ErrorResponse,
    "description": "La fecha de la reparación no puede ser futura.",
    "content": {
        "application/json": {
            "example": {
                "error": {
                    "code": "INVALID_REPAIR_DATE",
                    "message": "La fecha de la reparación no puede ser futura",
                    "details": [],
                }
            }
        }
    },
}
ERROR_404_ORDEN = {
    "model": ErrorResponse,
    "description": "La orden de trabajo indicada no existe.",
}
ERROR_404_REPARACION = {
    "model": ErrorResponse,
    "description": "No existe una reparación con el ID indicado.",
}


def get_reparacion_service() -> ReparacionService:
    return ReparacionService(
        repository=reparacion_repository_instance,
        orden_repository=orden_trabajo_repository_instance,
    )


def parse_error_message(error: Exception) -> tuple[str, str]:
    parts = str(error).split(":", 1)

    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()

    return "REPAIR_ERROR", str(error)


def error_json_response(
    code: str,
    message: str,
    status_code: int,
) -> JSONResponse:
    respuesta = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=respuesta.model_dump(),
    )


@router.post(
    "/",
    response_model=ReparacionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear reparación",
    description=(
        "Registra una reparación para una orden de trabajo existente. "
        "La fecha no puede ser futura y el costo debe ser mayor o igual a cero."
    ),
    responses={400: ERROR_400_FECHA, 404: ERROR_404_ORDEN, 422: ERROR_422},
)
def crear_reparacion(
    dto: ReparacionCreate,
    service: ReparacionService = Depends(get_reparacion_service),
):
    try:
        return service.crear_reparacion(dto)

    except LookupError as error:
        code, message = parse_error_message(error)

        return error_json_response(
            code,
            message,
            status.HTTP_404_NOT_FOUND,
        )

    except ValueError as error:
        code, message = parse_error_message(error)

        return error_json_response(
            code,
            message,
            status.HTTP_400_BAD_REQUEST,
        )


@router.get(
    "/",
    response_model=list[ReparacionResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar reparaciones",
    description="Devuelve todas las reparaciones registradas, ordenadas por ID.",
)
def listar_reparaciones(
    service: ReparacionService = Depends(get_reparacion_service),
):
    return service.listar_reparaciones()


@router.get(
    "/{reparacion_id}",
    response_model=ReparacionResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener reparación por ID",
    description="Consulta una reparación existente por su identificador numérico.",
    responses={404: ERROR_404_REPARACION, 422: ERROR_422},
)
def obtener_reparacion(
    reparacion_id: int,
    service: ReparacionService = Depends(get_reparacion_service),
):
    try:
        return service.obtener_reparacion_por_id(reparacion_id)

    except LookupError as error:
        code, message = parse_error_message(error)

        return error_json_response(
            code,
            message,
            status.HTTP_404_NOT_FOUND,
        )


@router.patch(
    "/{reparacion_id}",
    response_model=ReparacionResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar reparación",
    description=(
        "Actualiza los datos indicados de una reparación existente. "
        "La fecha no puede ser futura y el costo no puede ser negativo."
    ),
    responses={400: ERROR_400_FECHA, 404: ERROR_404_REPARACION, 422: ERROR_422},
)
def actualizar_reparacion(
    reparacion_id: int,
    dto: ReparacionUpdate,
    service: ReparacionService = Depends(get_reparacion_service),
):
    try:
        return service.actualizar_reparacion(
            reparacion_id,
            dto,
        )

    except LookupError as error:
        code, message = parse_error_message(error)

        return error_json_response(
            code,
            message,
            status.HTTP_404_NOT_FOUND,
        )

    except ValueError as error:
        code, message = parse_error_message(error)

        return error_json_response(
            code,
            message,
            status.HTTP_400_BAD_REQUEST,
        )


@router.delete(
    "/{reparacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar reparación",
    description="Elimina una reparación por ID. Devuelve 204 sin cuerpo si existe.",
    responses={404: ERROR_404_REPARACION, 422: ERROR_422},
)
def eliminar_reparacion(
    reparacion_id: int,
    service: ReparacionService = Depends(get_reparacion_service),
):
    try:
        service.eliminar_reparacion(reparacion_id)

        return Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )

    except LookupError as error:
        code, message = parse_error_message(error)

        return error_json_response(
            code,
            message,
            status.HTTP_404_NOT_FOUND,
        )