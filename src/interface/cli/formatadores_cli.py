"""Funções auxiliares de conversão de formato para a interface de linha de comando."""
from datetime import date


def ler_data_br(texto: str) -> date:
    """Converte uma data no formato brasileiro (DD/MM/AAAA) para um objeto date.
    Lança ValueError com mensagem amigável se o formato estiver errado."""
    partes = texto.strip().split("/")
    if len(partes) != 3:
        raise ValueError(f"Data '{texto}' inválida. Use o formato DD/MM/AAAA.")
    try:
        dia, mes, ano = (int(p) for p in partes)
        return date(ano, mes, dia)
    except ValueError:
        raise ValueError(f"Data '{texto}' inválida. Use o formato DD/MM/AAAA.")


def formatar_data_br(data: date) -> str:
    """Converte um objeto date para exibição no formato brasileiro (DD/MM/AAAA)."""
    return data.strftime("%d/%m/%Y")