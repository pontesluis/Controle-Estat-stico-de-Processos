from typing import List, Dict
from cep.prob import beta_shift_xbar

def analyze_shift_xbar(deltas: List[float], n: int) -> List[Dict[str, float]]:
    """
    Analisa os indicadores de deslocamento da média para a Carta X̄ baseada nos deltas dados.
    Calcula β (risco de não detecção imediata), Pd (probabilidade de detecção 1 - β) e ARL1 (1 / Pd).
    """
    results = []
    for delta in deltas:
        beta = beta_shift_xbar(delta, n)
        pd = 1.0 - beta
        arl1 = 1.0 / pd if pd > 1e-12 else float('inf')
        results.append({
            "delta": delta,
            "beta": beta,
            "Pd": pd,
            "ARL1": arl1
        })
    return results