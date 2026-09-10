from proyectobackend.domain.cliente import Cliente


class ClienteRepository:
    def __init__(self):
        self._clientes: list[Cliente] = []
        self._next_id = 1

    def crear(self, cliente: Cliente) -> Cliente:
        cliente.id = self._next_id
        self._next_id += 1

        self._clientes.append(cliente)
        return cliente

    def listar(self) -> list[Cliente]:
        return self._clientes.copy()

    def buscar_por_id(self, cliente_id: int) -> Cliente | None:
        for cliente in self._clientes:
            if cliente.id == cliente_id:
                return cliente

        return None

    def buscar_por_email(self, email: str) -> Cliente | None:
        for cliente in self._clientes:
            if cliente.email.lower() == email.lower():
                return cliente

        return None

    def actualizar(self, cliente: Cliente) -> Cliente | None:
        for indice, cliente_existente in enumerate(self._clientes):
            if cliente_existente.id == cliente.id:
                self._clientes[indice] = cliente
                return cliente

        return None

    def eliminar(self, cliente_id: int) -> bool:
        for indice, cliente in enumerate(self._clientes):
            if cliente.id == cliente_id:
                self._clientes.pop(indice)
                return True

        return False


cliente_repo = ClienteRepository()