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
        with SessionLocal() as session:
            model = VehiculoModel(
                patente=vehiculo.patente,
                marca=vehiculo.marca,
                modelo=vehiculo.modelo,
                anio=vehiculo.anio,
                kilometraje=vehiculo.kilometraje,
                cliente_id=vehiculo.cliente_id,
            )

            session.add(model)
            session.commit()
            session.refresh(model)

            return self._to_domain(model)

    def listar(self) -> list[Vehiculo]:
        with SessionLocal() as session:
            # Keep insertion order, as the previous in-memory dict did
            statement = select(VehiculoModel).order_by(VehiculoModel.id)
            modelos = session.scalars(statement).all()

            return [
                self._to_domain(model)
                for model in modelos
            ]

    def buscar_por_id(self, vehiculo_id: int) -> Vehiculo | None:
        with SessionLocal() as session:
            model = session.get(VehiculoModel, vehiculo_id)

            if model is None:
                return None

            return self._to_domain(model)

    def buscar_por_patente(self, patente: str) -> Vehiculo | None:
        with SessionLocal() as session:
            statement = select(VehiculoModel).where(
                VehiculoModel.patente == patente
            )

            model = session.scalar(statement)

            if model is None:
                return None

            return self._to_domain(model)

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