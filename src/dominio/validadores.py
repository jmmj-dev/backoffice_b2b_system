"""Funções de validação reutilizáveis para documentos brasileiros."""
import re


def limpar_documento(documento: str) -> str:
    """Remove tudo que não for dígito (pontos, traços, barras)."""
    return re.sub(r"\D", "", documento)


def validar_cpf(cpf: str) -> bool:
    """Valida um CPF através do cálculo dos dígitos verificadores."""
    cpf = limpar_documento(cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito_1 = 0 if resto == 10 else resto
    if digito_1 != int(cpf[9]):
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito_2 = 0 if resto == 10 else resto
    if digito_2 != int(cpf[10]):
        return False

    return True


def validar_cnpj(cnpj: str) -> bool:
    """Valida um CNPJ através do cálculo dos dígitos verificadores."""
    cnpj = limpar_documento(cnpj)

    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos_1[i] for i in range(12))
    resto = soma % 11
    digito_1 = 0 if resto < 2 else 11 - resto
    if digito_1 != int(cnpj[12]):
        return False

    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos_2[i] for i in range(13))
    resto = soma % 11
    digito_2 = 0 if resto < 2 else 11 - resto
    if digito_2 != int(cnpj[13]):
        return False

    return True