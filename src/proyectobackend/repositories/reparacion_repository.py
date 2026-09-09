from proyectobackend.domain.reparacion import Reparacion
from proyectobackend.schemas.reparacion import ReparacionCreate


class ReparacionRepository:

    def __init__(self) -> None:
        self._storage: dict[int, Reparacion] = {}
        self._next_id: int = 1

    def crear(self, dto: ReparacionCreate) -> Reparacion:
        reparacion = Reparacion(
            id=self._next_id,
            orden_trabajo_id=dto.orden_trabajo_id,
            descripcion=dto.descripcion,
            tipo=dto.tipo,
            costo=dto.costo,
            fecha=dto.fecha,
        )
        self._storage[self._next_id] = reparacion
        self._next_id += 1
        return reparacion

    def listar(self) -> list[Reparacion]:
        return list(self._storage.values())

    def buscar_por_id(self, reparacion_id: int) -> Reparacion | None:
        return self._storage.get(reparacion_id)

    def actualizar(self, reparacion_id: int, datos: dict) -> Reparacion | None:
        reparacion = self.buscar_por_id(reparacion_id)
        if not reparacion:
            return None
        for campo, valor in datos.items():
            setattr(reparacion, campo, valor)
        return reparacion

    def eliminar(self, reparacion_id: int) -> bool:
        if reparacion_id in self._storage:
            del self._storage[reparacion_id]
            return True
        return False


# Shared instance for dependency injection
reparacion_repository_instance = ReparacionRepository()