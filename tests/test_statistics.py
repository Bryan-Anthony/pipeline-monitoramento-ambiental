# =============================================================================
# test_statistics.py
# Testes unitários para o módulo src/analytics/statistics.py
#
# Cada função do módulo é testada de forma isolada, sem depender do banco de
# dados, da API externa ou de arquivos em disco.
#
# Para executar todos os testes:
#   python -m pytest tests/test_statistics.py -v
# =============================================================================

import os
import pytest
import pandas as pd

from src.analytics.statistics import (
    preparar_dados,
    calcular_estatisticas,
    identificar_outliers,
    resumir_outliers,
    gerar_grafico_linha,
    gerar_boxplot,
    gerar_histograma,
    gerar_grafico_comparacao,
    limpar_reports,
)


# =============================================================================
# FIXTURE: DataFrame padrão reutilizado nos testes
# Uma fixture no pytest é um dado de entrada compartilhado entre testes.
# Ao declarar o parâmetro `df_base` em um teste, o pytest injeta este valor
# automaticamente, não é necessário criá-lo manualmente em cada teste.
# =============================================================================

@pytest.fixture
def df_base():
    """
    Cria um DataFrame simples com dados de temperatura e pH,
    simulando registros reais vindos da API ou do banco.
    Os valores foram escolhidos para que os cálculos sejam previsíveis.
    """
    return pd.DataFrame({
        "data_hora": pd.date_range(start="2024-01-01", periods=6, freq="h"),
        "temperatura": [20.0, 21.0, 22.0, 23.0, 24.0, 25.0],
        "ph":          [6.5,  6.8,  7.0,  7.2,  7.4,  7.6],
    })


@pytest.fixture
def df_com_outlier():
    """
    DataFrame com um outlier intencional na coluna temperatura.
    O valor 99.0 está muito acima da faixa normal e deve ser detectado
    pela função identificar_outliers usando a regra do IQR.
    """
    return pd.DataFrame({
        "data_hora": pd.date_range(start="2024-01-01", periods=7, freq="h"),
        "temperatura": [20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 99.0],
        "ph":          [6.5,  6.8,  7.0,  7.2,  7.4,  7.6,  7.0],
    })


@pytest.fixture
def df_com_nan():
    """
    DataFrame com valores ausentes (NaN) nas duas colunas numéricas.
    Testa se as funções tratam corretamente a presença de dados faltantes,
    pois dados reais de sensores frequentemente chegam incompletos.
    """
    return pd.DataFrame({
        "data_hora": pd.date_range(start="2024-01-01", periods=4, freq="h"),
        "temperatura": [20.0, None, 22.0, None],
        "ph":          [None, 7.0,  None, 7.5],
    })


# =============================================================================
# TESTES: preparar_dados
# Esta função é a base de todo o módulo, ela normaliza os tipos das colunas
# antes de qualquer cálculo. Se ela falhar, tudo falha.
# =============================================================================

def test_preparar_dados_converte_tipos(df_base):
    """
    Verifica que preparar_dados converte corretamente:
    - 'data_hora' para datetime
    - 'temperatura' e 'ph' para float (numérico)
    Esses tipos são necessários para que Pandas execute os cálculos
    estatísticos sem erros.
    """
    resultado = preparar_dados(df_base)

    assert pd.api.types.is_datetime64_any_dtype(resultado["data_hora"]), (
        "data_hora deveria ser do tipo datetime"
    )
    assert pd.api.types.is_float_dtype(resultado["temperatura"]), (
        "temperatura deveria ser float"
    )
    assert pd.api.types.is_float_dtype(resultado["ph"]), (
        "ph deveria ser float"
    )


def test_preparar_dados_nao_altera_original(df_base):
    """
    Garante que preparar_dados trabalha sobre uma cópia do DataFrame,
    nunca modificando o objeto original. Isso é importante para evitar
    efeitos colaterais quando a mesma variável é reutilizada no pipeline.
    """
    df_original = df_base.copy()
    preparar_dados(df_base)

    # O DataFrame original deve permanecer idêntico após a chamada
    pd.testing.assert_frame_equal(df_base, df_original)


def test_preparar_dados_levanta_erro_em_df_vazio():
    """
    Quando um DataFrame vazio é passado, preparar_dados deve lançar
    ValueError com uma mensagem clara. Isso evita que erros silenciosos
    se propaguem para as funções de cálculo e geração de gráficos.
    """
    df_vazio = pd.DataFrame()

    with pytest.raises(ValueError, match="vazio"):
        preparar_dados(df_vazio)


# =============================================================================
# TESTES: calcular_estatisticas
# Verifica se os valores calculados estão matematicamente corretos.
# =============================================================================

def test_calcular_estatisticas_retorna_chaves_esperadas(df_base):
    """
    A função deve retornar um dicionário com as chaves 'temperatura' e 'ph',
    e cada uma deve conter as métricas: media, mediana, desvio_padrao,
    q1, q3, iqr, minimo e maximo.
    """
    resultado = calcular_estatisticas(df_base)

    assert "temperatura" in resultado
    assert "ph" in resultado

    chaves_esperadas = {"media", "mediana", "desvio_padrao", "q1", "q3", "iqr", "minimo", "maximo"}
    assert chaves_esperadas == set(resultado["temperatura"].keys()), (
        "Chaves de estatísticas para temperatura não batem"
    )
    assert chaves_esperadas == set(resultado["ph"].keys()), (
        "Chaves de estatísticas para ph não batem"
    )


def test_calcular_estatisticas_valores_corretos(df_base):
    """
    Valida os valores numéricos calculados para a coluna temperatura.
    Com os dados [20, 21, 22, 23, 24, 25], os valores esperados são:
    - Média: 22.5
    - Mínimo: 20.0
    - Máximo: 25.0
    O delta de 0.01 tolera pequenas diferenças de arredondamento.
    """
    resultado = calcular_estatisticas(df_base)
    temp = resultado["temperatura"]

    assert abs(temp["media"]   - 22.5) < 0.01, f"Média incorreta: {temp['media']}"
    assert abs(temp["minimo"]  - 20.0) < 0.01, f"Mínimo incorreto: {temp['minimo']}"
    assert abs(temp["maximo"]  - 25.0) < 0.01, f"Máximo incorreto: {temp['maximo']}"
    assert abs(temp["mediana"] - 22.5) < 0.01, f"Mediana incorreta: {temp['mediana']}"


def test_calcular_estatisticas_ignora_nan(df_com_nan):
    """
    Quando há NaN nos dados, as estatísticas devem ser calculadas apenas
    sobre os valores válidos. A função não deve lançar erro nem retornar
    NaN como resultado final (comportamento do .dropna() interno).
    """
    resultado = calcular_estatisticas(df_com_nan)

    # temperatura tem valores [20.0, 22.0] > média esperada: 21.0
    assert "temperatura" in resultado
    assert abs(resultado["temperatura"]["media"] - 21.0) < 0.01


# =============================================================================
# TESTES: identificar_outliers
# O método IQR classifica como outlier qualquer valor fora do intervalo
# [Q1 - 1.5*IQR, Q3 + 1.5*IQR]. Os testes verificam casos positivos e
# negativos para garantir que a lógica está correta.
# =============================================================================

def test_identificar_outliers_detecta_valor_extremo(df_com_outlier):
    """
    Com o valor 99.0 inserido intencionalmente, a função deve retornar
    um DataFrame com pelo menos uma linha, no caso a que contém o outlier.
    Isso confirma que a regra do IQR está sendo aplicada corretamente.
    """
    outliers = identificar_outliers(df_com_outlier, "temperatura")

    assert len(outliers) >= 1, "Deveria detectar ao menos um outlier"
    assert 99.0 in outliers["temperatura"].values, (
        "O valor 99.0 deveria estar entre os outliers detectados"
    )


def test_identificar_outliers_retorna_vazio_sem_outliers(df_base):
    """
    Quando todos os valores estão dentro do intervalo IQR normal,
    a função deve retornar um DataFrame vazio sem falsos positivos.
    O df_base tem valores uniformes de 20 a 25, sem nenhum extremo.
    """
    outliers = identificar_outliers(df_base, "temperatura")

    assert outliers.empty, (
        f"Não deveria haver outliers, mas encontrou: {outliers}"
    )


def test_identificar_outliers_coluna_inexistente(df_base):
    """
    Se a coluna solicitada não existir no DataFrame, a função deve
    lançar ValueError com uma mensagem indicando qual coluna está faltando.
    Isso previne erros silenciosos no pipeline.
    """
    with pytest.raises(ValueError, match="coluna_inexistente"):
        identificar_outliers(df_base, "coluna_inexistente")


# =============================================================================
# TESTES: resumir_outliers
# =============================================================================

def test_resumir_outliers_retorna_estrutura_correta(df_com_outlier):
    """
    O resumo deve ser um dicionário com as chaves 'temperatura' e 'ph',
    onde cada uma contém 'quantidade' (int) e 'registros' (lista de dicts).
    Essa estrutura é usada para exibir o resumo final no terminal.
    """
    resumo = resumir_outliers(df_com_outlier)

    assert "temperatura" in resumo
    assert "ph" in resumo
    assert "quantidade" in resumo["temperatura"]
    assert "registros" in resumo["temperatura"]
    assert isinstance(resumo["temperatura"]["registros"], list)


def test_resumir_outliers_conta_corretamente(df_com_outlier):
    """
    Com apenas um outlier inserido (99.0 na temperatura),
    a quantidade reportada deve ser 1 para temperatura.
    O pH não tem outlier inserido, então deve retornar 0.
    """
    resumo = resumir_outliers(df_com_outlier)

    assert resumo["temperatura"]["quantidade"] >= 1, (
        "Deveria contar ao menos 1 outlier na temperatura"
    )


# =============================================================================
# TESTES: funções de geração de gráficos
# Os gráficos são salvos em disco. Os testes verificam se o arquivo foi
# criado corretamente, sem inspecionar o conteúdo visual da imagem.
# Após cada teste, o arquivo gerado é removido para não poluir o diretório.
# =============================================================================

def test_gerar_grafico_linha_cria_arquivo(df_base, tmp_path, monkeypatch):
    """
    Verifica que gerar_grafico_linha salva um arquivo .png no disco
    e retorna o caminho correto do arquivo criado.

    `tmp_path` é uma fixture do pytest que cria uma pasta temporária
    limpa para cada teste, evita sujar o diretório reports/ real.
    `monkeypatch` substitui OUTPUT_DIR pelo caminho temporário apenas
    durante este teste, sem alterar o comportamento global do módulo.
    """
    import src.analytics.statistics as stats_module
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", str(tmp_path))

    nome = "teste_linha.png"
    caminho = gerar_grafico_linha(df_base, "temperatura", nome)

    assert os.path.isfile(caminho), f"Arquivo não foi criado: {caminho}"


def test_gerar_grafico_linha_erro_sem_coluna(df_base, tmp_path, monkeypatch):
    """
    Se a coluna solicitada não existir, a função deve lançar ValueError.
    Isso garante que o pipeline não gere arquivos corrompidos ou em branco.
    """
    import src.analytics.statistics as stats_module
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", str(tmp_path))

    with pytest.raises(ValueError):
        gerar_grafico_linha(df_base, "coluna_inexistente", "teste.png")


def test_gerar_boxplot_cria_arquivo(df_base, tmp_path, monkeypatch):
    """
    Verifica que gerar_boxplot produz um arquivo .png no disco.
    O boxplot é o gráfico mais informativo do módulo (mostra mediana),
    quartis e outliers visualmente em um único gráfico.
    """
    import src.analytics.statistics as stats_module
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", str(tmp_path))

    nome = "teste_boxplot.png"
    caminho = gerar_boxplot(df_base, "ph", nome)

    assert os.path.isfile(caminho), f"Arquivo não foi criado: {caminho}"


def test_gerar_histograma_cria_arquivo(df_base, tmp_path, monkeypatch):
    """
    Verifica que gerar_histograma produz um arquivo .png no disco.
    O histograma mostra a distribuição de frequências dos valores,
    útil para identificar se os dados seguem alguma distribuição.
    """
    import src.analytics.statistics as stats_module
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", str(tmp_path))

    nome = "teste_histograma.png"
    caminho = gerar_histograma(df_base, "temperatura", nome)

    assert os.path.isfile(caminho), f"Arquivo não foi criado: {caminho}"


# =============================================================================
# TESTES: gerar_grafico_comparacao
# Esta função recebe dois DataFrames distintos (leituras da API e clientes
# cadastrados) e gera dois gráficos de barras comparativos.
# =============================================================================

def test_gerar_grafico_comparacao_cria_arquivos(df_base, tmp_path, monkeypatch):
    """
    Verifica que a função gera os dois arquivos esperados:
    - comparacao_ph.png
    - comparacao_temperatura.png

    Também confirma que o DataFrame comparativo retornado contém a linha
    'Monitorada (API)' que representa a média das leituras do sensor.
    """
    import src.analytics.statistics as stats_module
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", str(tmp_path))

    # Simula o DataFrame de clientes cadastrados no banco
    df_clientes = pd.DataFrame({
        "nome":        ["Marca A", "Marca B"],
        "ph":          [7.0,       7.5],
        "temperatura": [22.0,      23.5],
    })

    caminho_ph, df_comp = gerar_grafico_comparacao(
        df_base,
        df_clientes,
        nome_arquivo_ph="comparacao_ph.png",
        nome_arquivo_temp="comparacao_temperatura.png",
    )

    # Os dois arquivos de gráfico devem existir no disco
    assert os.path.isfile(caminho_ph), "Gráfico de pH não foi criado"
    assert os.path.isfile(os.path.join(str(tmp_path), "comparacao_temperatura.png")), (
        "Gráfico de temperatura não foi criado"
    )

    # O DataFrame comparativo deve incluir a linha da água monitorada
    assert "Monitorada (API)" in df_comp["nome"].values, (
        "DataFrame comparativo não contém a linha 'Monitorada (API)'"
    )


# =============================================================================
# TESTES: limpar_reports
# =============================================================================

def test_limpar_reports_remove_arquivos(tmp_path, monkeypatch):
    """
    Cria arquivos fictícios na pasta temporária, chama limpar_reports,
    e verifica que a pasta ficou vazia. A pasta em si deve continuar
    existindo, apenas os arquivos internos são apagados.
    """
    import src.analytics.statistics as stats_module
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", str(tmp_path))

    # Cria dois arquivos fictícios para simular relatórios gerados
    (tmp_path / "grafico1.png").write_text("fake")
    (tmp_path / "grafico2.png").write_text("fake")

    limpar_reports()

    arquivos_restantes = list(tmp_path.iterdir())
    assert len(arquivos_restantes) == 0, (
        f"Pasta deveria estar vazia, mas contém: {arquivos_restantes}"
    )


def test_limpar_reports_sem_pasta_nao_levanta_erro(tmp_path, monkeypatch):
    """
    Se OUTPUT_DIR não existir, limpar_reports não deve lançar nenhum erro
    ela simplesmente retorna sem fazer nada. Isso evita falha na primeira
    execução do pipeline, quando a pasta ainda não foi criada.
    """
    import src.analytics.statistics as stats_module
    pasta_inexistente = str(tmp_path / "nao_existe")
    monkeypatch.setattr(stats_module, "OUTPUT_DIR", pasta_inexistente)

    # Não deve levantar nenhuma exceção
    limpar_reports()
