ACCENT = "#22C6A8"
ACCENT_HOVER = "#31D7B8"
BACKGROUND = "#0F141A"
SURFACE = "#161D26"
BORDER = "#243040"
TEXT_PRIMARY = "#E6EDF3"
TEXT_SECONDARY = "#9AA7B2"
WARNING = "#F59E0B"
DANGER = "#EF4444"

APP_STYLESHEET = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}

QLabel {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 4px 8px;
}}

QLabel[muted='true'] {{
    color: {TEXT_SECONDARY};
}}

QMainWindow::separator {{
    width: 1px;
    height: 1px;
    background: {BORDER};
}}

QFrame[card='true'] {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

QFrame[card='true']:hover {{
    border: 1px solid {ACCENT};
}}

QFrame[cardSelected='true'] {{
    border: 1px solid {ACCENT};
}}

QToolButton {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 10px;
}}

QToolButton:hover {{
    border: 1px solid {ACCENT};
}}

QPushButton {{
    background-color: {ACCENT};
    border: none;
    color: #02110D;
    border-radius: 8px;
    padding: 8px 12px;
    font-weight: 600;
    min-height: 28px;
}}

QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}

QPushButton:disabled {{
    background-color: {BORDER};
    color: {TEXT_SECONDARY};
}}

QPushButton[variant='secondary'] {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    color: {TEXT_PRIMARY};
    min-height: 28px;
}}

QPushButton[variant='secondary']:hover {{
    border: 1px solid {ACCENT};
}}

QPushButton[variant='warning'] {{
    background-color: {WARNING};
    color: #02110D;
    min-height: 28px;
    font-weight: 600;
}}

QPushButton[variant='warning']:hover {{
    background-color: #FBBF24;
}}

QPushButton[danger='true'] {{
    background-color: {DANGER};
    color: #FFFFFF;
    min-height: 28px;
}}

QPushButton[danger='true']:hover {{
    background-color: #FF5A5A;
}}

QLineEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 7px 12px;
    min-height: 24px;
}}

QLineEdit:focus {{
    border: 1px solid {ACCENT};
}}

QComboBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 6px 12px;
    min-height: 24px;
}}

QComboBox:focus {{
    border: 1px solid {ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {TEXT_SECONDARY};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: {ACCENT};
    selection-color: #02110D;
    padding: 4px;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 10px;
    top: -1px;
}}

QTabBar::tab {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-bottom: none;
    padding: 8px 12px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 6px;
}}

QTabBar::tab:selected {{
    border: 1px solid {ACCENT};
}}

QDockWidget {{
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}}

QDockWidget::title {{
    text-align: left;
    padding: 6px;
    background: {SURFACE};
    border: 1px solid {BORDER};
}}

QTextEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 8px;
}}

QCheckBox {{
    spacing: 6px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {BORDER};
    background: {SURFACE};
}}

QCheckBox::indicator:checked {{
    border: 1px solid {ACCENT};
    background: {ACCENT};
}}

QTableWidget {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    gridline-color: {BORDER};
}}

QHeaderView::section {{
    background-color: {SURFACE};
    color: {TEXT_SECONDARY};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 8px 10px;
}}

QTableWidget::item {{
    padding: 6px 8px;
}}

QTableWidget::item:selected {{
    background: #123229;
    color: {TEXT_PRIMARY};
}}

QToolButton[seg='true'] {{
    border: 1px solid {BORDER};
    padding: 8px 10px;
    background: {SURFACE};
    border-radius: 0px;
}}

QToolButton[seg='true'][segPos='left'] {{
    border-top-left-radius: 8px;
    border-bottom-left-radius: 8px;
}}

QToolButton[seg='true'][segPos='right'] {{
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}}

QToolButton[seg='true']:checked {{
    background: {ACCENT};
    color: #02110D;
    border: 1px solid {ACCENT};
}}

QToolButton[seg='true']:hover {{
    border: 1px solid {ACCENT};
}}
"""
