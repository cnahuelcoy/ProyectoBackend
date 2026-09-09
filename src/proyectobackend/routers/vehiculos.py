from fastapi import APIRouter, Response, status
from typing import List
from proyectobackend.schemas.vehiculo import VehiculoCreate, VehiculoResponse, VehiculoUpdate
from proyectobackend.repositories.vehiculo_repository import VehiculoRepository
from proyectobackend.services.vehiculo_service import VehiculoService

# IMPORTAMOS LA MEMORIA DE CLIENTES DE TUS COMPAÑEROS
from proyectobackend.routers.clientes import cliente_repo 

router = APIRouter(prefix="/vehiculos", tags=["Vehiculos"])

vehiculo_repo = VehiculoRepository()
# LE ENTREGAMOS EL SEGUNDO INGREDIENTE AL SERVICIO
vehiculo_service = VehiculoService(vehiculo_repo, cliente_repo) 

@router.post("/", response_model=VehiculoResponse, status_code=201)
def crear_vehiculo(vehiculo: VehiculoCreate):
    return vehiculo_service.crear_vehiculo(vehiculo)

@router.get("/", response_model=List[VehiculoResponse])
def listar_vehiculos():
    return vehiculo_service.listar_vehiculos()

@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
def obtener_vehiculo(vehiculo_id: int):
    return vehiculo_service.obtener_vehiculo_por_id(vehiculo_id)

# ==========================================
# NUEVOS ENDPOINTS: PATCH Y DELETE
# ==========================================

@router.patch("/{vehiculo_id}", response_model=VehiculoResponse)
def actualizar_vehiculo(vehiculo_id: int, vehiculo_data: VehiculoUpdate):
    return vehiculo_service.actualizar_vehiculo(vehiculo_id, vehiculo_data)

@router.delete("/{vehiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vehiculo(vehiculo_id: int):
    vehiculo_service.eliminar_vehiculo(vehiculo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)