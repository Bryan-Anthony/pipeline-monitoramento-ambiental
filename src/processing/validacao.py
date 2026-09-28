from src.ingestion.api_client import ApiClient
import pandas as pd


def validar_dados(df):

    # Verifica se o DataFrame está vazio
    if df.empty:
        raise ValueError(
            "Nenhum dado foi encontrado."
        )

    # Verifica se existe a coluna data_hora
    if "data_hora" not in df.columns:
        raise ValueError(
            "A coluna 'data_hora' não existe."
        )

    # Verifica se existe pelo menos uma data válida
    if df["data_hora"].isnull().all():
        raise ValueError(
            "Nenhum dado válido de 'data_hora' foi encontrado."
        )

    return True