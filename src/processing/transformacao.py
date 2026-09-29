import pandas as pd
from decimal import Decimal


def transformar_dados(df):

    #Converter data/hora para datetime
    df["data_hora"] = pd.to_datetime(
       df["data_hora"],
       errors="coerce",
       utc=True
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

    return df