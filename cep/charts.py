from typing import Tuple
from cep.constants import get_constants
import math

def compute_limits_xbar(x_double_bar: float, r_bar: float, n: int) -> Tuple[float, float, float]:
    _, _, _, a2 = get_constants(n)
    return (x_double_bar - (a2 * r_bar), x_double_bar, x_double_bar + (a2 * r_bar))

def compute_limits_r(r_bar: float, n: int) -> Tuple[float, float, float]:
    _, d3, d4, _ = get_constants(n)
    return (d3 * r_bar, r_bar, d4 * r_bar)

def compute_limits_imr(xbar: float, mrbar: float) -> Tuple[Tuple[float,float,float], Tuple[float,float,float]]:
    sigma_hat = mrbar / 1.128
    lic_i = xbar - 3.0 * sigma_hat
    lc_i = xbar
    lsc_i = xbar + 3.0 * sigma_hat
    
    lic_mr = 0.0
    lc_mr = mrbar
    lsc_mr = 3.267 * mrbar
    return (lic_i, lc_i, lsc_i), (lic_mr, lc_mr, lsc_mr)

def compute_limits_p(pbar: float, n: int) -> Tuple[float, float, float]:
    if n <= 0: return 0.0, pbar, 0.0
    std = math.sqrt(pbar * (1.0 - pbar) / n)
    lic = max(0.0, pbar - 3.0 * std)
    lc = pbar
    lsc = min(1.0, pbar + 3.0 * std)
    return lic, lc, lsc

def compute_limits_c(cbar: float) -> Tuple[float, float, float]:
    std = math.sqrt(cbar)
    lic = max(0.0, cbar - 3.0 * std)
    lc = cbar
    lsc = cbar + 3.0 * std
    return lic, lc, lsc