from typing import List, Dict

def check_we_rules(data: List[float], cl: float, sigma: float) -> Dict[str, List[int]]:
    """
    Verifica as 4 regras do Western Electric para cartas de variáveis.
    Retorna um dicionário com os índices das amostras que violaram cada regra.
    """
    n = len(data)
    violations = {"R1": [], "R2": [], "R3": [], "R4": []}
    
    if sigma <= 0:
        return violations

    for i in range(n):
        val = data[i]
        
        # Regra 1: 1 ponto além de 3 sigmas
        if abs(val - cl) > 3 * sigma:
            if i not in violations["R1"]: violations["R1"].append(i)
            
        # Regra 2: 2 de 3 pontos consecutivos além de 2 sigmas do mesmo lado
        if i >= 2:
            window = data[i-2:i+1]
            if sum(1 for x in window if x - cl > 2 * sigma) >= 2:
                if i not in violations["R2"]: violations["R2"].append(i)
            elif sum(1 for x in window if cl - x > 2 * sigma) >= 2:
                if i not in violations["R2"]: violations["R2"].append(i)
                
        # Regra 3: 4 de 5 pontos consecutivos além de 1 sigma do mesmo lado
        if i >= 4:
            window = data[i-4:i+1]
            if sum(1 for x in window if x - cl > 1 * sigma) >= 4:
                if i not in violations["R3"]: violations["R3"].append(i)
            elif sum(1 for x in window if cl - x > 1 * sigma) >= 4:
                if i not in violations["R3"]: violations["R3"].append(i)
                
        # Regra 4: 8 pontos consecutivos do mesmo lado da linha central
        if i >= 7:
            window = data[i-7:i+1]
            if all(x > cl for x in window):
                if i not in violations["R4"]: violations["R4"].append(i)
            elif all(x < cl for x in window):
                if i not in violations["R4"]: violations["R4"].append(i)
                
    return violations