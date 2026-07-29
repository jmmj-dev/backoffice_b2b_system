"""Entidade Servico: prestação vendável, cobrada por hora estimada."""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.dominio.formatadores import formatar_moeda


@dataclass
class Servico:
    nome: str
    valor_hora: Decimal
    horas_estimadas: Decimal
    descricao: str = ""
    id: Optional[int] = None
    ativo: bool = True
    data_cadastro: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self._validar_nome()
        if not isinstance(self.valor_hora, Decimal):
            self.valor_hora = Decimal(str(self.valor_hora))
        if not isinstance(self.horas_estimadas, Decimal):
            self.horas_estimadas = Decimal(str(self.horas_estimadas))
        self._validar_valor_hora()
        self._validar_horas_estimadas()

    def _validar_nome(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome do serviço não pode ser vazio.")

    def _validar_valor_hora(self) -> None:
        if self.valor_hora <= 0:
            raise ValueError("Valor por hora deve ser maior que zero.")

    def _validar_horas_estimadas(self) -> None:
        if self.horas_estimadas <= 0:
            raise ValueError("Horas estimadas devem ser maior que zero.")

    def inativar(self) -> None:
        self.ativo = False

    def reativar(self) -> None:
        self.ativo = True

    def valor_hora_formatado(self) -> str:
        return formatar_moeda(self.valor_hora)

    def calcular_valor_total_estimado(self) -> Decimal:
        """Calcula o valor total estimado (valor/hora × horas estimadas)."""
        return self.valor_hora * self.horas_estimadas