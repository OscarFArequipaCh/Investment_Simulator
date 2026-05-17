import sys
from pathlib import Path

# Al ejecutar `python src\solnaciente\gui\app.py`, añadimos `src` al path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from PySide6 import QtWidgets
from PySide6.QtGui import QPalette, QColor
from solnaciente.gui.main_window import MainWindow


def run_app(argv=None):
    app = QtWidgets.QApplication(argv or [])

    # Tema oscuro básico
    dark_palette = app.palette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    # Use stylesheet para un tema oscuro más consistente
    app.setStyleSheet("""
    QWidget { background-color: #2b2b2b; color: #e6e6e6; }
    QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit { background-color: #3c3f41; }
    QPushButton { background-color: #4b6eaf; color: white; padding: 6px; border-radius: 4px; }
    QPushButton:disabled { background-color: #555555; }
    QProgressBar { background-color: #3c3f41; color: #e6e6e6; }
    QTabWidget::pane { border-top: 2px solid #4b6eaf; }
    """)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    import sys

    sys.exit(run_app(sys.argv))
