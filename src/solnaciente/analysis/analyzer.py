"""Generador de reportes financieros automatizados.

Produce un texto profesional en español evaluando viabilidad, riesgo, recomendaciones
y conclusiones financieras a partir de resultados de Monte Carlo.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple
import math

from . import statistics


def _fmt_currency(x: float) -> str:
    return f"${x:,.2f}"


def _risk_level_from_metrics(var_value: float, volatility: float, success_prob: float) -> str:
    """Determina un nivel de riesgo cualitativo según reglas simples."""
    # reglas heurísticas
    if success_prob >= 0.75 and var_value >= 0:
        return "Bajo"
    if volatility < 0.1 and success_prob >= 0.6:
        return "Moderado"
    if volatility < 0.2 and success_prob >= 0.4:
        return "Alto"
    return "Muy alto"


def generate_financial_report(result: Dict) -> Dict[str, str]:
    """Genera un reporte textual profesional en español.

    `result` se espera que contenga al menos:
      - 'all_npvs': iterable de VANs por corrida
      - 'npv_mean' (opcional)
      - 'npv_ci' (opcional) tuple (low, high)
      - 'success_prob' (opcional)
      - 'daily_history' (opcional) con flujos

    Retorna un dict con claves: 'viability', 'risk_level', 'recommendations',
    'conclusions' y 'report_text'.
    """
    npvs = list(result.get('all_npvs', []))
    npv_mean = result.get('npv_mean')
    npv_ci = result.get('npv_ci')
    success_prob = result.get('success_prob')

    if not npvs:
        # No hay datos; retornar reporte vacío con nota
        report_text = (
            "No hay datos suficientes para generar un análisis financiero. "
            "Ejecute al menos una corrida de Monte Carlo para obtener métricas." 
        )
        return {
            'viability': 'Indeterminado',
            'risk_level': 'Indeterminado',
            'recommendations': 'No hay recomendaciones (sin datos)',
            'conclusions': report_text,
            'report_text': report_text,
        }

    # Métricas calculadas
    try:
        npv_mean = float(npv_mean) if npv_mean is not None else statistics.mean(npvs)
    except Exception:
        npv_mean = statistics.mean(npvs)

    try:
        npv_ci = tuple(npv_ci) if npv_ci is not None else statistics.ci95(npvs)
    except Exception:
        npv_ci = statistics.ci95(npvs)

    try:
        success_prob = float(success_prob) if success_prob is not None else statistics.prob_positive(npvs)
    except Exception:
        success_prob = statistics.prob_positive(npvs)

    volatility = statistics.std(npvs, ddof=1)
    # Riesgo: VaR 5% (cola izquierda)
    try:
        var_5 = statistics.var(npvs, alpha=0.05, method='historical')
    except Exception:
        var_5 = float('nan')

    # Evaluación de viabilidad
    viability = 'No viable'
    if npv_mean > 0 and success_prob >= 0.5:
        viability = 'Viable'
    elif npv_mean > 0 and success_prob < 0.5:
        viability = 'Marginalmente viable'

    # Nivel de riesgo
    risk_level = _risk_level_from_metrics(var_5, volatility, success_prob)

    # Recomendaciones (heurísticas)
    recommendations: List[str] = []
    if viability == 'Viable':
        recommendations.append('Considerar escalado gradual de la inversión y monitorizar métricas clave semanalmente.')
    else:
        recommendations.append('Revisar supuestos de tasa y tamaño de inversión antes de comprometer capital adicional.')

    if volatility > 0.2:
        recommendations.append('Aplicar estrategias de cobertura o diversificación para mitigar la alta volatilidad observada.')
    else:
        recommendations.append('Mantener políticas de gestión de riesgo y reservas para eventos extremos.')

    recommendations.append('Realizar análisis de sensibilidad en parámetros críticos (tasa de descuento, tasas diarias, tamaño de inversiones).')
    recommendations.append('Aumentar el número de iteraciones si la incertidumbre de estimación es alta.')

    # Construir texto profesional
    lines: List[str] = []
    lines.append('Resumen ejecutivo')
    lines.append('-----------------')
    lines.append(f"VAN promedio estimado: {_fmt_currency(npv_mean)}.")
    lines.append(f"Intervalo de confianza (95%): {_fmt_currency(npv_ci[0])} a {_fmt_currency(npv_ci[1])}.")
    lines.append(f"Probabilidad estimada de VAN positivo (éxito): {success_prob:.2%}.")
    lines.append(f"Volatilidad (desviación estándar del VAN): {volatility:.2f}.")
    lines.append(f"Value at Risk (VaR 5% histórico): {_fmt_currency(var_5)}.")
    lines.append("")

    lines.append('Evaluación de viabilidad')
    lines.append('-------------------------')
    if viability == 'Viable':
        lines.append('El proyecto presenta métricas financieras consistentes con viabilidad económica en el horizonte analizado.')
    elif viability == 'Marginalmente viable':
        lines.append('El proyecto muestra VAN positivo pero con probabilidad de éxito limitada; requiere mitigación de riesgos.')
    else:
        lines.append('El proyecto no muestra viabilidad financiera según las métricas simuladas; desaconsejamos el despliegue sin cambios importantes.')

    lines.append('')
    lines.append('Análisis de riesgo')
    lines.append('------------------')
    lines.append(f"Nivel de riesgo asignado: {risk_level}.")
    lines.append('El VaR y la volatilidad indican la magnitud potencial de pérdidas en escenarios adversos; se recomienda evaluar la tolerancia a pérdidas frente al capital disponible.')

    lines.append('')
    lines.append('Recomendaciones')
    lines.append('---------------')
    for rec in recommendations:
        lines.append(f"- {rec}")

    lines.append('')
    lines.append('Conclusiones financieras')
    lines.append('-------------------------')
    lines.append('En conjunto, los resultados ofrecen una base estadística para la toma de decisiones: combinar este análisis con juicios cualitativos y pruebas de estrés antes de decisiones de inversión de gran volumen.')

    report_text = '\n'.join(lines)

    return {
        'viability': viability,
        'risk_level': risk_level,
        'recommendations': '\n'.join(recommendations),
        'conclusions': report_text.split('\n\n')[-1],
        'report_text': report_text,
    }
