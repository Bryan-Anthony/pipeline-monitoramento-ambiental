import os
import glob

import pandas as pd
import matplotlib.pyplot as plt

# OUTPUT_DIR vem de config.py para manter uma única fonte de verdade
from src.config import OUTPUT_DIR


def limpar_reports():
    """
    Remove todos os arquivos da pasta reports/ antes de gerar novos.
    Evita acúmulo de arquivos de execuções anteriores.
    A pasta em si é mantida; apenas o conteúdo é apagado.
    """
    if not os.path.exists(OUTPUT_DIR):
        # Pasta ainda não existe, nada a limpar
        return

    # Lista todos os arquivos dentro de reports/ (não entra em subpastas)
    arquivos = glob.glob(os.path.join(OUTPUT_DIR, "*"))

    for arquivo in arquivos:
        if os.path.isfile(arquivo):
            os.remove(arquivo)

    print(f" Pasta '{OUTPUT_DIR}/' limpa. {len(arquivos)} arquivo(s) removido(s).")


def preparar_dados(df):
    """
    Prepara o DataFrame para análise:
    - Converte 'data_hora' para datetime
    - Converte 'temperatura' e 'ph' para numérico
    - Retorna uma cópia do DataFrame original sem alterar o original
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
    Calcula estatísticas básicas de temperatura e pH:
    média, mediana, desvio padrão, quartis (Q1, Q3), IQR, mínimo e máximo.
    Retorna um dicionário com os resultados por coluna.
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
    Identifica outliers em uma coluna usando a regra do IQR:
    valores abaixo de Q1 - 1.5*IQR ou acima de Q3 + 1.5*IQR são considerados outliers.
    Retorna um DataFrame com apenas as linhas que são outliers.
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

    # Limites para detecção de outliers pelo método IQR
    limite_inferior = q1 - (1.5 * iqr)
    limite_superior = q3 + (1.5 * iqr)

    outliers = df[
        (df[coluna] < limite_inferior) |
        (df[coluna] > limite_superior)
    ].copy()

    return outliers


def resumir_outliers(df):
    """
    Resume a quantidade de outliers encontrados em 'temperatura' e 'ph'.
    Retorna um dicionário com a contagem e os registros de cada coluna.
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
    Gera e salva um gráfico de linha mostrando a evolução de uma coluna ao longo do tempo.
    O arquivo é salvo em OUTPUT_DIR com o nome informado.
    Retorna o caminho completo do arquivo gerado.
    """
    df = preparar_dados(df)

    if "data_hora" not in df.columns or coluna not in df.columns:
        raise ValueError("O DataFrame precisa ter 'data_hora' e a coluna escolhida.")

    # Cria a pasta de saída se ela ainda não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dados = df[["data_hora", coluna]].dropna().sort_values("data_hora")
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)

    plt.figure(figsize=(10, 5))
    plt.plot(dados["data_hora"], dados[coluna], marker="o")
    plt.title(f"Evolução de {coluna}")
    plt.xlabel("Data/Hora")
    plt.ylabel(coluna.capitalize())
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()

    return caminho


def gerar_grafico_comparacao(df_leituras, df_clientes,
                             nome_arquivo_ph="comparacao_ph.png",
                             nome_arquivo_temp="comparacao_temperatura.png"):
    """
    Gera dois gráficos comparativos separados:
    - comparacao_ph.png: comparação de pH entre água monitorada e engarrafadas
    - comparacao_temperatura.png: comparação de temperatura entre as mesmas fontes

    A água monitorada é representada pela média das leituras do banco.
    Salva os dois arquivos em OUTPUT_DIR.
    Também imprime a tabela comparativa no terminal.
    Retorna o caminho do gráfico de pH e o DataFrame comparativo.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Calcula a média dos dados da API para representar a água monitorada
    media_leituras = {
        "nome": "Monitorada (API)",
        "ph": round(pd.to_numeric(df_leituras["ph"], errors="coerce").mean(), 2),
        "temperatura": round(pd.to_numeric(df_leituras["temperatura"], errors="coerce").mean(), 2),
    }

    # Garante que ph e temperatura dos clientes são numéricos
    df_clientes = df_clientes.copy()
    df_clientes["ph"] = pd.to_numeric(df_clientes["ph"], errors="coerce")
    df_clientes["temperatura"] = pd.to_numeric(df_clientes["temperatura"], errors="coerce")

    # Monta um DataFrame unificado com a água monitorada + águas engarrafadas
    df_monitorada = pd.DataFrame([media_leituras])
    df_comparacao = pd.concat([df_monitorada, df_clientes], ignore_index=True)

    # Exibe a tabela comparativa diretamente no terminal
    print("\n Comparação: Água Monitorada vs. Águas Engarrafadas")
    print(df_comparacao.to_string(index=False))

    nomes = df_comparacao["nome"]
    valores_ph = df_comparacao["ph"]
    valores_temp = df_comparacao["temperatura"]

    # Define cores: destaca a água monitorada em azul e as demais em cinza
    cores = ["steelblue" if n == "Monitorada (API)" else "lightgray" for n in nomes]

    # --- Gráfico 1: Comparação de pH (arquivo separado) ---
    plt.figure(figsize=(8, 5))
    plt.bar(nomes, valores_ph, color=cores, edgecolor="black")
    plt.title("Comparação de pH")
    plt.xlabel("Fonte")
    plt.ylabel("pH")
    plt.xticks(rotation=30)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    caminho_ph = os.path.join(OUTPUT_DIR, nome_arquivo_ph)
    plt.savefig(caminho_ph)
    plt.close()

    # --- Gráfico 2: Comparação de Temperatura (arquivo separado) ---
    plt.figure(figsize=(8, 5))
    plt.bar(nomes, valores_temp, color=cores, edgecolor="black")
    plt.title("Comparação de Temperatura")
    plt.xlabel("Fonte")
    plt.ylabel("Temperatura (°C)")
    plt.xticks(rotation=30)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    caminho_temp = os.path.join(OUTPUT_DIR, nome_arquivo_temp)
    plt.savefig(caminho_temp)
    plt.close()

    return caminho_ph, df_comparacao


def gerar_boxplot(df, coluna, nome_arquivo):
    """
    Gera e salva um boxplot de uma coluna.
    Útil para visualizar a distribuição dos dados e identificar outliers visualmente.
    Retorna o caminho completo do arquivo gerado.
    """
    df = preparar_dados(df)

    if coluna not in df.columns:
        raise ValueError(f"A coluna '{coluna}' não existe no DataFrame.")

    # Cria a pasta de saída se ela ainda não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dados = df[coluna].dropna()
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)

    # Calcula os valores de referência para anotação
    mediana = dados.median()
    media   = dados.mean()
    q1      = dados.quantile(0.25)
    q3      = dados.quantile(0.75)
    iqr     = q3 - q1
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr

    plt.figure(figsize=(8, 6))
    plt.boxplot(dados)
    plt.title(f"Boxplot de {coluna}")
    plt.ylabel(coluna.capitalize())
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    # Linhas horizontais de referência
    plt.axhline(media,   color="red",    linestyle="--", linewidth=1, alpha=0.7)
    plt.axhline(lim_inf, color="orange", linestyle=":",  linewidth=1, alpha=0.7)
    plt.axhline(lim_sup, color="orange", linestyle=":",  linewidth=1, alpha=0.7)

    # Rótulos anotados à direita de cada linha
    x_pos = 1.35
    plt.text(x_pos, mediana, f"Mediana: {mediana:.2f}", va="center", fontsize=8, color="black")
    plt.text(x_pos, media,   f"Média:   {media:.2f}",   va="center", fontsize=8, color="red")
    plt.text(x_pos, q1,      f"Q1: {q1:.2f}",           va="center", fontsize=8, color="steelblue")
    plt.text(x_pos, q3,      f"Q3: {q3:.2f}",           va="center", fontsize=8, color="steelblue")
    plt.text(x_pos, lim_inf, f"Lim inf: {lim_inf:.2f}", va="center", fontsize=8, color="orange")
    plt.text(x_pos, lim_sup, f"Lim sup: {lim_sup:.2f}", va="center", fontsize=8, color="orange")

    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()

    return caminho


def gerar_histograma(df, coluna, nome_arquivo):
    """
    Gera e salva um histograma de uma coluna.
    Mostra a frequência de cada faixa de valores, útil para entender a distribuição.
    Retorna o caminho completo do arquivo gerado.
    """
    df = preparar_dados(df)

    if coluna not in df.columns:
        raise ValueError(f"A coluna '{coluna}' não existe no DataFrame.")

    # Cria a pasta de saída se ela ainda não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    dados = df[coluna].dropna()
    caminho = os.path.join(OUTPUT_DIR, nome_arquivo)

    plt.figure(figsize=(8, 5))
    plt.hist(dados, bins=10, edgecolor="black")
    plt.title(f"Histograma de {coluna}")
    plt.xlabel(coluna.capitalize())
    plt.ylabel("Frequência")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()

    return caminho
