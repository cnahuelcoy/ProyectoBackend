from typing import Literal

from fastapi import APIRouter, Query, Response, status
from fastapi.responses import JSONResponse

from proyectobackend.repositories.cliente_repository import cliente_repo
from proyectobackend.schemas.cliente import (
    ClienteCreate,
    ClienteListadoResponse,
    ClienteResponse,
    ClienteUpdate,
)
from proyectobackend.schemas.error import ErrorDetail, ErrorResponse
from proyectobackend.services.cliente_service import ClienteService


router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
)

repository = cliente_repo
service = ClienteService(repository)


def crear_error(
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    error = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
        )
    )

    return JSONResponse(
        status_code=status_code,
        content=error.model_dump(),
    )


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un cliente",
    responses={
        409: {"model": ErrorResponse},
    },
)
def crear_cliente(datos: ClienteCreate):
    try:
        return service.crear(datos)
    except ValueError as error:
        return crear_error(
            status_code=status.HTTP_409_CONFLICT,
            code="CLIENT_EMAIL_ALREADY_EXISTS",
            message=str(error),
        )


@router.get(
    "",
    response_model=ClienteListadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar clientes",
    description=(
        "Lista clientes permitiendo filtrado por nombre, "
        "ordenamiento y paginación."
    ),
)
def listar_clientes(
    nombre: str | None = Query(
        default=None,
        min_length=2,
        max_length=50,
    ),
    ordenar_por: Literal[
        "id",
        "nombre",
        "apellido",
        "email",
    ] = Query(default="id"),
    direccion: Literal["asc", "desc"] = Query(default="asc"),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=10, ge=1, le=100),
):
    return service.listar(
        nombre=nombre,
        ordenar_por=ordenar_por,
        direccion=direccion,
        pagina=pagina,
        limite=limite,
    )


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un cliente por ID",
    responses={
        404: {"model": ErrorResponse},
    },
)
def obtener_cliente(cliente_id: int):
    cliente = service.obtener_por_id(cliente_id)

    if cliente is None:
        return crear_error(
            status_code=status.HTTP_404_NOT_FOUND,
            code="CLIENT_NOT_FOUND",
            message="Cliente no encontrado",
        )

    return cliente


@router.patch(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente un cliente",
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
def actualizar_cliente(
    cliente_id: int,
    datos: ClienteUpdate,
):
    try:
        cliente = service.actualizar(cliente_id, datos)
    except ValueError as error:
        return crear_error(
            status_code=status.HTTP_409_CONFLICT,
            code="CLIENT_EMAIL_ALREADY_EXISTS",
            message=str(error),
        )

    if cliente is None:
        return crear_error(
            status_code=status.HTTP_404_NOT_FOUND,
            code="CLIENT_NOT_FOUND",
            message="Cliente no encontrado",
        )

    return cliente


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un cliente",
    responses={
        404: {"model": ErrorResponse},
    },
)
def eliminar_cliente(cliente_id: int):
    eliminado = service.eliminar(cliente_id)

    if not eliminado:
        return crear_error(
            status_code=status.HTTP_404_NOT_FOUND,
            code="CLIENT_NOT_FOUND",
            message="Cliente no encontrado",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
