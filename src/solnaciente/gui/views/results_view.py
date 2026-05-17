from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from solnaciente.analysis.analyzer import generate_financial_report
from solnaciente.gui.widgets.kpi_card import KpiCard
from solnaciente.reports.exporter import export_report_to_pdf, export_to_excel


class ResultsView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.report_text = ""
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(16)

        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("<h2>Panel de análisis</h2>")
        title.setTextFormat(QtCore.Qt.TextFormat.RichText)
        header.addWidget(title)
        header.addStretch()
        self.btn_export_pdf = QtWidgets.QPushButton("Exportar PDF")
        self.btn_export_pdf.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_export_pdf.clicked.connect(self._on_export_pdf)
        header.addWidget(self.btn_export_pdf)
        self.btn_export_excel = QtWidgets.QPushButton("Exportar Excel")
        self.btn_export_excel.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.btn_export_excel.clicked.connect(self._on_export_excel)
        header.addWidget(self.btn_export_excel)
        layout.addLayout(header)

        cards = QtWidgets.QHBoxLayout()
        cards.setSpacing(12)
        self.kpi_van = KpiCard("VAN Promedio")
        self.kpi_success = KpiCard("Probabilidad de éxito")
        self.kpi_risk = KpiCard("Nivel de riesgo")
        self.kpi_volatility = KpiCard("Volatilidad")
        cards.addWidget(self.kpi_van)
        cards.addWidget(self.kpi_success)
        cards.addWidget(self.kpi_risk)
        cards.addWidget(self.kpi_volatility)
        layout.addLayout(cards)

        self.table = QtWidgets.QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Métrica", "Valor"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        layout.addWidget(self.table)

        self.summary = QtWidgets.QTextEdit()
        self.summary.setReadOnly(True)
        self.summary.setMinimumHeight(220)
        layout.addWidget(self.summary)

    def update_results(self, result: dict) -> None:
        report = generate_financial_report(result)
        self.report_text = report['report_text']

        van = float(result.get('npv_mean', 0.0) or 0.0)
        prob = float(result.get('success_prob', 0.0) or 0.0)
        risk = report.get('risk_level', 'Indeterminado')
        volatility = float(result.get('volatility', 0.0) or 0.0)

        self.kpi_van.set_value(f"${van:,.2f}", subtext="Rentabilidad promedio", positive=van >= 0)
        self.kpi_success.set_value(f"{prob:.2%}", subtext="Probabilidad de éxito", positive=prob >= 0.6)
        self.kpi_risk.set_value(risk, subtext="Indicador de riesgo", positive=(risk in ['Bajo', 'Moderado']))
        self.kpi_volatility.set_value(f"{volatility:.2f}", subtext="Desviación estándar", positive=volatility <= 0.2)

        self.table.setRowCount(0)
        rows = [
            ("VAN promedio", f"${van:,.2f}"),
            ("Intervalo IC95", f"${result.get('npv_ci', (0,0))[0]:,.2f} – ${result.get('npv_ci', (0,0))[1]:,.2f}"),
            ("Probabilidad de éxito", f"{prob:.2%}"),
            ("VaR 5%", f"${result.get('var_5', 0.0):,.2f}"),
            ("Volatilidad", f"{volatility:.2f}"),
            ("Ganancias promedio", f"${result.get('total_gains_mean', 0.0):,.2f}"),
        ]
        for label, value in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(label))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(value))

        self.summary.setPlainText(report['report_text'])

    def _on_export_pdf(self) -> None:
        path = Path.cwd() / "solnaciente_report.pdf"
        export_report_to_pdf(self.report_text, str(path))

    def _on_export_excel(self) -> None:
        result = {
            'npv_mean': float(self.kpi_van.value_label.text().replace('$','').replace(',','') or 0.0),
            'success_prob': float(self.kpi_success.value_label.text().replace('%','') or 0.0) / 100.0,
            'total_gains_mean': float(self.table.item(5, 1).text().replace('$','').replace(',','') or 0.0),
            'npv_ci': (float(self.table.item(1, 1).text().split('–')[0].replace('$','').replace(',','') or 0.0), float(self.table.item(1, 1).text().split('–')[1].replace('$','').replace(',','') or 0.0)),
        }
        export_to_excel(result, str(Path.cwd() / "solnaciente_report.xlsx"))
