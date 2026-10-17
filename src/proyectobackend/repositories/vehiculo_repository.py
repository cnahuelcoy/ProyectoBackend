from typing import List, Optional

from sqlalchemy import select

from proyectobackend.database.session import SessionLocal
from proyectobackend.domain.vehiculo import Vehiculo
from proyectobackend.models.vehiculo import VehiculoModel


class VehiculoRepository:
    def __init__(self):
        self._vehiculos: dict[int, Vehiculo] = {}
        self._contador_id: int = 1

    @staticmethod
    def _to_domain(model: VehiculoModel) -> Vehiculo:
        return Vehiculo(
            id=model.id,
            patente=model.patente,
            marca=model.marca,
            modelo=model.modelo,
            anio=model.anio,
            kilometraje=model.kilometraje,
            cliente_id=model.cliente_id,
        )

    def crear(self, vehiculo: Vehiculo) -> Vehiculo:
        vehiculo.id = self._contador_id
        self._vehiculos[self._contador_id] = vehiculo
        self._contador_id += 1
        return vehiculo

    def listar(self) -> List[Vehiculo]:
        return list(self._vehiculos.values())

    def buscar_por_id(self, vehiculo_id: int) -> Optional[Vehiculo]:
        return self._vehiculos.get(vehiculo_id)

    def buscar_por_patente(self, patente: str) -> Optional[Vehiculo]:
        for vehiculo in self._vehiculos.values():
            if vehiculo.patente == patente:
                return vehiculo
        return None

    def actualizar(self, vehiculo: Vehiculo) -> Vehiculo:
        self._vehiculos[vehiculo.id] = vehiculo
        return vehiculo

    def eliminar(self, vehiculo_id: int) -> bool:
        if vehiculo_id in self._vehiculos:
            del self._vehiculos[vehiculo_id]
            return True
        return False


# INSTANCIA COMPARTIDA UNICA REQUERIDA POR ARQUITECTURA
vehiculo_repository_instance = VehiculoRepository()