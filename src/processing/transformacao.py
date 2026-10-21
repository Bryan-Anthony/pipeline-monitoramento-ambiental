import pandas as pd
from decimal import Decimal
from src.utils.logger import Logger

logger = Logger.configurar()


def transformar_dados(df):

    logger.info("Inicio do transformação das colunas da api.")

    # Converter data/hora sem interpretar números como milissegundos
    df["data_hora"] = pd.to_datetime(
        df["data_hora"],
        errors="coerce"
    )

    # Remover timezone, caso exista
    if df["data_hora"].dt.tz is not None:
        df["data_hora"] = (
            df["data_hora"].dt.tz_localize(None)
        )

    # Converter temperatura para Decimal
    df["temperatura"] = pd.to_numeric(
        df["temperatura"],
        errors="coerce"
    ).round(2)

    # Converter pH para Decimal
    df["ph"] = pd.to_numeric(
        df["ph"],
        errors="coerce"
    ).round(2)

    logger.info("Finalização do tranformação das colunas da api.")

    return df