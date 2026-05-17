"""Integración de Matplotlib con PySide6 para las gráficas del simulador.

Provee widgets reutilizables basados en FigureCanvasQTAgg que pueden actualizarse
dinámicamente desde la lógica de la aplicación.
"""
from __future__ import annotations

from typing import Iterable, List, Sequence, Optional

import numpy as np
from PySide6 import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartWidget(QtWidgets.QWidget):
    """Widget genérico que contiene un `FigureCanvas` y un único eje.

    Métodos de actualización (idempotentes):
      - update_histogram(npvs)
      - update_cashflows(cashflows)
      - update_daily_gains(daily_matrix)
      - update_investment_distribution(amounts)
      - update_cumulative_benefits(cumulatives)
    """

    def __init__(self, figsize: tuple = (6, 4), parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.fig = Figure(figsize=figsize, tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def update_histogram(self, npvs: Sequence[float], bins: int = 30, color: str = "#4b6eaf") -> None:
        """Dibuja el histograma del VAN (npvs).

        `npvs` debe ser un iterable de valores reales.
        """
        arr = np.asarray(list(npvs), dtype=float)
        if arr.size == 0:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No data", ha="center")
            self.canvas.draw_idle()
            return

        self.ax.clear()
        self.ax.hist(arr, bins=bins, color=color, edgecolor="#222222", alpha=0.9)
        self.ax.set_title("Histograma de VAN")
        self.ax.set_xlabel("VAN")
        self.ax.set_ylabel("Frecuencia")
        self.canvas.draw_idle()

    def update_cashflows(self, cashflows: Sequence[Sequence[float]], labels: Optional[Sequence[str]] = None) -> None:
        """Grafica flujos de caja simulados.

        `cashflows` puede ser una lista/array de vectores (cada vector = flujos por día).
        Dibuja la media y bandas percentiles.
        """
        arr = np.array([np.asarray(c, dtype=float) for c in cashflows])
        if arr.size == 0:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No data", ha="center")
            self.canvas.draw_idle()
            return

        # Normalizar longitud (truncar al mínimo)
        minlen = min(a.size for a in arr)
        arr = arr[:, :minlen]
        mean = np.mean(arr, axis=0)
        p10 = np.percentile(arr, 10, axis=0)
        p90 = np.percentile(arr, 90, axis=0)

        x = np.arange(minlen)
        self.ax.clear()
        self.ax.plot(x, mean, color="#e6e6e6", label="Media")
        self.ax.fill_between(x, p10, p90, color="#4b6eaf", alpha=0.2, label="P10-P90")
        self.ax.set_title("Flujos de caja simulados (media y banda 10-90%)")
        self.ax.set_xlabel("Día")
        self.ax.set_ylabel("Flujo")
        self.ax.legend()
        self.canvas.draw_idle()

    def update_daily_gains(self, daily_matrix: Sequence[Sequence[float]]) -> None:
        """Dibuja la evolución diaria de ganancias agregadas.

        `daily_matrix` forma (n_runs, days) o (n_entries, days).
        Se grafica la media y la mediana.
        """
        arr = np.array(daily_matrix, dtype=float)
        if arr.size == 0:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No data", ha="center")
            self.canvas.draw_idle()
            return

        minlen = arr.shape[1]
        mean = np.mean(arr, axis=0)
        med = np.median(arr, axis=0)
        x = np.arange(minlen)

        self.ax.clear()
        self.ax.plot(x, mean, label="Media diaria", color="#e6e6e6")
        self.ax.plot(x, med, label="Mediana", color="#4b6eaf", linestyle="--")
        self.ax.set_title("Evolución diaria de ganancias")
        self.ax.set_xlabel("Día")
        self.ax.set_ylabel("Ganancias")
        self.ax.legend()
        self.canvas.draw_idle()

    def update_investment_distribution(self, amounts: Sequence[float], bins: int = 30) -> None:
        """Histograma / distribución de magnitudes de inversión."""
        arr = np.asarray(list(amounts), dtype=float)
        if arr.size == 0:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No data", ha="center")
            self.canvas.draw_idle()
            return
        self.ax.clear()
        self.ax.hist(arr, bins=bins, color="#7fb070", edgecolor="#222222")
        self.ax.set_title("Distribución de inversiones")
        self.ax.set_xlabel("Monto")
        self.ax.set_ylabel("Frecuencia")
        self.canvas.draw_idle()

    def update_cumulative_benefits(self, cumulatives: Sequence[Sequence[float]]) -> None:
        """Dibuja la curva acumulativa de beneficios (media y percentiles).

        `cumulatives` puede ser una colección de series acumuladas por corrida.
        """
        arr = np.array([np.asarray(c, dtype=float) for c in cumulatives])
        if arr.size == 0:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "No data", ha="center")
            self.canvas.draw_idle()
            return

        minlen = min(a.size for a in arr)
        arr = arr[:, :minlen]
        mean = np.mean(arr, axis=0)
        p5 = np.percentile(arr, 5, axis=0)
        p95 = np.percentile(arr, 95, axis=0)

        x = np.arange(minlen)
        self.ax.clear()
        self.ax.plot(x, mean, color="#e6e6e6", label="Media acumulada")
        self.ax.fill_between(x, p5, p95, color="#ffb86b", alpha=0.25, label="P5-P95")
        self.ax.set_title("Curva acumulativa de beneficios")
        self.ax.set_xlabel("Día")
        self.ax.set_ylabel("Beneficio acumulado")
        self.ax.legend()
        self.canvas.draw_idle()


__all__ = ["ChartWidget"]
