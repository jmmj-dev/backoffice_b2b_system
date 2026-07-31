"""Entidade PedidoVenda: gerada a partir de um Orcamento aceito, com itens congelados
(snapshot) e uma máquina de estados de fulfillment (separação → faturamento → entrega)."""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from src.dominio.entidades.tabela_preco import TipoItem


class StatusPedidoVenda(Enum):
    PENDENTE = "PENDENTE"
    EM_SEPARACAO = "EM_SEPARACAO"
    FATURADO = "FATURADO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


# Define quais transições são permitidas a partir de cada status.
_TRANSICOES_PERMITIDAS = {
    StatusPedidoVenda.PENDENTE: {StatusPedidoVenda.EM_SEPARACAO, StatusPedidoVenda.CANCELADO},
    StatusPedidoVenda.EM_SEPARACAO: {StatusPedidoVenda.FATURADO, StatusPedidoVenda.CANCELADO},
    StatusPedidoVenda.FATURADO: {StatusPedidoVenda.ENTREGUE, StatusPedidoVenda.CANCELADO},
    StatusPedidoVenda.ENTREGUE: set(),
    StatusPedidoVenda.CANCELADO: set(),
}


@dataclass
class ItemPedidoVenda:
    """Snapshot de um item, copiado de um ItemOrcamento no momento da criação do pedido."""
    tipo_item: TipoItem
    referencia_id: int
    descricao: str
    preco_unitario: Decimal
    quantidade: Decimal
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if not isinstance(self.preco_unitario, Decimal):
            self.preco_unitario = Decimal(str(self.preco_unitario))
        if not isinstance(self.quantidade, Decimal):
            self.quantidade = Decimal(str(self.quantidade))

    def calcular_subtotal(self) -> Decimal:
        return self.preco_unitario * self.quantidade


@dataclass
class PedidoVenda:
    orcamento_id: int
    cliente_id: int
    itens: List[ItemPedidoVenda]
    id: Optional[int] = None
    status: StatusPedidoVenda = StatusPedidoVenda.PENDENTE
    data_criacao: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        pass  # Validação de "não pode ter zero itens" pertence à criação via ServicoPedidoVenda,
              # não à entidade — reconstituir um pedido existente do banco não deve reexecutar essa regra.

    def calcular_total(self) -> Decimal:
        return sum((item.calcular_subtotal() for item in self.itens), Decimal("0"))

    def avancar_para_em_separacao(self) -> None:
        self._transicionar_para(StatusPedidoVenda.EM_SEPARACAO)

    def faturar(self) -> None:
        self._transicionar_para(StatusPedidoVenda.FATURADO)

    def marcar_como_entregue(self) -> None:
        self._transicionar_para(StatusPedidoVenda.ENTREGUE)

    def cancelar(self) -> None:
        self._transicionar_para(StatusPedidoVenda.CANCELADO)

    def _transicionar_para(self, novo_status: StatusPedidoVenda) -> None:
        transicoes_validas = _TRANSICOES_PERMITIDAS[self.status]
        if novo_status not in transicoes_validas:
            raise ValueError(
                f"Não é possível mudar de '{self.status.value}' para '{novo_status.value}'. "
                f"Transições válidas a partir de '{self.status.value}': "
                f"{sorted(t.value for t in transicoes_validas) or 'nenhuma (status final)'}."
            )
        self.status = novo_status