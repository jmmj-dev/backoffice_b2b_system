"""Janela principal da GUI: barra lateral de navegação + área de conteúdo que troca de tela."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFrame, QStackedWidget, QLabel
)

from src.interface.gui.telas.cliente_view import ClienteView
from src.servicos.servico_cliente import ServicoCliente
from src.servicos.servico_tabela_preco import ServicoTabelaPreco
from src.interface.gui.telas.produto_view import ProdutoView
from src.servicos.servico_produto import ServicoProduto


class MainWindow(QMainWindow):
    def __init__(
        self, servico_cliente: ServicoCliente, servico_tabela_preco: ServicoTabelaPreco,
        servico_produto: ServicoProduto,
    ) -> None:
        super().__init__()
        self.setWindowTitle("BackOffice B2B")
        self.resize(1100, 700)

        widget_central = QWidget()
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        layout_principal.addWidget(self._construir_sidebar())

        self.conteudo = QStackedWidget()
        self._pagina_clientes = ClienteView(servico_cliente, servico_tabela_preco)
        self.conteudo.addWidget(self._pagina_clientes)
        self.conteudo.addWidget(ProdutoView(servico_produto))
        self.conteudo.addWidget(self._construir_pagina_em_breve("Serviços"))
        self.conteudo.addWidget(self._construir_pagina_em_breve("Tabelas de Preço"))
        self.conteudo.addWidget(self._construir_pagina_em_breve("Orçamentos"))
        self.conteudo.addWidget(self._construir_pagina_em_breve("Pedidos de Venda"))

        layout_principal.addWidget(self.conteudo, stretch=1)
        self.setCentralWidget(widget_central)

    def _construir_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(4)

        titulo = QLabel("  BackOffice B2B")
        titulo.setStyleSheet("color: white; font-size: 16px; font-weight: 700; padding: 8px 16px;")
        layout.addWidget(titulo)
        layout.addSpacing(16)

        secoes = ["Clientes", "Produtos", "Serviços", "Tabelas de Preço", "Orçamentos", "Pedidos de Venda"]
        self._botoes_sidebar = []
        for indice, nome in enumerate(secoes):
            botao = QPushButton(nome)
            botao.setObjectName("botaoSidebar")
            botao.setCheckable(True)
            botao.clicked.connect(lambda _checked, i=indice: self._trocar_pagina(i))
            layout.addWidget(botao)
            self._botoes_sidebar.append(botao)

        self._botoes_sidebar[0].setChecked(True)
        layout.addStretch()
        return sidebar

    def _construir_pagina_em_breve(self, nome_secao: str) -> QWidget:
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        label = QLabel(f"{nome_secao} — em construção")
        label.setObjectName("titulo")
        layout.addWidget(label)
        layout.addStretch()
        return pagina

    def _trocar_pagina(self, indice: int) -> None:
        self.conteudo.setCurrentIndex(indice)
        for i, botao in enumerate(self._botoes_sidebar):
            botao.setChecked(i == indice)