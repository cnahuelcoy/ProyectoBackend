from fastapi import HTTPException
from typing import List
from proyectobackend.domain.vehiculo import Vehiculo
from proyectobackend.schemas.vehiculo import VehiculoCreate
from proyectobackend.repositories.vehiculo_repository import VehiculoRepository

class VehiculoService:
    def __init__(self, repository: VehiculoRepository):
        self.repository = repository

    def crear_vehiculo(self, vehiculo_data: VehiculoCreate) -> Vehiculo:
        vehiculo_existente = self.repository.buscar_por_patente(vehiculo_data.patente)
        if vehiculo_existente:
            raise HTTPException(status_code=409, detail="Ya existe un vehículo registrado con esta patente")

        nuevo_vehiculo = Vehiculo(
            id=None,
            patente=vehiculo_data.patente,
            marca=vehiculo_data.marca,
            modelo=vehiculo_data.modelo,
            anio=vehiculo_data.anio,
            kilometraje=vehiculo_data.kilometraje,
            cliente_id=vehiculo_data.cliente_id
        )

        return self.repository.crear(nuevo_vehiculo)

    def listar_vehiculos(self) -> List[Vehiculo]:
        return self.repository.listar()

    def obtener_vehiculo_por_id(self, vehiculo_id: int) -> Vehiculo:
        vehiculo = self.repository.buscar_por_id(vehiculo_id)
        if not vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        return vehiculo