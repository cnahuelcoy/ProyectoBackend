
from datetime import date

from sqlalchemy import Date, Enum as SQLAlchemyEnum, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from proyectobackend.database.base import Base
from proyectobackend.domain.reparacion import TipoReparacion


class ReparacionModel(Base):
    __tablename__ = "reparaciones"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    orden_trabajo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ordenes_trabajo.id"),
        nullable=False,
    )

    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    tipo: Mapped[TipoReparacion] = mapped_column(
        SQLAlchemyEnum(
            TipoReparacion,
            name="tipo_reparacion",
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ],
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
    )

    costo: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
