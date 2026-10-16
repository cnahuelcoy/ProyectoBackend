from proyectobackend.database.base import Base
from proyectobackend.database.session import engine
from proyectobackend.models.cliente import ClienteModel
from proyectobackend.models.orden_trabajo import OrdenTrabajoModel
from proyectobackend.models.reparacion import ReparacionModel
from proyectobackend.models.vehiculo import VehiculoModel


def init_db() -> None:
    Base.metadata.create_all(bind=engine)