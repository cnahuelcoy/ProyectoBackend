from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from proyectobackend.domain.orden_trabajo import EstadoOrdenTrabajo


class OrdenTrabajoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    vehiculo_id: int
    fecha_ingreso: date
    descripcion_problema: str = Field(min_length=5)
    estado: EstadoOrdenTrabajo = EstadoOrdenTrabajo.PENDIENTE
    kilometraje_ingreso: int = Field(ge=0)


class OrdenTrabajoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    vehiculo_id: int | None = None
    fecha_ingreso: date | None = None
    descripcion_problema: str | None = Field(default=None, min_length=5)
    estado: EstadoOrdenTrabajo | None = None
    kilometraje_ingreso: int | None = Field(default=None, ge=0)


class OrdenTrabajoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehiculo_id: int
    fecha_ingreso: date
    descripcion_problema: str
    estado: EstadoOrdenTrabajo
    kilometraje_ingreso: int