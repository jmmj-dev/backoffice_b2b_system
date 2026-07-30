"""Ponto de entrada do Sistema BackOffice B2B.

Este arquivo é o Composition Root: o único lugar do sistema onde as
implementações concretas (SQLite) são conectadas às regras de negócio (Serviços).
"""
from src.infraestrutura.conexao import obter_conexao
from src.infraestrutura.schema import criar_tabelas
from src.interface.cli.menu_principal import exibir_menu_principal
from src.repositorios.sqlite.cliente_repositorio_sqlite import ClienteRepositorioSQLite
from src.repositorios.sqlite.produto_repositorio_sqlite import ProdutoRepositorioSQLite
from src.servicos.servico_cliente import ServicoCliente
from src.servicos.servico_produto import ServicoProduto


def main() -> None:
    conexao = obter_conexao()
    criar_tabelas(conexao)

    cliente_repositorio = ClienteRepositorioSQLite(conexao)
    produto_repositorio = ProdutoRepositorioSQLite(conexao)

    servico_cliente = ServicoCliente(cliente_repositorio)
    servico_produto = ServicoProduto(produto_repositorio)

    try:
        exibir_menu_principal(servico_cliente, servico_produto)
    finally:
        conexao.close()


if __name__ == "__main__":
    main()