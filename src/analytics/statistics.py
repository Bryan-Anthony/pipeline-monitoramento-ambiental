"""
Análise estatística das leituras de qualidade da água.

Gera:
1. Estatísticas e outliers por parâmetro
2. 1 boxplot e 1 histograma para cada parâmetro
3. Comparação com os clientes (só parâmetros que existem na tabela cliente)
4. Correlação entre todos os parâmetros
"""
import glob
import logging
import os

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # gera PNG sem abrir janela
import matplotlib.pyplot as plt

from src.config import OUTPUT_DIR

logger = logging.getLogger(__name__)

# nome no banco -> (nome na análise, rótulo, unidade)
PARAMETROS_INFO = {
    "temperaturaAgua": ("temperatura", "Temperatura da água", "°C"),
    "temperaturaAr": ("temperatura_ar", "Temperatura do ar", "°C"),
    "ph": ("ph", "pH", ""),
    "oxigenioDissolvido": ("oxigenio_dissolvido", "Oxigênio dissolvido", "mg/L"),
    "condutividadeEletrica": ("condutividade", "Condutividade elétrica", "µS/cm"),
    "turbidezAgua": ("turbidez", "Turbidez", "NTU"),
}

MAPA_COLUNAS = {"dataHora": "data_hora"}
MAPA_COLUNAS.update({k: v[0] for k, v in PARAMETROS_INFO.items()})

PARAMETROS = [v[0] for v in PARAMETROS_INFO.values()]
ROTULOS = {v[0]: f"{v[1]} ({v[2]})" if v[2] else v[1] for v in PARAMETROS_INFO.values()}


def rotulo(coluna):
    """Ex: 'turbidez' -> 'Turbidez (NTU)'."""
    return ROTULOS.get(coluna, coluna)


# ------------------------------------------------------------------ dados

def limpar_reports():
    """Apaga os arquivos da pasta reports/ antes de gerar novos."""
    for arquivo in glob.glob(os.path.join(OUTPUT_DIR, "*")):
        if os.path.isfile(arquivo):
            os.remove(arquivo)


def preparar_dados(df):
    """Renomeia as colunas do banco e converte os parâmetros para número."""
    if df.empty:
        raise ValueError("O DataFrame está vazio.")

    df = df.rename(columns={a: n for a, n in MAPA_COLUNAS.items()
                            if a in df.columns and n not in df.columns})
    if "data_hora" in df.columns:
        df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce")

    for coluna in PARAMETROS:
        if coluna in df.columns:
            df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    return df


def _com_dados(df):
    """Parâmetros que existem no DataFrame e têm ao menos 1 valor."""
    return [c for c in PARAMETROS if c in df.columns and df[c].notna().any()]


# ------------------------------------------------------------ estatísticas

def calcular_estatisticas(df):
    """Média, mediana, desvio, quartis, IQR, mínimo e máximo por parâmetro."""
    df = preparar_dados(df)
    resultado = {}
    for coluna in _com_dados(df):
        s = df[coluna].dropna()
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        resultado[coluna] = {
            "media": round(s.mean(), 2),
            "mediana": round(s.median(), 2),
            "desvio_padrao": round(s.std(), 2),
            "q1": round(q1, 2),
            "q3": round(q3, 2),
            "iqr": round(q3 - q1, 2),
            "minimo": round(s.min(), 2),
            "maximo": round(s.max(), 2),
            "assimetria": round(s.skew(), 2),
            "coef_variacao": round(s.std() / s.mean() * 100, 2) if s.mean() else None,
        }
    return resultado


def calcular_conformidade(df_leituras, df_clientes, tolerancia=0.10):
    """
    % de leituras dentro do valor de referência de cada cliente (± tolerância).
    Só entram os parâmetros que existem na tabela cliente.
    """
    df_leituras = preparar_dados(df_leituras)
    df_clientes = preparar_dados(df_clientes)

    parametros = [c for c in _com_dados(df_clientes) if c in _com_dados(df_leituras)]
    linhas = []
    for _, cliente in df_clientes.iterrows():
        for c in parametros:
            ref = cliente[c]
            if pd.isna(ref):
                continue
            leituras = df_leituras[c].dropna()
            dentro = (leituras - ref).abs() <= abs(ref) * tolerancia
            linhas.append({
                "cliente": cliente["nomeCliente"],
                "parametro": rotulo(c),
                "referencia": round(ref, 2),
                "media_monitorada": round(leituras.mean(), 2),
                "pct_conforme": round(dentro.mean() * 100, 1),
            })
    return pd.DataFrame(linhas)


def identificar_outliers(df, coluna):
    """Linhas fora de [Q1 - 1.5*IQR, Q3 + 1.5*IQR]."""
    df = preparar_dados(df)
    if coluna not in df.columns:
        raise ValueError(f"A coluna '{coluna}' não existe no DataFrame.")

    q1, q3 = df[coluna].quantile(0.25), df[coluna].quantile(0.75)
    iqr = q3 - q1
    return df[(df[coluna] < q1 - 1.5 * iqr) | (df[coluna] > q3 + 1.5 * iqr)]


def resumir_outliers(df):
    """Quantidade e registros (data/hora e valor) de outliers por parâmetro."""
    df = preparar_dados(df)
    resumo = {}
    for c in _com_dados(df):
        outliers = identificar_outliers(df, c)
        colunas = [col for col in ("data_hora", c) if col in outliers.columns]
        resumo[c] = {
            "quantidade": len(outliers),
            "registros": outliers[colunas].to_dict(orient="records"),
        }
    return resumo


# ----------------------------------------------------------------- gráficos

def _salvar(nome_arquivo):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)
    plt.tight_layout()
    plt.savefig(caminho, dpi=120)
    plt.close()
    return caminho


def gerar_boxplot(df, coluna, nome_arquivo):
    """
    1 boxplot do parâmetro.
    Caixa = 50% central das leituras (Q1 a Q3); linha laranja = mediana;
    triângulo verde = média; bolinhas fora das hastes = outliers.
    """
    dados = preparar_dados(df)[coluna].dropna()
    q1, q3 = dados.quantile(0.25), dados.quantile(0.75)

    plt.figure(figsize=(7, 6))
    plt.boxplot(dados, showmeans=True, widths=0.4,
                medianprops={"color": "orange", "linewidth": 2},
                meanprops={"marker": "^", "markerfacecolor": "green", "markeredgecolor": "green"},
                flierprops={"marker": "o", "markerfacecolor": "red", "markeredgecolor": "red"})
    plt.title(f"Boxplot - {rotulo(coluna)}\n{len(dados)} leituras")
    plt.ylabel(rotulo(coluna))
    plt.xticks([])
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    # legenda explicando cada elemento do gráfico
    plt.plot([], [], color="orange", linewidth=2, label=f"Mediana: {dados.median():.2f}")
    plt.plot([], [], "^", color="green", label=f"Média: {dados.mean():.2f}")
    plt.plot([], [], "s", color="white", markeredgecolor="black",
             label=f"Caixa (Q1 a Q3): {q1:.2f} a {q3:.2f}")
    plt.plot([], [], "_", color="black", label=f"Mín / Máx: {dados.min():.2f} / {dados.max():.2f}")
    plt.plot([], [], "o", color="red", label="Outlier (valor atípico)")
    plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
    return _salvar(nome_arquivo)


def gerar_histograma(df, coluna, nome_arquivo):
    """
    1 histograma do parâmetro.
    Cada barra = faixa de valores; altura = quantas leituras caíram nela.
    """
    dados = preparar_dados(df)[coluna].dropna()

    plt.figure(figsize=(8, 5))
    plt.hist(dados, bins=10, edgecolor="black", color="steelblue", alpha=0.8,
             label="Nº de leituras na faixa")
    plt.axvline(dados.mean(), color="red", linestyle="--", label=f"Média: {dados.mean():.2f}")
    plt.axvline(dados.median(), color="green", label=f"Mediana: {dados.median():.2f}")
    plt.title(f"Histograma - {rotulo(coluna)}\n{len(dados)} leituras")
    plt.xlabel(f"{rotulo(coluna)}  (cada barra = uma faixa de valores)")
    plt.ylabel("Frequência (nº de leituras)")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend(loc="best", fontsize=8)
    return _salvar(nome_arquivo)


def gerar_graficos_individuais(df):
    """1 boxplot + 1 histograma por parâmetro. Retorna os caminhos."""
    df = preparar_dados(df)
    caminhos = []
    for coluna in _com_dados(df):
        caminhos.append(gerar_boxplot(df, coluna, f"boxplot_{coluna}.png"))
        caminhos.append(gerar_histograma(df, coluna, f"histograma_{coluna}.png"))
    return caminhos


def gerar_grafico_comparacao(df_leituras, df_clientes):
    """
    Compara a média da água monitorada com a água de cada cliente.
    Só entram os parâmetros que existem na tabela cliente.
    Retorna (caminhos, tabela_de_comparacao).
    """
    df_leituras = preparar_dados(df_leituras)
    df_clientes = preparar_dados(df_clientes)

    if "nomeCliente" not in df_clientes.columns:
        raise ValueError("O DataFrame de clientes precisa ter 'nomeCliente'.")

    parametros = [c for c in _com_dados(df_clientes) if c in _com_dados(df_leituras)]

    monitorada = {"nome": "Monitorada (API)"}
    for c in parametros:
        monitorada[c] = round(df_leituras[c].mean(), 2)

    clientes = df_clientes.rename(columns={"nomeCliente": "nome"})[["nome"] + parametros]
    tabela = pd.concat([pd.DataFrame([monitorada]), clientes], ignore_index=True)
    logger.info("Comparação:\n%s", tabela.to_string(index=False))

    cores = ["steelblue"] + ["lightgray"] * (len(tabela) - 1)
    caminhos = []
    for c in parametros:
        plt.figure(figsize=(8, 5))
        barras = plt.bar(tabela["nome"], tabela[c].fillna(0), color=cores, edgecolor="black")
        for barra, valor in zip(barras, tabela[c]):
            texto = "s/ dado" if pd.isna(valor) else f"{valor:.2f}"
            plt.text(barra.get_x() + barra.get_width() / 2, barra.get_height(), texto,
                     ha="center", va="bottom", fontsize=9)
        plt.title(f"Comparação - {rotulo(c)}\nMédia da água monitorada vs. águas dos clientes")
        plt.xlabel("Fonte da água")
        plt.ylabel(rotulo(c))
        plt.xticks(rotation=30, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        plt.bar([], [], color="steelblue", edgecolor="black", label="Água monitorada (média das leituras)")
        plt.bar([], [], color="lightgray", edgecolor="black", label="Água do cliente (valor cadastrado)")
        plt.legend(loc="best", fontsize=8)
        caminhos.append(_salvar(f"comparacao_{c}.png"))

    return caminhos, tabela


def gerar_matriz_correlacao(df, nome_arquivo="correlacao_parametros.png"):
    """
    Mapa de calor da correlação entre todos os parâmetros.
    Vermelho (+1): sobem juntos | Azul (-1): um sobe e o outro desce | Branco (0): sem relação.
    """
    df = preparar_dados(df)
    colunas = _com_dados(df)
    if len(colunas) < 2:
        raise ValueError("São necessárias ao menos 2 colunas para a correlação.")

    corr = df[colunas].corr()
    nomes = [rotulo(c).replace(" (", "\n(") for c in colunas]

    plt.figure(figsize=(10, 8))
    plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(label="Correlação (-1 inversa | 0 nenhuma | +1 direta)")
    plt.xticks(range(len(colunas)), nomes, rotation=45, ha="right", fontsize=8)
    plt.yticks(range(len(colunas)), nomes, fontsize=8)
    for i in range(len(colunas)):
        for j in range(len(colunas)):
            if pd.notna(corr.iloc[i, j]):
                plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
    plt.title("Correlação entre os parâmetros\nQuanto mais forte a cor, mais um parâmetro acompanha o outro")
    plt.xlabel("Parâmetros medidos")
    plt.ylabel("Parâmetros medidos")
    plt.figtext(0.5, 0.01, "Leitura: |valor| acima de 0,7 = relação forte | entre 0,3 e 0,7 = moderada | abaixo de 0,3 = fraca",
                ha="center", fontsize=8)
    plt.tight_layout(rect=(0, 0.03, 1, 1))
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.savefig(caminho, dpi=120)
    plt.close()
    return caminho
