import argparse
import sys
from pathlib import Path

from cep.io_json import read_and_validate_json
from cep.modes import run_calibration, run_monitoring
from cep.report import generate_text_report, save_json_results
from cep.plots import plot_xbar_r, plot_capability


def main():
    parser = argparse.ArgumentParser(
        description="Software de Controle Estatístico de Processos (CEP) - Cartas X̄ e R",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("dados", type=Path, help="Caminho para o arquivo JSON de entrada")
    parser.add_argument("--saida", type=Path, default=Path("saida"), help="Pasta de saída dos resultados")
    parser.add_argument("--sem-revisao", action="store_true", help="Desliga a revisão iterativa na Fase I")
    parser.add_argument("--kalman", action="store_true", help="Ativa o Filtro de Kalman (Etapa 3)")
    parser.add_argument("--q", type=float, default=0.05, help="Parâmetro 'q' do ruído no Filtro de Kalman")
    parser.add_argument("--deltas", type=float, nargs="+", default=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0], help="Deslocamentos δ (múltiplos de σ)")
    parser.add_argument("--sem-graficos", action="store_true", help="Não gerar imagens PNG (apenas JSON e Relatório)")

    args = parser.parse_args()

    try:
        dados_entrada = read_and_validate_json(args.dados)
    except Exception as e:
        print(f"ERRO DE VALIDAÇÃO: {e}")
        sys.exit(1)
    
    goal = dados_entrada["Goal"].lower()
    
    if goal in ("calibrar", "calibração"):
        resultados = run_calibration(
            dados_entrada, 
            allow_revision=not args.sem_revisao,
            deltas=args.deltas
        )
    elif goal in ("acompanhar", "acompanhamento"):
        resultados = run_monitoring(
            dados_entrada,
            deltas=args.deltas
        )
    else:
        print(f"ERRO: Objetivo '{goal}' não suportado.")
        sys.exit(1)
        
    # Preparar diretório de saída
    out_dir = args.saida / args.dados.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Relatório Texto
    report_text = generate_text_report(resultados)
    report_path = out_dir / "relatorio.txt"
    report_path.write_text(report_text, encoding="utf-8")
    print(report_text)
    
    # 2. JSON Resultados
    save_json_results(resultados, out_dir / "resultados.json")
    
    # 3. Gráficos
    if not args.sem_graficos:
        if resultados["type"] == "X":
            plot_xbar_r(resultados, out_dir / "carta_xbar_r.png")
            
            # Gráfico de Capacidade (se houver especificação LSE e LIE)
            if "LSE" in dados_entrada and "LIE" in dados_entrada:
                plot_capability(resultados, out_dir / "capacidade.png")

    print(f"\nResultados salvos com sucesso em: {out_dir.absolute()}")


if __name__ == "__main__":
    main()