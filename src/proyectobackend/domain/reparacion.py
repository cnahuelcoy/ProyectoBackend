from dataclasses import dataclass
from datetime import date
from enum import Enum


class TipoReparacion(str, Enum):
    REPARACION = "reparacion"
    MANTENCION = "mantencion"
    DIAGNOSTICO = "diagnostico"


@dataclass
class Reparacion:
    orden_trabajo_id: int
    descripcion: str
    tipo: TipoReparacion
    costo: float
    fecha: date
    id: int | None = None