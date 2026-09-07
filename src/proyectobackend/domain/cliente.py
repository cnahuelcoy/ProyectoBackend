from dataclasses import dataclass

@dataclass
class Cliente:
    id: int
    nombre: str
    apellido: str
    telefono: str
    email: str
    direccion: str