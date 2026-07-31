"""Contrato (interface abstrata) para persistência de PedidoVenda (agregado, com seus itens)."""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.dominio.entidades.pedido_venda import PedidoVenda


class PedidoVendaRepositorio(ABC):
    @abstractmethod
    def salvar(self, pedido: PedidoVenda) -> PedidoVenda:
        """Persiste um novo pedido de venda e todos os seus itens."""

    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[PedidoVenda]:
        """Busca um pedido de venda, já com seus itens carregados. Retorna None se não encontrado."""

    @abstractmethod
    def buscar_por_orcamento_id(self, orcamento_id: int) -> Optional[PedidoVenda]:
        """Busca o pedido de venda gerado a partir de um orçamento específico, se existir."""

    @abstractmethod
    def listar_por_cliente(self, cliente_id: int) -> List[PedidoVenda]:
        """Lista todos os pedidos de venda de um cliente (com itens carregados)."""

    @abstractmethod
    def listar_todos(self) -> List[PedidoVenda]:
        """Lista todos os pedidos de venda do sistema (sem carregar itens, para listagens rápidas)."""

    @abstractmethod
    def atualizar(self, pedido: PedidoVenda) -> PedidoVenda:
        """Atualiza o status do pedido de venda."""