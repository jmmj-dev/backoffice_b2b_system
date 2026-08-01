"""Ponto de entrada do Sistema BackOffice B2B.

Este arquivo e o Composition Root: o unico lugar do sistema onde as
implementacoes concretas (SQLite) sao conectadas as regras de negocio (Servicos).
"""
from src.infraestrutura.conexao import obter_conexao
from src.infraestrutura.schema import criar_tabelas
from src.interface.cli.menu_principal import exibir_menu_principal
from src.repositorios.sqlite.cliente_repositorio_sqlite import ClienteRepositorioSQLite
from src.repositorios.sqlite.orcamento_repositorio_sqlite import OrcamentoRepositorioSQLite
from src.repositorios.sqlite.pedido_venda_repositorio_sqlite import PedidoVendaRepositorioSQLite
from src.repositorios.sqlite.produto_repositorio_sqlite import ProdutoRepositorioSQLite
from src.repositorios.sqlite.servico_repositorio_sqlite import ServicoRepositorioSQLite
from src.repositorios.sqlite.tabela_preco_repositorio_sqlite import TabelaPrecoRepositorioSQLite
from src.servicos.servico_cliente import ServicoCliente
from src.servicos.servico_orcamento import ServicoOrcamento
from src.servicos.servico_pedido_venda import ServicoPedidoVenda
from src.servicos.servico_produto import ServicoProduto
from src.servicos.servico_servico import ServicoServico
from src.servicos.servico_tabela_preco import ServicoTabelaPreco


def main() -> None:
    conexao = obter_conexao()
    criar_tabelas(conexao)

    cliente_repositorio = ClienteRepositorioSQLite(conexao)
    produto_repositorio = ProdutoRepositorioSQLite(conexao)
    servico_repositorio = ServicoRepositorioSQLite(conexao)
    tabela_preco_repositorio = TabelaPrecoRepositorioSQLite(conexao)
    orcamento_repositorio = OrcamentoRepositorioSQLite(conexao)
    pedido_venda_repositorio = PedidoVendaRepositorioSQLite(conexao)

    servico_cliente = ServicoCliente(cliente_repositorio, tabela_preco_repositorio)
    servico_produto = ServicoProduto(produto_repositorio)
    servico_servico = ServicoServico(servico_repositorio)
    servico_tabela_preco = ServicoTabelaPreco(tabela_preco_repositorio, produto_repositorio, servico_repositorio)
    servico_orcamento = ServicoOrcamento(
        orcamento_repositorio, cliente_repositorio, tabela_preco_repositorio, produto_repositorio, servico_repositorio
    )
    servico_pedido_venda = ServicoPedidoVenda(pedido_venda_repositorio, orcamento_repositorio)

    try:
        exibir_menu_principal(
            servico_cliente, servico_produto, servico_servico, servico_tabela_preco,
            servico_orcamento, servico_pedido_venda,
        )
    finally:
        conexao.close()


if __name__ == "__main__":
    main()