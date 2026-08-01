"""Tela de gestão de Serviços prestados na GUI."""
from decimal import Decimal, InvalidOperation

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QLineEdit, QMessageBox, QHeaderView
)

from src.dominio.entidades.servico import Servico
from src.servicos.servico_servico import ServicoServico


class ServicoView(QWidget):
    def __init__(self, servico: ServicoServico) -> None:
        super().__init__()
        self._servico = servico
        self._construir_interface()
        self._carregar_servicos()

    def _construir_interface(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel("Serviços")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        barra_acoes = QHBoxLayout()
        botao_novo = QPushButton("+ Novo Serviço")
        botao_novo.clicked.connect(self._abrir_dialogo_novo_servico)
        barra_acoes.addWidget(botao_novo)

        botao_editar_valor = QPushButton("Editar Valor/Hora")
        botao_editar_valor.setObjectName("botaoSecundario")
        botao_editar_valor.clicked.connect(self._editar_valor_hora)
        barra_acoes.addWidget(botao_editar_valor)

        botao_inativar = QPushButton("Inativar")
        botao_inativar.setObjectName("botaoPerigo")
        botao_inativar.clicked.connect(self._inativar_servico)
        barra_acoes.addWidget(botao_inativar)

        barra_acoes.addStretch()
        layout.addLayout(barra_acoes)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(5)
        self._tabela.setHorizontalHeaderLabels(["Id", "Nome", "Valor/Hora", "Horas Estimadas", "Descrição"])
        self._tabela.setAlternatingRowColors(True)
        self._tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self._tabela)

    def _carregar_servicos(self) -> None:
        servicos = self._servico.listar_servicos_ativos()
        self._tabela.setRowCount(len(servicos))
        for linha, servico in enumerate(servicos):
            self._tabela.setItem(linha, 0, QTableWidgetItem(str(servico.id)))
            self._tabela.setItem(linha, 1, QTableWidgetItem(servico.nome))
            self._tabela.setItem(linha, 2, QTableWidgetItem(servico.valor_hora_formatado()))
            self._tabela.setItem(linha, 3, QTableWidgetItem(str(servico.horas_estimadas)))
            self._tabela.setItem(linha, 4, QTableWidgetItem(servico.descricao))

    def _servico_selecionado_id(self) -> int | None:
        linha_atual = self._tabela.currentRow()
        if linha_atual < 0:
            QMessageBox.warning(self, "Nenhuma seleção", "Selecione um serviço na tabela primeiro.")
            return None
        return int(self._tabela.item(linha_atual, 0).text())

    def _abrir_dialogo_novo_servico(self) -> None:
        dialogo = DialogoServico(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                dados = dialogo.obter_dados()
                servico = Servico(**dados)
                self._servico.criar_servico(servico)
                self._carregar_servicos()
            except (ValueError, InvalidOperation) as erro:
                QMessageBox.critical(self, "Erro ao cadastrar", str(erro))

    def _editar_valor_hora(self) -> None:
        servico_id = self._servico_selecionado_id()
        if servico_id is None:
            return

        servico = self._servico.buscar_por_id(servico_id)
        dialogo = DialogoEditarValorHora(servico, self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            try:
                servico.valor_hora = dialogo.novo_valor()
                self._servico.atualizar_servico(servico)
                self._carregar_servicos()
            except (ValueError, InvalidOperation) as erro:
                QMessageBox.critical(self, "Erro ao atualizar", str(erro))

    def _inativar_servico(self) -> None:
        servico_id = self._servico_selecionado_id()
        if servico_id is None:
            return

        resposta = QMessageBox.question(
            self, "Confirmar inativação",
            f"Deseja inativar o serviço id {servico_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta != QMessageBox.StandardButton.Yes:
            return

        try:
            self._servico.inativar_servico(servico_id)
            self._carregar_servicos()
        except ValueError as erro:
            QMessageBox.critical(self, "Erro", str(erro))


class DialogoServico(QDialog):
    """Formulário modal para cadastro de um novo serviço."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Novo Serviço")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        self._campo_nome = QLineEdit()
        self._campo_valor_hora = QLineEdit()
        self._campo_valor_hora.setPlaceholderText("Ex: 150.00")
        self._campo_horas = QLineEdit()
        self._campo_horas.setPlaceholderText("Ex: 10")
        self._campo_descricao = QLineEdit()

        layout.addRow("Nome:", self._campo_nome)
        layout.addRow("Valor por hora:", self._campo_valor_hora)
        layout.addRow("Horas estimadas:", self._campo_horas)
        layout.addRow("Descrição:", self._campo_descricao)

        botoes = QHBoxLayout()
        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.setObjectName("botaoSecundario")
        botao_cancelar.clicked.connect(self.reject)
        botao_salvar = QPushButton("Salvar")
        botao_salvar.clicked.connect(self.accept)
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(botao_salvar)
        layout.addRow(botoes)

    def obter_dados(self) -> dict:
        return {
            "nome": self._campo_nome.text().strip(),
            "valor_hora": Decimal(self._campo_valor_hora.text().strip()),
            "horas_estimadas": Decimal(self._campo_horas.text().strip()),
            "descricao": self._campo_descricao.text().strip(),
        }


class DialogoEditarValorHora(QDialog):
    """Formulário modal simples para atualizar o valor/hora de um serviço existente."""

    def __init__(self, servico: Servico, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Editar Valor/Hora — {servico.nome}")
        self.setMinimumWidth(320)

        layout = QFormLayout(self)
        layout.addRow("Valor/hora atual:", QLabel(servico.valor_hora_formatado()))
        self._campo_novo_valor = QLineEdit()
        self._campo_novo_valor.setPlaceholderText("Ex: 180.00")
        layout.addRow("Novo valor/hora:", self._campo_novo_valor)

        botoes = QHBoxLayout()
        botao_cancelar = QPushButton("Cancelar")
        botao_cancelar.setObjectName("botaoSecundario")
        botao_cancelar.clicked.connect(self.reject)
        botao_confirmar = QPushButton("Salvar")
        botao_confirmar.clicked.connect(self.accept)
        botoes.addWidget(botao_cancelar)
        botoes.addWidget(botao_confirmar)
        layout.addRow(botoes)

    def novo_valor(self) -> Decimal:
        return Decimal(self._campo_novo_valor.text().strip())