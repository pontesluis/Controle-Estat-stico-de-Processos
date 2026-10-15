import argparse
import sys
from pathlib import Path
import matplotlib.pyplot as plt

from cep.io_json import read_and_validate_json
from cep.modes import run_calibration, run_monitoring
from cep.report import generate_text_report, save_json_results
from cep.plots import plot_xbar_r, plot_imr, plot_p, plot_c, plot_capability

def main():
    parser = argparse.ArgumentParser(
        description="Software de Controle Estatístico de Processos (CEP)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("dados", type=Path, help="Caminho para o arquivo JSON de entrada")
    parser.add_argument("--saida", type=Path, default=Path("saida"), help="Pasta de saída")
    parser.add_argument("--sem-revisao", action="store_true", help="Desliga a revisão iterativa")
    parser.add_argument("--kalman", action="store_true", help="Ativa o Filtro de Kalman")
    parser.add_argument("--q", type=float, default=0.05, help="Parâmetro 'q' do Kalman")
    parser.add_argument("--deltas", type=float, nargs="+", default=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0], help="Deltas em σ")
    parser.add_argument("--sem-graficos", action="store_true", help="Apenas JSON e Relatório")

    args = parser.parse_args()

    try:
        dados_entrada = read_and_validate_json(args.dados)
    except Exception as e:
        print(f"ERRO DE VALIDAÇÃO: {e}")
        sys.exit(1)
    
    goal = dados_entrada["Goal"]
    if goal == "calibrar": resultados = run_calibration(dados_entrada, not args.sem_revisao, args.deltas)
    else: resultados = run_monitoring(dados_entrada, args.deltas)
        
    out_dir = args.saida / args.dados.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    
    report_text = generate_text_report(resultados)
    (out_dir / "relatorio.txt").write_text(report_text, encoding="utf-8")
    print(report_text)
    
    save_json_results(resultados, out_dir / "resultados.json")
    
    if not args.sem_graficos:
        if resultados["type"] == "X":
            plot_xbar_r(resultados, out_dir / "carta_xbar_r.png")
            img_c = plt.imread(out_dir / "carta_xbar_r.png")
        elif resultados["type"] == "IMR":
            plot_imr(resultados, out_dir / "carta_imr.png")
            img_c = plt.imread(out_dir / "carta_imr.png")
        elif resultados["type"] == "P":
            plot_p(resultados, out_dir / "carta_p.png")
            img_c = plt.imread(out_dir / "carta_p.png")
        elif resultados["type"] == "C":
            plot_c(resultados, out_dir / "carta_c.png")
            img_c = plt.imread(out_dir / "carta_c.png")

        fig1 = plt.figure("Carta de Controle")
        plt.imshow(img_c)
        plt.axis('off')
        
        if resultados["type"] in ["X", "IMR"] and "LSE" in dados_entrada:
            plot_capability(resultados, out_dir / "capacidade.png")
            img_cap = plt.imread(out_dir / "capacidade.png")
            fig2 = plt.figure("Análise de Capacidade")
            plt.imshow(img_cap)
            plt.axis('off')

        plt.show() 

    print(f"\nResultados salvos com sucesso em: {out_dir.absolute()}")

if __name__ == "__main__":
    main()