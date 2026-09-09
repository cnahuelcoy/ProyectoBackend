from proyectobackend.domain.reparacion import Reparacion


class ReparacionRepository:

    def __init__(self) -> None:
        self._storage: dict[int, Reparacion] = {}
        self._next_id: int = 1

    def crear(self, reparacion: Reparacion) -> Reparacion:
        reparacion.id = self._next_id
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