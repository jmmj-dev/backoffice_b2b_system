"""ServicoCliente: orquestra as regras de negócio de cadastro e gestão de clientes."""
from typing import List

from src.dominio.entidades.cliente import Cliente
from src.dominio.validadores import limpar_documento
from src.repositorios.contratos.cliente_repositorio import ClienteRepositorio


class ServicoCliente:
    def __init__(self, cliente_repositorio: ClienteRepositorio) -> None:
        self._repositorio = cliente_repositorio

    def criar_cliente(self, cliente: Cliente) -> Cliente:
        """Cadastra um novo cliente, impedindo duplicidade de documento (mesmo com cliente inativo)."""
        existente = self._repositorio.buscar_por_documento(cliente.documento)
        if existente is not None:
            if existente.ativo:
                raise ValueError(
                    f"Já existe um cliente ativo com o documento {existente.documento_formatado()}."
                )
            raise ValueError(
                f"Já existe um cliente inativo com o documento {existente.documento_formatado()}. "
                f"Reative o cliente existente (id {existente.id}) em vez de criar um novo."
            )
        return self._repositorio.salvar(cliente)

    def atualizar_cliente(self, cliente: Cliente) -> Cliente:
        """Atualiza os dados de um cliente já existente."""
        if cliente.id is None:
            raise ValueError("Não é possível atualizar um cliente sem id.")
        existente = self._repositorio.buscar_por_id(cliente.id)
        if existente is None:
            raise ValueError(f"Cliente com id {cliente.id} não encontrado.")

        documento_limpo = limpar_documento(cliente.documento)
        if documento_limpo != existente.documento:
            outro = self._repositorio.buscar_por_documento(documento_limpo)
            if outro is not None and outro.id != cliente.id:
                raise ValueError(f"O documento {cliente.documento_formatado()} já pertence a outro cliente.")

        return self._repositorio.atualizar(cliente)

    def inativar_cliente(self, id: int) -> Cliente:
        """Inativa (soft delete) um cliente pelo id."""
        cliente = self._buscar_ou_lancar_erro(id)
        cliente.inativar()
        return self._repositorio.atualizar(cliente)

    def reativar_cliente(self, id: int) -> Cliente:
        """Reativa um cliente previamente inativado."""
        cliente = self._buscar_ou_lancar_erro(id)
        cliente.reativar()
        return self._repositorio.atualizar(cliente)

    def buscar_por_id(self, id: int) -> Cliente:
        return self._buscar_ou_lancar_erro(id)

    def listar_clientes_ativos(self) -> List[Cliente]:
        return self._repositorio.listar_ativos()

    def listar_todos_os_clientes(self) -> List[Cliente]:
        return self._repositorio.listar_todos()

    def _buscar_ou_lancar_erro(self, id: int) -> Cliente:
        cliente = self._repositorio.buscar_por_id(id)
        if cliente is None:
            raise ValueError(f"Cliente com id {id} não encontrado.")
        return cliente