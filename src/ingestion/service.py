from src.ingestion.api_client import ApiClient

class IngestionService:

    def __init__(self):
        self.api_client = ApiClient()

    def importar_dados(self):
        dados = self.api_client.get_dados()

        # Tratamento dos dados
        # Validação
        # Transformação


        return dados