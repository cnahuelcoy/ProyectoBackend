from dataclasses import dataclass
from datetime import date
from enum import Enum


class EstadoOrdenTrabajo(str, Enum):
    PENDIENTE = "pendiente"
    EN_REPARACION = "en_reparacion"
    FINALIZADA = "finalizada"


@dataclass
class OrdenTrabajo:
    vehiculo_id: int
    fecha_ingreso: date
    descripcion_problema: str
    kilometraje_ingreso: int
    estado: EstadoOrdenTrabajo = EstadoOrdenTrabajo.PENDIENTE
    id: int | None = None