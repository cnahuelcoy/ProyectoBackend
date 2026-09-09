from fastapi import HTTPException
from typing import List
from proyectobackend.domain.vehiculo import Vehiculo
from proyectobackend.schemas.vehiculo import VehiculoCreate, VehiculoUpdate
from proyectobackend.repositories.vehiculo_repository import VehiculoRepository
from proyectobackend.repositories.cliente_repository import ClienteRepository

class VehiculoService:
    def __init__(self, repository: VehiculoRepository, cliente_repository: ClienteRepository):
        self.repository = repository
        self.cliente_repository = cliente_repository

    def crear_vehiculo(self, vehiculo_data: VehiculoCreate) -> Vehiculo:
        cliente_existente = self.cliente_repository.buscar_por_id(vehiculo_data.cliente_id)
        if not cliente_existente:
            raise HTTPException(status_code=404, detail="El cliente especificado no existe")

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


    def actualizar_vehiculo(self, vehiculo_id: int, vehiculo_data: VehiculoUpdate) -> Vehiculo:
        # 1. Buscamos el vehículo (si no existe, lanza 404 automáticamente gracias a la función de arriba)
        vehiculo = self.obtener_vehiculo_por_id(vehiculo_id)

        
        if vehiculo_data.patente is not None and vehiculo_data.patente != vehiculo.patente:
            vehiculo_existente = self.repository.buscar_por_patente(vehiculo_data.patente)
            if vehiculo_existente:
                raise HTTPException(status_code=409, detail="Ya existe un vehículo registrado con esta patente")
            vehiculo.patente = vehiculo_data.patente

        # 3. Validamos el cliente (si es que lo enviaron)
        if vehiculo_data.cliente_id is not None and vehiculo_data.cliente_id != vehiculo.cliente_id:
            cliente_existente = self.cliente_repository.buscar_por_id(vehiculo_data.cliente_id)
            if not cliente_existente:
                raise HTTPException(status_code=404, detail="El nuevo cliente especificado no existe")
            vehiculo.cliente_id = vehiculo_data.cliente_id

        
        if vehiculo_data.marca is not None:
            vehiculo.marca = vehiculo_data.marca
        if vehiculo_data.modelo is not None:
            vehiculo.modelo = vehiculo_data.modelo
        if vehiculo_data.anio is not None:
            vehiculo.anio = vehiculo_data.anio
        if vehiculo_data.kilometraje is not None:
            vehiculo.kilometraje = vehiculo_data.kilometraje

        return self.repository.actualizar(vehiculo)

    def eliminar_vehiculo(self, vehiculo_id: int):
        # lanza 404 
        self.obtener_vehiculo_por_id(vehiculo_id)
        
        self.repository.eliminar(vehiculo_id)