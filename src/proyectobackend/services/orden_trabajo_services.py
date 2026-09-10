from typing import Literal

from proyectobackend.domain.orden_trabajo import EstadoOrdenTrabajo, OrdenTrabajo
from proyectobackend.repositories.orden_trabajo_repositorio import OrdenTrabajoRepository
from proyectobackend.schemas.orden_trabajo_schemas import (
    OrdenTrabajoCreate,
    OrdenTrabajoListadoResponse,
    OrdenTrabajoResponse,
    OrdenTrabajoUpdate,
)
from proyectobackend.repositories.vehiculo_repository import VehiculoRepository

class OrdenTrabajoService:
    def __init__(
        self,
        repository: OrdenTrabajoRepository,
        vehiculo_repository: VehiculoRepository,
    ):
        self.repository = repository
        self.vehiculo_repository = vehiculo_repository

    def crear(self, datos: OrdenTrabajoCreate) -> OrdenTrabajo:
        vehiculo = self.vehiculo_repository.buscar_por_id(datos.vehiculo_id)
        if vehiculo is None:
            raise LookupError(
                f"VEHICLE_NOT_FOUND:No se encontró el vehículo con ID {datos.vehiculo_id}"
            )
        
        orden = OrdenTrabajo(
            vehiculo_id=datos.vehiculo_id,
            fecha_ingreso=datos.fecha_ingreso,
            descripcion_problema=datos.descripcion_problema,
            estado=datos.estado,
            kilometraje_ingreso=datos.kilometraje_ingreso,
        )
        return self.repository.crear(orden)

    def listar(
        self,
        estado: EstadoOrdenTrabajo | None = None,
        ordenar_por: Literal["id", "fecha_ingreso", "kilometraje_ingreso"] = "id",
        direccion: Literal["asc", "desc"] = "asc",
        pagina: int = 1,
        limite: int = 10,
    ) -> OrdenTrabajoListadoResponse:
        ordenes = self.repository.listar()

        # Filtrar antes de ordenar y paginar.
        if estado is not None:
            ordenes = [
                orden
                for orden in ordenes
                if orden.estado == estado
            ]

        ordenes = sorted(
            ordenes,
            key=lambda orden: getattr(orden, ordenar_por),
            reverse=direccion == "desc",
        )

        total = len(ordenes)
        total_paginas = (total + limite - 1) // limite
        inicio = (pagina - 1) * limite
        ordenes_pagina = ordenes[inicio:inicio + limite]

        return OrdenTrabajoListadoResponse(
            items=[
                OrdenTrabajoResponse.model_validate(orden)
                for orden in ordenes_pagina
            ],
            total=total,
            pagina=pagina,
            limite=limite,
            total_paginas=total_paginas,
        )

    def obtener_por_id(self, orden_id: int) -> OrdenTrabajo:
        orden = self.repository.buscar_por_id(orden_id)

        if orden is None:
            raise LookupError(
                f"WORK_ORDER_NOT_FOUND:No se encontró la orden de trabajo con ID {orden_id}"
            )

        return orden

    def actualizar(self, orden_id: int, datos: OrdenTrabajoUpdate) -> OrdenTrabajo:
        orden = self.repository.buscar_por_id(orden_id)
        if orden is None:
            raise LookupError(
                f"WORK_ORDER_NOT_FOUND:No se encontró la orden de trabajo con ID {orden_id}"
            )

        cambios = datos.model_dump(exclude_unset=True, exclude_none=True)

        if "vehiculo_id" in cambios:
            vehiculo = self.vehiculo_repository.buscar_por_id(cambios["vehiculo_id"])
            if vehiculo is None:
                raise LookupError(
                    f"VEHICLE_NOT_FOUND:No se encontró el vehículo con ID {cambios['vehiculo_id']}"
                )

        estado_nuevo = cambios.get("estado")
        if estado_nuevo is not None:
            self._validar_transicion_estado(orden.estado, estado_nuevo)

        for campo, valor in cambios.items():
            setattr(orden, campo, valor)

        orden_actualizada = self.repository.actualizar(orden_id, orden)
        if orden_actualizada is None:
            raise LookupError(
                f"WORK_ORDER_NOT_FOUND:No se encontró la orden de trabajo con ID {orden_id}"
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
                "INVALID_WORK_ORDER_STATE:Una orden finalizada no puede volver a un estado anterior"
            )
