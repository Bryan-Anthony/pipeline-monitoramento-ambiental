import requests
from src.config import API_BASE_URL

class ApiClient:
    def __init__(self):
        self.base_url = API_BASE_URL
    
    def get_dados(self):
        url = f"{self.base_url}"

        
        response = requests.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        return response.json()