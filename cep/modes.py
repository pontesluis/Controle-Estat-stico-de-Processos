from typing import Dict, Any, List
from cep.stats import sample_mean, sample_range, sample_stdev
from cep.charts import compute_limits_xbar, compute_limits_r
from cep.capability import compute_capability
from cep.rules import check_rule_1
from cep.shift import analyze_shift_xbar
from cep.constants import get_constants

def _process_xbar_r_data(data_matrix: List[List[float]], active_indices: List[int]) -> Dict[str, Any]:
    """Calcula estatísticas de sumário com base apenas nos índices ativos (Fase I ou II)."""
    n = len(data_matrix[0])
    xbar_list = []
    r_list = []
    s_list = []

    for i in active_indices:
        sample = data_matrix[i]
        xbar_list.append(sample_mean(sample))
        r_list.append(sample_range(sample))
        s_list.append(sample_stdev(sample))

    x_double_bar = sum(xbar_list) / len(xbar_list)
    r_bar = sum(r_list) / len(r_list)
    s_bar = sum(s_list) / len(s_list)
    
    d2, _, _, _ = get_constants(n)
    sigma_hat = r_bar / d2

    return {
        "xbar_list": xbar_list,
        "r_list": r_list,
        "s_list": s_list,
        "x_double_bar": x_double_bar,
        "r_bar": r_bar,
        "s_bar": s_bar,
        "sigma_hat": sigma_hat,
        "n": n
    }

def run_calibration(config: Dict[str, Any], allow_revision: bool = True, deltas: List[float] = None) -> Dict[str, Any]:
    """
    Fase I: Calibração iterativa descartando pontos que violam a Regra 1 
    em qualquer carta do par (X e R).
    """
    data = config["Data"]
    m = len(data)
    n = len(data[0])
    
    active_indices = list(range(m))
    excluded_indices = []
    iterations_log = []
    
    max_iter = 10 if allow_revision else 1
    
    for it in range(max_iter):
        stats = _process_xbar_r_data(data, active_indices)
        
        # Limites
        lic_x, lc_x, lsc_x = compute_limits_xbar(stats["x_double_bar"], stats["r_bar"], n)
        lic_r, lc_r, lsc_r = compute_limits_r(stats["r_bar"], n)
        
        # Verificações de Regra 1
        v_x = check_rule_1(stats["xbar_list"], lic_x, lsc_x)
        v_r = check_rule_1(stats["r_list"], lic_r, lsc_r)
        
        # Mapeamento do subíndice (da lista filtrada) para o índice global
        violators = set([active_indices[i] for i in v_x] + [active_indices[i] for i in v_r])
        
        iter_info = {
            "iter": it,
            "active_count": len(active_indices),
            "x_double_bar": stats["x_double_bar"],
            "r_bar": stats["r_bar"],
            "sigma_hat": stats["sigma_hat"],
            "lic_x": lic_x, "lc_x": lc_x, "lsc_x": lsc_x,
            "lic_r": lic_r, "lc_r": lc_r, "lsc_r": lsc_r,
            "violators": list(violators)
        }
        iterations_log.append(iter_info)
        
        if not violators:
            break
            
        # Condições de parada
        if (len(active_indices) - len(violators)) < max(10, 0.5 * m):
            break
            
        excluded_indices.extend(violators)
        active_indices = [idx for idx in active_indices if idx not in violators]
    
    # Processamento Final p/ retorno global (preservando o dataset inteiro para gráficos)
    final_stats = _process_xbar_r_data(data, list(range(m))) # Valores brutos inteiros
    
    cap = compute_capability(config["LSE"], config["LIE"], iter_info["lc_x"], iter_info["sigma_hat"])
    shift_analysis = analyze_shift_xbar(deltas or [0.5, 1.0, 1.5, 2.0, 2.5, 3.0], n)
    
    return {
        "metadata": {
            "Label": config["Label"],
            "Unit": config["Unit"],
            "Measured_at": config["Measured_at"],
            "Created_by": config["Created_by"]
        },
        "type": "X",
        "goal": "Calibrar",
        "n": n,
        "m_total": m,
        "excluded": excluded_indices,
        "iterations": iterations_log,
        "final_limits": iter_info,
        "data_raw": data,
        "xbar_all": final_stats["xbar_list"],
        "r_all": final_stats["r_list"],
        "s_all": final_stats["s_list"],
        "capability": cap,
        "shift": shift_analysis,
        "lse": config["LSE"],
        "lie": config["LIE"]
    }

def run_monitoring(config: Dict[str, Any], deltas: List[float] = None) -> Dict[str, Any]:
    """
    Fase II: Acompanhamento. Avalia dados novos contra uma baseline estática fixada.
    """
    data = config["Data"]
    m = len(data)
    n = len(data[0])
    
    lc_x = config["LC_ref"]
    lic_x = config["LIC_ref"]
    lsc_x = config["LSC_ref"]
    sigma = config["Sigma_ref"]
    
    d2, _, d4, d3 = get_constants(n)
    r_bar = sigma * d2
    lc_r = r_bar
    lic_r = d3 * r_bar
    lsc_r = d4 * r_bar
    
    stats = _process_xbar_r_data(data, list(range(m)))
    
    v_x_indices = check_rule_1(stats["xbar_list"], lic_x, lsc_x)
    v_r_indices = check_rule_1(stats["r_list"], lic_r, lsc_r)
    
    cap = compute_capability(config["LSE"], config["LIE"], lc_x, sigma)
    cap_atual = compute_capability(config["LSE"], config["LIE"], stats["x_double_bar"], sigma)
    
    shift_analysis = analyze_shift_xbar(deltas or [0.5, 1.0, 1.5, 2.0, 2.5, 3.0], n)
    
    delta_hat = (stats["x_double_bar"] - lc_x) / sigma if sigma > 0 else 0
    beta_hat = analyze_shift_xbar([abs(delta_hat)], n)[0]
    
    return {
        "metadata": {
            "Label": config["Label"], "Unit": config["Unit"],
            "Measured_at": config["Measured_at"], "Created_by": config["Created_by"]
        },
        "type": "X",
        "goal": "Acompanhar",
        "n": n, "m_total": m,
        "final_limits": {
            "x_double_bar_atual": stats["x_double_bar"],
            "lc_x": lc_x, "lic_x": lic_x, "lsc_x": lsc_x,
            "lc_r": lc_r, "lic_r": lic_r, "lsc_r": lsc_r,
            "sigma_hat": sigma
        },
        "data_raw": data,
        "xbar_all": stats["xbar_list"],
        "r_all": stats["r_list"],
        "s_all": stats["s_list"],
        "rule_1_x": v_x_indices,
        "rule_1_r": v_r_indices,
        "capability": cap,
        "capability_atual": cap_atual,
        "shift": shift_analysis,
        "delta_hat_analysis": beta_hat,
        "lse": config["LSE"], "lie": config["LIE"]
    }