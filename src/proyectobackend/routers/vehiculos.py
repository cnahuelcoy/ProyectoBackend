from typing import List

from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse

from proyectobackend.repositories.cliente_repository import cliente_repo
from proyectobackend.repositories.vehiculo_repository import (
    vehiculo_repository_instance,
)
from proyectobackend.schemas.error import ErrorDetail, ErrorResponse
from proyectobackend.schemas.vehiculo import (
    VehiculoCreate,
    VehiculoResponse,
    VehiculoUpdate,
)
from proyectobackend.services.vehiculo_service import VehiculoService


router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehiculos"],
    responses={
        422: {"model": ErrorResponse},
    },
)

vehiculo_service = VehiculoService(
    vehiculo_repository_instance,
    cliente_repo,
)


def _formatear_error(ex: Exception) -> JSONResponse:
    mensaje_completo = str(ex)

    if ":" in mensaje_completo:
        code, message = mensaje_completo.split(":", 1)
    else:
        code = "VEHICLE_ERROR"
        message = mensaje_completo

    status_code = status.HTTP_400_BAD_REQUEST

    if code in [
        "CLIENT_NOT_FOUND",
        "VEHICLE_NOT_FOUND",
    ]:
        status_code = status.HTTP_404_NOT_FOUND

    elif code == "VEHICLE_LICENSE_PLATE_ALREADY_EXISTS":
        status_code = status.HTTP_409_CONFLICT

    respuesta = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message.strip(),
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=respuesta.model_dump(),
    )


@router.post(
    "/",
    response_model=VehiculoResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def crear_vehiculo(vehiculo: VehiculoCreate):
    try:
        return vehiculo_service.crear_vehiculo(vehiculo)

    except (LookupError, ValueError) as error:
        return _formatear_error(error)


@router.get(
    "/",
    response_model=List[VehiculoResponse],
    status_code=status.HTTP_200_OK,
)
def listar_vehiculos():
    return vehiculo_service.listar_vehiculos()


@router.get(
    "/{vehiculo_id}",
    response_model=VehiculoResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse},
    },
)
def obtener_vehiculo(vehiculo_id: int):
    try:
        return vehiculo_service.obtener_vehiculo_por_id(vehiculo_id)

    except LookupError as error:
        return _formatear_error(error)


@router.patch(
    "/{vehiculo_id}",
    response_model=VehiculoResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def actualizar_vehiculo(
    vehiculo_id: int,
    vehiculo_data: VehiculoUpdate,
):
    try:
        return vehiculo_service.actualizar_vehiculo(
            vehiculo_id,
            vehiculo_data,
        )

    except (LookupError, ValueError) as error:
        return _formatear_error(error)


@router.delete(
    "/{vehiculo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse},
    },
)
def eliminar_vehiculo(vehiculo_id: int):
    try:
        vehiculo_service.eliminar_vehiculo(vehiculo_id)

        return Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )

    except LookupError as error:
        return _formatear_error(error)