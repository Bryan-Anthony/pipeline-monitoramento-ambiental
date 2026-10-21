import requests
from src.config import API_BASE_URL
from src.utils.logger import Logger

class ApiClient:

    logger = Logger.configurar()

    def __init__(self):
        self.base_url = API_BASE_URL
    
    def get_dados(self):
        url = f"{self.base_url}"

        try:

            self.logger.info("Iniciando requisição para a API: %s", url)
            response = requests.get(
                url,
                timeout=30
            )

            response.raise_for_status()

            return response.json()

        except ConnectionError:
            self.logger.error(
                "Não foi possível estabelecer conexão com a API."
            )
            raise

        except Exception as erro:
            self.logger.error(
                "Erro na requisição para a API: %s",
                erro
            )
            raise

        except Exception:
            self.logger.exception(
                "Erro inesperado ao obter dados da API."
            )
            raise