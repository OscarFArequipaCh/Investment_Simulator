"""Funciones estadísticas financieras usando NumPy y SciPy.

Incluye: promedio, desviación, percentiles, IC95, probabilidad de VAN positivo,
VaR (histórico y paramétrico) y análisis de sensibilidad sencillo.
"""
from __future__ import annotations

from typing import Iterable, List, Tuple, Dict

import numpy as np
from scipy import stats


def mean(data: Iterable[float]) -> float:
    """Devuelve la media de `data`.

    Lanza ValueError si `data` está vacío.
    """
    arr = np.asarray(list(data), dtype=float)
    if arr.size == 0:
        raise ValueError("data must not be empty")
    return float(np.mean(arr))


def std(data: Iterable[float], ddof: int = 1) -> float:
    """Desviación estándar muestral (por defecto `ddof=1`)."""
    arr = np.asarray(list(data), dtype=float)
    if arr.size == 0:
        raise ValueError("data must not be empty")
    if arr.size == 1:
        return 0.0
    return float(np.std(arr, ddof=ddof))


def percentiles(data: Iterable[float], qs: Iterable[float]) -> List[float]:
    """Calcula percentiles para `qs`.

    `qs` puede estar en [0,1] o [0,100]. Se normaliza internamente.
    """
    arr = np.asarray(list(data), dtype=float)
    if arr.size == 0:
        raise ValueError("data must not be empty")
    qs_arr = np.asarray(list(qs), dtype=float)
    if np.any((qs_arr < 0) & (qs_arr > 1)) and np.any((qs_arr < 0) & (qs_arr > 100)):
        pass
    # Normalizar a 0-100
    if np.all(qs_arr <= 1.0):
        qs_pct = qs_arr * 100.0
    else:
        qs_pct = qs_arr
    return list(np.percentile(arr, qs_pct))


def ci95(data: Iterable[float]) -> Tuple[float, float]:
    """Intervalo de confianza del 95% para la media usando t-student.

    Retorna (low, high).
    """
    arr = np.asarray(list(data), dtype=float)
    n = arr.size
    if n == 0:
        raise ValueError("data must not be empty")
    m = float(np.mean(arr))
    if n == 1:
        return (m, m)
    se = float(stats.sem(arr, ddof=1))
    t_val = float(stats.t.ppf(0.975, df=n - 1))
    delta = t_val * se
    return (m - delta, m + delta)


def prob_positive(data: Iterable[float]) -> float:
    """Probabilidad estimada de que los valores en `data` sean > 0.

    Retorna un float en [0,1].
    """
    arr = np.asarray(list(data), dtype=float)
    if arr.size == 0:
        return 0.0
    return float(np.mean(arr > 0))


def var(
    data: Iterable[float], *, alpha: float = 0.05, method: str = "historical"
) -> float:
    """Calcula Value at Risk (VaR) al nivel `alpha`.

    - `historical`: devuelve el percentil `alpha` (cola izquierda).
    - `parametric`: asume normalidad y calcula `mean + z_alpha * std`.

    Nota: el resultado puede ser negativo si representa pérdidas.
    """
    arr = np.asarray(list(data), dtype=float)
    if arr.size == 0:
        raise ValueError("data must not be empty")
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0,1)")
    method = method.lower()
    if method == "historical":
        return float(np.percentile(arr, 100.0 * alpha))
    elif method == "parametric":
        mu = float(np.mean(arr))
        sigma = float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0
        z = float(stats.norm.ppf(alpha))
        return mu + z * sigma
    else:
        raise ValueError("method must be 'historical' or 'parametric'")


def sensitivity_analysis(x: Iterable[float], y: Iterable[float]) -> Dict[str, float]:
    """Análisis de sensibilidad simple entre variable `x` (entrada) y `y` (salida).

    Calcula:
      - correlación de Pearson y su p-valor
      - correlación de Spearman y su p-valor
      - regresión lineal (slope, intercept)
      - coeficiente estándar (beta estandarizado)

    Retorna un dict con las métricas.
    """
    x_arr = np.asarray(list(x), dtype=float)
    y_arr = np.asarray(list(y), dtype=float)
    if x_arr.size == 0 or y_arr.size == 0:
        raise ValueError("x and y must not be empty")
    if x_arr.size != y_arr.size:
        raise ValueError("x and y must have the same length")

    pearson_r, pearson_p = stats.pearsonr(x_arr, y_arr) if x_arr.size > 1 else (0.0, 1.0)
    spearman_r, spearman_p = stats.spearmanr(x_arr, y_arr) if x_arr.size > 1 else (0.0, 1.0)
    lr = stats.linregress(x_arr, y_arr) if x_arr.size > 1 else stats.linregress(np.array([0.0, 1.0]), np.array([0.0, 0.0]))

    std_x = float(np.std(x_arr, ddof=1)) if x_arr.size > 1 else 0.0
    std_y = float(np.std(y_arr, ddof=1)) if y_arr.size > 1 else 0.0
    if std_y == 0.0:
        beta_std = 0.0
    else:
        beta_std = float(lr.slope * (std_x / std_y)) if std_y else 0.0

    return {
        "pearson_r": float(pearson_r),
        "pearson_p": float(pearson_p),
        "spearman_r": float(spearman_r),
        "spearman_p": float(spearman_p),
        "slope": float(lr.slope),
        "intercept": float(lr.intercept),
        "beta_std": float(beta_std),
    }


__all__ = [
    "mean",
    "std",
    "percentiles",
    "ci95",
    "prob_positive",
    "var",
    "sensitivity_analysis",
]
