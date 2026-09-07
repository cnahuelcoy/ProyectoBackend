from pydantic import BaseModel, Field, ConfigDict

class VehiculoBase(BaseModel):
    patente: str = Field(..., min_length=6, max_length=6, description="Patente del vehículo (6 caracteres)")
    marca: str = Field(..., min_length=1, description="Marca no puede estar vacía")
    modelo: str = Field(..., min_length=1, description="Modelo no puede estar vacío")
    anio: int = Field(..., ge=1886, le=2027, description="Año de fabricación válido")
    kilometraje: int = Field(..., ge=0, description="El kilometraje no puede ser negativo")
    cliente_id: int = Field(..., gt=0, description="ID del cliente asociado")

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoResponse(VehiculoBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)