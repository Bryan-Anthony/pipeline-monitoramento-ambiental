from src.processing.transformacao import transformar_dados  # import da função

import pandas as pd
from decimal import Decimal


# Testa a transformação da temperatura
def test_transformar_temperatura():
    df = pd.DataFrame({
        "temperatura": ["25.5", "18.123", "30"],
        "ph": ["7.2", "6.789", "8"]
    })

    resultado = transformar_dados(df)

    # Verifica se o primeiro valor de temperatura foi convertido para Decimal
    assert isinstance(resultado["temperatura"].iloc[0], Decimal)

    # Verifica se a temperatura foi convertida e formatada com duas casas decimais
    assert resultado["temperatura"].iloc[0] == Decimal("25.50")


# Testa a transformação do pH
def test_transformar_ph():
    df = pd.DataFrame({
        "temperatura": ["25.5", "18.123", "30"],
        "ph": ["7.2", "6.789", "8"]
    })

    resultado = transformar_dados(df)

    # Verifica se o primeiro valor de pH foi convertido para Decimal
    assert isinstance(resultado["ph"].iloc[0], Decimal)

    # Verifica se o pH foi convertido e formatado com duas casas decimais
    assert resultado["ph"].iloc[0] == Decimal("7.20")

#Para testar valores invalidos 
def test_transformar_valores_invalidos():
    df = pd.DataFrame({  # valores nulos 
        "temperatura": ["abc"],
        "ph": ["invalido"]
    })
    resultado = transformar_dados(df)

    # Verifica se um valor de temperatura inválido foi convertido para None
    assert resultado["temperatura"].iloc[0] is None

    # Verifica se um valor de pH inválido foi convertido para None
    assert resultado["ph"].iloc[0] is None

#testa quando o valor ja vem nulo
def test_transformar_valores_nulos():
    df = pd.DataFrame({ # Valores nulos
        "temperatura": [None],
        "ph": [None]
    }) 
    #passa os valores pela função
    resultado = transformar_dados(df)

     # Verifica se um valor nulo de temperatura continua sendo None
    assert resultado["temperatura"].iloc[0] is None

    # Verifica se um valor nulo de pH continua sendo None
    assert resultado["ph"].iloc[0] is None

def test_transformar_todos_os_registros():
    df = pd.DataFrame({
        "temperatura": ["25.5", "18.123", "30"],
        "ph": ["7.2", "6.789", "8"]
    })

    resultado = transformar_dados(df)

    # Verifica se todos os valores de temperatura foram convertidos para Decimal
    assert all(isinstance(valor, Decimal) for valor in resultado["temperatura"])

    # Verifica se todos os valores de pH foram convertidos para Decimal
    assert all(isinstance(valor, Decimal) for valor in resultado["ph"])