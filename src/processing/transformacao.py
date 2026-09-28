import pandas as pd
from decimal import Decimal


def transformar_dados(df):

    # Converter data/hora para datetime
    #df["data_hora"] = pd.to_datetime(
    #    df["data_hora"],
    #    errors="coerce",
    #    utc=True
    #)

    # Converter temperatura para Decimal
    df["temperatura"] = pd.to_numeric(
        df["temperatura"],
        errors="coerce"
    ).apply(lambda x: Decimal(str(x)).quantize(Decimal("0.01")) if pd.notna(x) else None)

    # Converter pH para Decimal
    df["ph"] = pd.to_numeric(
        df["ph"],
        errors="coerce"
    ).apply(lambda x: Decimal(str(x)).quantize(Decimal("0.01")) if pd.notna(x) else None)

    return df