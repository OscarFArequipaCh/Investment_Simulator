from PySide6 import QtWidgets
from typing import Optional

from solnaciente.plots.charts import ChartWidget


class ChartsView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()

        # Usar ChartWidget para cada pestaña
        self.hist_widget = ChartWidget(figsize=(6, 4))
        tab1 = QtWidgets.QWidget()
        t1_layout = QtWidgets.QVBoxLayout(tab1)
        t1_layout.addWidget(self.hist_widget)
        self.tabs.addTab(tab1, "Histograma VAN")

        self.cashflow_widget = ChartWidget(figsize=(6, 4))
        tab2 = QtWidgets.QWidget()
        t2_layout = QtWidgets.QVBoxLayout(tab2)
        t2_layout.addWidget(self.cashflow_widget)
        self.tabs.addTab(tab2, "Flujos y series")

        layout.addWidget(self.tabs)

    def update_charts(self, result: dict) -> None:
        # Histograma de NPVs
        all_npvs = result.get('all_npvs')
        if all_npvs is not None:
            self.hist_widget.update_histogram(all_npvs)

        # Series diarias: promedio new investments
        daily = result.get('daily_history', {}).get('avg_new_investments')
        if daily is not None:
            # Representar la serie promedio como 'daily gains' plot
            # ChartWidget espera una matriz; pasar una sola serie como 1xN
            self.cashflow_widget.update_daily_gains([daily])
