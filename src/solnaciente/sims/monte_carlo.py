"""Simulador Monte Carlo para la operación de la compañía Sol Naciente.

La clase `MonteCarloSimulator` simula `days` días de operación por corrida y
permite ejecutar múltiples corridas para obtener estadísticas agregadas.
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import math

import numpy as np

from solnaciente.models.investment import Investment
from solnaciente.sims import distributions


class MonteCarloSimulator:
    """Simulador Monte Carlo orientado a objetos.

    Parámetros principales:
        days: número de días a simular por corrida (por defecto 360).
        fixed_fee: ingreso fijo por inversión para la compañía (por inversión).
        company_share: fracción de la utilidad del proyecto que toma la compañía.
    """

    def __init__(self, days: int = 360, fixed_fee: float = 100.0, company_share: float = 0.10) -> None:
        if days <= 0:
            raise ValueError("days must be > 0")
        if not (0.0 <= company_share <= 1.0):
            raise ValueError("company_share must be between 0 and 1")

        self.days = days
        self.fixed_fee = float(fixed_fee)
        self.company_share = float(company_share)

    @staticmethod
    def _discount_cashflows(cashflows: Dict[int, float], discount_rate_annual: float) -> float:
        """Calcula el VAN (NPV) de un diccionario de flujos por día.

        `cashflows` mapea día -> monto. Se usa descuento diario: (1+r)^(t/365).
        """
        if discount_rate_annual <= -1.0:
            raise ValueError("discount_rate_annual must be > -1.0")
        npv = 0.0
        for day, cf in cashflows.items():
            npv += cf / ((1.0 + discount_rate_annual) ** (day / 365.0))
        return npv

    def run(
        self,
        n_runs: int = 1000,
        discount_rate_annual: float = 0.05,
        seed: Optional[int] = None,
    ) -> Dict[str, object]:
        """Ejecuta `n_runs` corridas Monte Carlo y devuelve estadísticas agregadas.

        Returns a dictionary with keys:
            - "npv_mean": VAN promedio
            - "npv_ci": (low, high) intervalo de confianza 95%
            - "success_prob": probabilidad de VAN>0
            - "total_gains_mean": ganancia promedio acumulada (fees + share)
            - "active_mean_final": promedio de inversiones activas al final del horizonte
            - "daily_history": dict con arrays promedio por día: new_investments, active_investments, company_cashflow
            - "all_npvs": array de NPVs por corrida
        """
        if n_runs <= 0:
            raise ValueError("n_runs must be > 0")

        master_rng = np.random.default_rng(seed)

        npvs: List[float] = []
        total_gains_list: List[float] = []
        active_final_list: List[int] = []

        # Acumuladores diarios (para promedios)
        daily_new_acc = np.zeros(self.days, dtype=float)
        daily_active_acc = np.zeros(self.days, dtype=float)
        daily_company_cash_acc = np.zeros(self.days, dtype=float)

        for run_idx in range(n_runs):
            run_seed = int(master_rng.integers(0, 2 ** 31))
            run_rng = np.random.default_rng(run_seed)

            # Registrar inversiones: lista de dicts con keys: investment, start, end
            investments: List[Dict] = []

            # company cashflows mapeado por día (puede superar self.days)
            company_cashflows: Dict[int, float] = defaultdict(float)

            # Historial diario de la corrida
            daily_new = np.zeros(self.days, dtype=int)
            daily_active = np.zeros(self.days, dtype=int)
            daily_company_cash = np.zeros(self.days, dtype=float)

            for day in range(self.days):
                # nuevas inversiones por Poisson
                lam_seed = int(run_rng.integers(0, 2 ** 31))
                new_count = int(distributions.daily_new_investments_poisson(size=1, lam=0.8, seed=lam_seed)[0])
                daily_new[day] = new_count

                # crear nuevas inversiones
                for _ in range(new_count):
                    # sample magnitude, duration, rate usando seeds derivados
                    amt_seed = int(run_rng.integers(0, 2 ** 31))
                    amount = float(distributions.magnitude_erlang(size=1, mean=1000.0, var=4000.0, seed=amt_seed)[0])

                    dur_seed = int(run_rng.integers(0, 2 ** 31))
                    duration = int(distributions.duration_geometric(size=1, mean=200.0, seed=dur_seed)[0])

                    rate_seed = int(run_rng.integers(0, 2 ** 31))
                    daily_rate = float(distributions.daily_rate_normal(size=1, mean=0.0008, std=0.0009, seed=rate_seed)[0])

                    inv = Investment(initial_amount=amount, duration_days=duration, daily_rate=daily_rate)
                    start = day
                    end = day + duration
                    investments.append({"investment": inv, "start": start, "end": end})

                    # company receives fixed fee at creation day
                    company_cashflows[start] += self.fixed_fee
                    if start < self.days:
                        daily_company_cash[start] += self.fixed_fee

                # calcular inversiones activas en este día (iniciadas y no finalizadas aún)
                active_count = 0
                for entry in investments:
                    if entry["start"] <= day < entry["end"]:
                        active_count += 1
                daily_active[day] = active_count

            # Al finalizar el horizonte, procesar pagos de utilidades y calcular ganancias totales
            total_company_gain = 0.0
            for entry in investments:
                inv: Investment = entry["investment"]
                start = entry["start"]
                end = entry["end"]
                # calcular utilidad del proyecto
                generated = inv.calculate_generated_profit()
                company_cut = generated * self.company_share
                # registrar en el día de finalización
                company_cashflows[end] += company_cut
                # si el día de finalización está dentro del horizonte, sumar a diario
                if 0 <= end < self.days:
                    daily_company_cash[end] += company_cut

                total_company_gain += company_cut + self.fixed_fee

            # calcular VAN de la corrida sobre company_cashflows
            run_npv = float(self._discount_cashflows(company_cashflows, discount_rate_annual))
            npvs.append(run_npv)
            total_gains_list.append(total_company_gain)
            active_final_list.append(int(daily_active[-1]))

            # acumular para promedios diarios (solo hasta self.days)
            daily_new_acc += daily_new
            daily_active_acc += daily_active
            daily_company_cash_acc += daily_company_cash

        # Agregar resultados agregados
        npvs_arr = np.array(npvs, dtype=float)
        mean_npv = float(npvs_arr.mean())
        std_npv = float(npvs_arr.std(ddof=1)) if n_runs > 1 else 0.0
        # intervalo de confianza 95% (aprox. normal)
        z = 1.959963984540054
        ci_low = mean_npv - z * (std_npv / math.sqrt(n_runs))
        ci_high = mean_npv + z * (std_npv / math.sqrt(n_runs))

        success_prob = float(np.sum(npvs_arr > 0) / n_runs)
        total_gains_mean = float(np.mean(total_gains_list))
        active_mean_final = float(np.mean(active_final_list))

        daily_history = {
            "avg_new_investments": (daily_new_acc / n_runs).tolist(),
            "avg_active_investments": (daily_active_acc / n_runs).tolist(),
            "avg_company_cashflow": (daily_company_cash_acc / n_runs).tolist(),
        }

        result = {
            "npv_mean": mean_npv,
            "npv_ci": (ci_low, ci_high),
            "success_prob": success_prob,
            "total_gains_mean": total_gains_mean,
            "active_mean_final": active_mean_final,
            "daily_history": daily_history,
            "all_npvs": npvs_arr,
        }

        return result
