import math
from typing import List

def sample_mean(sample: List[float]) -> float:
    """Calcula a média x̄_i de uma amostra."""
    return sum(sample) / len(sample)

def sample_range(sample: List[float]) -> float:
    """Calcula a amplitude r_i de uma amostra (máx - mín)."""
    return max(sample) - min(sample)

def sample_stdev(sample: List[float]) -> float:
    """Calcula o desvio-padrão amostral s_i (divisor n - 1)."""
    n = len(sample)
    if n < 2:
        return 0.0
    mean_val = sample_mean(sample)
    variance = sum((x - mean_val) ** 2 for x in sample) / (n - 1)
    return math.sqrt(variance)