from src.ingestion.api_client import ApiClient
from datetime import datetime
from src.processing.data_contract import validar_data_contract
from pydantic import ValidationError

import pandas as pd
from pathlib import Path

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

        # 2. Verificar o Data Contract
        try:
            validar_data_contract(dados)
            print("Data Contract validado com sucesso!")

        except ValidationError as erro:
            raise ValueError(
                f"A resposta da API não atende ao Data Contract: {erro}"
            ) from erro

        # 3. Verificar se a resposta possui channel
        if not dados or "channel" not in dados:
            raise ValueError(
                "Resposta da API não possui 'channel'."
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
        # Selecionar somente os registros únicos
        entry_ids_processados = set()

        for registro in feeds:

            entry_id = registro.get("entry_id")

            # Ignorar registros sem ID ou com ID já processado
            if entry_id is None or entry_id in entry_ids_processados:
                continue

            # Registrar o ID como processado
            entry_ids_processados.add(entry_id)

            item = {
                "entry_id_api": entry_id,
                "data_hora": self.converter_datetime(registro.get("created_at")),
                "temperatura": registro.get("field1"),
                "condutividade": registro.get("field3"),
                "temperatura_do_ar": registro.get("field5"),
                "turbidez": registro.get("field6"),
                "oxigenio_dissolvido": registro.get("field7"),
                "ph": registro.get("field8"),
            }

            dados_tratados.append(item)
      

        # 4. Criar DataFrame
        df = pd.DataFrame(dados_tratados)

        # 5. Salvar os dados brutos no CSV (Bronze)
        pasta_csv = Path.cwd() / "data" / "bronze"
        pasta_csv.mkdir(parents=True, exist_ok=True)

        arquivo_csv = pasta_csv / "leituras_api.csv"

        df.to_csv(
            arquivo_csv,
            index=False,
            encoding="utf-8"
        )

        print(f"CSV salvo em: {arquivo_csv}")
        print(f"Registros salvos: {len(df)}")

        # 6. Ler os dados novamente do CSV
        df = pd.read_csv(arquivo_csv, encoding="utf-8")

        # 7. Converter data/hora para o formato utilizado pelo projeto
        df["data_hora"] = df["data_hora"].apply(
            self.converter_datetime
        )

        # 8. Tratamento
        df = tratar_dados(df)

        # 9. Validação
        validar_data_contract(dados)
        validar_dados(df)

        # 10. Transformação
        df = transformar_dados(df)

        print("\nTipos DEPOIS da transformação:")
        print(df.dtypes)

        if not df.empty:
            print("\nPrimeira data:")
            print(df["data_hora"].iloc[0])

        return df