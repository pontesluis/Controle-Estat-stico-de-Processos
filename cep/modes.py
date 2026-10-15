from typing import Dict, Any, List
from cep.stats import sample_mean, sample_range, sample_stdev
from cep.charts import compute_limits_xbar, compute_limits_r, compute_limits_imr, compute_limits_p, compute_limits_c
from cep.capability import compute_capability
from cep.rules import check_we_rules
from cep.kalman import run_kalman_filter
from cep.shift import analyze_shift_xbar, analyze_shift_imr, analyze_shift_p, analyze_shift_c
from cep.constants import get_constants

def run_calibration(config: Dict[str, Any], allow_revision: bool = True, deltas: List[float] = None) -> Dict[str, Any]:
    t = config["Type"]
    if t == "X": return _cal_xbar(config, allow_revision, deltas)
    if t == "IMR": return _cal_imr(config, allow_revision, deltas)
    if t == "P": return _cal_p(config, allow_revision, deltas)
    if t == "C": return _cal_c(config, allow_revision, deltas)

def run_monitoring(config: Dict[str, Any], deltas: List[float] = None, use_kalman: bool = False, q: float = 0.05) -> Dict[str, Any]:
    t = config["Type"]
    if t == "X": return _mon_xbar(config, deltas, use_kalman, q)
    if t == "IMR": return _mon_imr(config, deltas, use_kalman, q)
    if t == "P": return _mon_p(config, deltas)
    if t == "C": return _mon_c(config, deltas)

# ============================== FASE I (CALIBRAR) ==============================
def _cal_xbar(config, allow_revision, deltas):
    data = config["Data"]
    m = len(data)
    n = len(data[0])
    active = list(range(m))
    excluded = []
    iterations = []
    
    for it in range(10 if allow_revision else 1):
        xbar_l = [sample_mean(data[i]) for i in active]
        r_l = [sample_range(data[i]) for i in active]
        x_dbar = sum(xbar_l)/len(xbar_l)
        r_bar = sum(r_l)/len(r_l)
        
        lic_x, lc_x, lsc_x = compute_limits_xbar(x_dbar, r_bar, n)
        lic_r, lc_r, lsc_r = compute_limits_r(r_bar, n)
        
        v_x = [active[i] for i, v in enumerate(xbar_l) if v < lic_x or v > lsc_x]
        v_r = [active[i] for i, v in enumerate(r_l) if v < lic_r or v > lsc_r]
        violators = set(v_x + v_r)
        
        d2, _, _, _ = get_constants(n)
        iterations.append({"iter": it, "active_count": len(active), "x_double_bar": x_dbar, "r_bar": r_bar, 
                           "sigma_hat": r_bar/d2, "lic_x": lic_x, "lc_x": lc_x, "lsc_x": lsc_x, 
                           "lic_r": lic_r, "lc_r": lc_r, "lsc_r": lsc_r, "violators": list(violators)})
        if not violators or (len(active) - len(violators)) < max(10, 0.5 * m): break
        excluded.extend(violators)
        active = [x for x in active if x not in violators]

    cap = compute_capability(config["LSE"], config["LIE"], iterations[-1]["lc_x"], iterations[-1]["sigma_hat"])
    return {"metadata": _get_meta(config), "type": "X", "goal": "Calibrar", "n": n, "m_total": m, "excluded": excluded, 
            "iterations": iterations, "final_limits": iterations[-1], "data_raw": data, 
            "xbar_all": [sample_mean(d) for d in data], "r_all": [sample_range(d) for d in data], 
            "s_all": [sample_stdev(d) for d in data], "capability": cap, "shift": analyze_shift_xbar(deltas or _d(), n), 
            "lse": config["LSE"], "lie": config["LIE"]}

def _cal_imr(config, allow_revision, deltas):
    data = config["Data"]
    m = len(data)
    mr_raw = [None] + [abs(data[i] - data[i-1]) for i in range(1, m)]
    act_x, act_mr = list(range(m)), list(range(1, m))
    excluded = []
    iterations = []
    
    for it in range(10 if allow_revision else 1):
        xbar = sum(data[i] for i in act_x)/len(act_x)
        mrbar = sum(mr_raw[i] for i in act_mr)/len(act_mr)
        (lic_i, lc_i, lsc_i), (lic_mr, lc_mr, lsc_mr) = compute_limits_imr(xbar, mrbar)
        
        v_x = [i for i in act_x if data[i] < lic_i or data[i] > lsc_i]
        v_mr = [i for i in act_mr if mr_raw[i] < lic_mr or mr_raw[i] > lsc_mr]
        violators = set(v_x + v_mr)
        
        iterations.append({"iter": it, "active_count": len(act_x), "xbar": xbar, "mrbar": mrbar, "sigma_hat": mrbar/1.128,
                           "lic_x": lic_i, "lc_x": lc_i, "lsc_x": lsc_i, "lic_mr": lic_mr, "lc_mr": lc_mr, "lsc_mr": lsc_mr,
                           "violators": list(violators)})
        if not violators or (len(act_x) - len(violators)) < max(10, 0.5 * m): break
        
        for v in violators:
            if v not in excluded: excluded.append(v)
            if v in act_x: act_x.remove(v)
            if v in act_mr: act_mr.remove(v)
            if v+1 in act_mr: act_mr.remove(v+1)
            
    cap = compute_capability(config["LSE"], config["LIE"], iterations[-1]["lc_x"], iterations[-1]["sigma_hat"])
    return {"metadata": _get_meta(config), "type": "IMR", "goal": "Calibrar", "n": 1, "m_total": m, "excluded": excluded, 
            "iterations": iterations, "final_limits": iterations[-1], "data_raw": data, "mr_raw": mr_raw,
            "capability": cap, "shift": analyze_shift_imr(deltas or _d()), "lse": config["LSE"], "lie": config["LIE"]}

def _cal_p(config, allow_revision, deltas):
    data = config["Data"]
    m = len(data)
    active = list(range(m))
    excluded = []
    iterations = []
    
    for it in range(10 if allow_revision else 1):
        pbar = sum(data[i]["d"] for i in active) / sum(data[i]["n"] for i in active)
        violators = []
        for i in active:
            lic, _, lsc = compute_limits_p(pbar, data[i]["n"])
            pi = data[i]["d"] / data[i]["n"]
            if pi < lic or pi > lsc: violators.append(i)
        
        iterations.append({"iter": it, "active_count": len(active), "pbar": pbar, "violators": violators})
        if not violators or (len(active) - len(violators)) < max(10, 0.5 * m): break
        for v in violators:
            excluded.append(v)
            active.remove(v)
            
    nbar = round(sum(d["n"] for d in data) / m)
    lims = [compute_limits_p(iterations[-1]["pbar"], d["n"]) for d in data]
    return {"metadata": _get_meta(config), "type": "P", "goal": "Calibrar", "m_total": m, "excluded": excluded, 
            "iterations": iterations, "final_limits": {"pbar": iterations[-1]["pbar"], "limits_per_sample": lims}, 
            "data_raw": data, "shift": analyze_shift_p(deltas or _d(), iterations[-1]["pbar"], nbar)}

def _cal_c(config, allow_revision, deltas):
    data = config["Data"]
    m = len(data)
    active = list(range(m))
    excluded, iterations = [], []
    
    for it in range(10 if allow_revision else 1):
        cbar = sum(data[i] for i in active) / len(active)
        lic, lc, lsc = compute_limits_c(cbar)
        v_c = [i for i in active if data[i] < lic or data[i] > lsc]
        iterations.append({"iter": it, "active_count": len(active), "cbar": cbar, "lic": lic, "lc": lc, "lsc": lsc, "violators": v_c})
        if not v_c or (len(active) - len(v_c)) < max(10, 0.5 * m): break
        for v in v_c:
            excluded.append(v)
            active.remove(v)
            
    return {"metadata": _get_meta(config), "type": "C", "goal": "Calibrar", "m_total": m, "excluded": excluded, 
            "iterations": iterations, "final_limits": iterations[-1], "data_raw": data, "shift": analyze_shift_c(deltas or _d(), iterations[-1]["cbar"])}

# ============================== FASE II (ACOMPANHAR) ==============================
def _mon_xbar(config, deltas, use_kalman, q):
    data = config["Data"]
    n = len(data[0])
    lc_x, lic_x, lsc_x, sigma = config["LC_ref"], config["LIC_ref"], config["LSC_ref"], config["Sigma_ref"]
    d2, _, d4, d3 = get_constants(n)
    r_bar = sigma * d2
    lic_r, lc_r, lsc_r = d3 * r_bar, r_bar, d4 * r_bar
    
    xbar_l = [sample_mean(d) for d in data]
    r_l = [sample_range(d) for d in data]
    
    sigma_xbar = sigma / (n**0.5)
    we_rules = check_we_rules(xbar_l, lc_x, sigma_xbar)
    we_rules_r = {"R1": [i for i, v in enumerate(r_l) if v < lic_r or v > lsc_r]}
    
    kalman_est = []
    if use_kalman:
        kalman_est = run_kalman_filter(xbar_l, initial_estimate=lc_x, measurement_variance=(sigma_xbar**2), process_variance=q)
    
    cap = compute_capability(config["LSE"], config["LIE"], lc_x, sigma)
    cap_atual = compute_capability(config["LSE"], config["LIE"], sum(xbar_l)/len(xbar_l), sigma)
    delta_hat = (sum(xbar_l)/len(xbar_l) - lc_x) / sigma if sigma > 0 else 0
    
    return {"metadata": _get_meta(config), "type": "X", "goal": "Acompanhar", "n": n, "m_total": len(data),
            "final_limits": {"lc_x": lc_x, "lic_x": lic_x, "lsc_x": lsc_x, "lc_r": lc_r, "lic_r": lic_r, "lsc_r": lsc_r, "sigma_hat": sigma},
            "data_raw": data, "xbar_all": xbar_l, "r_all": r_l, "s_all": [sample_stdev(d) for d in data],
            "we_rules_x": we_rules, "we_rules_r": we_rules_r, "kalman": kalman_est,
            "capability": cap, "capability_atual": cap_atual, "shift": analyze_shift_xbar(deltas or _d(), n),
            "delta_hat_analysis": analyze_shift_xbar([abs(delta_hat)], n)[0], "lse": config["LSE"], "lie": config["LIE"]}

def _mon_imr(config, deltas, use_kalman, q):
    data = config["Data"]
    lc_x, lic_x, lsc_x, sigma = config["LC_ref"], config["LIC_ref"], config["LSC_ref"], config["Sigma_ref"]
    mrbar = sigma * 1.128
    lic_mr, lc_mr, lsc_mr = 0.0, mrbar, 3.267 * mrbar
    mr_raw = [None] + [abs(data[i] - data[i-1]) for i in range(1, len(data))]
    
    we_rules = check_we_rules(data, lc_x, sigma)
    we_rules_mr = {"R1": [i for i in range(1, len(data)) if mr_raw[i] < lic_mr or mr_raw[i] > lsc_mr]}
    
    kalman_est = []
    if use_kalman:
        kalman_est = run_kalman_filter(data, initial_estimate=lc_x, measurement_variance=(sigma**2), process_variance=q)
    
    cap = compute_capability(config["LSE"], config["LIE"], lc_x, sigma)
    cap_atual = compute_capability(config["LSE"], config["LIE"], sum(data)/len(data), sigma)
    delta_hat = (sum(data)/len(data) - lc_x) / sigma if sigma > 0 else 0
    
    return {"metadata": _get_meta(config), "type": "IMR", "goal": "Acompanhar", "n": 1, "m_total": len(data),
            "final_limits": {"lc_x": lc_x, "lic_x": lic_x, "lsc_x": lsc_x, "lc_mr": lc_mr, "lic_mr": lic_mr, "lsc_mr": lsc_mr, "sigma_hat": sigma},
            "data_raw": data, "mr_raw": mr_raw, "we_rules_x": we_rules, "we_rules_mr": we_rules_mr, "kalman": kalman_est,
            "capability": cap, "capability_atual": cap_atual, "shift": analyze_shift_imr(deltas or _d()),
            "delta_hat_analysis": analyze_shift_imr([abs(delta_hat)])[0], "lse": config["LSE"], "lie": config["LIE"]}

def _mon_p(config, deltas):
    data, pbar = config["Data"], config["LC_ref"]
    has_static = "LSC_ref" in config and "LIC_ref" in config
    lims, v_p = [], []
    for i, d in enumerate(data):
        lic = config["LIC_ref"] if has_static else compute_limits_p(pbar, d["n"])[0]
        lsc = config["LSC_ref"] if has_static else compute_limits_p(pbar, d["n"])[2]
        lims.append((lic, pbar, lsc))
        pi = d["d"]/d["n"]
        if pi < lic or pi > lsc: v_p.append(i)
        
    nbar = round(sum(d["n"] for d in data) / len(data))
    return {"metadata": _get_meta(config), "type": "P", "goal": "Acompanhar", "m_total": len(data),
            "final_limits": {"pbar": pbar, "limits_per_sample": lims}, "data_raw": data,
            "we_rules_p": {"R1": v_p}, "shift": analyze_shift_p(deltas or _d(), pbar, nbar)}

def _mon_c(config, deltas):
    data, cbar = config["Data"], config["LC_ref"]
    lic = config.get("LIC_ref", max(0, cbar - 3.0 * (cbar**0.5)))
    lsc = config.get("LSC_ref", cbar + 3.0 * (cbar**0.5))
    v_c = [i for i, v in enumerate(data) if v < lic or v > lsc]
    
    return {"metadata": _get_meta(config), "type": "C", "goal": "Acompanhar", "m_total": len(data),
            "final_limits": {"lic": lic, "lc": cbar, "lsc": lsc}, "data_raw": data,
            "we_rules_c": {"R1": v_c}, "shift": analyze_shift_c(deltas or _d(), cbar)}

def _get_meta(config): return {k: config[k] for k in ["Label", "Unit", "Measured_at", "Created_by"]}
def _d(): return [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]