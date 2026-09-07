from proyectobackend.domain.orden_trabajo import OrdenTrabajo

class OrdenTrabajoRepository:   
    def __init__(self):
        self.ordenes: dict[int, OrdenTrabajo] = {}
        self.siguiente_id: int = 1

    def crear(self, orden: OrdenTrabajo) -> OrdenTrabajo:
        orden.id = self.siguiente_id
        self.siguiente_id += 1

        self.ordenes[orden.id] = orden
        return orden

    def listar(self) -> list[OrdenTrabajo]:
        return list(self.ordenes.values())

    def buscar_por_id(self, orden_id: int) -> OrdenTrabajo | None:
        return self.ordenes.get(orden_id)

    def actualizar(self, orden_id: int, orden_actualizada: OrdenTrabajo) -> OrdenTrabajo | None:
        if orden_id in self.ordenes:
            orden_actualizada.id = orden_id
            self.ordenes[orden_id] = orden_actualizada
            return orden_actualizada
        return None 