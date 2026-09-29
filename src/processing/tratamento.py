from src.ingestion.api_client import ApiClient
import pandas as pd


def tratar_dados(df):

    # Colunas que devem ser numéricas
    colunas_numericas = [
        "temperatura",
        "ph"
    ]

    for coluna in colunas_numericas:

        # Converte os valores para números
        # Valores inválidos viram NaN
        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

        # -9999 representa valor inválido/ausente
        df.loc[df[coluna] == -9999, coluna] = None

        # Garantir que a data seja datetime
        df["data_hora"] = pd.to_datetime(
            df["data_hora"],
            errors="coerce"
        )

    return df