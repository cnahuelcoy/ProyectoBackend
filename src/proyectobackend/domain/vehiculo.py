from dataclasses import dataclass
from typing import Optional

@dataclass
class Vehiculo:
    id: Optional[int]
    patente: str
    marca: str
    modelo: str
    anio: int
    kilometraje: int
    cliente_id: int