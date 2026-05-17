from __future__ import annotations

from PySide6 import QtCore
from typing import Any, Dict

from solnaciente.sims.monte_carlo import MonteCarloSimulator


class WorkerSignals(QtCore.QObject):
    progress = QtCore.Signal(int)
    log = QtCore.Signal(str)
    finished = QtCore.Signal(dict)


class SimulationWorker(QtCore.QObject):
    """Worker que corre la simulación en un `QThread`.

    Uso:
        thread = QThread()
        worker = SimulationWorker(params)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.signals.finished.connect(thread.quit)
    """

    def __init__(self, params: Dict[str, Any]):
        super().__init__()
        self.params = params
        self.signals = WorkerSignals()

    @QtCore.Slot()
    def run(self) -> None:
        """Slot que ejecuta la simulación; emite señales de progreso y log."""
        try:
            self.signals.log.emit("Inicio de simulación...")
            days = int(self.params.get('days', 360))
            n_runs = int(self.params.get('n_runs', 1000))
            discount = float(self.params.get('discount_rate', 0.05))

            sim = MonteCarloSimulator(days=days)

            # Ejecutar corrida (síncrono dentro del hilo)
            result = sim.run(n_runs=n_runs, discount_rate_annual=discount)

            self.signals.progress.emit(100)
            self.signals.log.emit("Simulación finalizada")
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.log.emit(f"Error en simulación: {e}")
            self.signals.finished.emit({"error": str(e)})
