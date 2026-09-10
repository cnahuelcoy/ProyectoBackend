from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
from typing import List

from proyectobackend.schemas.vehiculo import VehiculoCreate, VehiculoResponse, VehiculoUpdate
from proyectobackend.repositories.vehiculo_repository import vehiculo_repository_instance
from proyectobackend.repositories.cliente_repository import cliente_repo  # Instancia compartida desde el repositorio de clientes
from proyectobackend.services.vehiculo_service import VehiculoService

router = APIRouter(prefix="/vehiculos", tags=["Vehiculos"])

# Inyectamos las instancias compartidas
vehiculo_service = VehiculoService(vehiculo_repository_instance, cliente_repo)

def _formatear_error(ex: Exception) -> JSONResponse:
    mensaje_completo = str(ex)
    if ":" in mensaje_completo:
        code, message = mensaje_completo.split(":", 1)
    else:
        code, message = "INTERNAL_ERROR", mensaje_completo

    status_code = 400
    if code in ["CLIENT_NOT_FOUND", "VEHICLE_NOT_FOUND"]:
        status_code = 404
    elif code == "VEHICLE_LICENSE_PLATE_ALREADY_EXISTS":
        status_code = 409

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": []
            }
        }
    )

@router.post("/", response_model=VehiculoResponse, status_code=201)
def crear_vehiculo(vehiculo: VehiculoCreate):
    try:
        return vehiculo_service.crear_vehiculo(vehiculo)
    except (LookupError, ValueError) as e:
        return _formatear_error(e)

@router.get("/", response_model=List[VehiculoResponse])
def listar_vehiculos():
    return vehiculo_service.listar_vehiculos()

@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
def obtener_vehiculo(vehiculo_id: int):
    try:
        return vehiculo_service.obtener_vehiculo_por_id(vehiculo_id)
    except LookupError as e:
        return _formatear_error(e)

@router.patch("/{vehiculo_id}", response_model=VehiculoResponse)
def actualizar_vehiculo(vehiculo_id: int, vehiculo_data: VehiculoUpdate):
    try:
        return vehiculo_service.actualizar_vehiculo(vehiculo_id, vehiculo_data)
    except (LookupError, ValueError) as e:
        return _formatear_error(e)

@router.delete("/{vehiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vehiculo(vehiculo_id: int):
    try:
        vehiculo_service.eliminar_vehiculo(vehiculo_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LookupError as e:
        return _formatear_error(e)
