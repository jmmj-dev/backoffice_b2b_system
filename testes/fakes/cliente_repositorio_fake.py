"""Implementação fake em memória do ClienteRepositorio, usada apenas em testes de serviço."""
import copy
from typing import List, Optional

from src.dominio.entidades.cliente import Cliente
from src.repositorios.contratos.cliente_repositorio import ClienteRepositorio


class ClienteRepositorioFake(ClienteRepositorio):
    def __init__(self) -> None:
        self._clientes: List[Cliente] = []
        self._proximo_id = 1

    def salvar(self, cliente: Cliente) -> Cliente:
        cliente.id = self._proximo_id
        self._proximo_id += 1
        self._clientes.append(copy.deepcopy(cliente))
        return copy.deepcopy(cliente)

    def buscar_por_id(self, id: int) -> Optional[Cliente]:
        cliente = next((c for c in self._clientes if c.id == id), None)
        return copy.deepcopy(cliente) if cliente else None

    def buscar_por_documento(self, documento: str) -> Optional[Cliente]:
        cliente = next((c for c in self._clientes if c.documento == documento), None)
        return copy.deepcopy(cliente) if cliente else None

    def listar_ativos(self) -> List[Cliente]:
        return [copy.deepcopy(c) for c in self._clientes if c.ativo]

    def listar_todos(self) -> List[Cliente]:
        return [copy.deepcopy(c) for c in self._clientes]

    def atualizar(self, cliente: Cliente) -> Cliente:
        for i, c in enumerate(self._clientes):
            if c.id == cliente.id:
                self._clientes[i] = copy.deepcopy(cliente)
                return copy.deepcopy(cliente)
        raise ValueError(f"Cliente com id {cliente.id} não encontrado para atualização.")