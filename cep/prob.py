import math

def phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

def prob_normal(mu: float, sigma: float, a: float = None, b: float = None) -> float:
    p_b = phi((b - mu) / sigma) if b is not None else 1.0
    p_a = phi((a - mu) / sigma) if a is not None else 0.0
    return max(0.0, p_b - p_a)

def beta_shift_xbar(delta: float, n: int) -> float:
    shift = delta * math.sqrt(n)
    return phi(3.0 - shift) - phi(-3.0 - shift)

def prob_binomial_eq(n: int, k: int, p: float) -> float:
    if k < 0 or k > n: return 0.0
    return math.comb(n, k) * (p ** k) * ((1.0 - p) ** (n - k))

def prob_binomial_leq(n: int, k: int, p: float) -> float:
    return sum(prob_binomial_eq(n, j, p) for j in range(k + 1))

def prob_poisson_eq(lam: float, k: int) -> float:
    if k < 0: return 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def prob_poisson_leq(lam: float, k: int) -> float:
    if k < 0: return 0.0
    return sum(prob_poisson_eq(lam, j) for j in range(k + 1))

def beta_shift_imr(delta: float) -> float:
    return phi(3.0 - delta) - phi(-3.0 - delta)

def beta_shift_p(delta: float, pbar: float, nbar: int) -> float:
    if pbar <= 0.0 or pbar >= 1.0 or nbar <= 0:
        return 0.0
    p1 = pbar + delta * math.sqrt(pbar * (1.0 - pbar) / nbar)
    p1 = max(0.0, min(1.0, p1))
    
    std = math.sqrt(pbar * (1.0 - pbar) / nbar)
    lic = max(0.0, pbar - 3.0 * std)
    lsc = min(1.0, pbar + 3.0 * std)
    
    k_min = math.ceil(nbar * lic)
    k_max = math.floor(nbar * lsc)
    if k_min > k_max:
        return 0.0
        
    return sum(prob_binomial_eq(nbar, k, p1) for k in range(k_min, k_max + 1))

def beta_shift_c(delta: float, cbar: float) -> float:
    if cbar <= 0.0:
        return 0.0
    c1 = max(0.0, cbar + delta * math.sqrt(cbar))
    
    lic = max(0.0, cbar - 3.0 * math.sqrt(cbar))
    lsc = cbar + 3.0 * math.sqrt(cbar)
    
    k_min = math.ceil(lic)
    k_max = math.floor(lsc)
    if k_min > k_max:
        return 0.0
        
    return sum(prob_poisson_eq(c1, k) for k in range(k_min, k_max + 1))