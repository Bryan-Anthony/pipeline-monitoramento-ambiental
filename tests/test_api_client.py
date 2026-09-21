# Dado uma resposta de channel com field1 : temperature e feeds com field1: -9999.00  quando get dados então deve exibir "Temperature" e "-9999,00".
# dado resposta com sucesso da api quando get dados então responda corretamente  

from unittest.mock import patch, Mock

from src.ingestion.api_client import ApiClient

def test_apiClient():
    # Dado uma resposta da API com temperatura 
    resposta_falsa = Mock() 
    resposta_falsa.json.return_value = {
       
    "channel": {
        "id": 2412377,
        "name": "WQMStation1",
        "description": "Testing connectivity and usability for remote Water Quality Monitoring Station",
        "latitude": "37.424946",
        "longitude": "-79.191969",
        "field1": "Temperature",
        "field2": "Depth",
        "field3": "Conductivity",
        "field4": "Battery",
        "field5": "Air Temperature",
        "field6": "Turbidity",
        "field7": "Dissolved Oxygen",
        "field8": "pH",
        "created_at": "2024-01-25T14:16:26Z",
        "updated_at": "2024-03-18T13:07:02Z",
        "last_entry_id": 505
    },
    "feeds": [
        {
            "created_at": "2024-07-01T13:10:34Z",
            "entry_id": 504,
            "field1": "-9999.00",
            "field2": "-9999.0",
            "field3": "-9999.0",
            "field4": "4.852",
            "field5": "23.25",
            "field6": "-9999.0",
            "field7": "-9999.00",
            "field8": "-9999.000"
        }
    ]
    }
    

    # Quando o get_dados() for chamado
    with patch("src.ingestion.api_client.requests.get", return_value=resposta_falsa):
        client = ApiClient()
        dados = client.get_dados() # aqui testa a função get_dados
        print(dados)
     
    
