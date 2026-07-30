"""Entidades TabelaPreco e ItemTabelaPreco: definem preços nomeados por produto/serviço."""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class TipoItem(Enum):
    PRODUTO = "PRODUTO"
    SERVICO = "SERVICO"


@dataclass
class ItemTabelaPreco:
    tipo_item: TipoItem
    referencia_id: int
    preco: Decimal
    id: Optional[int] = None
    ativo: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.preco, Decimal):
            self.preco = Decimal(str(self.preco))
        if self.preco <= 0:
            raise ValueError("Preço do item na tabela deve ser maior que zero.")

    def inativar(self) -> None:
        self.ativo = False


@dataclass
class TabelaPreco:
    nome: str
    descricao: str = ""
    id: Optional[int] = None
    ativa: bool = True
    data_cadastro: datetime = field(default_factory=datetime.now)
    itens: List[ItemTabelaPreco] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validar_nome()

    def _validar_nome(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome da tabela de preço não pode ser vazio.")

    def _buscar_item_ativo(self, tipo_item: TipoItem, referencia_id: int) -> Optional[ItemTabelaPreco]:
        for item in self.itens:
            if item.tipo_item == tipo_item and item.referencia_id == referencia_id and item.ativo:
                return item
        return None

    def adicionar_item(self, tipo_item: TipoItem, referencia_id: int, preco: Decimal) -> ItemTabelaPreco:
        """Adiciona um produto ou serviço a esta tabela de preço, com o valor específico dela."""
        if self._buscar_item_ativo(tipo_item, referencia_id) is not None:
            raise ValueError(
                f"Já existe um item ativo do tipo {tipo_item.value} com referência {referencia_id} nesta tabela."
            )
        novo_item = ItemTabelaPreco(tipo_item=tipo_item, referencia_id=referencia_id, preco=preco)
        self.itens.append(novo_item)
        return novo_item

    def atualizar_preco_item(self, tipo_item: TipoItem, referencia_id: int, novo_preco: Decimal) -> None:
        """Atualiza o preço de um item já existente e ativo na tabela."""
        item = self._buscar_item_ativo(tipo_item, referencia_id)
        if item is None:
            raise ValueError(
                f"Nenhum item ativo do tipo {tipo_item.value} com referência {referencia_id} encontrado nesta tabela."
            )
        if not isinstance(novo_preco, Decimal):
            novo_preco = Decimal(str(novo_preco))
        if novo_preco <= 0:
            raise ValueError("Novo preço deve ser maior que zero.")
        item.preco = novo_preco

    def remover_item(self, tipo_item: TipoItem, referencia_id: int) -> None:
        """Remove (soft delete) um item da tabela. Preserva histórico de propostas antigas que usaram esse preço."""
        item = self._buscar_item_ativo(tipo_item, referencia_id)
        if item is None:
            raise ValueError(
                f"Nenhum item ativo do tipo {tipo_item.value} com referência {referencia_id} encontrado nesta tabela."
            )
        item.inativar()

    def obter_preco(self, tipo_item: TipoItem, referencia_id: int) -> Optional[Decimal]:
        """Retorna o preço de um item nesta tabela, ou None se ele não existir/estiver ativo."""
        item = self._buscar_item_ativo(tipo_item, referencia_id)
        return item.preco if item else None

    def inativar(self) -> None:
        self.ativa = False

    def reativar(self) -> None:
        self.ativa = True