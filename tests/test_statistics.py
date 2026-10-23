# Testes do módulo src/analytics/statistics.py
# Executar: python -m pytest tests/test_statistics.py -v
import os

import pandas as pd
import pytest

from src.analytics import statistics as st


@pytest.fixture
def df_banco():
    """Leituras com as colunas do jeito que vêm do banco."""
    n = 20
    return pd.DataFrame({
        "dataHora": pd.date_range("2026-01-01", periods=n, freq="h"),
        "fkEstacao": [1] * n,
        "temperaturaAgua": [20 + i * 0.1 for i in range(n)],
        "temperaturaAr": [25 + i * 0.2 for i in range(n)],
        "ph": [7 + (i % 3) * 0.1 for i in range(n)],
        "oxigenioDissolvido": [8 - i * 0.05 for i in range(n)],
        "condutividadeEletrica": [150 + i for i in range(n)],
        "turbidezAgua": [5 + (i % 4) for i in range(n)],
    })


@pytest.fixture
def df_clientes():
    return pd.DataFrame({
        "nomeCliente": ["Agua A", "Agua B"],
        "ph": [7.2, 6.8],
        "temperatura": [20.0, 18.0],
    })


@pytest.fixture(autouse=True)
def pasta_reports(tmp_path, monkeypatch):
    monkeypatch.setattr(st, "OUTPUT_DIR", str(tmp_path))
    return tmp_path


def test_preparar_dados_renomeia_colunas(df_banco):
    df = st.preparar_dados(df_banco)
    for coluna in st.PARAMETROS:
        assert coluna in df.columns
    assert "data_hora" in df.columns


def test_preparar_dados_df_vazio_levanta_erro():
    with pytest.raises(ValueError):
        st.preparar_dados(pd.DataFrame())


def test_calcular_estatisticas_todos_parametros(df_banco):
    r = st.calcular_estatisticas(df_banco)
    assert set(r) == set(st.PARAMETROS)
    assert r["condutividade"]["minimo"] == 150
    assert r["condutividade"]["maximo"] == 169


def test_outliers_detecta_valor_extremo(df_banco):
    df_banco.loc[0, "ph"] = 14
    assert st.resumir_outliers(df_banco)["ph"]["quantidade"] == 1


def test_outliers_coluna_inexistente(df_banco):
    with pytest.raises(ValueError):
        st.identificar_outliers(df_banco, "xyz")


def test_limpar_reports(pasta_reports):
    (pasta_reports / "a.png").write_text("x")
    st.limpar_reports()
    assert os.listdir(pasta_reports) == []


def test_graficos_individuais_um_boxplot_e_um_histograma_por_parametro(df_banco):
    caminhos = st.gerar_graficos_individuais(df_banco)
    assert len(caminhos) == 2 * len(st.PARAMETROS)
    assert all(os.path.exists(c) for c in caminhos)


def test_comparacao_so_com_parametros_do_cliente(df_banco, df_clientes):
    caminhos, df_comp = st.gerar_grafico_comparacao(df_banco, df_clientes)
    assert len(caminhos) == 2  # ph e temperatura
    assert set(df_comp.columns) == {"nome", "ph", "temperatura"}
    assert len(df_comp) == 3  # monitorada + 2 clientes


def test_comparacao_exige_nome_do_cliente(df_banco):
    with pytest.raises(ValueError):
        st.gerar_grafico_comparacao(df_banco, pd.DataFrame({"ph": [7.0]}))


def test_matriz_correlacao_cria_arquivo(df_banco):
    assert os.path.exists(st.gerar_matriz_correlacao(df_banco))


def test_matriz_correlacao_exige_duas_colunas():
    df = pd.DataFrame({"ph": [7.0, 7.1, 7.2]})
    with pytest.raises(ValueError):
        st.gerar_matriz_correlacao(df)
