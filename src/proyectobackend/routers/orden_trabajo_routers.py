from typing import Literal

from proyectobackend.domain.orden_trabajo import EstadoOrdenTrabajo
from fastapi import APIRouter, HTTPException, Query, status

from proyectobackend.repositories.orden_trabajo_repositorio import (
    OrdenTrabajoRepository,
)
from proyectobackend.schemas.orden_trabajo_schemas import (
    OrdenTrabajoCreate,
    OrdenTrabajoListadoResponse,
    OrdenTrabajoResponse,
    OrdenTrabajoUpdate,
)
from proyectobackend.services.orden_trabajo_services import OrdenTrabajoService
from proyectobackend.routers.vehiculos import vehiculo_repository


router = APIRouter(prefix="/ordenes-trabajo", tags=["ordenes-trabajo"])

repository = OrdenTrabajoRepository()
service = OrdenTrabajoService(repository , vehiculo_repository)


@router.post(
    "",
    response_model=OrdenTrabajoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_orden_trabajo(datos: OrdenTrabajoCreate):
    try:
        return service.crear(datos)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/{orden_id}",
    response_model=OrdenTrabajoResponse,
    status_code=status.HTTP_200_OK,
)

def obtener_orden_trabajo(orden_id: int):
    try:
        return service.obtener_por_id(orden_id)
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=OrdenTrabajoListadoResponse,
    status_code=status.HTTP_200_OK,
)    
def listar_ordenes_trabajo(
    estado: EstadoOrdenTrabajo | None = None,
    ordenar_por: Literal["id", "fecha_ingreso", "kilometraje_ingreso"] = "id",
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
)
def actualizar_orden_trabajo(orden_id: int, datos: OrdenTrabajoUpdate):
    try:
        return service.actualizar(orden_id, datos)
    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
