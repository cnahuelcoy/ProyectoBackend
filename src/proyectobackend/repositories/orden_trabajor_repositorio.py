from proyectobackend.domain.orden_trabajo import OrdenTrabajo


class OrdenTrabajoRepository:
    def __init__(self):
        self._ordenes: dict[int, OrdenTrabajo] = {}
        self._next_id = 1

    def crear(self, orden: OrdenTrabajo) -> OrdenTrabajo:
        orden.id = self._next_id
        self._ordenes[self._next_id] = orden
        self._next_id += 1
        return orden

    def listar(self) -> list[OrdenTrabajo]:
        return list(self._ordenes.values())

    def buscar_por_id(self, orden_id: int) -> OrdenTrabajo | None:
        return self._ordenes.get(orden_id)

    def actualizar(self, orden_id: int, orden: OrdenTrabajo) -> OrdenTrabajo | None:
        if orden_id not in self._ordenes:
            return None
        self._ordenes[orden_id] = orden
        return orden
