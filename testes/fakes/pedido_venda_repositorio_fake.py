"""Implementação fake em memória do PedidoVendaRepositorio, usada apenas em testes de serviço."""
import copy
from typing import List, Optional

from src.dominio.entidades.pedido_venda import PedidoVenda
from src.repositorios.contratos.pedido_venda_repositorio import PedidoVendaRepositorio


class PedidoVendaRepositorioFake(PedidoVendaRepositorio):
    def __init__(self) -> None:
        self._pedidos: List[PedidoVenda] = []
        self._proximo_id = 1
        self._proximo_id_item = 1

    def salvar(self, pedido: PedidoVenda) -> PedidoVenda:
        pedido.id = self._proximo_id
        self._proximo_id += 1
        for item in pedido.itens:
            item.id = self._proximo_id_item
            self._proximo_id_item += 1
        self._pedidos.append(copy.deepcopy(pedido))
        return copy.deepcopy(pedido)

    def buscar_por_id(self, id: int) -> Optional[PedidoVenda]:
        pedido = next((p for p in self._pedidos if p.id == id), None)
        return copy.deepcopy(pedido) if pedido else None

    def buscar_por_orcamento_id(self, orcamento_id: int) -> Optional[PedidoVenda]:
        pedido = next((p for p in self._pedidos if p.orcamento_id == orcamento_id), None)
        return copy.deepcopy(pedido) if pedido else None

    def listar_por_cliente(self, cliente_id: int) -> List[PedidoVenda]:
        return [copy.deepcopy(p) for p in self._pedidos if p.cliente_id == cliente_id]

    def listar_todos(self) -> List[PedidoVenda]:
        return [copy.deepcopy(p) for p in self._pedidos]

    def atualizar(self, pedido: PedidoVenda) -> PedidoVenda:
        for i, p in enumerate(self._pedidos):
            if p.id == pedido.id:
                self._pedidos[i] = copy.deepcopy(pedido)
                return copy.deepcopy(pedido)
        raise ValueError(f"Pedido de venda com id {pedido.id} não encontrado para atualização.")