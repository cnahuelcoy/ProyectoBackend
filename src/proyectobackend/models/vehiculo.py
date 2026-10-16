from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from proyectobackend.database.base import Base


class VehiculoModel(Base):
    __tablename__ = "vehiculos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    patente: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
        unique=True,
    )

    marca: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    modelo: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    anio: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    kilometraje: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    cliente_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clientes.id"),
        nullable=False,
    )