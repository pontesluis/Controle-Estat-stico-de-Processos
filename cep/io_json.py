import json
import math
from pathlib import Path
from typing import Dict, Any

def read_and_validate_json(filepath: Path) -> Dict[str, Any]:
    """
    Lê o JSON, ignora chaves desconhecidas e valida obrigatoriedades para todos os tipos de cartas.
    """
    if not filepath.exists():
        raise ValueError(f"Arquivo não encontrado: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro de sintaxe no JSON: {e}")

    required_keys = ["Type", "Goal", "Data"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Chave obrigatória ausente: '{key}'")

    parsed_data = {
        "Unit": data.get("Unit", ""),
        "Measured_at": data.get("Measured_at", "Desconhecido"),
        "Created_by": data.get("Created_by", "Anônimo"),
        "Label": data.get("Label", "Processo"),
        "Type": str(data["Type"]).upper(),
        "Goal": str(data["Goal"]).lower(),
        "Deltas": data.get("Deltas", [0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    }
    
    if parsed_data["Type"] in ["X", "XBAR", "X-R", "X̄"]:
        parsed_data["Type"] = "X"
    elif parsed_data["Type"] not in ["R", "IMR", "P", "C"]:
        raise ValueError(f"Type inválido: {data['Type']}. Esperado: X, R, IMR, P ou C.")
        
    if parsed_data["Goal"] in ["calibrar", "calibração"]:
        parsed_data["Goal"] = "calibrar"
    elif parsed_data["Goal"] in ["acompanhar", "acompanhamento"]:
        parsed_data["Goal"] = "acompanhar"
    else:
        raise ValueError(f"Goal inválido: {data['Goal']}. Esperado: Calibrar ou Acompanhar.")

    if parsed_data["Type"] in ["X", "R", "IMR"]:
        if "LSE" not in data or "LIE" not in data:
            raise ValueError("LSE e LIE são obrigatórios para cartas X, R e IMR.")
        parsed_data["LSE"] = float(data["LSE"])
        parsed_data["LIE"] = float(data["LIE"])
        if parsed_data["LSE"] <= parsed_data["LIE"]:
            raise ValueError("LSE deve ser estritamente maior que LIE.")

    raw_data = data["Data"]
    if not isinstance(raw_data, list) or len(raw_data) == 0:
        raise ValueError("Chave 'Data' deve ser uma lista não vazia.")

    parsed_data["Data"] = []
    
    # Processamento específico por tipo de carta
    if parsed_data["Type"] in ["X", "R"]:
        first_len = len(raw_data[0])
        if not (2 <= first_len <= 25):
            raise ValueError(f"Tamanho da amostra (n) deve estar entre 2 e 25.")
        for i, am in enumerate(raw_data):
            if not isinstance(am, list) or len(am) != first_len:
                raise ValueError(f"Amostra no índice {i} tem tamanho inconsistente.")
            parsed_data["Data"].append([float(v) for v in am])
            
    elif parsed_data["Type"] == "IMR":
        for i, am in enumerate(raw_data):
            if isinstance(am, list):
                if len(am) != 1: raise ValueError(f"IMR: amostra {i} deve ter tamanho 1.")
                parsed_data["Data"].append(float(am[0]))
            else:
                parsed_data["Data"].append(float(am))
                
    elif parsed_data["Type"] == "P":
        for i, am in enumerate(raw_data):
            if isinstance(am, dict):
                parsed_data["Data"].append({"n": int(am["n"]), "d": int(am["d"])})
            elif isinstance(am, list):
                parsed_data["Data"].append({"n": len(am), "d": sum(am)})
            else:
                raise ValueError(f"P: amostra {i} com formato inválido.")
                
    elif parsed_data["Type"] == "C":
        for i, am in enumerate(raw_data):
            if isinstance(am, list):
                if len(am) != 1: raise ValueError(f"C: amostra {i} deve ter tamanho 1.")
                parsed_data["Data"].append(int(am[0]))
            else:
                parsed_data["Data"].append(int(am))

    if parsed_data["Goal"] == "calibrar" and len(parsed_data["Data"]) < 20:
        print(f"AVISO: Calibração iniciada com menos de 20 amostras (m={len(parsed_data['Data'])}).")

    if parsed_data["Goal"] == "acompanhar":
        if parsed_data["Type"] in ["X", "R", "IMR"]:
            if "LSC" not in data or "LIC" not in data:
                raise ValueError("Em Acompanhar, as chaves 'LSC' e 'LIC' base são obrigatórias.")
            parsed_data["LSC_ref"] = float(data["LSC"])
            parsed_data["LIC_ref"] = float(data["LIC"])
            parsed_data["LC_ref"] = float(data.get("LC", (parsed_data["LSC_ref"] + parsed_data["LIC_ref"]) / 2.0))
            if "Sigma" in data:
                parsed_data["Sigma_ref"] = float(data["Sigma"])
            else:
                if parsed_data["Type"] in ["X", "R"]:
                    n_size = len(parsed_data["Data"][0])
                    parsed_data["Sigma_ref"] = math.sqrt(n_size) * (parsed_data["LSC_ref"] - parsed_data["LIC_ref"]) / 6.0
                elif parsed_data["Type"] == "IMR":
                    parsed_data["Sigma_ref"] = (parsed_data["LSC_ref"] - parsed_data["LIC_ref"]) / 6.0
        elif parsed_data["Type"] in ["P", "C"]:
            if "LC" not in data:
                raise ValueError("Em Acompanhar P/C, a chave 'LC' base é obrigatória.")
            parsed_data["LC_ref"] = float(data["LC"])
            if "LSC" in data: parsed_data["LSC_ref"] = float(data["LSC"])
            if "LIC" in data: parsed_data["LIC_ref"] = float(data["LIC"])

    return parsed_data