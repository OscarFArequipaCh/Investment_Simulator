"""Funciones para generar variables aleatorias usadas en la simulación.

Incluye:
- Número diario de nuevas inversiones (Poisson, λ=0.80)
- Magnitud de inversiones (Erlang / Gamma con parámetros calculados)
- Duración en días (Geométrica, media=200)
- Tasa diaria (Normal, media=0.08%, desviación=0.09%)

Todas las funciones aceptan una semilla opcional para reproducibilidad
y realizan validaciones básicas para retornar valores realistas.
"""
from __future__ import annotations

from typing import Optional, Tuple, Union

import numpy as np


def _get_rng(seed: Optional[int]) -> np.random.Generator:
    return np.random.default_rng(seed)


def daily_new_investments_poisson(
    size: int = 1, *, lam: float = 0.8, seed: Optional[int] = None
) -> np.ndarray:
    """Muestra el número diario de nuevas inversiones usando Poisson.

    Args:
        size: cantidad de muestras a generar (enteros positivos).
        lam: media λ de la distribución Poisson (por defecto 0.8).
        seed: semilla opcional para reproducibilidad.

    Returns:
        Array de enteros >= 0 de longitud `size`.

    Raises:
        ValueError: si `size` <= 0 o `lam` < 0.
    """
    if size <= 0:
        raise ValueError("size must be a positive integer")
    if lam < 0:
        raise ValueError("lam must be non-negative")

    rng = _get_rng(seed)
    samples = rng.poisson(lam=lam, size=size)
    # Validación: asegurar enteros no negativos y tipo int
    samples = np.asarray(samples, dtype=int)
    samples[samples < 0] = 0
    return samples


def magnitude_erlang(
    size: int = 1, *, mean: float = 1000.0, var: float = 4000.0, seed: Optional[int] = None
) -> np.ndarray:
    """Muestra magnitudes de inversión usando distribución Erlang (Gamma con k entero).

    Calcula parámetros k y theta a partir de la media y varianza:
        k = mean^2 / var
        theta = mean / k

    Args:
        size: número de muestras a generar.
        mean: media objetivo (por defecto 1000).
        var: varianza objetivo (por defecto 4000).
        seed: semilla opcional.

    Returns:
        Array de floats positivos.

    Raises:
        ValueError: si mean <= 0 o var <= 0.
    """
    if size <= 0:
        raise ValueError("size must be a positive integer")
    if mean <= 0 or var <= 0:
        raise ValueError("mean and var must be positive")

    # Estimación de parámetros Erlang (k entero)
    k_float = (mean ** 2) / var
    k = max(1, int(round(k_float)))
    theta = mean / k

    rng = _get_rng(seed)
    samples = rng.gamma(shape=k, scale=theta, size=size)
    samples = np.asarray(samples, dtype=float)

    # Validación / saneamiento: evitar ceros y valores extremadamente grandes
    std = np.sqrt(var)
    upper = mean + 10.0 * std
    samples = np.clip(samples, a_min=1e-6, a_max=upper)
    return samples


def duration_geometric(
    size: int = 1, *, mean: float = 200.0, seed: Optional[int] = None
) -> np.ndarray:
    """Muestra duraciones en días usando distribución geométrica.

    Se usa la parametrización: mean = 1 / p  => p = 1 / mean

    Args:
        size: número de muestras a generar.
        mean: media deseada en días (por defecto 200).
        seed: semilla opcional.

    Returns:
        Array de enteros >=1 representando días.

    Raises:
        ValueError: si mean <= 1.
    """
    if size <= 0:
        raise ValueError("size must be a positive integer")
    if mean <= 1.0:
        raise ValueError("mean must be > 1")

    p = 1.0 / mean
    rng = _get_rng(seed)
    samples = rng.geometric(p=p, size=size)
    samples = np.asarray(samples, dtype=int)

    # Capar valores extremos para mantener realismo (p.ej. no más de 10*mean)
    max_days = int(max(3650, mean * 10))
    samples = np.clip(samples, a_min=1, a_max=max_days)
    return samples


def daily_rate_normal(
    size: int = 1,
    *,
    mean: float = 0.0008,
    std: float = 0.0009,
    seed: Optional[int] = None,
    clip: Tuple[float, float] = (-0.2, 0.2),
) -> np.ndarray:
    """Muestra tasas diarias usando una distribución normal.

    Args:
        size: número de muestras a generar.
        mean: media diaria en decimal (por defecto 0.0008 = 0.08%).
        std: desviación estándar diaria (por defecto 0.0009 = 0.09%).
        seed: semilla opcional.
        clip: (min, max) para recortar resultados y mantener realismo.

    Returns:
        Array de floats con tasas diarias.

    Raises:
        ValueError: si std < 0 o clip mal formado.
    """
    if size <= 0:
        raise ValueError("size must be a positive integer")
    if std < 0:
        raise ValueError("std must be non-negative")
    if clip[0] >= clip[1]:
        raise ValueError("clip must be (min, max) with min < max")

    rng = _get_rng(seed)
    samples = rng.normal(loc=mean, scale=std, size=size)
    samples = np.asarray(samples, dtype=float)

    # Recortar a rango realista (p.ej. evitar tasas diarias absurdas)
    samples = np.clip(samples, a_min=clip[0], a_max=clip[1])
    return samples


__all__ = [
    "daily_new_investments_poisson",
    "magnitude_erlang",
    "duration_geometric",
    "daily_rate_normal",
]
