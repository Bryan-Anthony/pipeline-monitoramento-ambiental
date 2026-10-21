from src.ingestion.api_client import ApiClient
import pandas as pd
from src.utils.logger import Logger

logger = Logger.configurar()


def validar_dados(df):

    logger.info("Inicio da validação das colunas da api.")
    logger.info("Verifica se o DataFrame está vazio.")
    # Verifica se o DataFrame está vazio
    if df.empty:
        raise ValueError(
            "Nenhum dado foi encontrado."
        )

    logger.info("Verifica se existe a coluna data_hora.")
    # Verifica se existe a coluna data_hora
    if "data_hora" not in df.columns:
        raise ValueError(
            "A coluna 'data_hora' não existe."
        )

    logger.info("Verifica se existe pelo menos uma data válida.")
    # Verifica se existe pelo menos uma data válida
    if df["data_hora"].isnull().all():
        raise ValueError(
            "Nenhum dado válido de 'data_hora' foi encontrado."
        )

    logger.info("Valores validados com sucesso.")
    return True