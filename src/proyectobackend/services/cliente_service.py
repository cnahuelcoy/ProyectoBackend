from proyectobackend.domain.cliente import Cliente
from proyectobackend.repositories.cliente_repository import ClienteRepository
from proyectobackend.schemas.cliente import ClienteCreate, ClienteUpdate


class ClienteService:
    def __init__(self, repository: ClienteRepository):
        self._repository = repository

    def crear(self, datos: ClienteCreate) -> Cliente:
        cliente = Cliente(
            id=0,
            nombre=datos.nombre,
            apellido=datos.apellido,
            telefono=datos.telefono,
            email=datos.email,
            direccion=datos.direccion,
        )

        return self._repository.crear(cliente)

    def listar(self) -> list[Cliente]:
        return self._repository.listar()

    def obtener_por_id(self, cliente_id: int) -> Cliente | None:
        return self._repository.buscar_por_id(cliente_id)

    def actualizar(
        self,
        cliente_id: int,
        datos: ClienteUpdate,
    ) -> Cliente | None:
        cliente = self._repository.buscar_por_id(cliente_id)

        if cliente is None:
            return None

        cambios = datos.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        for campo, valor in cambios.items():
            setattr(cliente, campo, valor)

        return self._repository.actualizar(cliente)

    def eliminar(self, cliente_id: int) -> bool:
        return self._repository.eliminar(cliente_id)