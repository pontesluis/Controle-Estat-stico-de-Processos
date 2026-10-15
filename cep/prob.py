import math

def phi(z: float) -> float:
    """
    Função distribuição acumulada (CDF) da Normal Padrão, N(0,1).
    Fórmula: Φ(z) = 0.5 * (1 + erf(z / √2))
    """
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

def prob_normal(mu: float, sigma: float, a: float = None, b: float = None) -> float:
    """
    Calcula a probabilidade de x cair no intervalo (a, b) em uma distribuição N(μ, σ).
    Se 'a' ou 'b' forem omitidos, a cauda se estende ao infinito.
    """
    p_b = phi((b - mu) / sigma) if b is not None else 1.0
    p_a = phi((a - mu) / sigma) if a is not None else 0.0
    return max(0.0, p_b - p_a)

def beta_shift_xbar(delta: float, n: int) -> float:
    """
    Calcula o risco β (probabilidade de não detecção do deslocamento) para a carta X̄.
    Fórmula: β(δ) = Φ(3 - δ√n) - Φ(-3 - δ√n)
    """
    shift = delta * math.sqrt(n)
    return phi(3.0 - shift) - phi(-3.0 - shift)

def prob_binomial_eq(n: int, k: int, p: float) -> float:
    """Calcula P(X = k) para X ~ B(n, p)."""
    return math.comb(n, k) * (p ** k) * ((1.0 - p) ** (n - k))

def prob_binomial_leq(n: int, k: int, p: float) -> float:
    """Calcula P(X <= k) para X ~ B(n, p)."""
    return sum(prob_binomial_eq(n, j, p) for j in range(k + 1))

def prob_poisson_eq(lam: float, k: int) -> float:
    """Calcula P(X = k) para X ~ Poisson(λ)."""
    return math.exp(-lam) * (lam ** k) / math.factorial(k)