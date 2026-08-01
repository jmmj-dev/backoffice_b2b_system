"""Define o tema visual claro da aplicação, usado em toda a GUI (QSS = CSS do Qt)."""

COR_PRIMARIA = "#2563EB"       # azul principal (botões, destaques)
COR_PRIMARIA_HOVER = "#1D4ED8"
COR_FUNDO = "#F8FAFC"          # fundo geral, quase branco
COR_FUNDO_SIDEBAR = "#1E293B"  # barra lateral em tom escuro contrastante
COR_TEXTO_SIDEBAR = "#E2E8F0"
COR_TEXTO = "#0F172A"
COR_BORDA = "#CBD5E1"
COR_ZEBRA = "#EEF2FF"
COR_ERRO = "#DC2626"
COR_SUCESSO = "#16A34A"

FOLHA_DE_ESTILO = f"""
QWidget {{
    background-color: {COR_FUNDO};
    color: {COR_TEXTO};
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 13px;
}}

QPushButton {{
    background-color: {COR_PRIMARIA};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {COR_PRIMARIA_HOVER};
}}
QPushButton:disabled {{
    background-color: {COR_BORDA};
    color: #94A3B8;
}}
QPushButton#botaoSecundario {{
    background-color: white;
    color: {COR_PRIMARIA};
    border: 1px solid {COR_PRIMARIA};
}}
QPushButton#botaoSecundario:hover {{
    background-color: {COR_ZEBRA};
}}
QPushButton#botaoPerigo {{
    background-color: white;
    color: {COR_ERRO};
    border: 1px solid {COR_ERRO};
}}
QPushButton#botaoPerigo:hover {{
    background-color: #FEF2F2;
}}

QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {{
    background-color: white;
    border: 1px solid {COR_BORDA};
    border-radius: 6px;
    padding: 6px 8px;
}}
QLineEdit:focus, QComboBox:focus {{
    border: 1px solid {COR_PRIMARIA};
}}

QTableWidget {{
    background-color: white;
    alternate-background-color: {COR_ZEBRA};
    gridline-color: {COR_BORDA};
    border: 1px solid {COR_BORDA};
    border-radius: 6px;
}}
QHeaderView::section {{
    background-color: {COR_FUNDO_SIDEBAR};
    color: white;
    padding: 8px;
    border: none;
    font-weight: 600;
}}

QFrame#sidebar {{
    background-color: {COR_FUNDO_SIDEBAR};
}}
QPushButton#botaoSidebar {{
    background-color: transparent;
    color: {COR_TEXTO_SIDEBAR};
    text-align: left;
    padding: 12px 16px;
    border-radius: 0px;
    font-weight: 500;
}}
QPushButton#botaoSidebar:hover {{
    background-color: #334155;
}}
QPushButton#botaoSidebar:checked {{
    background-color: {COR_PRIMARIA};
    color: white;
}}

QLabel#titulo {{
    font-size: 20px;
    font-weight: 700;
    padding-bottom: 8px;
}}
QLabel#erro {{
    color: {COR_ERRO};
    font-weight: 600;
}}
"""