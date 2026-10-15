from typing import List, Dict
from cep.prob import beta_shift_xbar, beta_shift_imr, beta_shift_p, beta_shift_c

def _build_shift_results(deltas: List[float], beta_func) -> List[Dict[str, float]]:
    results = []
    for delta in deltas:
        beta = beta_func(delta)
        pd = 1.0 - beta
        arl1 = 1.0 / pd if pd > 1e-12 else float('inf')
        results.append({"delta": delta, "beta": beta, "Pd": pd, "ARL1": arl1})
    return results

def analyze_shift_xbar(deltas: List[float], n: int) -> List[Dict[str, float]]:
    return _build_shift_results(deltas, lambda d: beta_shift_xbar(d, n))

def analyze_shift_imr(deltas: List[float]) -> List[Dict[str, float]]:
    return _build_shift_results(deltas, lambda d: beta_shift_imr(d))

def analyze_shift_p(deltas: List[float], pbar: float, nbar: int) -> List[Dict[str, float]]:
    return _build_shift_results(deltas, lambda d: beta_shift_p(d, pbar, nbar))

def analyze_shift_c(deltas: List[float], cbar: float) -> List[Dict[str, float]]:
    return _build_shift_results(deltas, lambda d: beta_shift_c(d, cbar))