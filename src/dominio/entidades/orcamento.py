"""Entidade Orcamento: representa uma proposta de preço para um cliente, com itens
congelados (snapshot) no momento da inclusão, histórico de negociação e uma
máquina de estados de aprovação."""
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from src.dominio.entidades.tabela_preco import TipoItem


class StatusOrcamento(Enum):
    RASCUNHO = "RASCUNHO"
    ENVIADO = "ENVIADO"
    ACEITO = "ACEITO"
    RECUSADO = "RECUSADO"
    EXPIRADO = "EXPIRADO"


class TipoRegistroHistorico(Enum):
    AUTOMATICO = "AUTOMATICO"
    MANUAL = "MANUAL"


@dataclass
class ItemOrcamento:
    tipo_item: TipoItem
    referencia_id: int
    descricao: str
    preco_unitario: Decimal
    quantidade: Decimal
    id: Optional[int] = None
    ativo: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.preco_unitario, Decimal):
            self.preco_unitario = Decimal(str(self.preco_unitario))
        if not isinstance(self.quantidade, Decimal):
            self.quantidade = Decimal(str(self.quantidade))
        if self.preco_unitario <= 0:
            raise ValueError("Preço unitário do item deve ser maior que zero.")
        if self.quantidade <= 0:
            raise ValueError("Quantidade do item deve ser maior que zero.")

    def calcular_subtotal(self) -> Decimal:
        return self.preco_unitario * self.quantidade

    def inativar(self) -> None:
        self.ativo = False


@dataclass
class RegistroHistorico:
    tipo: TipoRegistroHistorico
    descricao: str
    id: Optional[int] = None
    data_hora: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.descricao or not self.descricao.strip():
            raise ValueError("Descrição do registro de histórico não pode ser vazia.")


@dataclass
class Orcamento:
    cliente_id: int
    tabela_preco_id: int
    data_validade: date
    id: Optional[int] = None
    status: StatusOrcamento = StatusOrcamento.RASCUNHO
    desconto_percentual: Decimal = field(default_factory=lambda: Decimal("0"))
    data_criacao: datetime = field(default_factory=datetime.now)
    itens: List[ItemOrcamento] = field(default_factory=list)
    historico: List[RegistroHistorico] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.desconto_percentual, Decimal):
            self.desconto_percentual = Decimal(str(self.desconto_percentual))
        self._validar_desconto(self.desconto_percentual)
        if self.data_validade <= self.data_criacao.date():
            raise ValueError("Data de validade deve ser posterior à data de criação.")

    # --- Gestão de itens (só permitida em RASCUNHO) ---

    def adicionar_item(
        self, tipo_item: TipoItem, referencia_id: int, descricao: str, preco_unitario: Decimal, quantidade: Decimal
    ) -> ItemOrcamento:
        self._exigir_status(StatusOrcamento.RASCUNHO, "adicionar item")
        item = ItemOrcamento(
            tipo_item=tipo_item,
            referencia_id=referencia_id,
            descricao=descricao,
            preco_unitario=preco_unitario,
            quantidade=quantidade,
        )
        self.itens.append(item)
        return item

    def remover_item(self, item_id: int) -> None:
        self._exigir_status(StatusOrcamento.RASCUNHO, "remover item")
        item = self._buscar_item_ativo(item_id)
        if item is None:
            raise ValueError(f"Item com id {item_id} não encontrado ou já removido.")
        item.inativar()

    def aplicar_desconto(self, percentual: Decimal) -> None:
        self._exigir_status(StatusOrcamento.RASCUNHO, "aplicar desconto")
        if not isinstance(percentual, Decimal):
            percentual = Decimal(str(percentual))
        self._validar_desconto(percentual)
        self.desconto_percentual = percentual

    # --- Cálculos ---

    def calcular_subtotal(self) -> Decimal:
        return sum((item.calcular_subtotal() for item in self.itens if item.ativo), Decimal("0"))

    def calcular_valor_desconto(self) -> Decimal:
        return (self.calcular_subtotal() * self.desconto_percentual) / Decimal("100")

    def calcular_total(self) -> Decimal:
        return self.calcular_subtotal() - self.calcular_valor_desconto()

    # --- Histórico de negociação ---

    def adicionar_anotacao(self, texto: str) -> RegistroHistorico:
        """Adiciona uma anotação manual ao histórico. Permitido em qualquer status."""
        registro = RegistroHistorico(tipo=TipoRegistroHistorico.MANUAL, descricao=texto)
        self.historico.append(registro)
        return registro

    def _registrar_evento_automatico(self, descricao: str) -> None:
        """Registra internamente uma mudança de status no histórico, de forma automática."""
        registro = RegistroHistorico(tipo=TipoRegistroHistorico.AUTOMATICO, descricao=descricao)
        self.historico.append(registro)

    # --- Transições de status ---

    def enviar(self) -> None:
        self._exigir_status(StatusOrcamento.RASCUNHO, "enviar")
        if not any(item.ativo for item in self.itens):
            raise ValueError("Não é possível enviar um orçamento sem itens.")
        self.status = StatusOrcamento.ENVIADO
        self._registrar_evento_automatico("Orçamento enviado ao cliente.")

    def aceitar(self) -> None:
        self._exigir_status(StatusOrcamento.ENVIADO, "aceitar")
        if self.esta_expirado():
            raise ValueError("Orçamento expirado. Não pode mais ser aceito.")
        self.status = StatusOrcamento.ACEITO
        self._registrar_evento_automatico("Orçamento aceito pelo cliente.")

    def recusar(self) -> None:
        self._exigir_status(StatusOrcamento.ENVIADO, "recusar")
        if self.esta_expirado():
            raise ValueError("Orçamento expirado. Não pode mais ser recusado.")
        self.status = StatusOrcamento.RECUSADO
        self._registrar_evento_automatico("Orçamento recusado pelo cliente.")

    def verificar_expiracao(self) -> bool:
        """Verifica se o prazo passou e, se sim, transiciona automaticamente para EXPIRADO.
        Retorna True se o status mudou nesta chamada."""
        if self.status == StatusOrcamento.ENVIADO and self.esta_expirado():
            self.status = StatusOrcamento.EXPIRADO
            self._registrar_evento_automatico("Orçamento expirou sem resposta do cliente.")
            return True
        return False

    def esta_expirado(self) -> bool:
        return date.today() > self.data_validade

    # --- Auxiliares privados ---

    def _exigir_status(self, status_esperado: StatusOrcamento, acao: str) -> None:
        if self.status != status_esperado:
            raise ValueError(
                f"Não é possível {acao}: orçamento está em '{self.status.value}', "
                f"esperado '{status_esperado.value}'."
            )

    def _buscar_item_ativo(self, item_id: int) -> Optional[ItemOrcamento]:
        return next((item for item in self.itens if item.id == item_id and item.ativo), None)

    def _validar_desconto(self, percentual: Decimal) -> None:
        if percentual < 0 or percentual > 100:
            raise ValueError("Desconto percentual deve estar entre 0 e 100.")