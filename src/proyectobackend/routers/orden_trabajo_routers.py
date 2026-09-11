from typing import Literal

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from proyectobackend.domain.orden_trabajo import EstadoOrdenTrabajo
from proyectobackend.repositories.orden_trabajo_repositorio import (
    orden_trabajo_repository_instance,
)
from proyectobackend.repositories.vehiculo_repository import (
    vehiculo_repository_instance,
)
from proyectobackend.schemas.error import ErrorDetail, ErrorResponse
from proyectobackend.schemas.orden_trabajo_schemas import (
    OrdenTrabajoCreate,
    OrdenTrabajoListadoResponse,
    OrdenTrabajoResponse,
    OrdenTrabajoUpdate,
)
from proyectobackend.services.orden_trabajo_services import OrdenTrabajoService


router = APIRouter(
    prefix="/ordenes-trabajo",
    tags=["ordenes-trabajo"],
    responses={
        422: {"model": ErrorResponse},
    },
)

repository = orden_trabajo_repository_instance
service = OrdenTrabajoService(
    repository,
    vehiculo_repository_instance,
)


def _respuesta_error(
    error: Exception,
    status_code: int,
) -> JSONResponse:
    code, separador, message = str(error).partition(":")

    respuesta = ErrorResponse(
        error=ErrorDetail(
            code=code if separador else "WORK_ORDER_ERROR",
            message=message.strip() if separador else str(error),
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=respuesta.model_dump(),
    )


@router.post(
    "",
    response_model=OrdenTrabajoResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse},
    },
)
def crear_orden_trabajo(datos: OrdenTrabajoCreate):
    try:
        return service.crear(datos)
    except LookupError as error:
        return _respuesta_error(
            error,
            status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "/{orden_id}",
    response_model=OrdenTrabajoResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse},
    },
)
def obtener_orden_trabajo(orden_id: int):
    try:
        return service.obtener_por_id(orden_id)
    except LookupError as error:
        return _respuesta_error(
            error,
            status.HTTP_404_NOT_FOUND,
        )


@router.get(
    "",
    response_model=OrdenTrabajoListadoResponse,
    status_code=status.HTTP_200_OK,
)
def listar_ordenes_trabajo(
    estado: EstadoOrdenTrabajo | None = None,
    ordenar_por: Literal[
        "id",
        "fecha_ingreso",
        "kilometraje_ingreso",
    ] = "id",
    direccion: Literal["asc", "desc"] = "asc",
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=10, ge=1, le=100),
):
    return service.listar(
        estado=estado,
        ordenar_por=ordenar_por,
        direccion=direccion,
        pagina=pagina,
        limite=limite,
    )


@router.patch(
    "/{orden_id}",
    response_model=OrdenTrabajoResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def actualizar_orden_trabajo(
    orden_id: int,
    datos: OrdenTrabajoUpdate,
):
    try:
        return service.actualizar(
            orden_id,
            datos,
        )
    except LookupError as error:
        return _respuesta_error(
            error,
            status.HTTP_404_NOT_FOUND,
        )
    except ValueError as error:
        return _respuesta_error(
            error,
            status.HTTP_400_BAD_REQUEST,
        )