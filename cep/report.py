import json
from pathlib import Path
from typing import Dict, Any

def save_json_results(data: Dict[str, Any], filepath: Path):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _get_violations(rules_dict, idx):
    if not rules_dict: return ""
    v = [r for r, indices in rules_dict.items() if idx in indices]
    return "Violação: " + ", ".join(v) if v else ""

def _status_str(res, idx, rule_keys, rule_names):
    if res["goal"] == "Calibrar" and idx in res.get("excluded", []): return "Excluída do cálculo"
    errs = [name for k, name in zip(rule_keys, rule_names) if k in res and idx in res[k]]
    return "Violação: " + ", ".join(errs) if errs else ""

def generate_text_report(res: Dict[str, Any]) -> str:
    lines = []
    lines.append("="*60)
    lines.append("RELATÓRIO DE CONTROLE ESTATÍSTICO DE PROCESSOS (CEP)")
    lines.append("="*60)
    
    meta = res["metadata"]
    lines.append(f"Rótulo (Label): {meta['Label']}")
    lines.append(f"Criado por: {meta['Created_by']} em {meta['Measured_at']}")
    lines.append(f"Objetivo: {res['goal']} | Tipo: Carta {res['type']}")
    n_str = res['n'] if 'n' in res else 'Variável'
    lines.append(f"Amostras (m): {res['m_total']} | Tamanho (n): {n_str} | Unidade: {meta['Unit']}")
    lines.append("-" * 60)
    
    fl = res["final_limits"]
    if res["goal"] == "Calibrar":
        lines.append(f"Iterações realizadas: {len(res['iterations'])}")
        lines.append(f"Amostras Excluídas: {res.get('excluded', [])}")
        
    if res["type"] in ["X", "IMR"]:
        lines.append(f"σ̂ do processo: {fl['sigma_hat']:.6f}")
        lines.append(f"\n[Carta {res['type'].replace('IMR', 'I')}]")
        lines.append(f"LIC = {fl['lic_x']:.6f} | LC = {fl['lc_x']:.6f} | LSC = {fl['lsc_x']:.6f}")
        lines.append(f"\n[Carta {'R' if res['type']=='X' else 'MR'}]")
        tipo2 = 'r' if res['type'] == 'X' else 'mr'
        lines.append(f"LIC = {fl['lic_'+tipo2]:.6f} | LC = {fl['lc_'+tipo2]:.6f} | LSC = {fl['lsc_'+tipo2]:.6f}")
    elif res["type"] == "P":
        lines.append(f"LC (p̄) = {fl['pbar']:.6f}  (Limites dinâmicos na tabela)")
    elif res["type"] == "C":
        lines.append(f"LIC = {fl['lic']:.6f} | LC (c̄) = {fl['lc']:.6f} | LSC = {fl['lsc']:.6f}")

    lines.append("-" * 60)
    lines.append("TABELA DE DADOS (POR AMOSTRA)")
    
    kal = res.get("kalman", [])
    has_k = len(kal) > 0
    
    if res["type"] == "X":
        k_header = " | Kalman(x̄)" if has_k else ""
        lines.append(f"{'i':>3} | {'x̄':>8} | {'r':>8} | {'s':>8}{k_header} | Status")
        for i in range(res["m_total"]):
            if res["goal"] == "Calibrar":
                st = _status_str(res, i, ["rule_1_x", "rule_1_r"], ["R1(X)", "R1(R)"])
            else:
                st_x = _get_violations(res.get("we_rules_x", {}), i)
                st_r = _get_violations(res.get("we_rules_r", {}), i)
                st = f"{st_x} | {st_r}".strip(" |")
            k_val = f" | {kal[i]:10.4f}" if has_k else ""
            lines.append(f"{i:>3} | {res['xbar_all'][i]:8.4f} | {res['r_all'][i]:8.4f} | {res['s_all'][i]:8.4f}{k_val} | {st}")
            
    elif res["type"] == "IMR":
        k_header = " | Kalman(I)" if has_k else ""
        lines.append(f"{'i':>3} | {'I':>8} | {'MR':>8}{k_header} | Status")
        for i in range(res["m_total"]):
            mr_val = f"{res['mr_raw'][i]:8.4f}" if res['mr_raw'][i] is not None else "     ---"
            if res["goal"] == "Calibrar":
                st = _status_str(res, i, ["rule_1_x", "rule_1_mr"], ["R1(I)", "R1(MR)"])
            else:
                st_x = _get_violations(res.get("we_rules_x", {}), i)
                st_mr = _get_violations(res.get("we_rules_mr", {}), i)
                st = f"{st_x} | {st_mr}".strip(" |")
            k_val = f" | {kal[i]:10.4f}" if has_k else ""
            lines.append(f"{i:>3} | {res['data_raw'][i]:8.4f} | {mr_val}{k_val} | {st}")
            
    elif res["type"] == "P":
        lines.append(f"{'i':>3} | {'n':>6} | {'d':>4} | {'p':>8} | {'LIC':>8} | {'LSC':>8} | Status")
        for i, d in enumerate(res["data_raw"]):
            st = _status_str(res, i, ["rule_1"], ["R1"]) if res["goal"] == "Calibrar" else _get_violations(res.get("we_rules_p", {}), i)
            lim = fl["limits_per_sample"][i] if res["goal"] == "Calibrar" else fl["limits_per_sample"][i]
            lines.append(f"{i:>3} | {d['n']:6} | {d['d']:4} | {d['d']/d['n']:8.4f} | {lim[0]:8.4f} | {lim[2]:8.4f} | {st}")
            
    elif res["type"] == "C":
        lines.append(f"{'i':>3} | {'c':>8} | Status")
        for i, v in enumerate(res["data_raw"]):
            st = _status_str(res, i, ["rule_1"], ["R1"]) if res["goal"] == "Calibrar" else _get_violations(res.get("we_rules_c", {}), i)
            lines.append(f"{i:>3} | {v:8} | {st}")

    if res["goal"] == "Calibrar":
        lines.append("\n[BASELINE GERADO PARA ACOMPANHAMENTO]")
        if res["type"] in ["X", "IMR"]:
            base = {"LSC": round(fl['lsc_x'], 6), "LC": round(fl['lc_x'], 6), "LIC": round(fl['lic_x'], 6), "Sigma": round(fl['sigma_hat'], 6)}
        elif res["type"] == "P": base = {"LC": round(fl['pbar'], 6)}
        elif res["type"] == "C": base = {"LC": round(fl['lc'], 6)}
        lines.append(json.dumps(base, indent=2))

    if "capability" in res and res["capability"]:
        cap = res["capability"]
        lines.append("-" * 60)
        lines.append("CAPACIDADE DO PROCESSO")
        lines.append(f"RCP = {cap['RCP']:.4f} | RCPk = {cap['RCPk']:.4f} | k = {cap['k']:.4f}")
        if "capability_atual" in res:
            lines.append(f"RCPk Atual (Média Deslocada) = {res['capability_atual']['RCPk']:.4f}")
        status_cap = "Capaz" if cap['RCPk'] >= 1.33 else ("Marginal" if cap['RCPk'] >= 1.0 else "Incapaz")
        lines.append(f"Classificação: {status_cap} | Fora de especificação: {cap['ppm']:.2f} ppm")
    elif res["type"] in ["P", "C"]:
        lines.append("-" * 60)
        lines.append("MÉTRICAS DO PROCESSO (ATRIBUTOS)")
        val = fl['pbar'] if res['type'] == 'P' else fl['lc']
        if res["type"] == "P": lines.append(f"Média de não conformes (p̄): {val*100:.4f}% ({val*1_000_000:.2f} ppm)")
        else: lines.append(f"Média de defeitos por amostra (c̄): {val:.4f}")

    lines.append("-" * 60)
    lines.append("PROBABILIDADES E ANÁLISE DE DESLOCAMENTO (β, Pd, ARL1)")
    lines.append(f"\n{'Desloc. (δ)':>11} | {'β':>7} | {'Pd':>7} | {'ARL1':>7}")
    for s in res["shift"]:
        lines.append(f"{s['delta']:11.2f} | {s['beta']:7.4f} | {s['Pd']:7.4f} | {s['ARL1']:7.2f}")
    
    if res["goal"] == "Acompanhar" and "delta_hat_analysis" in res:
        dh = res["delta_hat_analysis"]
        lines.append(f"\nDeslocamento atual (δ̂) = {dh['delta']:.2f} | β = {dh['beta']:.4f} | ARL1 = {dh['ARL1']:.2f}")

    lines.append("-" * 60)
    return "\n".join(lines)