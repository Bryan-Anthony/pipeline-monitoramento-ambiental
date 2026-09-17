from src.ingestion.service import IngestionService

def main():
    service = IngestionService()

    dados = service.importar_dados()

    print(dados)

if __name__ == "__main__":
    main()  