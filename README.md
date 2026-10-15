# 📈 Software de Controle Estatístico de Processos (CEP)

Projeto desenvolvido para a disciplina de **Tópicos Especiais em Eletrônica** da **Universidade de Brasília (UnB) – Faculdade do Gama (FGA)**.

Este software implementa uma ferramenta completa de Controle Estatístico de Processos (CEP / SPC) em **Python puro**. Ele lê dados de um arquivo JSON, realiza todos os cálculos estatísticos internamente, e gera relatórios em texto, dados consolidados em JSON e gráficos de cartas de controle.

> **Nota Técnica:** Seguindo os requisitos do projeto, este software **não** utiliza bibliotecas como `numpy`, `scipy` ou `pandas`. Todos os cálculos, constantes estatísticas e distribuições de probabilidade foram implementados do zero utilizando a biblioteca matemática padrão do Python. Apenas o `matplotlib` é utilizado para a geração dos gráficos.

---

## ✨ Funcionalidades

- **Cartas de Controle Suportadas:**
  - **Variáveis:** $\bar{X}$ e $R$ (Média e Amplitude), I-MR (Individuais e Amplitude Móvel).
  - **Atributos:** P (Fração não conforme), C (Número de defeitos).
- **Modos de Operação:**
  - **Fase I (Calibrar):** Estabelecimento de parâmetros base com revisão iterativa automática de limites (remoção de amostras que violam a Regra 1).
  - **Fase II (Acompanhar):** Monitoramento de novas amostras contra uma *baseline* fixa.
- **Análise de Capacidade:** Cálculo de RCP, RCPk, $k$ e estimativa de fração (ppm) fora de especificação para dados aproximadamente normais.
- **Análise de Deslocamento:**
  - Cálculo de Risco $\beta$, Probabilidade de Detecção ($Pd$) e $ARL_1$ para diferentes cenários de deslocamento ($\delta$).
  - Detecção precoce de deslocamento da média utilizando **Filtro de Kalman Escalar** e **Regras do Western Electric Handbook**.
- **Regras de Controle:** Implementação da Regra 1 (pontos fora dos limites de controle $\pm 3\sigma$) e testes de padrões adicionais nas zonas A, B e C.

---

## 🚀 Instalação e Execução

### Pré-requisitos
- **Python 3.10** ou superior.

### 1. Clonando e preparando o ambiente
Clone o repositório e crie um ambiente virtual (recomendado):
```bash
git clone https://github.com/pontesluis/Controle-Estat-stico-de-Processos.git
cd Controle-Estat-stico-de-Processos

# Criar ambiente virtual
python -m venv venv

# Ativar no Linux/Mac:
source venv/bin/activate
# Ativar no Windows:
venv\Scripts\activate

# Instalar a única dependência externa (matplotlib)
pip install -r requirements.txt
