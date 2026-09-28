from src.ingestion.service import IngestionService
#from src.database.repository import MonitoramentoRepository

def main():
    service = IngestionService()

    dados = service.importar_dados()

    print("\n Dados processados:")
    print(dados)

    print("\n Tipos das colunas:")
    print(dados.dtypes)

    # Enviar dados para o banco
    #repository = MonitoramentoRepository()

    #repository.inserir_dados(dados)

    #print(dados)

if __name__ == "__main__":
    main()  