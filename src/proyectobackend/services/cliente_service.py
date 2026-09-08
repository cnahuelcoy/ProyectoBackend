import math

from proyectobackend.domain.cliente import Cliente
from proyectobackend.repositories.cliente_repository import ClienteRepository
from proyectobackend.schemas.cliente import ClienteCreate, ClienteUpdate


class ClienteService:
    def __init__(self, repository: ClienteRepository):
        self._repository = repository

    def crear(self, datos: ClienteCreate) -> Cliente:
        cliente_existente = self._repository.buscar_por_email(datos.email)

        if cliente_existente is not None:
            raise ValueError("Ya existe un cliente registrado con este correo")

        cliente = Cliente(
            id=0,
            nombre=datos.nombre,
            apellido=datos.apellido,
            telefono=datos.telefono,
            email=datos.email,
            direccion=datos.direccion,
        )

        return self._repository.crear(cliente)

    def listar(
        self,
        nombre: str | None = None,
        ordenar_por: str = "id",
        direccion: str = "asc",
        pagina: int = 1,
        limite: int = 10,
    ) -> dict:
        clientes = self._repository.listar()

        # 1. FILTRAR
        if nombre is not None:
            clientes = [
                cliente
                for cliente in clientes
                if cliente.nombre.lower() == nombre.lower()
            ]

        # 2. ORDENAR
        descendente = direccion == "desc"

        clientes = sorted(
            clientes,
            key=lambda cliente: getattr(cliente, ordenar_por),
            reverse=descendente,
        )

        # Total después de filtrar, pero antes de paginar
        total = len(clientes)

        # 3. PAGINAR
        inicio = (pagina - 1) * limite
        fin = inicio + limite

        items = clientes[inicio:fin]

        total_paginas = math.ceil(total / limite) if total > 0 else 0

        return {
            "items": items,
            "total": total,
            "pagina": pagina,
            "limite": limite,
            "total_paginas": total_paginas,
        }

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

        email_nuevo = cambios.get("email")

        if email_nuevo is not None:
            cliente_con_email = self._repository.buscar_por_email(email_nuevo)

            if (
                cliente_con_email is not None
                and cliente_con_email.id != cliente_id
            ):
                raise ValueError(
                    "Ya existe un cliente registrado con este correo"
                )

        for campo, valor in cambios.items():
            setattr(cliente, campo, valor)

        return self._repository.actualizar(cliente)

    def eliminar(self, cliente_id: int) -> bool:
        return self._repository.eliminar(cliente_id)