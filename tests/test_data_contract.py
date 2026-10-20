from src.processing.data_contract import validar_data_contract
import pytest
from pydantic import ValidationError


# Testa se a função valida uma resposta da API com os campos obrigatórios
# preenchidos corretamente e retorna os dados originais sem alterações.
def test_validar_data_contract_com_dados_validos():
    dados = {
        "channel": {
            "id": 123,
            "name": "Canal de teste",
            "created_at": "2026-10-19",
            "updated_at": "2026-10-19"
        },
        "feeds": [
            {
                "entry_id": 1,
                "created_at": "2026-10-19T10:00:00",
                "field1": 25.5
            }
        ]
    }

    resultado = validar_data_contract(dados)

    assert resultado == dados


# testa se afunção rejeita dados com tipos imcompatíveis
# com o contrato definido pelo Pydantic.
def test_validar_data_contract_com_id_invalido():
    dados = {
        "channel": {
            "id": "abc",
            "name": "Canal de teste",
            "created_at": "2026-10-19",
            "updated_at": "2026-10-19"
        },
        "feeds": []
    }

    with pytest.raises(ValidationError):
        validar_data_contract(dados)



# Testa se a função rejeita uma resposta da API
# quando falta o campo obrigatório "name" do canal.
def test_validar_data_contract_sem_name():
    dados = {
        "channel": {
            "id": 123,
            "created_at": "2026-10-19",
            "updated_at": "2026-10-19"
        },
        "feeds": []
    }

    with pytest.raises(ValidationError):
        validar_data_contract(dados)


# Testa se a função rejeita um registro de feeds
# quando falta o campo obrigatório "entry_id".
def test_validar_data_contract_sem_entry_id():
    dados = {
        "channel": {
            "id": 123,
            "name": "Canal de teste",
            "created_at": "2026-10-19",
            "updated_at": "2026-10-19"
        },
        "feeds": [
            {
                "created_at": "2026-10-19T10:00:00",
                "field1": 25.5
            }
        ]
    }

    with pytest.raises(ValidationError):
        validar_data_contract(dados)
