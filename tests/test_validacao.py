from src.processing.validacao import validar_dados
import pandas as pd
import pytest

#Testa se do DataFrame estiver vazio
def test_validar_dados_dataframe_vazio():
    df = pd.DataFrame()

    # Diz ao pytest que espero que aconteça um erro
    # do tipo ValueError dentro deste bloco
    with pytest.raises(ValueError):

        # Chamamos a função que estamos testando.
        # Como o DataFrame está vazio, esperamos que ela
        # lance um ValueError.
        validar_dados(df)

# Testa quando não existe a coluna data_hora
def test_validar_dados_sem_coluna_data_hora():
    df = pd.DataFrame({
        "temperatura": [25.5],
        "ph": [7.2]
    })

    # Esperado um ValueError porque a coluna data_hora não existe
    with pytest.raises(ValueError):
        validar_dados(df)

#testa quando os dados de data_hora estão vazios
def test_validar_dados_data_hora_invalida():
    df = pd.DataFrame({
        "data_hora": [None, None],
        "temperatura": [25.5, 26.0],
        "ph": [7.2, 7.0]
    })

    # Esperado um ValueError porque todas as datas estão vazias
    with pytest.raises(ValueError):
        validar_dados(df)


# aqui testa se todos os dados estiverem corretos
def test_validar_dados_validos():
    df = pd.DataFrame({
        "data_hora": ["2026-09-28 10:00:00"],
        "temperatura": [25.5],
        "ph": [7.2]
    })

    resultado = validar_dados(df)

    # Verifica se a validação foi concluída com sucesso
    assert resultado is True