from PySide6 import QtWidgets, QtCore
from solnaciente.gui.sidebar import Sidebar
from solnaciente.gui.views.results_view import ResultsView
from solnaciente.gui.views.charts_view import ChartsView
from solnaciente.gui.workers import SimulationWorker
from solnaciente.analysis import statistics


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sol Naciente - Simulador de Inversión")
        self.resize(1200, 800)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)

        splitter = QtWidgets.QSplitter()
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)
        layout.addWidget(splitter)

        # Barra lateral izquierda
        self.sidebar = Sidebar()
        splitter.addWidget(self.sidebar)
        self.sidebar.setMinimumWidth(320)

        # Panel central con pestañas
        self.tabs = QtWidgets.QTabWidget()
        self.results_view = ResultsView()
        self.charts_view = ChartsView()
        self.tabs.addTab(self.results_view, "Resultados")
        self.tabs.addTab(self.charts_view, "Gráficas")
        splitter.addWidget(self.tabs)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        # Conexiones
        self.sidebar.start_requested.connect(self._on_start_requested)

    def _on_start_requested(self, params: dict) -> None:
        # Deshabilitar inputs mientras corre
        self.sidebar.setEnabled(False)

        # Crear hilo y worker (QThread + QObject pattern)
        self.thread = QtCore.QThread()
        self.worker = SimulationWorker(params)
        self.worker.moveToThread(self.thread)

        # Conectar señales
        self.thread.started.connect(self.worker.run)
        self.worker.signals.progress.connect(self.sidebar.progress_bar.setValue)
        self.worker.signals.log.connect(self.sidebar.append_log)
        self.worker.signals.finished.connect(self._on_simulation_finished)
        self.worker.signals.finished.connect(self.thread.quit)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Iniciar hilo
        self.thread.start()

    def _on_simulation_finished(self, result: dict) -> None:
        # Rehabilitar UI
        self.sidebar.setEnabled(True)

        if result.get("error"):
            self.sidebar.append_log(f"Simulación terminó con error: {result['error']}")
            return

        # Calcular métricas adicionales usando módulo statistics
        npvs = result.get('all_npvs', [])
        try:
            npv_mean = statistics.mean(npvs)
            npv_ci = statistics.ci95(npvs)
            success_prob = statistics.prob_positive(npvs)
        except Exception:
            npv_mean = result.get('npv_mean')
            npv_ci = result.get('npv_ci')
            success_prob = result.get('success_prob')

        # Enriquecer result para vistas
        result.update({
            'npv_mean': npv_mean,
            'npv_ci': npv_ci,
            'success_prob': success_prob,
        })

        # Actualizar vistas con resultados
        self.results_view.update_results(result)
        self.charts_view.update_charts(result)

        # Mostrar resumen automático en logs
        summary = f"VAN medio: {npv_mean:.2f} | IC95: {npv_ci[0]:.2f}-{npv_ci[1]:.2f} | P(VAN>0)={success_prob:.2%}"
        self.sidebar.append_log(summary)
