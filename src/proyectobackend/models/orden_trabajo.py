from datetime import date

from sqlalchemy import Date, Enum as SQLAlchemyEnum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from proyectobackend.database.base import Base
from proyectobackend.domain.orden_trabajo import EstadoOrdenTrabajo


class OrdenTrabajoModel(Base):
    __tablename__ = "ordenes_trabajo"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    vehiculo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("vehiculos.id"),
        nullable=False,
    )

    fecha_ingreso: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    descripcion_problema: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    kilometraje_ingreso: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    estado: Mapped[EstadoOrdenTrabajo] = mapped_column(
        SQLAlchemyEnum(
            EstadoOrdenTrabajo,
            name="estado_orden_trabajo",
            values_callable=lambda estados: [estado.value for estado in estados],
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
        ),
        nullable=False,
        default=EstadoOrdenTrabajo.PENDIENTE,
    )
