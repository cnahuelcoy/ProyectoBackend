class DummyOrdenTrabajo:
    def __init__(self, id: int) -> None:
        self.id = id


class OrdenTrabajoRepository:
    def __init__(self) -> None:
        # Inicializamos con la orden ID 1 creada para pruebas
        self._storage: dict[int, DummyOrdenTrabajo] = {1: DummyOrdenTrabajo(id=1)}

    def buscar_por_id(self, orden_id: int) -> DummyOrdenTrabajo | None:
        return self._storage.get(orden_id)


orden_trabajo_repository_instance = OrdenTrabajoRepository()