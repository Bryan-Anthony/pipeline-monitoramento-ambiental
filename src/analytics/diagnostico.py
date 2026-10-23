"""Gera o diagnostico em .txt a partir das estatisticas calculadas."""
import os
from datetime import datetime

from src.analytics.statistics import rotulo
from src.config import OUTPUT_DIR


def gerar_diagnostico(total, estatisticas, outliers, df_comparacao, arquivos, erro=None):
    """Salva reports/diagnostico.txt e retorna o caminho do arquivo."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    caminho = os.path.join(OUTPUT_DIR, "diagnostico.txt")

    linhas = [
        "DIAGNOSTICO - MONITORAMENTO AMBIENTAL",
        f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}",
        f"Total de leituras analisadas: {total}",
        "",
        "ESTATISTICAS POR PARAMETRO",
    ]

    for coluna, e in estatisticas.items():
        linhas.append(f"\n{rotulo(coluna)}")
        linhas.append(f"  Media: {e['media']} | Mediana: {e['mediana']} | Desvio: {e['desvio_padrao']}")
        linhas.append(f"  Minimo: {e['minimo']} | Maximo: {e['maximo']} | IQR: {e['iqr']}")
        linhas.append(f"  Outliers: {outliers.get(coluna, {}).get('quantidade', 0)}")

    if df_comparacao is not None:
        linhas += ["", "COMPARACAO COM OS CLIENTES", df_comparacao.to_string(index=False)]

    if erro:
        linhas += ["", f"ERRO AO GERAR GRAFICOS: {erro}"]

    linhas += ["", f"GRAFICOS GERADOS ({len(arquivos)})"]
    linhas += [f"  - {os.path.basename(a)}" for a in arquivos]

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    return caminho
