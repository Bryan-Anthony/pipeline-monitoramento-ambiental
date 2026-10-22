from src.processing.tratamento import tratar_dados #import da função 
import pandas as pd

def test_tratar_dados_converte_para_numerico():
    df = pd.DataFrame({
         "entry_id_api": [1],
        "data_hora": ["2026-09-28 10:00:00"],
        "temperatura": ["25.5"],
        "condutividade": ["120"],
        "temperatura_do_ar": ["28.0"],
        "turbidez": ["10.5"],
        "oxigenio_dissolvido": ["8.2"],
        "ph": ["7.2"]
    })

    resultado = tratar_dados(df)

    # Verifica se a temperatura foi convertida para um número
    assert isinstance(resultado["temperatura"].iloc[0], (int, float))

    # Verifica se o pH foi convertido para um número
    assert isinstance(resultado["ph"].iloc[0], (int, float))

# testa valores invalidos
def test_tratar_dados_valor_invalido():
    df = pd.DataFrame({
        "entry_id_api": [1],
        "data_hora": ["2026-09-28 10:00:00"],
        "temperatura": ["abc"],
        "condutividade": ["120"],
        "temperatura_do_ar": ["28.0"],
        "turbidez": ["10.5"],
        "oxigenio_dissolvido": ["8.2"],
        "ph": ["invalido"]
    })
    #passa os dados pela função 
    resultado = tratar_dados(df)

    # Verifica se um valor de temperatura inválido foi convertido para NaN
    assert pd.isna(resultado["temperatura"].iloc[0])

    # Verifica se um valor de pH inválido foi convertido para NaN
    assert pd.isna(resultado["ph"].iloc[0])

# Testa se transforma -9999 em NaN
def test_tratar_dados_valor_menos_9999():
    df = pd.DataFrame({
        "entry_id_api": [1],
        "data_hora": ["2026-09-28 10:00:00"],
        "temperatura": [-9999],
        "condutividade": [120],
        "temperatura_do_ar": [28.0],
        "turbidez": [10.5],
        "oxigenio_dissolvido": [8.2],
        "ph": [-9999]
    })

    resultado = tratar_dados(df)

    # Verifica se -9999 foi convertido para valor ausente na temperatura (NaN)
    assert pd.isna(resultado["temperatura"].iloc[0])

    # Verifica se -9999 foi convertido para valor ausente no pH (NaN)
    assert pd.isna(resultado["ph"].iloc[0])

#testa se ela consegue tratar varias linhas de uma vez 
def test_tratar_dados_varias_linhas():
    df = pd.DataFrame({
           "entry_id_api": [1, 2, 3],
        "data_hora": [
            "2026-09-28 10:00:00",
            "2026-09-28 11:00:00",
            "2026-09-28 12:00:00"
        ],
        "temperatura": ["25.5", "30.2", "abc"],
        "condutividade": ["120", "130", "140"],
        "temperatura_do_ar": ["28.0", "29.0", "30.0"],
        "turbidez": ["10.5", "11.5", "12.5"],
        "oxigenio_dissolvido": ["8.2", "7.9", "8.0"],
        "ph": ["7.2", "6.8", "invalido"]
    })

    resultado = tratar_dados(df)

    # Verifica se a primeira linha os valores foram corretamente convertidos para números 
    assert resultado["temperatura"].iloc[0] == 25.5
    assert resultado["ph"].iloc[0] == 7.2

    # Verifica se a segunda linha os valores foram corretamente convertidos para números 
    assert resultado["temperatura"].iloc[1] == 30.2
    assert resultado["ph"].iloc[1] == 6.8

    # Verifica a terceira linha, que contém valores inválidos ( Transforma em NaN)
    assert pd.isna(resultado["temperatura"].iloc[2])
    assert pd.isna(resultado["ph"].iloc[2])