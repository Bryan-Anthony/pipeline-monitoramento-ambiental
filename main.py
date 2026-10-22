import argparse
import os

from src.analytics import statistics
from src.analytics.diagnostico import gerar_diagnostico
from src.config import OUTPUT_DIR
from src.database.repository import MonitoramentoRepository
from src.operadors.cadastro import CadastroOperador
from src.services.service import IngestionService
from src.utils.logger import Logger

logger = Logger.configurar()


def cadastrar_operadores():
    """Cadastra operadores em loop. Só termina quando o técnico escolher parar."""
    while True:
        logger.info("Iniciando cadastro do operador")
        CadastroOperador().cadastrar()

        while True:
            opcao = input("Cadastrar outro operador? (1 - Sim / 0 - Não): ").strip()
            if opcao in ("0", "1"):
                break
            print("Opção inválida. Digite 1 ou 0.")

        if opcao == "0":
            return


def main(cadastro=False):

    # --- 0. Cadastro do operador (somente com --cadastro) ---
    if cadastro:
        cadastrar_operadores()

    logger.info("Iniciando pipeline de monitoramento ambiental")

    # --- 1. Ingestão ---
    service = IngestionService()
    df = service.importar_dados()

    # --- 2. Persistência ---
    repository = MonitoramentoRepository()
    repository.inserir_dados(df, id_projeto=1)

    # --- 3. Busca dados do banco para análise ---
    df_leituras = repository.buscar_leituras()
    df_clientes = repository.buscar_clientes()

    # --- 4. Análise estatística sobre as leituras do banco ---
    estatisticas = statistics.calcular_estatisticas(df_leituras)
    outliers = statistics.resumir_outliers(df_leituras)

    # --- 5. Gráficos (salvos em reports/) ---
    statistics.limpar_reports()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    arquivos = []
    df_comparacao = None
    erro = None

    try:
        # 1 boxplot + 1 histograma para cada parâmetro
        arquivos += statistics.gerar_graficos_individuais(df_leituras)

        # Comparação com clientes (só parâmetros da tabela cliente)
        caminhos_comparacao, df_comparacao = statistics.gerar_grafico_comparacao(
            df_leituras, df_clientes
        )
        arquivos += caminhos_comparacao

        # Correlação entre todos os parâmetros
        arquivos.append(statistics.gerar_matriz_correlacao(df_leituras))
    except Exception as e:
        erro = str(e)
        logger.error(f"Erro ao gerar gráficos: {e}")

    # --- 6. Diagnóstico em .txt (sempre gerado) ---
    caminho = gerar_diagnostico(
        len(df_leituras), estatisticas, outliers, df_comparacao, arquivos, erro
    )

    print(f"{len(arquivos)} gráficos gerados. Diagnóstico salvo em: {caminho}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline de monitoramento ambiental")
    parser.add_argument(
        "--cadastro",
        action="store_true",
        help="cadastra operadores antes de executar o pipeline",
    )
    args = parser.parse_args()
    main(cadastro=args.cadastro)
