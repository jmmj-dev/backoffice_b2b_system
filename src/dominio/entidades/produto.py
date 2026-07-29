"""Entidade Produto: item físico vendável, medido por unidade."""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from src.dominio.formatadores import formatar_moeda


class UnidadeMedida(Enum):
    UNIDADE = "UN"
    CAIXA = "CX"
    QUILOGRAMA = "KG"
    LITRO = "L"
    METRO = "M"
    PACOTE = "PCT"


@dataclass
class Produto:
    nome: str
    unidade_medida: UnidadeMedida
    preco_unitario: Decimal
    descricao: str = ""
    id: Optional[int] = None
    ativo: bool = True
    data_cadastro: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self._validar_nome()
        self._validar_preco()
        if not isinstance(self.preco_unitario, Decimal):
            self.preco_unitario = Decimal(str(self.preco_unitario))

    def _validar_nome(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome do produto não pode ser vazio.")

    def _validar_preco(self) -> None:
        if self.preco_unitario <= 0:
            raise ValueError("Preço unitário deve ser maior que zero.")

    def inativar(self) -> None:
        self.ativo = False

    def reativar(self) -> None:
        self.ativo = True

    def preco_formatado(self) -> str:
        return formatar_moeda(self.preco_unitario)

    def calcular_subtotal(self, quantidade: Decimal) -> Decimal:
        """Calcula o subtotal para uma dada quantidade deste produto."""
        if quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")
        return self.preco_unitario * Decimal(str(quantidade))