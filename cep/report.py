import json
from pathlib import Path
from typing import Dict, Any

def save_json_results(data: Dict[str, Any], filepath: Path):
    """Salva os resultados consolidados."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_text_report(res: Dict[str, Any]) -> str:
    """Gera um relatório descritivo padronizado."""
    lines = []
    lines.append("="*60)
    lines.append("RELATÓRIO DE CONTROLE ESTATÍSTICO DE PROCESSOS (CEP)")
    lines.append("="*60)
    
    meta = res["metadata"]
    lines.append(f"Rótulo (Label): {meta['Label']}")
    lines.append(f"Criado por: {meta['Created_by']} em {meta['Measured_at']}")
    lines.append(f"Objetivo: {res['goal']} | Tipo: Carta {res['type']}")
    lines.append(f"Amostras (m): {res['m_total']} | Tamanho (n): {res['n']} | Unidade: {meta['Unit']}")
    lines.append("-" * 60)
    
    fl = res["final_limits"]
    
    lines.append("PARÂMETROS E LIMITES (Finais)")
    if res["goal"] == "Calibrar":
        lines.append(f"Iterações realizadas: {len(res['iterations'])}")
        lines.append(f"Amostras Excluídas do Cálculo: {res['excluded']}")
    lines.append(f"σ̂ do processo: {fl['sigma_hat']:.6f}")
    
    lines.append(f"\n[Carta X̄]")
    lines.append(f"LIC = {fl['lic_x']:.6f} | LC (x̿) = {fl['lc_x']:.6f} | LSC = {fl['lsc_x']:.6f}")
    
    lines.append(f"\n[Carta R]")
    lines.append(f"LIC = {fl['lic_r']:.6f} | LC (R̄) = {fl['lc_r']:.6f} | LSC = {fl['lsc_r']:.6f}")
    
    lines.append("-" * 60)
    lines.append("TABELA DE DADOS (POR AMOSTRA)")
    lines.append(f"{'i':>3} | {'x̄':>8} | {'r':>8} | {'s':>8} | Status")
    
    for i in range(res["m_total"]):
        xbar = res["xbar_all"][i]
        r = res["r_all"][i]
        s = res["s_all"][i]
        status = ""
        
        if res["goal"] == "Calibrar":
            if i in res["excluded"]:
                status = "Excluída do cálculo"
        elif res["goal"] == "Acompanhar":
            errs = []
            if i in res["rule_1_x"]: errs.append("R1(X)")
            if i in res["rule_1_r"]: errs.append("R1(R)")
            if errs:
                status = "Violação: " + ", ".join(errs)
                
        lines.append(f"{i:>3} | {xbar:8.4f} | {r:8.4f} | {s:8.4f} | {status}")

    if res["goal"] == "Calibrar":
        lines.append("\n[BASELINE GERADO PARA ACOMPANHAMENTO]")
        baseline = {
            "LSC": round(fl['lsc_x'], 6),
            "LC": round(fl['lc_x'], 6),
            "LIC": round(fl['lic_x'], 6),
            "Sigma": round(fl['sigma_hat'], 6)
        }
        lines.append(json.dumps(baseline, indent=2))

    cap = res["capability"]
    if cap:
        lines.append("-" * 60)
        lines.append("CAPACIDADE DO PROCESSO")
        lines.append(f"LSE = {res['lse']} | LIE = {res['lie']}")
        lines.append(f"RCP = {cap['RCP']:.4f} | RCPk = {cap['RCPk']:.4f} | k = {cap['k']:.4f}")
        
        if "capability_atual" in res:
            ca = res["capability_atual"]
            lines.append(f"RCPk Atual (Média Deslocada) = {ca['RCPk']:.4f}")
            
        status_cap = "Capaz" if cap['RCPk'] >= 1.33 else ("Marginal" if cap['RCPk'] >= 1.0 else "Incapaz")
        lines.append(f"Classificação: {status_cap}")
        lines.append(f"Fração fora de especificação: {cap['ppm']:.2f} ppm")
        lines.append("\n*Aviso: Os índices só são confiáveis se o processo estiver sob controle estatístico e os dados forem aproximadamente normais.*")
    
    lines.append("-" * 60)
    lines.append("PROBABILIDADES E ANÁLISE DE DESLOCAMENTO (β, Pd, ARL1)")
    alpha = 0.0027
    lines.append(f"Falso Alarme (α) ≈ {alpha:.4f} | ARL0 ≈ {1/alpha:.1f}")
    lines.append(f"\n{'Desloc. (δ)':>11} | {'β':>7} | {'Pd':>7} | {'ARL1':>7}")
    for shift in res["shift"]:
        lines.append(f"{shift['delta']:11.2f} | {shift['beta']:7.4f} | {shift['Pd']:7.4f} | {shift['ARL1']:7.2f}")
    
    if res["goal"] == "Acompanhar" and "delta_hat_analysis" in res:
        lines.append(f"\nDeslocamento atual percebido (δ̂) estimado.")
        d_hat = res["delta_hat_analysis"]
        lines.append(f"δ̂ = {d_hat['delta']:.2f} | β = {d_hat['beta']:.4f} | ARL1 = {d_hat['ARL1']:.2f}")

    lines.append("-" * 60)
    return "\n".join(lines)