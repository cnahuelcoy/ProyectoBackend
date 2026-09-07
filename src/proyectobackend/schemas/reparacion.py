from datetime import date
from typing import Optional

from pydantic import BaseModel, Field
from proyectobackend.domain.reparacion import TipoReparacion


class ReparacionCreate(BaseModel):
    orden_trabajo_id: int = Field(
        ..., gt=0, description="ID de la orden de trabajo asociada"
    )
    descripcion: str = Field(
        ..., min_length=5, description="Descripción detallada de la reparación"
    )
    tipo: TipoReparacion = Field(
        ..., description="Tipo de trabajo: reparacion, mantencion o diagnostico"
    )
    costo: float = Field(
        ..., ge=0, description="Costo de la reparación, debe ser mayor o igual a 0"
    )
    fecha: date = Field(
        ..., description="Fecha de la reparación (formato YYYY-MM-DD)"
    )


class ReparacionResponse(BaseModel):
    id: int
    orden_trabajo_id: int
    descripcion: str
    tipo: TipoReparacion
    costo: float
    fecha: date

    class Config:
        from_attributes = True

class ReparacionUpdate(BaseModel):
    descripcion: Optional[str] = Field(None, min_length=5)
    tipo: Optional[TipoReparacion] = None
    costo: Optional[float] = Field(None, ge=0)
    fecha: Optional[date] = None