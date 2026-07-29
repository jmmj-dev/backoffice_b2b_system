"""Entidade Cliente: representa uma pessoa física ou jurídica que compra da empresa."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from src.dominio.validadores import limpar_documento, validar_cpf, validar_cnpj


class TipoPessoa(Enum):
    FISICA = "FISICA"
    JURIDICA = "JURIDICA"


@dataclass
class Cliente:
    nome: str
    tipo_pessoa: TipoPessoa
    documento: str
    email: str
    telefone: str
    id: Optional[int] = None
    ativo: bool = True
    data_cadastro: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        self.documento = limpar_documento(self.documento)
        self._validar_nome()
        self._validar_documento()
        self._validar_email()

    def _validar_nome(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome do cliente não pode ser vazio.")

    def _validar_documento(self) -> None:
        if self.tipo_pessoa == TipoPessoa.FISICA:
            if not validar_cpf(self.documento):
                raise ValueError(f"CPF inválido: {self.documento}")
        elif self.tipo_pessoa == TipoPessoa.JURIDICA:
            if not validar_cnpj(self.documento):
                raise ValueError(f"CNPJ inválido: {self.documento}")

    def _validar_email(self) -> None:
        if "@" not in self.email or "." not in self.email.split("@")[-1]:
            raise ValueError(f"E-mail inválido: {self.email}")

    def inativar(self) -> None:
        """Soft delete: cliente deixa de ser usável em novas operações, mas seu histórico é preservado."""
        self.ativo = False

    def reativar(self) -> None:
        self.ativo = True

    def documento_formatado(self) -> str:
        """Retorna o documento no formato de exibição brasileiro (com pontuação)."""
        d = self.documento
        if self.tipo_pessoa == TipoPessoa.FISICA:
            return f"{d[0:3]}.{d[3:6]}.{d[6:9]}-{d[9:11]}"
        return f"{d[0:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:14]}"