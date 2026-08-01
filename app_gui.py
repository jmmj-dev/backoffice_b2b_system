"""Ponto de entrada da GUI do Sistema BackOffice B2B (PySide6).

Assim como main.py para a CLI, este arquivo é o Composition Root da GUI:
conecta as implementações concretas (SQLite) às regras de negócio (Serviços).
"""
import sys

from PySide6.QtWidgets import QApplication

from src.infraestrutura.conexao import obter_conexao
from src.infraestrutura.schema import criar_tabelas
from src.interface.gui.main_window import MainWindow
from src.interface.gui.tema import FOLHA_DE_ESTILO
from src.repositorios.sqlite.cliente_repositorio_sqlite import ClienteRepositorioSQLite
from src.repositorios.sqlite.tabela_preco_repositorio_sqlite import TabelaPrecoRepositorioSQLite
from src.servicos.servico_cliente import ServicoCliente
from src.servicos.servico_tabela_preco import ServicoTabelaPreco
from src.servicos.servico_produto import ServicoProduto
from src.repositorios.sqlite.produto_repositorio_sqlite import ProdutoRepositorioSQLite
from src.servicos.servico_servico import ServicoServico
from src.repositorios.sqlite.servico_repositorio_sqlite import ServicoRepositorioSQLite


def main() -> None:
    conexao = obter_conexao()
    criar_tabelas(conexao)

    cliente_repositorio = ClienteRepositorioSQLite(conexao)
    tabela_preco_repositorio = TabelaPrecoRepositorioSQLite(conexao)
    produto_repositorio = ProdutoRepositorioSQLite(conexao)
    servico_repositorio = ServicoRepositorioSQLite(conexao)

    servico_cliente = ServicoCliente(cliente_repositorio, tabela_preco_repositorio)
    servico_tabela_preco = ServicoTabelaPreco(tabela_preco_repositorio, produto_repositorio, servico_repositorio)
    servico_produto = ServicoProduto(produto_repositorio)
    servico_servico = ServicoServico(servico_repositorio)


    app = QApplication(sys.argv)
    app.setStyleSheet(FOLHA_DE_ESTILO)

    janela = MainWindow(servico_cliente, servico_tabela_preco, servico_produto, servico_servico)
    janela.show()

    codigo_saida = app.exec()
    conexao.close()
    sys.exit(codigo_saida)


if __name__ == "__main__":
    main()