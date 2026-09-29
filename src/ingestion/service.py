from src.ingestion.api_client import ApiClient
from datetime import datetime

import pandas as pd

from src.processing.tratamento import tratar_dados
from src.processing.validacao import validar_dados
from src.processing.transformacao import transformar_dados


class IngestionService:

    def __init__(self):
        self.api_client = ApiClient()
    
    # Converter string para datetime
    def converter_datetime(self, valor):
        if not valor:
            return None

        data = datetime.fromisoformat(
            valor.replace("Z", "+00:00")
        )
    # Remove o timezone para compatibilidade com SQL Server DATETIME
        return data.replace(tzinfo=None)

    def importar_dados(self):

        # 1. Buscar dados da API
        dados = self.api_client.get_dados()

         # 2. Verificar se a resposta possui channel - cabeçalho da api
        if not dados or "channel" not in dados:
            raise ValueError(
                "Resposta da API não possui 'channel - cabeçalho da api'."
            )

        cabecalho_api = dados["channel"]

        cabecalho = {
            "CodigoProjeto": cabecalho_api.get("id"),
            "nomeProjeto": cabecalho_api.get("name"),
            "Descricao": cabecalho_api.get("description"),
            "Latitude": cabecalho_api.get("latitude"),
            "Longitude": cabecalho_api.get("longitude"),
            "DataInicialColeta": self.converter_datetime(cabecalho_api.get("created_at")),
            "DataFinalColeta": self.converter_datetime(cabecalho_api.get("updated_at")),
        }
        print(cabecalho)
        

        # 2.1 Verificar se a resposta possui feeds
        if not dados or "feeds" not in dados:
            raise ValueError(
                "Resposta da API não possui 'feeds'."
            )

        feeds = dados["feeds"]

        # 3. Selecionar somente os campos necessários
        dados_tratados = []

        for registro in feeds:

            item = {
               
                "data_hora": self.converter_datetime(registro.get("created_at")),
                "temperatura": registro.get("field1"),
                "ph": registro.get("field8"),
            }

            dados_tratados.append(item)
      

        # 4. Criar DataFrame
        df = pd.DataFrame(dados_tratados)

        # 5. Tratamento
        df = tratar_dados(df)

        # 6. Validação
        validar_dados(df)

        # 7. Transformação
        df = transformar_dados(df)

        print("\nTipos DEPOIS da transformação:")
        print(df.dtypes)

        print("\nPrimeira data:")
        print(df["data_hora"].iloc[0])

        return df