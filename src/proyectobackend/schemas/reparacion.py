"""Validaciones y ejemplos OpenAPI del módulo de Reparaciones."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from proyectobackend.domain.reparacion import TipoReparacion


class ReparacionCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "orden_trabajo_id": 1,
                    "descripcion": "Cambio de pastillas de freno",
                    "tipo": "mantencion",
                    "costo": 45000.0,
                    "fecha": "2025-10-07",
                }
            ]
        }
    )

    orden_trabajo_id: int = Field(
        ...,
        gt=0,
        description="ID positivo de una orden de trabajo existente",
    )
    descripcion: str = Field(
        ...,
        min_length=5,
        description="Descripción de la reparación (mínimo 5 caracteres)",
    )
    tipo: TipoReparacion = Field(
        ...,
        description="Tipo de trabajo: reparacion, mantencion o diagnostico",
    )
    costo: float = Field(
        ...,
        ge=0,
        description="Costo no negativo de la reparación",
    )
    fecha: date = Field(
        ...,
        description="Fecha de la reparación (YYYY-MM-DD); no puede ser futura",
    )


class ReparacionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "orden_trabajo_id": 1,
                    "descripcion": "Cambio de pastillas de freno",
                    "tipo": "mantencion",
                    "costo": 45000.0,
                    "fecha": "2025-10-07",
                }
            ]
        },
    )

    id: int
    orden_trabajo_id: int
    descripcion: str
    tipo: TipoReparacion
    costo: float
    fecha: date


class ReparacionUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "descripcion": "Cambio de pastillas y revisión de discos",
                    "costo": 48000.0,
                }
            ]
        }
    )

    descripcion: Optional[str] = Field(
        default=None,
        min_length=5,
        description="Nueva descripción, si corresponde (mínimo 5 caracteres)",
    )
    tipo: Optional[TipoReparacion] = Field(
        default=None,
        description="Nuevo tipo, si corresponde",
    )
    costo: Optional[float] = Field(
        default=None,
        ge=0,
        description="Nuevo costo no negativo, si corresponde",
    )
    fecha: Optional[date] = Field(
        default=None,
        description="Nueva fecha (YYYY-MM-DD); no puede ser futura",
    )
