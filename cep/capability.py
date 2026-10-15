from typing import Dict, Any
from cep.prob import prob_normal

def compute_capability(lse: float, lie: float, lc: float, sigma_hat: float) -> Dict[str, float]:
    """
    Calcula os índices de capacidade (RCP, RCPS, RCPI, RCPk, k) 
    e a fração estimada fora de especificação para processos com dados aproximadamente normais.
    Fórmulas baseadas em N(LC, σ̂).
    """
    if sigma_hat == 0:
        return {}

    rcp = (lse - lie) / (6 * sigma_hat)
    rcps = (lse - lc) / (3 * sigma_hat)
    rcpi = (lc - lie) / (3 * sigma_hat)
    rcpk = min(rcps, rcpi)
    
    m = (lse + lie) / 2.0
    k = abs(lc - m) / ((lse - lie) / 2.0)
    
    prob_lower = prob_normal(mu=lc, sigma=sigma_hat, b=lie)  # P(x < LIE)
    prob_upper = prob_normal(mu=lc, sigma=sigma_hat, a=lse)  # P(x > LSE)
    fraction_out = prob_lower + prob_upper
    
    return {
        "RCP": rcp,
        "RCPS": rcps,
        "RCPI": rcpi,
        "RCPk": rcpk,
        "k": k,
        "fraction_out": fraction_out,
        "ppm": fraction_out * 1_000_000
    }