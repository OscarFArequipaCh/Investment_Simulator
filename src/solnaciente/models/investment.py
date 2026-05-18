from dataclasses import dataclass, field
from typing import List, Optional
from itertools import accumulate


@dataclass
class Investment:
    """Representa una inversión individual.

    Atributos:
        initial_amount: Monto inicial invertido (positivo).
        duration_days: Duración de la inversión en días (entero > 0).
        daily_rates: Lista de tasas diarias en decimal (longitud = duration_days).
        generated_profit: Utilidad generada (se calcula con métodos).
        company_profit: Parte de la utilidad que corresponde a la compañía.
        cumulative_cashflow: Flujo de caja acumulado (se llena al generar cashflows).
    """

    initial_amount: float
    duration_days: int
    daily_rates: List[float]
    generated_profit: float = 0.0
    company_profit: float = 0.0
    cumulative_cashflow: List[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.duration_days <= 0:
            raise ValueError("duration_days must be > 0")
        if not isinstance(self.duration_days, int):
            raise TypeError("duration_days must be an integer")
        if self.initial_amount < 0:
            raise ValueError("initial_amount must be non-negative")
        if len(self.daily_rates) != self.duration_days:
            raise ValueError("daily_rates length must equal duration_days")

    def growth_series(self) -> List[float]:
        """Devuelve la serie de balance diario (incluye día 0).

        Retorna una lista de longitud `duration_days + 1` con el valor
        acumulado de la inversión en cada día.
        """
        series: List[float] = [self.initial_amount]
        for i in range(self.duration_days):
            series.append(series[-1] * (1.0 + self.daily_rates[i]))
        return series

    def final_amount(self) -> float:
        """Calcula el monto final después de capitalización diaria compuesta."""
        amount = self.initial_amount
        for r in self.daily_rates:
            amount *= (1.0 + r)
        return amount

    def calculate_generated_profit(self) -> float:
        """Calcula y almacena la utilidad generada (final - inicial)."""
        self.generated_profit = self.final_amount() - self.initial_amount
        return self.generated_profit

    def calculate_company_profit(self, company_share: float) -> float:
        """Calcula y almacena la porción de la utilidad que recibe la compañía.

        Args:
            company_share: fracción en [0, 1] de la utilidad generada.
        """
        if not (0.0 <= company_share <= 1.0):
            raise ValueError("company_share must be between 0 and 1")
        if self.generated_profit == 0.0:
            self.calculate_generated_profit()
        self.company_profit = self.generated_profit * company_share
        return self.company_profit

    def generate_daily_cashflow(self, include_initial: bool = True) -> List[float]:
        """Genera el flujo de caja diario como lista de floats.

        Formato de salida cuando `include_initial=True`:
            t=0: -initial_amount (salida)
            t=1..duration-1: interés diario
            t=duration: interés diario + retorno del principal

        Almacena también `cumulative_cashflow` como acumulado de los flujos.
        """
        balances = self.growth_series()
        # intereses diarios: diferencia entre cada día
        daily_interest: List[float] = [balances[i + 1] - balances[i] for i in range(len(balances) - 1)]

        cashflows: List[float] = []
        if include_initial:
            cashflows.append(-self.initial_amount)

        for i in range(self.duration_days):
            amt = daily_interest[i]
            # En el último día devolvemos también el principal
            if i == self.duration_days - 1 and include_initial:
                amt += self.initial_amount
            cashflows.append(amt)

        # Guardar flujo acumulado
        self.cumulative_cashflow = list(accumulate(cashflows))
        return cashflows

    def npv(self, discount_rate_annual: float) -> float:
        """Calcula el VAN (NPV) de la inversión usando `discount_rate_annual`.

        Se asume `discount_rate_annual` como tasa anual en decimal (p.ej. 0.05 = 5%).
        Los flujos son diarios y se descuentan usando potencias fraccionarias: (1+r)^(t/365).
        """
        if discount_rate_annual <= -1.0:
            raise ValueError("discount_rate_annual must be > -1.0")

        cashflows = self.generate_daily_cashflow(include_initial=True)
        npv_value = 0.0
        for t, cf in enumerate(cashflows):
            # t está en días; convertir a años como t/365
            npv_value += cf / ((1.0 + discount_rate_annual) ** (t / 365.0))
        return npv_value
