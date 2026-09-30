from src.processing.transformacao import transformar_dados  # import da função

import pandas as pd


def test_transformar_data_hora():
    df = pd.DataFrame({
        "data_hora": [
            "2026-09-28T10:00:00Z",
            "data-invalida"
        ],
        "temperatura": ["25.5", "18.123"],
        "ph": ["7.2", "6.789"]
    })

    resultado = transformar_dados(df)

    # Verifica se a data válida foi convertida para datetime (2026-09-28 10:00:00+00:00)
    assert pd.api.types.is_datetime64_any_dtype(resultado["data_hora"])

    # Verifica se a data inválida foi convertida para NaT (Not a Time)
    assert pd.isna(resultado["data_hora"].iloc[1])


# Testa a transformação da temperatura
def test_transformar_temperatura():
    df = pd.DataFrame({
        "data_hora": ["2026-09-28 10:00:00"],
        "temperatura": ["18.123"],
        "ph": ["7.2"]
    })

    resultado = transformar_dados(df)

    # Verifica se a temperatura foi convertida para número e arredondada para duas casas decimais
    assert resultado["temperatura"].iloc[0] == 18.12

# Testa a transformação do pH
def test_transformar_ph():
    df = pd.DataFrame({
        "data_hora": ["2026-09-28 10:00:00"],
        "temperatura": ["25.5"],
        "ph": ["6.789"]
    })

    resultado = transformar_dados(df)

    # Verifica se o valor  foi convertido para número e arredondado para duas casas decimais
    assert resultado["ph"].iloc[0] == 6.79

#testa se por acaso o valor vim null
def test_transformar_valores_nulos():
    df = pd.DataFrame({
        "data_hora": ["2026-09-28 10:00:00"],
        "temperatura": [None],
        "ph": [None]
    })

    resultado = transformar_dados(df)

    # Verifica se o valor nulo de temperatura continua como valor ausente (NaN)
    assert pd.isna(resultado["temperatura"].iloc[0])

    # Verifica se o valor nulo de pH continua como valor ausente (NaN)
    assert pd.isna(resultado["ph"].iloc[0])

#testa quando o valor vem invalido
def test_transformar_valores_invalidos():
    df = pd.DataFrame({
        "data_hora": ["2026-09-28 10:00:00"],
        "temperatura": ["abc"],
        "ph": ["invalido"]
    })

    resultado = transformar_dados(df)

    # Verifica se o valor de temperatura inválido foi convertido para NaN
    assert pd.isna(resultado["temperatura"].iloc[0])

    # Verifica se o valor de pH inválido foi convertido para NaN
    assert pd.isna(resultado["ph"].iloc[0])
def test_transformar_todos_os_registros():
    df = pd.DataFrame({
        "data_hora": [
            "2026-09-28 10:00:00",
            "2026-09-28 11:00:00",
            "2026-09-28 12:00:00"
        ],
        "temperatura": ["25.5", "18.123", "30"],
        "ph": ["7.2", "6.789", "8"]
    })

    resultado = transformar_dados(df)

    # Verifica se todas as temperaturas foram convertidas e arredondadas corretamente
    assert resultado["temperatura"].tolist() == [25.5, 18.12, 30.0]

    # Verifica se todos os valores de pH foram convertidos e arredondados corretamente
    assert resultado["ph"].tolist() == [7.2, 6.79, 8.0]