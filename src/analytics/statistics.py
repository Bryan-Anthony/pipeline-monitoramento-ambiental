import os

import pandas as pd
import matplotlib.pyplot as plt


OUTPUT_DIR = "outputs"


def preparar_dados(df):
    """
    Prepara os dados para a análise.
    """
    if df.empty:
        raise ValueError("O DataFrame está vazio.")

    df = df.copy()

    if "data_hora" in df.columns:
        df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce")

    if "temperatura" in df.columns:
        df["temperatura"] = pd.to_numeric(df["temperatura"], errors="coerce")

    if "ph" in df.columns:
        df["ph"] = pd.to_numeric(df["ph"], errors="coerce")

    return df


def calcular_estatisticas(df):
    """
    Calcula estatísticas básicas de temperatura e pH.
    """
    df = preparar_dados(df)
    resultado = {}

    for coluna in ["temperatura", "ph"]:
        if coluna in df.columns:
            serie = df[coluna].dropna()

            if not serie.empty:
                q1 = serie.quantile(0.25)
                q3 = serie.quantile(0.75)
                iqr = q3 - q1

                resultado[coluna] = {
                    "media": round(serie.mean(), 2),
                    "mediana": round(serie.median(), 2),
                    "desvio_padrao": round(serie.std(), 2),
                    "q1": round(q1, 2),
                    "q3": round(q3, 2),
                    "iqr": round(iqr, 2),
                    "minimo": round(serie.min(), 2),
                    "maximo": round(serie.max(), 2),
                }

    return resultado


def identificar_outliers(df, coluna):
    """
    Identifica outliers usando a regra do IQR.
    """
    df = preparar_dados(df)

    if coluna not in df.columns:
        raise ValueError(f"A coluna '{coluna}' não existe no DataFrame.")

    serie = df[coluna].dropna()

    if serie.empty:
        return pd.DataFrame()

    q1 = serie.quantile(0.25)
    q3 = serie.quantile(0.75)
    iqr = q3 - q1

    limite_inferior = q1 - (1.5 * iqr)
    limite_superior = q3 + (1.5 * iqr)

    outliers = df[
        (df[coluna] < limite_inferior) |
        (df[coluna] > limite_superior)
    ].copy()

    return outliers


def resumir_outliers(df):
    """
    Resume a quantidade de outliers por coluna.
    """
    df = preparar_dados(df)
    resumo = {}

    for coluna in ["temperatura", "ph"]:
        if coluna in df.columns:
            outliers = identificar_outliers(df, coluna)
            resumo[coluna] = {
                "quantidade": len(outliers),
                "registros": outliers.to_dict(orient="records")
            }

    return resumo


def gerar_grafico_linha(df, coluna, nome_arquivo):
    """
    Gera gráfico de linha.
    """
    df = preparar_dados(df)

    if "data_hora" not in df.columns or coluna not in df.columns:
        raise ValueError("O DataFrame precisa ter 'data_hora' e a coluna escolhida.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dados = df[["data_hora", coluna]].dropna().sort_values("data_hora")
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)

    plt.figure(figsize=(10, 5))
    plt.plot(dados["data_hora"], dados[coluna], marker="o")
    plt.title(f"Evolução de {coluna}")
    plt.xlabel("Data/Hora")
    plt.ylabel(coluna.capitalize())
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()

    return caminho


def gerar_boxplot(df, coluna, nome_arquivo):
    """
    Gera boxplot.
    """
    df = preparar_dados(df)

    if coluna not in df.columns:
        raise ValueError(f"A coluna '{coluna}' não existe no DataFrame.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dados = df[coluna].dropna()
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)

    plt.figure(figsize=(8, 5))
    plt.boxplot(dados)
    plt.title(f"Boxplot de {coluna}")
    plt.ylabel(coluna.capitalize())
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()

    return caminho


def gerar_histograma(df, coluna, nome_arquivo):
    """
    Gera histograma.
    """
    df = preparar_dados(df)

    if coluna not in df.columns:
        raise ValueError(f"A coluna '{coluna}' não existe no DataFrame.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dados = df[coluna].dropna()
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)

    plt.figure(figsize=(8, 5))
    plt.hist(dados, bins=10, edgecolor="black")
    plt.title(f"Histograma de {coluna}")
    plt.xlabel(coluna.capitalize())
    plt.ylabel("Frequência")
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()

    return caminho
