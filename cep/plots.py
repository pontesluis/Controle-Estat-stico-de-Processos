# projeto_cep/cep/plots.py
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any
import math

def plot_xbar_r(res: Dict[str, Any], filepath: Path):
    """Gera o par de gráficos X̄ e R e mostra-os num ecrã interativo."""
    fl = res["final_limits"]
    m = res["m_total"]
    indices = list(range(m))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    meta = res["metadata"]
    fig.suptitle(f"{meta['Label']} - Carta {res['type']} ({res['goal']})\nMedido em: {meta['Measured_at']}", fontsize=12)
    
    # ---------------- CARTA XBAR ----------------
    x_vals = res["xbar_all"]
    ax1.plot(indices, x_vals, marker='o', linestyle='-', color='blue')
    ax1.axhline(fl['lc_x'], color='green', linestyle='-', label='LC')
    ax1.axhline(fl['lsc_x'], color='red', linestyle='--', label='LSC')
    ax1.axhline(fl['lic_x'], color='red', linestyle='--', label='LIC')
    
    # Zonas
    sigma_plot_x = (fl['lsc_x'] - fl['lc_x']) / 3.0
    ax1.axhline(fl['lc_x'] + sigma_plot_x, color='gray', linestyle=':', alpha=0.5)
    ax1.axhline(fl['lc_x'] + 2*sigma_plot_x, color='gray', linestyle=':', alpha=0.5)
    ax1.axhline(fl['lc_x'] - sigma_plot_x, color='gray', linestyle=':', alpha=0.5)
    ax1.axhline(fl['lc_x'] - 2*sigma_plot_x, color='gray', linestyle=':', alpha=0.5)

    _mark_violations_and_exclusions(ax1, indices, x_vals, res, fl['lic_x'], fl['lsc_x'])
    ax1.set_ylabel(f"Média X̄ ({meta['Unit']})")
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    
    # ---------------- CARTA R ----------------
    r_vals = res["r_all"]
    ax2.plot(indices, r_vals, marker='o', linestyle='-', color='purple')
    ax2.axhline(fl['lc_r'], color='green', linestyle='-', label='LC')
    ax2.axhline(fl['lsc_r'], color='red', linestyle='--', label='LSC')
    ax2.axhline(fl['lic_r'], color='red', linestyle='--', label='LIC')

    _mark_violations_and_exclusions(ax2, indices, r_vals, res, fl['lic_r'], fl['lsc_r'])
    ax2.set_ylabel(f"Amplitude R ({meta['Unit']})")
    ax2.set_xlabel("Amostra")
    ax2.set_xticks(indices)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150) # Continua a guardar o ficheiro PNG
    plt.show()                     # <--- ABRE A JANELA INTERATIVA NO ECRÃ
    plt.close()

def _mark_violations_and_exclusions(ax, indices, vals, res, lic, lsc):
    """Pinta de vermelho pontos que quebram R1 e marca com x os removidos na calibração."""
    for i, v in enumerate(vals):
        if res["goal"] == "Calibrar" and i in res.get("excluded", []):
            ax.plot(i, v, marker='x', markersize=10, color='gray')
            ax.text(i+0.1, v, "×", color="gray", fontsize=10)
        elif v > lsc or v < lic:
            ax.plot(i, v, marker='o', markersize=8, color='red')
            ax.text(i+0.1, v, "R1", color="red", fontsize=10)

def plot_capability(res: Dict[str, Any], filepath: Path):
    """Histograma sobreposto à curva de probabilidade normal simulada."""
    fl = res["final_limits"]
    mu = fl["lc_x"]
    sigma = fl["sigma_hat"]
    
    lse = res["lse"]
    lie = res["lie"]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Gerando a malha para a curva teórica
    x_min = min(lie, mu - 4*sigma)
    x_max = max(lse, mu + 4*sigma)
    step = (x_max - x_min) / 200
    
    xs, ys = [], []
    curr = x_min
    while curr <= x_max:
        xs.append(curr)
        # PDF Normal
        pdf = (1.0 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((curr - mu) / sigma)**2)
        ys.append(pdf)
        curr += step
        
    ax.plot(xs, ys, color='blue', label='N(LC, σ̂)')
    
    ax.axvline(lse, color='red', linestyle='--', label='LSE')
    ax.axvline(lie, color='red', linestyle='--', label='LIE')
    ax.axvline(mu, color='green', linestyle='-', label='Alvo/Média')
    
    ax.set_title(f"Análise de Capacidade - {res['metadata']['Label']}")
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150) # Continua a guardar o ficheiro PNG
    plt.show()                     # <--- ABRE A JANELA INTERATIVA NO ECRÃ
    plt.close()