import os
from datetime import datetime

from src.ingestion.service import IngestionService
from src.database.repository import MonitoramentoRepository
from src.config import OUTPUT_DIR
from src.analytics import statistics


def main():
    # --- 1. Ingestão ---
    service = IngestionService()
    df = service.importar_dados()

    print("\n Dados processados:")
    print(df)

    print("\n Tipos das colunas:")
    print(df.dtypes)

    # --- 2. Persistência ---
    repository = MonitoramentoRepository()
    repository.inserir_dados(df, id_projeto=1)

    # --- 3. Busca dados do banco para análise ---
    # Leituras da API já persistidas no banco
    df_leituras = repository.buscar_leituras()

    # Águas engarrafadas cadastradas como referência de comparação
    df_clientes = repository.buscar_clientes()

    # --- 4. Análise estatística sobre as leituras do banco ---
    estatisticas = statistics.calcular_estatisticas(df_leituras)
    outliers = statistics.resumir_outliers(df_leituras)

    # --- 5. Gráficos individuais das leituras (salvos em reports/) ---
    # Limpa arquivos antigos antes de gerar os novos
    statistics.limpar_reports()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Histogramas: distribuição de frequência de temperatura e pH
    caminho_hist_temp = statistics.gerar_histograma(df_leituras, "temperatura", "histograma_temperatura.png")
    caminho_hist_ph   = statistics.gerar_histograma(df_leituras, "ph",          "histograma_ph.png")

    # Boxplots: distribuição e outliers de temperatura e pH
    caminho_box_temp = statistics.gerar_boxplot(df_leituras, "temperatura", "boxplot_temperatura.png")
    caminho_box_ph   = statistics.gerar_boxplot(df_leituras, "ph",          "boxplot_ph.png")

    print(f"\n Gráficos individuais gerados:")
    print(f"  - {caminho_hist_temp}")
    print(f"  - {caminho_hist_ph}")
    print(f"  - {caminho_box_temp}")
    print(f"  - {caminho_box_ph}")

    # --- 6. Gráficos comparativos: água monitorada vs. águas engarrafadas ---
    # Gera um PNG separado para pH e outro para temperatura
    caminho_comp_ph, df_comparacao = statistics.gerar_grafico_comparacao(
        df_leituras, df_clientes,
        nome_arquivo_ph="comparacao_ph.png",
        nome_arquivo_temp="comparacao_temperatura.png"
    )

    print(f"\n Gráficos comparativos gerados:")
    print(f"  - {caminho_comp_ph}")
    print(f"  - {os.path.join(OUTPUT_DIR, 'comparacao_temperatura.png')}")

    # --- 7. Diagnóstico em .txt ---
    caminho_diagnostico = os.path.join(OUTPUT_DIR, "diagnostico.txt")
    gerado_em = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    separador = "=" * 60
    linha     = "-" * 60

    with open(caminho_diagnostico, "w", encoding="utf-8") as f:

        # -------------------------------------------------- cabeçalho
        f.write(f"{separador}\n")
        f.write(f"  RELATORIO DE MONITORAMENTO AMBIENTAL\n")
        f.write(f"  Pipeline de Qualidade da Água\n")
        f.write(f"{separador}\n")
        f.write(f"  Gerado em : {gerado_em}\n")
        f.write(f"  Fonte     : ThingSpeak API (canal 2412377)\n")
        f.write(f"  Registros : {len(df_leituras)} leituras carregadas do banco\n")
        f.write(f"{separador}\n\n")

        # ----------------------------------------- estatísticas por coluna
        f.write(f"{linha}\n")
        f.write(f"  1. ESTATISTICAS DAS LEITURAS\n")
        f.write(f"{linha}\n")

        for coluna, v in estatisticas.items():
            unidade = "graus C" if coluna == "temperatura" else "escala 0-14"
            f.write(f"\n  [{coluna.upper()}]  ({unidade})\n")
            f.write(f"  {'Metrica':<20} {'Valor':>10}\n")
            f.write(f"  {'-'*32}\n")
            f.write(f"  {'Media':<20} {v['media']:>10}\n")
            f.write(f"  {'Mediana':<20} {v['mediana']:>10}\n")
            f.write(f"  {'Desvio Padrao':<20} {v['desvio_padrao']:>10}\n")
            f.write(f"  {'Minimo':<20} {v['minimo']:>10}\n")
            f.write(f"  {'Q1 (25%)':<20} {v['q1']:>10}\n")
            f.write(f"  {'Q3 (75%)':<20} {v['q3']:>10}\n")
            f.write(f"  {'IQR':<20} {v['iqr']:>10}\n")
            f.write(f"  {'Maximo':<20} {v['maximo']:>10}\n")

        f.write(f"\n{linha}\n")
        f.write(f"  2. DETECCAO DE OUTLIERS  (metodo IQR)\n")
        f.write(f"{linha}\n")

        for coluna, dados in outliers.items():
            qtd = dados['quantidade']
            status = "ATENCAO - outliers detectados" if qtd > 0 else "OK - nenhum outlier"
            f.write(f"\n  [{coluna.upper()}]\n")
            f.write(f"  Quantidade encontrada : {qtd}\n")
            f.write(f"  Status                : {status}\n")

            # Se houver outliers, lista os registros
            if qtd > 0:
                f.write(f"\n  {'#':<5} {'Data/Hora':<22} {'Valor':>10}\n")
                f.write(f"  {'-'*40}\n")
                for i, reg in enumerate(dados['registros'], start=1):
                    data_hora = reg.get('data_hora', 'N/A')
                    valor     = reg.get(coluna, 'N/A')
                    f.write(f"  {i:<5} {str(data_hora):<22} {str(valor):>10}\n")

        f.write(f"\n{linha}\n")
        f.write(f"  3. COMPARACAO: AGUA MONITORADA vs. AGUAS ENGARRAFADAS\n")
        f.write(f"{linha}\n")
        f.write(f"  {'Fonte':<25} {'pH':>8} {'Temp (C)':>12}\n")
        f.write(f"  {'-'*47}\n")
        for _, row in df_comparacao.iterrows():
            f.write(f"  {str(row['nome']):<25} {str(row['ph']):>8} {str(row['temperatura']):>12}\n")

        f.write(f"\n{linha}\n")
        f.write(f"  4. ARQUIVOS GERADOS EM reports/\n")
        f.write(f"{linha}\n")
        arquivos_gerados = [
            ("Histograma Temperatura" , caminho_hist_temp),
            ("Histograma pH"          , caminho_hist_ph),
            ("Boxplot Temperatura"    , caminho_box_temp),
            ("Boxplot pH"             , caminho_box_ph),
            ("Comparacao pH"          , caminho_comp_ph),
            ("Comparacao Temperatura" , os.path.join(OUTPUT_DIR, "comparacao_temperatura.png")),
            ("Este relatorio"         , caminho_diagnostico),
        ]
        for nome_arq, caminho_arq in arquivos_gerados:
            f.write(f"\n  {nome_arq:<25} {os.path.basename(caminho_arq)}")

        # -------------------------------------------------- rodape
        f.write(f"\n\n{separador}\n")
        f.write(f"  FIM DO RELATORIO\n")
        f.write(f"{separador}\n")

    print(f"\n Diagnóstico salvo em: {caminho_diagnostico}")


if __name__ == "__main__":
    main()