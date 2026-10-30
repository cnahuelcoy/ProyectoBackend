"""Endpoints de Reparaciones y documentación de sus respuestas HTTP."""

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


router = APIRouter(prefix="/reparaciones", tags=["Reparaciones"])

# Se documentan únicamente los códigos que pueden producir estas rutas.
ERROR_VALIDACION = {
    422: {
        "model": ErrorResponse,
        "description": "Datos del cuerpo o parámetros de la URL inválidos.",
    }
}
ERROR_FECHA = {
    400: {
        "model": ErrorResponse,
        "description": "La fecha de reparación no puede ser futura (INVALID_REPAIR_DATE).",
    }
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
        "Registra una reparación asociada a una orden de trabajo existente. "
        "La fecha no puede ser posterior al día actual. "
        "Una orden inexistente devuelve 404; una fecha futura, 400."
    ),
    responses={
        400: ERROR_FECHA[400],
        404: {
            "model": ErrorResponse,
            "description": "La orden de trabajo indicada no existe (WORK_ORDER_NOT_FOUND).",
        },
        **ERROR_VALIDACION,
    },
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
    description="Obtiene las reparaciones registradas, ordenadas por ID.",
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
    description="Consulta una reparación existente. Devuelve 404 si no existe.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Reparación no encontrada (REPAIR_NOT_FOUND).",
        },
        **ERROR_VALIDACION,
    },
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
        "Actualiza los campos enviados de una reparación existente. "
        "Una fecha futura devuelve 400; una reparación inexistente, 404."
    ),
    responses={
        **ERROR_FECHA,
        404: {
            "model": ErrorResponse,
            "description": "Reparación no encontrada (REPAIR_NOT_FOUND).",
        },
        **ERROR_VALIDACION,
    },
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
    description="Elimina una reparación existente sin devolver cuerpo (204).",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Reparación no encontrada (REPAIR_NOT_FOUND).",
        },
        **ERROR_VALIDACION,
    },
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
