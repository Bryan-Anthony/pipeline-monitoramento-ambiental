from src.ingestion.service import IngestionService
from src.database.repository import MonitoramentoRepository

def main():
    service = IngestionService()

    df = service.importar_dados()

    print("\n Dados processados:")
    print(df)

    print("\n Tipos das colunas:")
    print(df.dtypes)

    # Enviar dados para o banco
    repository = MonitoramentoRepository()

    repository.inserir_dados(df,id_projeto = 1)


    #print(dados)

if __name__ == "__main__":
    main()  