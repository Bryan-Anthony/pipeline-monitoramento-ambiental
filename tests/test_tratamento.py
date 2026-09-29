from src.processing.tratamento import tratar_dados #import da função 
import pandas as pd

def test_tratar_dados_converte_para_numerico():
    df = pd.DataFrame({
        "temperatura": ["25.5"],
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
        "temperatura": ["abc"],
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
        "temperatura": [-9999],
        "ph": [-9999]
    })

    resultado = tratar_dados(df)

    # Verifica se -9999 foi convertido para valor ausente na temperatura
    assert pd.isna(resultado["temperatura"].iloc[0])

    # Verifica se -9999 foi convertido para valor ausente no pH
    assert pd.isna(resultado["ph"].iloc[0])

#testa se ela consegue tratar varias linhas de uma vez 
def test_tratar_dados_varias_linhas():
    df = pd.DataFrame({
        "temperatura": ["25.5", "30.2", "abc"],
        "ph": ["7.2", "6.8", "invalido"]
    })

    resultado = tratar_dados(df)

    # Verifica a primeira linha
    assert resultado["temperatura"].iloc[0] == 25.5
    assert resultado["ph"].iloc[0] == 7.2

    # Verifica a segunda linha
    assert resultado["temperatura"].iloc[1] == 30.2
    assert resultado["ph"].iloc[1] == 6.8

    # Verifica a terceira linha, que contém valores inválidos
    assert pd.isna(resultado["temperatura"].iloc[2])
    assert pd.isna(resultado["ph"].iloc[2])