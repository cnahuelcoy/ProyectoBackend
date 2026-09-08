from fastapi import APIRouter, HTTPException, Response, status

from proyectobackend.repositories.cliente_repository import ClienteRepository
from proyectobackend.schemas.cliente import (
    ClienteCreate,
    ClienteResponse,
    ClienteUpdate,
)
from proyectobackend.services.cliente_service import ClienteService


router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
)

repository = ClienteRepository()
service = ClienteService(repository)


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un cliente",
)
def crear_cliente(datos: ClienteCreate):
    try:
        return service.crear(datos)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=list[ClienteResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar clientes",
)
def listar_clientes():
    return service.listar()


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un cliente por ID",
)
def obtener_cliente(cliente_id: int):
    cliente = service.obtener_por_id(cliente_id)

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )

    return cliente


@router.patch(
    "/{cliente_id}",
    response_model=ClienteResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente un cliente",
)
def actualizar_cliente(
    cliente_id: int,
    datos: ClienteUpdate,
):
    try:
        cliente = service.actualizar(cliente_id, datos)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    if cliente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )

    return cliente


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un cliente",
)
def eliminar_cliente(cliente_id: int):
    eliminado = service.eliminar(cliente_id)

    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)