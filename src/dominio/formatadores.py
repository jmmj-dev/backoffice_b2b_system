"""Funções de formatação para exibição, seguindo o padrão brasileiro."""
from decimal import Decimal


def formatar_moeda(valor: Decimal) -> str:
    """Formata um valor Decimal no padrão brasileiro: R$ 1.234,56"""
    valor_str = f"{valor:,.2f}"
    valor_str = valor_str.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    return f"R$ {valor_str}"