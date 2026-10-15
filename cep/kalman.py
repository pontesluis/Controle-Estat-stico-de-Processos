from typing import List

def run_kalman_filter(measurements: List[float], initial_estimate: float, 
                      measurement_variance: float, process_variance: float) -> List[float]:
    """
    Filtro de Kalman 1D.
    - measurement_variance (R): Variância do ruído da medição (ex: sigma_processo^2 / n)
    - process_variance (Q): Variância do ruído do processo (fator de ajuste 'q')
    """
    estimates = []
    x = initial_estimate  # Estado inicial (x_k)
    p = 1.0               # Covariância do erro inicial (P_k)
    
    for z in measurements:
        # 1. Previsão (Predict)
        x_pred = x
        p_pred = p + process_variance
        
        # 2. Atualização (Update)
        k = p_pred / (p_pred + measurement_variance) if (p_pred + measurement_variance) > 0 else 0
        x = x_pred + k * (z - x_pred)
        p = (1 - k) * p_pred
        
        estimates.append(x)
        
    return estimates