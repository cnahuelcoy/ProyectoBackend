from fastapi import APIRouter, HTTPException, status

from proyectobackend.repositories.orden_trabajo_repositorio import (
    OrdenTrabajoRepository,
)
from proyectobackend.schemas.orden_trabajo_schemas import (
    OrdenTrabajoCreate,
    OrdenTrabajoResponse,
    OrdenTrabajoUpdate,
)
from proyectobackend.services.orden_trabajo_services import OrdenTrabajoService


router = APIRouter(prefix="/ordenes-trabajo", tags=["ordenes-trabajo"])

repository = OrdenTrabajoRepository()
service = OrdenTrabajoService(repository)


@router.post(
    "",
    response_model=OrdenTrabajoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_orden_trabajo(datos: OrdenTrabajoCreate):
    return service.crear(datos)


@router.get(
    "",
    response_model=list[OrdenTrabajoResponse],
    status_code=status.HTTP_200_OK,
)
def listar_ordenes_trabajo():
    return service.listar()


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
