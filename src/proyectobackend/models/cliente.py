from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from proyectobackend.database.base import Base


class ClienteModel(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    apellido: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    telefono: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    direccion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )