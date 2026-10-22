import pandas as pd

from src.utils.logger import Logger

logger = Logger.configurar()

def tratar_dados(df):
    
    logger.info("Padroniza os campos retornados pela API ThingSpeak.")
    logger.info("Iniciando o tratamento dos dados.")

    mapeamento = {
        "entry_id": "entry_id_api",
        "created_at": "data_hora",
        "field1": "temperatura",
        "field3": "condutividade",
        "field5": "temperaturaDoAr",
        "field6": "turbidez",
        "field7": "oxigenioDissolvido",
        "field8": "ph",
    }

    logger.info("Mapeamento de colunas definidas.")
    # Renomeia somente as colunas que realmente existem.
    df = df.rename(
        columns={
            origem: destino
            for origem, destino in mapeamento.items()
            if origem in df.columns
        }
    ).copy()

    
    # Confere se as colunas necessárias estão presentes.
    colunas_obrigatorias = [
        "entry_id_api",
        "data_hora",
        "temperatura",
        "condutividade",
        "temperatura_do_ar",
        "turbidez",
        "oxigenio_dissolvido",
        "ph"
    ]

    faltantes = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"Colunas ausentes nos dados da API: {faltantes}. "
            f"Colunas recebidas: {list(df.columns)}"
        )

    logger.info("Verificando se todas as colunas obrigatórias estão presentes.")
    logger.info(f"Colunas obrigatórias: {colunas_obrigatorias}")
    logger.info(f"Colunas faltantes: {faltantes}")
    logger.info("Convertendo as medições para números.")

    df["data_hora"] = pd.to_datetime(
            df["data_hora"],
            errors="coerce",
            utc=True
        )
    
        # Remover timezone para compatibilidade com SQL Server.
    df["data_hora"] = df["data_hora"].dt.tz_localize(None)
    
    logger.info("Conversão da coluna data_hora concluída.")

    # Converte as medições para números.
    colunas_numericas = [
        "entry_id_api",
        "temperatura",
        "condutividade",
        "temperatura_do_ar",
        "turbidez",
        "oxigenio_dissolvido",
        "ph"
    ]

    for coluna in colunas_numericas:

        # Converte os valores para números
        # Valores inválidos viram NaN
        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

        logger.info(f"Convertendo a coluna '{coluna}' para números.")
        # -9999 representa valor inválido/ausente
        df.loc[df[coluna] == -9999, coluna] = None

        logger.info(f"Conversão da coluna '{coluna}' para números concluída.")
        logger.info("Conversão da coluna 'data_hora' para datetime concluída.")

    return df
