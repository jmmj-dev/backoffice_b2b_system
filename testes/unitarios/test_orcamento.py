"""Testes da entidade Orcamento e sua máquina de estados."""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.dominio.entidades.orcamento import Orcamento, StatusOrcamento
from src.dominio.entidades.tabela_preco import TipoItem


def _criar_orcamento(dias_validade=15):
    return Orcamento(
        cliente_id=1,
        tabela_preco_id=1,
        data_validade=date.today() + timedelta(days=dias_validade),
    )


def test_criar_orcamento_valido():
    orcamento = _criar_orcamento()
    assert orcamento.status == StatusOrcamento.RASCUNHO
    assert orcamento.desconto_percentual == Decimal("0")


def test_data_validade_no_passado_lanca_erro():
    with pytest.raises(ValueError, match="posterior à data de criação"):
        Orcamento(cliente_id=1, tabela_preco_id=1, data_validade=date.today() - timedelta(days=1))


def test_adicionar_item():
    orcamento = _criar_orcamento()
    item = orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="Parafuso", preco_unitario=Decimal("5.00"), quantidade=Decimal("10")
    )
    assert item.calcular_subtotal() == Decimal("50.00")
    assert len(orcamento.itens) == 1


def test_adicionar_item_fora_de_rascunho_lanca_erro():
    orcamento = _criar_orcamento()
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="Parafuso", preco_unitario=Decimal("5.00"), quantidade=Decimal("1")
    )
    orcamento.enviar()
    with pytest.raises(ValueError, match="adicionar item"):
        orcamento.adicionar_item(
            TipoItem.PRODUTO, referencia_id=2, descricao="Porca", preco_unitario=Decimal("2.00"), quantidade=Decimal("1")
        )


def test_calcular_subtotal_soma_apenas_itens_ativos():
    orcamento = _criar_orcamento()
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("2")
    )
    item_b = orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=2, descricao="B", preco_unitario=Decimal("5.00"), quantidade=Decimal("1")
    )
    item_b.inativar()  # simula remoção direta, já que ainda não há id atribuído por repositório
    assert orcamento.calcular_subtotal() == Decimal("20.00")


def test_remover_item_inexistente_lanca_erro():
    orcamento = _criar_orcamento()
    with pytest.raises(ValueError, match="não encontrado"):
        orcamento.remover_item(999)


def test_aplicar_desconto_valido():
    orcamento = _criar_orcamento()
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("100.00"), quantidade=Decimal("1")
    )
    orcamento.aplicar_desconto(Decimal("10"))
    assert orcamento.calcular_valor_desconto() == Decimal("10.00")
    assert orcamento.calcular_total() == Decimal("90.00")


def test_aplicar_desconto_fora_do_intervalo_lanca_erro():
    orcamento = _criar_orcamento()
    with pytest.raises(ValueError, match="entre 0 e 100"):
        orcamento.aplicar_desconto(Decimal("150"))


def test_enviar_sem_itens_lanca_erro():
    orcamento = _criar_orcamento()
    with pytest.raises(ValueError, match="sem itens"):
        orcamento.enviar()


def test_fluxo_completo_ate_aceito():
    orcamento = _criar_orcamento()
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    orcamento.enviar()
    assert orcamento.status == StatusOrcamento.ENVIADO
    orcamento.aceitar()
    assert orcamento.status == StatusOrcamento.ACEITO


def test_recusar_orcamento():
    orcamento = _criar_orcamento()
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    orcamento.enviar()
    orcamento.recusar()
    assert orcamento.status == StatusOrcamento.RECUSADO


def test_aceitar_sem_enviar_lanca_erro():
    orcamento = _criar_orcamento()
    with pytest.raises(ValueError, match="aceitar"):
        orcamento.aceitar()


def test_esta_expirado_com_data_passada():
    orcamento = _criar_orcamento(dias_validade=1)
    orcamento.data_validade = date.today() - timedelta(days=1)
    assert orcamento.esta_expirado() is True


def test_verificar_expiracao_transiciona_status():
    orcamento = _criar_orcamento()
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    orcamento.enviar()
    orcamento.data_validade = date.today() - timedelta(days=1)

    mudou = orcamento.verificar_expiracao()
    assert mudou is True
    assert orcamento.status == StatusOrcamento.EXPIRADO


def test_aceitar_orcamento_expirado_lanca_erro():
    orcamento = _criar_orcamento()
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    orcamento.enviar()
    orcamento.data_validade = date.today() - timedelta(days=1)

    with pytest.raises(ValueError, match="expirado"):
        orcamento.aceitar()

def test_enviar_registra_evento_automatico_no_historico():
    orcamento = _criar_orcamento()
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    orcamento.enviar()

    assert len(orcamento.historico) == 1
    assert orcamento.historico[0].tipo.value == "AUTOMATICO"
    assert "enviado" in orcamento.historico[0].descricao.lower()


def test_adicionar_anotacao_manual():
    orcamento = _criar_orcamento()
    registro = orcamento.adicionar_anotacao("Cliente pediu desconto extra, negado.")

    assert registro.tipo.value == "MANUAL"
    assert len(orcamento.historico) == 1


def test_anotacao_manual_permitida_em_qualquer_status():
    orcamento = _criar_orcamento()
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    orcamento.enviar()
    orcamento.aceitar()
    # Não deve lançar erro mesmo com o orçamento já ACEITO
    orcamento.adicionar_anotacao("Cliente solicitou entrega expressa.")
    assert len(orcamento.historico) == 3  # enviar + aceitar (automáticos) + anotação manual


def test_anotacao_vazia_lanca_erro():
    orcamento = _criar_orcamento()
    with pytest.raises(ValueError, match="não pode ser vazia"):
        orcamento.adicionar_anotacao("   ")


def test_fluxo_completo_gera_historico_ordenado():
    orcamento = _criar_orcamento()
    orcamento.adicionar_item(
        TipoItem.PRODUTO, referencia_id=1, descricao="A", preco_unitario=Decimal("10.00"), quantidade=Decimal("1")
    )
    orcamento.enviar()
    orcamento.recusar()

    descricoes = [r.descricao for r in orcamento.historico]
    assert "enviado" in descricoes[0].lower()
    assert "recusado" in descricoes[1].lower()        