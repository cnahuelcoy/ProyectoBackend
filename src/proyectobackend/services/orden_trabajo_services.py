from proyectobackend.domain.orden_trabajo import EstadoOrdenTrabajo, OrdenTrabajo
from proyectobackend.repositories.orden_trabajo_repositorio import OrdenTrabajoRepository
from proyectobackend.schemas.orden_trabajo_schemas import OrdenTrabajoCreate, OrdenTrabajoUpdate


class OrdenTrabajoService:
    def __init__(self, repository: OrdenTrabajoRepository):
        self.repository = repository

    def crear(self, datos: OrdenTrabajoCreate) -> OrdenTrabajo:
        orden = OrdenTrabajo(
            vehiculo_id=datos.vehiculo_id,
            fecha_ingreso=datos.fecha_ingreso,
            descripcion_problema=datos.descripcion_problema,
            estado=datos.estado,
            kilometraje_ingreso=datos.kilometraje_ingreso,
        )
        return self.repository.crear(orden)

    def listar(self) -> list[OrdenTrabajo]:
        return self.repository.listar()

    def actualizar(self, orden_id: int, datos: OrdenTrabajoUpdate) -> OrdenTrabajo:
        orden = self.repository.buscar_por_id(orden_id)
        if orden is None:
            raise LookupError(
                f"No se encontró la orden de trabajo con ID {orden_id}"
            )

        cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

        estado_nuevo = cambios.get("estado")
        if estado_nuevo is not None:
            self._validar_transicion_estado(orden.estado, estado_nuevo)

        for campo, valor in cambios.items():
            setattr(orden, campo, valor)

        orden_actualizada = self.repository.actualizar(orden_id, orden)
        if orden_actualizada is None:
            raise LookupError(
                f"No se encontró la orden de trabajo con ID {orden_id}"
            )
        return orden_actualizada

    @staticmethod
    def _validar_transicion_estado(
        estado_actual: EstadoOrdenTrabajo,
        estado_nuevo: EstadoOrdenTrabajo,
    ) -> None:
        if (
            estado_actual == EstadoOrdenTrabajo.FINALIZADA
            and estado_nuevo != EstadoOrdenTrabajo.FINALIZADA
        ):
            raise ValueError(
                "Una orden finalizada no puede volver a un estado anterior"
            )
