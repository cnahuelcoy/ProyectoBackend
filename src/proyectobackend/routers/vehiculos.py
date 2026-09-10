from fastapi import APIRouter, status
from typing import List
from proyectobackend.schemas.vehiculo import VehiculoCreate, VehiculoResponse
from proyectobackend.repositories.vehiculo_repository import vehiculo_repository_instance
from proyectobackend.services.vehiculo_service import VehiculoService

# Instancias globales para mantener los datos en memoria
vehiculo_repository = vehiculo_repository_instance
vehiculo_service = VehiculoService(vehiculo_repository)

router = APIRouter(
    prefix="/vehiculos",
    tags=["Vehículos"]
)

@router.post("", response_model=VehiculoResponse, status_code=status.HTTP_201_CREATED, summary="Registrar un nuevo vehículo")
def crear_vehiculo(vehiculo_data: VehiculoCreate):
    # El Router no toma decisiones, solo delega al Service
    return vehiculo_service.crear_vehiculo(vehiculo_data)

@router.get("", response_model=List[VehiculoResponse], status_code=status.HTTP_200_OK, summary="Listar todos los vehículos")
def listar_vehiculos():
    return vehiculo_service.listar_vehiculos()

@router.get("/{vehiculo_id}", response_model=VehiculoResponse, status_code=status.HTTP_200_OK, summary="Obtener un vehículo por su ID")
def obtener_vehiculo(vehiculo_id: int):
    return vehiculo_service.obtener_vehiculo_por_id(vehiculo_id)