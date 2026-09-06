from pydantic import BaseModel, ConfigDict, Field


EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class ClienteBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=50)
    apellido: str = Field(min_length=2, max_length=50)
    telefono: str = Field(min_length=8, max_length=15)
    email: str = Field(pattern=EMAIL_PATTERN)
    direccion: str = Field(min_length=3, max_length=100)


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=50)
    apellido: str | None = Field(default=None, min_length=2, max_length=50)
    telefono: str | None = Field(default=None, min_length=8, max_length=15)
    email: str | None = Field(default=None, pattern=EMAIL_PATTERN)
    direccion: str | None = Field(default=None, min_length=3, max_length=100)


class ClienteResponse(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int