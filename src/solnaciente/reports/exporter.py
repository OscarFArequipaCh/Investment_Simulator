from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Sequence

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


def export_to_excel(result: Dict, path: str) -> str:
    df = pd.DataFrame(
        {
            'Métrica': [
                'VAN promedio',
                'Probabilidad éxito',
                'Ganancias promedio',
                'IC95 bajo',
                'IC95 alto',
            ],
            'Valor': [
                result.get('npv_mean'),
                result.get('success_prob'),
                result.get('total_gains_mean'),
                result.get('npv_ci', (None, None))[0],
                result.get('npv_ci', (None, None))[1],
            ],
        }
    )
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)
    return str(output_path)


def export_report_to_pdf(report_text: str, path: str) -> str:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(output_path) as pdf:
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        lines = report_text.split('\n')
        wrapped = []
        for line in lines:
            wrapped.extend([line[i:i+90] for i in range(0, len(line), 90)])
        y = 0.95
        for entry in wrapped:
            ax.text(0.02, y, entry, fontsize=10, family='monospace')
            y -= 0.025
            if y < 0.05:
                fig, ax = plt.subplots(figsize=(8.5, 11))
                ax.axis('off')
                y = 0.95
                pdf.savefig(fig)
                plt.close(fig)
        pdf.savefig(fig)
        plt.close(fig)
    return str(output_path)
