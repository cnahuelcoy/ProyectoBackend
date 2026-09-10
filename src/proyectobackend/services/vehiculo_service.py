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
        # Validar existencia del cliente
        cliente_existente = self.cliente_repository.buscar_por_id(vehiculo_data.cliente_id)
        if not cliente_existente:
            raise LookupError(f"CLIENT_NOT_FOUND:No se encontró el cliente con ID {vehiculo_data.cliente_id}")

        # Validar patente única
        vehiculo_existente = self.repository.buscar_por_patente(vehiculo_data.patente)
        if vehiculo_existente:
            raise ValueError(f"VEHICLE_LICENSE_PLATE_ALREADY_EXISTS:Ya existe un vehículo registrado con la patente {vehiculo_data.patente}")

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
            raise LookupError(f"VEHICLE_NOT_FOUND:Vehículo con ID {vehiculo_id} no encontrado")
        return vehiculo

    def actualizar_vehiculo(self, vehiculo_id: int, vehiculo_data: VehiculoUpdate) -> Vehiculo:
        vehiculo = self.obtener_vehiculo_por_id(vehiculo_id)

        # Validar patente si viene en el update y es diferente
        if vehiculo_data.patente is not None and vehiculo_data.patente != vehiculo.patente:
            vehiculo_existente = self.repository.buscar_por_patente(vehiculo_data.patente)
            if vehiculo_existente:
                raise ValueError(f"VEHICLE_LICENSE_PLATE_ALREADY_EXISTS:Ya existe un vehículo registrado con la patente {vehiculo_data.patente}")
            vehiculo.patente = vehiculo_data.patente

        # Validar cliente si viene en el update y es diferente
        if vehiculo_data.cliente_id is not None and vehiculo_data.cliente_id != vehiculo.cliente_id:
            cliente_existente = self.cliente_repository.buscar_por_id(vehiculo_data.cliente_id)
            if not cliente_existente:
                raise LookupError(f"CLIENT_NOT_FOUND:No se encontró el cliente con ID {vehiculo_data.cliente_id}")
            vehiculo.cliente_id = vehiculo_data.cliente_id

        # Actualizar campos opcionales
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
        self.obtener_vehiculo_por_id(vehiculo_id)
        self.repository.eliminar(vehiculo_id)