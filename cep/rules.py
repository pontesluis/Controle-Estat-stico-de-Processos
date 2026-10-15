from typing import List

def check_rule_1(points: List[float], lic: float, lsc: float) -> List[int]:
    """
    Regra 1: Um ou mais pontos além dos limites de controle (estritamente).
    Retorna uma lista com os índices (0-based) das amostras que violam a regra.
    """
    violations = []
    for i, val in enumerate(points):
        if val > lsc or val < lic:
            violations.append(i)
    return violations