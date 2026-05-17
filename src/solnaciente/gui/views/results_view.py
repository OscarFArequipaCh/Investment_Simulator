from PySide6 import QtWidgets


class ResultsView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self.summary = QtWidgets.QTextEdit()
        self.summary.setReadOnly(True)
        layout.addWidget(self.summary)

    def update_results(self, result: dict) -> None:
        lines = []
        lines.append(f"VAN promedio: {result.get('npv_mean'):.2f}")
        ci = result.get('npv_ci', (None, None))
        lines.append(f"IC95 VAN: {ci[0]:.2f} — {ci[1]:.2f}")
        lines.append(f"Probabilidad de éxito (VAN>0): {result.get('success_prob'):.2%}")
        lines.append(f"Ganancias promedio: {result.get('total_gains_mean'):.2f}")
        self.summary.setPlainText('\n'.join(lines))
