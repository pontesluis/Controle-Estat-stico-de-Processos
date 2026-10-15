import json
from pathlib import Path
from typing import Dict, Any

def read_and_validate_json(filepath: Path) -> Dict[str, Any]:
    """
    Lê o JSON, ignora chaves desconhecidas e valida obrigatoriedades.
    Erros disparam ValueError para controle seguro e limpo de fluxo.
    """
    if not filepath.exists():
        raise ValueError(f"Arquivo não encontrado: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro de sintaxe no JSON: {e}")

    # Normalizar chaves obrigatórias e essenciais
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
        "Data": data["Data"],
        "Deltas": data.get("Deltas", [0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    }
    
    # Tratamento de grafias do tipo de carta
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

    # Validar limites de especificação se for contínuo (X, R, IMR)
    if parsed_data["Type"] in ["X", "R", "IMR"]:
        if "LSE" not in data or "LIE" not in data:
            raise ValueError("LSE e LIE são obrigatórios para cartas X, R e IMR.")
        parsed_data["LSE"] = float(data["LSE"])
        parsed_data["LIE"] = float(data["LIE"])
        if parsed_data["LSE"] <= parsed_data["LIE"]:
            raise ValueError("LSE deve ser estritamente maior que LIE.")

    # Validar formato Data
    if not isinstance(parsed_data["Data"], list) or len(parsed_data["Data"]) == 0:
        raise ValueError("Chave 'Data' deve ser uma lista não vazia.")

    # Validação estrutural de Data (somente X, R na Etapa 1)
    if parsed_data["Type"] in ["X", "R"]:
        first_len = len(parsed_data["Data"][0])
        if not (2 <= first_len <= 25):
            raise ValueError(f"Tamanho da amostra (n) deve estar entre 2 e 25. Encontrado: {first_len}")
        for i, amostra in enumerate(parsed_data["Data"]):
            if not isinstance(amostra, list) or len(amostra) != first_len:
                raise ValueError(f"Amostra no índice {i} tem tamanho inconsistente. Esperado: {first_len}")
            if any(val is None or not isinstance(val, (int, float)) for val in amostra):
                raise ValueError(f"Amostra no índice {i} contém valores numéricos inválidos ou nulos/NaN.")
                
        if parsed_data["Goal"] == "calibrar" and len(parsed_data["Data"]) < 20:
            print(f"AVISO: Calibração iniciada com menos de 20 amostras (m={len(parsed_data['Data'])}).")

    # Acompanhar: checar limites base
    if parsed_data["Goal"] == "acompanhar":
        if "LSC" not in data or "LIC" not in data:
            raise ValueError("Em Acompanhar, as chaves 'LSC' e 'LIC' base são obrigatórias no JSON.")
        parsed_data["LSC_ref"] = float(data["LSC"])
        parsed_data["LIC_ref"] = float(data["LIC"])
        parsed_data["LC_ref"] = float(data.get("LC", (parsed_data["LSC_ref"] + parsed_data["LIC_ref"]) / 2.0))
        
        # Sigma é inferido se não for passado
        if "Sigma" in data:
            parsed_data["Sigma_ref"] = float(data["Sigma"])
        else:
            if parsed_data["Type"] in ["X", "R"]:
                n_size = len(parsed_data["Data"][0])
                parsed_data["Sigma_ref"] = math.sqrt(n_size) * (parsed_data["LSC_ref"] - parsed_data["LIC_ref"]) / 6.0
                
    return parsed_data