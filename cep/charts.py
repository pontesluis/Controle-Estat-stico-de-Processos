from typing import Tuple, List, Dict
from cep.constants import get_constants

def compute_limits_xbar(x_double_bar: float, r_bar: float, n: int) -> Tuple[float, float, float]:
    """
    Calcula os limites (LIC, LC, LSC) para a Carta X̄.
    Fórmula: LSC/LIC = x̿ ± A2 * R̄
    """
    _, _, _, a2 = get_constants(n)
    lc = x_double_bar
    lsc = x_double_bar + (a2 * r_bar)
    lic = x_double_bar - (a2 * r_bar)
    return lic, lc, lsc

def compute_limits_r(r_bar: float, n: int) -> Tuple[float, float, float]:
    """
    Calcula os limites (LIC, LC, LSC) para a Carta R.
    Fórmula: LSC = D4 * R̄; LIC = D3 * R̄
    """
    _, d3, d4, _ = get_constants(n)
    lc = r_bar
    lsc = d4 * r_bar
    lic = d3 * r_bar
    return lic, lc, lsc