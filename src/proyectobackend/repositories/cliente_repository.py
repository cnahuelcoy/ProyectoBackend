
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from proyectobackend.database.session import SessionLocal
from proyectobackend.domain.cliente import Cliente
from proyectobackend.models.cliente import ClienteModel
from proyectobackend.models.vehiculo import VehiculoModel


class ClienteRepository:
    @staticmethod
    def _to_domain(model: ClienteModel) -> Cliente:
        return Cliente(
            id=model.id,
            nombre=model.nombre,
            apellido=model.apellido,
            telefono=model.telefono,
            email=model.email,
            direccion=model.direccion,
        )

    def crear(self, cliente: Cliente) -> Cliente:
        with SessionLocal() as session:
            model = ClienteModel(
                nombre=cliente.nombre,
                apellido=cliente.apellido,
                telefono=cliente.telefono,
                email=cliente.email,
                direccion=cliente.direccion,
            )

            session.add(model)
            session.commit()
            session.refresh(model)

            return self._to_domain(model)

    def listar(self) -> list[Cliente]:
        with SessionLocal() as session:
            statement = select(ClienteModel)
            modelos = session.scalars(statement).all()

            return [
                self._to_domain(model)
                for model in modelos
            ]

    def buscar_por_id(self, cliente_id: int) -> Cliente | None:
        with SessionLocal() as session:
            model = session.get(ClienteModel, cliente_id)

            if model is None:
                return None

            return self._to_domain(model)

    def buscar_por_email(self, email: str) -> Cliente | None:
        with SessionLocal() as session:
            statement = select(ClienteModel).where(
                func.lower(ClienteModel.email) == email.lower()
            )

            model = session.scalar(statement)

            if model is None:
                return None

            return self._to_domain(model)

    def actualizar(self, cliente: Cliente) -> Cliente | None:
        with SessionLocal() as session:
            model = session.get(ClienteModel, cliente.id)

            if model is None:
                return None

            model.nombre = cliente.nombre
            model.apellido = cliente.apellido
            model.telefono = cliente.telefono
            model.email = cliente.email
            model.direccion = cliente.direccion

            session.commit()
            session.refresh(model)

            return self._to_domain(model)

    def eliminar(self, cliente_id: int) -> bool:
        with SessionLocal() as session:
            model = session.get(ClienteModel, cliente_id)

            if model is None:
                return False

            vehiculo_asociado = session.scalar(
                select(VehiculoModel.id)
                .where(VehiculoModel.cliente_id == cliente_id)
                .limit(1)
            )

            if vehiculo_asociado is not None:
                raise ValueError(
                    "No se puede eliminar un cliente con vehículos asociados"
                )

            try:
                session.delete(model)
                session.commit()
            except IntegrityError as error:
                session.rollback()
                raise ValueError(
                    "No se puede eliminar un cliente con vehículos asociados"
                ) from error

            return True


cliente_repo = ClienteRepository()
