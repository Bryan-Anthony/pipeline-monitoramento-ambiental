"""Dashboard Streamlit do pipeline de monitoramento da qualidade da água.

Executar na raiz do projeto:
    streamlit run dashboard.py
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src.analytics import statistics as estat
from src.database.db_manager import DatabaseManager

BRONZE = Path(__file__).parent / "data" / "bronze" / "leituras_api.csv"

SQL = """
    SELECT
        l.dataHora,
        l.ph,
        l.temperaturaAgua,
        l.temperaturaAr,
        l.oxigenioDissolvido,
        l.condutividadeEletrica,
        l.turbidezAgua,
        e.nome AS estacao
    FROM leitura l
    JOIN estacao e ON e.idEstacao = l.fkEstacao
"""

PARAMETROS = {
    "pH": "ph",
    "Temperatura da água (°C)": "temperaturaAgua",
    "Temperatura do ar (°C)": "temperaturaAr",
    "Oxigênio dissolvido (mg/L)": "oxigenioDissolvido",
    "Condutividade (µS/cm)": "condutividadeEletrica",
    "Turbidez (NTU)": "turbidezAgua",
}
ROTULOS = {coluna: nome.split(" (")[0] for nome, coluna in PARAMETROS.items()}

VERDE = "#2DD4BF"
AZUL = "#38BDF8"
ALERTA = "#F59E0B"
TEXTO = "#CBD5E1"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, .stMarkdown, .stMarkdown *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] input { font-family: 'Inter', sans-serif; }
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"] { display: none !important; }
[data-testid="stSidebar"] { transform: none !important; min-width: 300px !important; }
.stApp { background: radial-gradient(1200px 600px at 10% -10%, #10243a 0%, #0B0F1A 55%); }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 2rem; max-width: 1280px; }

[data-testid="stSidebar"] { background: #0D1322; border-right: 1px solid rgba(148,163,184,.12); }

[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,.04));
    border: 1px solid rgba(148,163,184,.28) !important;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,.25);
}

.topo { display:flex; justify-content:space-between; align-items:center; margin-bottom: 1.5rem; }
.topo h1 { font-size: 1.6rem; font-weight: 700; color:#F1F5F9; margin:0; letter-spacing:-.02em; }
.topo p { color:#CBD5E1; margin:.2rem 0 0; font-size:.9rem; }
.pill { display:inline-flex; align-items:center; gap:.5rem; padding:.45rem .9rem; border-radius:999px;
        background:rgba(45,212,191,.1); color:#2DD4BF; font-size:.8rem; font-weight:600;
        border:1px solid rgba(45,212,191,.25); }
.pill i { width:8px; height:8px; border-radius:50%; background:#2DD4BF; animation: pulso 1.8s infinite; }
@keyframes pulso { 0%{box-shadow:0 0 0 0 rgba(45,212,191,.6)} 100%{box-shadow:0 0 0 10px rgba(45,212,191,0)} }

.secao { color:#F8FAFC; font-size:1.05rem; font-weight:600; margin:1.6rem 0 .8rem; }
.secao span { color:#94A3B8; font-weight:400; font-size:.85rem; margin-left:.5rem; }

/* ---------- Pipeline ---------- */
.pipeline { display:flex; align-items:stretch; gap:0; overflow-x:auto; padding:.4rem 0 .2rem; }
.etapa { flex:1; min-width:170px; padding:1.1rem 1.1rem; border-radius:18px; position:relative;
         background:linear-gradient(160deg, rgba(255,255,255,.07), rgba(255,255,255,.02));
         border:1px solid rgba(148,163,184,.16); }
.etapa .icone { font-size:1.3rem; }
.etapa .nome { color:#F1F5F9; font-weight:600; margin-top:.5rem; font-size:.95rem; }
.etapa .detalhe { color:#94A3B8; font-size:.75rem; margin-top:.1rem; }
.etapa .valor { color:#F8FAFC; font-weight:700; font-size:1.5rem; margin-top:.7rem; letter-spacing:-.02em; }
.etapa .legenda { color:#CBD5E1; font-size:.75rem; }
.etapa::after { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:18px 18px 0 0;
                background:var(--cor); }
.etapa .ok { position:absolute; top:.9rem; right:.9rem; width:9px; height:9px; border-radius:50%;
             background:#2DD4BF; box-shadow:0 0 10px #2DD4BF; }
.fio { flex:0 0 44px; align-self:center; height:3px; margin:0 -2px; z-index:1; border-radius:3px;
       background:repeating-linear-gradient(90deg,#2DD4BF 0 8px,transparent 8px 16px);
       background-size:32px 3px; animation: fluxo 1s linear infinite; }
@keyframes fluxo { from{background-position:0 0} to{background-position:32px 0} }

/* ---------- KPIs ---------- */
.kpi .rotulo { color:#CBD5E1; font-size:.8rem; font-weight:500; }
.kpi .numero { color:#F8FAFC; font-size:2rem; font-weight:700; letter-spacing:-.03em; margin:.2rem 0 .4rem; }
.kpi .sub { font-size:.78rem; font-weight:600; }
.kpi .sub.ok { color:#2DD4BF; } .kpi .sub.alerta { color:#F59E0B; }
.kpi svg { width:100%; height:44px; margin-top:.4rem; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] > div:first-child { padding: 1.2rem .6rem; }
.marca { display:flex; align-items:center; gap:.7rem; padding:.2rem .4rem 1.1rem; margin-bottom:1rem;
         border-bottom:1px solid rgba(148,163,184,.12); }
.marca .logo { width:38px; height:38px; border-radius:12px; display:flex; align-items:center;
               justify-content:center; font-size:1.2rem;
               background:linear-gradient(135deg,#2DD4BF,#38BDF8); }
.marca b { color:#F1F5F9; font-size:.95rem; display:block; line-height:1.1; }
.marca small { color:#94A3B8; font-size:.72rem; }
.filtro-titulo { color:#94A3B8; font-size:.7rem; font-weight:600; letter-spacing:.12em;
                 text-transform:uppercase; margin:.4rem .4rem .2rem; }
[data-testid="stSidebar"] label p { color:#CBD5E1 !important; font-size:.82rem; font-weight:500; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,.04); border:1px solid rgba(148,163,184,.18);
    border-radius:12px; }
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover { border-color:rgba(45,212,191,.5); }
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: rgba(45,212,191,.14); color:#2DD4BF; border-radius:999px; font-weight:600; }
[data-testid="stSidebar"] [data-baseweb="tag"] span[role="presentation"] { color:#2DD4BF; }
.resumo-filtro { margin:1.2rem .4rem 0; padding:.9rem 1rem; border-radius:14px;
                 background:rgba(45,212,191,.07); border:1px solid rgba(45,212,191,.18); }
.resumo-filtro .n { color:#F8FAFC; font-size:1.4rem; font-weight:700; letter-spacing:-.02em; }
.resumo-filtro .t { color:#CBD5E1; font-size:.75rem; }
</style>
"""


@st.cache_data(ttl=600)
def carregar_dados():
    db = DatabaseManager()
    conexao = db.conectar()
    try:
        df = pd.read_sql(SQL, conexao)
    finally:
        db.fechar(conexao)
    df["dataHora"] = pd.to_datetime(df["dataHora"], errors="coerce")
    for coluna in PARAMETROS.values():
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    return df.dropna(subset=["dataHora"]).sort_values("dataHora")


@st.cache_data(ttl=600)
def carregar_clientes():
    from src.database.repository import MonitoramentoRepository

    clientes = MonitoramentoRepository().buscar_clientes()
    clientes = clientes.rename(columns={"temperatura": "temperaturaAgua", "turbidez": "turbidezAgua"})
    for coluna in PARAMETROS.values():
        if coluna in clientes.columns:
            clientes[coluna] = pd.to_numeric(clientes[coluna], errors="coerce")
    return clientes


def contar_bronze():
    if not BRONZE.exists():
        return None
    return len(pd.read_csv(BRONZE))


def limites_iqr(serie):
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def html(texto):
    """Remove a indentação para o Markdown não tratar o HTML como código."""
    st.markdown("".join(linha.strip() for linha in texto.splitlines()), unsafe_allow_html=True)


def sparkline(valores, cor=VERDE):
    valores = list(valores)[-40:]
    if len(valores) < 2:
        return ""
    minimo, maximo = min(valores), max(valores)
    faixa = (maximo - minimo) or 1
    pontos = [
        f"{i * 200 / (len(valores) - 1):.1f},{40 - (v - minimo) / faixa * 36:.1f}"
        for i, v in enumerate(valores)
    ]
    linha = " ".join(pontos)
    return (
        f'<svg viewBox="0 0 200 44" preserveAspectRatio="none">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{cor}" stop-opacity=".35"/>'
        f'<stop offset="1" stop-color="{cor}" stop-opacity="0"/></linearGradient></defs>'
        f'<polygon points="0,44 {linha} 200,44" fill="url(#g)"/>'
        f'<polyline points="{linha}" fill="none" stroke="{cor}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


def estilo(grafico, altura=300):
    return (
        grafico.properties(height=altura, background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=TEXTO, titleColor=TEXTO, gridColor="#1E293B", domainColor="#1E293B",
            tickColor="#1E293B", labelFont="Inter", titleFont="Inter",
        )
        .configure_legend(labelColor=TEXTO, titleColor=TEXTO, orient="bottom")
    )


def card_pipeline(icone, nome, detalhe, valor, legenda, cor):
    return (
        f'<div class="etapa" style="--cor:{cor}"><span class="ok"></span>'
        f'<div class="icone">{icone}</div><div class="nome">{nome}</div>'
        f'<div class="detalhe">{detalhe}</div><div class="valor">{valor}</div>'
        f'<div class="legenda">{legenda}</div></div>'
    )


st.set_page_config(page_title="Qualidade da Água", page_icon="💧", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

df = carregar_dados()
if df.empty:
    st.warning("Nenhuma leitura encontrada no banco.")
    st.stop()

# ---------- Menu: abrir e fechar ----------
if "menu_aberto" not in st.session_state:
    st.session_state.menu_aberto = True


def alternar_menu():
    st.session_state.menu_aberto = not st.session_state.menu_aberto


if not st.session_state.menu_aberto:
    st.markdown(
        '<style>[data-testid="stSidebar"]{display:none !important;}</style>',
        unsafe_allow_html=True,
    )
    st.button("☰ Abrir menu", on_click=alternar_menu, key="abrir_menu")

# ---------- Filtros ----------
with st.sidebar:
    st.button("◀ Fechar menu", on_click=alternar_menu, key="fechar_menu", use_container_width=True)
    html(
        """
        <div class="marca"><div class="logo">💧</div>
        <div><b>AquaMonitor</b><small>Qualidade da água</small></div></div>
        """
    )
    html('<div class="filtro-titulo">Filtros</div>')
    lista_estacoes = sorted(df["estacao"].dropna().unique())
    estacoes = st.multiselect("Estação", lista_estacoes, default=lista_estacoes,
                              placeholder="Selecione as estações")
    nome_parametro = st.selectbox("Parâmetro em destaque", list(PARAMETROS))
    n_leituras = int(df["estacao"].isin(estacoes).sum())
    html(
        f"""
        <div class="resumo-filtro"><div class="n">{n_leituras:,}</div>
        <div class="t">leituras nos filtros atuais</div></div>
        """.replace(",", ".")
    )
coluna = PARAMETROS[nome_parametro]

df = df[df["estacao"].isin(estacoes)]
df_param = df.dropna(subset=[coluna]).copy()
if df_param.empty:
    st.warning("Sem dados para os filtros selecionados.")
    st.stop()

inf, sup = limites_iqr(df_param[coluna])
df_param["outlier"] = (df_param[coluna] < inf) | (df_param[coluna] > sup)

# ---------- Topo ----------
ultima = df["dataHora"].max().strftime("%d/%m/%Y %H:%M")
html(
    f"""
    <div class="topo">
        <div><h1>Monitoramento da qualidade da água</h1>
        <p>Estação QMStation1 · última leitura em {ultima}</p></div>
        <span class="pill"><i></i>Pipeline ativo</span>
    </div>
    """
)

# ---------- Pipeline ----------
bronze = contar_bronze()
colunas_param = list(PARAMETROS.values())
completos = df[colunas_param].notna().to_numpy().mean() * 100
total_outliers = int(df_param["outlier"].sum())

html('<div class="secao">Pipeline de dados<span>Do sensor ao dashboard</span></div>')
html(
    "<div class='pipeline'>"
    + card_pipeline("🛰️", "API ThingSpeak", "Canal 2412377", "500", "leituras por consulta", AZUL)
    + "<div class='fio'></div>"
    + card_pipeline("📋", "Contrato", "Validação Pydantic", "100%", "formato conferido", AZUL)
    + "<div class='fio'></div>"
    + card_pipeline(
        "🥉", "Bronze", "CSV bruto", f"{bronze:,}".replace(",", ".") if bronze else "—",
        "registros salvos", "#CD7F32",
    )
    + "<div class='fio'></div>"
    + card_pipeline(
        "🥈", "Silver", "SQL Server", f"{len(df):,}".replace(",", "."),
        f"linhas · {completos:.0f}% completas", "#CBD5E1",
    )
    + "<div class='fio'></div>"
    + card_pipeline(
        "🥇", "Gold", "Estatística + dashboard", str(total_outliers),
        f"outliers em {ROTULOS[coluna].lower()}", "#FACC15",
    )
    + "</div>"
)

# ---------- Indicadores ----------
html('<div class="secao">Indicadores<span>' + nome_parametro + "</span></div>")
serie = df_param[coluna]
pct_outlier = total_outliers / len(df_param) * 100
indicadores = [
    ("Leituras", f"{len(df_param)}", "dados válidos", "ok", sparkline(range(len(df_param)))),
    ("Média", f"{serie.mean():.2f}", f"desvio {serie.std():.2f}", "ok", sparkline(serie)),
    ("Mediana", f"{serie.median():.2f}", f"IQR {serie.quantile(.75) - serie.quantile(.25):.2f}", "ok", sparkline(serie.rolling(5, min_periods=1).median())),
    (
        "Outliers", f"{total_outliers}", f"{pct_outlier:.1f}% das leituras",
        "alerta" if total_outliers else "ok", sparkline(df_param["outlier"].astype(int).cumsum(), ALERTA),
    ),
]
for coluna_st, (rotulo, numero, sub, tom, grafico) in zip(st.columns(4), indicadores):
    with coluna_st, st.container(border=True):
        html(
            f'<div class="kpi"><div class="rotulo">{rotulo}</div>'
            f'<div class="numero">{numero}</div><div class="sub {tom}">{sub}</div>{grafico}</div>'
        )

# ---------- Gráficos: tempo e histograma ----------
html('<div class="secao">Análise<span>Evolução e distribuição</span></div>')
esquerda, direita = st.columns([3, 2])

with esquerda, st.container(border=True):
    st.markdown(f"**{nome_parametro} ao longo do tempo**")
    base = alt.Chart(df_param).encode(
        x=alt.X("dataHora:T", title="Data e hora", axis=alt.Axis(format="%d/%m/%Y %H:%M", labelAngle=-30)),
        y=alt.Y(f"{coluna}:Q", title=nome_parametro, scale=alt.Scale(zero=False)),
    )
    dica = [
        alt.Tooltip("dataHora:T", title="Data e hora", format="%d/%m/%Y %H:%M"),
        alt.Tooltip(f"{coluna}:Q", title=nome_parametro),
    ]
    todos = base.mark_point(opacity=0, size=60).encode(tooltip=dica)
    area = base.mark_area(
        line={"color": VERDE, "strokeWidth": 2},
        color=alt.Gradient(
            gradient="linear", x1=1, x2=1, y1=1, y2=0,
            stops=[alt.GradientStop(color="rgba(45,212,191,0)", offset=0),
                   alt.GradientStop(color="rgba(45,212,191,.35)", offset=1)],
        ),
    )
    pontos = (
        base.transform_filter(alt.datum.outlier)
        .mark_point(color=ALERTA, size=70, filled=True)
        .encode(tooltip=dica)
    )
    st.altair_chart(estilo(area + todos + pontos).interactive(bind_y=False), use_container_width=True, theme=None)
    st.caption("Pontos laranja: outliers pelo método IQR.")

with direita, st.container(border=True):
    st.markdown("**Histograma**")
    histograma = (
        alt.Chart(df_param)
        .mark_bar(color=AZUL, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(f"{coluna}:Q", bin=alt.Bin(maxbins=20), title=nome_parametro),
            y=alt.Y("count()", title="Nº de leituras"),
        )
    )
    st.altair_chart(estilo(histograma), use_container_width=True, theme=None)
    st.caption("Quantidade de leituras por faixa de valor.")

# ---------- Gráficos: boxplot e correlação ----------
esquerda, direita = st.columns([2, 3])

with esquerda, st.container(border=True):
    st.markdown("**Boxplot**")
    boxplot = (
        alt.Chart(df_param)
        .mark_boxplot(color=VERDE, size=50, extent=1.5, median={"color": "#F8FAFC"})
        .encode(
            x=alt.X("estacao:N", title="Estação"),
            y=alt.Y(f"{coluna}:Q", title=nome_parametro, scale=alt.Scale(zero=False)),
        )
    )
    st.altair_chart(estilo(boxplot, 320), use_container_width=True, theme=None)
    st.caption("Caixa: Q1 a Q3. Linha branca: mediana. Pontos: outliers.")

with direita, st.container(border=True):
    st.markdown("**Correlação entre parâmetros**")
    corr = df[colunas_param].corr().rename(columns=ROTULOS, index=ROTULOS)
    corr = corr.reset_index(names="a").melt(id_vars="a", var_name="b", value_name="r").dropna()
    mapa = alt.Chart(corr).encode(
        x=alt.X("b:N", title=None, axis=alt.Axis(labelAngle=-35)),
        y=alt.Y("a:N", title=None),
    )
    celulas = mapa.mark_rect(cornerRadius=6, stroke="#0B0F1A", strokeWidth=3).encode(
        color=alt.Color(
            "r:Q", scale=alt.Scale(domain=[-1, 0, 1], range=["#F59E0B", "#1E293B", "#2DD4BF"]),
            legend=alt.Legend(title="Correlação (-1 a 1)", orient="bottom", gradientLength=200),
        ),
        tooltip=["a", "b", alt.Tooltip("r:Q", format=".2f")],
    )
    textos = mapa.mark_text(fontSize=11, fontWeight=600, color="#F8FAFC").encode(
        text=alt.Text("r:Q", format=".2f")
    )
    st.altair_chart(estilo(celulas + textos, 320), use_container_width=True, theme=None)
    st.caption("Verde: correlação positiva. Laranja: negativa. Quanto mais forte a cor, maior a relação.")

# ---------- Leituras com alerta ----------
html('<div class="secao">Leituras com alerta<span>Valores fora dos limites IQR</span></div>')
with st.container(border=True):
    alertas = df_param[df_param["outlier"]][["dataHora", "estacao", coluna]]
    if alertas.empty:
        st.success("Nenhum outlier encontrado para os filtros selecionados.")
    else:
        st.dataframe(
            alertas.rename(columns={"dataHora": "Data e hora", "estacao": "Estação", coluna: nome_parametro}),
            hide_index=True, use_container_width=True,
        )


# ---------- Abas: grade de gráficos e clientes ----------
html('<div class="secao">Explorar<span>Todos os parâmetros e comparação com clientes</span></div>')
aba_grade, aba_clientes, aba_stats = st.tabs(["📊 Grade de gráficos", "🏢 Clientes", "📐 Estatísticas"])

with aba_grade:
    st.caption("Um boxplot e um histograma para cada parâmetro, com o filtro de estação aplicado.")
    for nome, col in PARAMETROS.items():
        dados = df.dropna(subset=[col])
        if dados.empty:
            continue
        html(f'<div class="secao" style="font-size:.95rem;margin:1rem 0 .4rem">{nome}</div>')
        c_box, c_hist = st.columns(2)
        with c_box, st.container(border=True):
            box = (
                alt.Chart(dados)
                .mark_boxplot(color=VERDE, size=40, extent=1.5, median={"color": "#F8FAFC"})
                .encode(y=alt.Y(f"{col}:Q", title=nome, scale=alt.Scale(zero=False)))
            )
            st.altair_chart(estilo(box, 220), use_container_width=True, theme=None)
            st.caption("Boxplot: caixa = Q1 a Q3, linha branca = mediana, pontos = outliers.")
        with c_hist, st.container(border=True):
            hist = (
                alt.Chart(dados)
                .mark_bar(color=AZUL, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(x=alt.X(f"{col}:Q", bin=alt.Bin(maxbins=20), title=nome), y=alt.Y("count()", title="Nº de leituras"))
            )
            st.altair_chart(estilo(hist, 220), use_container_width=True, theme=None)
            st.caption("Histograma: quantas leituras caem em cada faixa de valor.")

with aba_clientes:
    try:
        clientes = carregar_clientes()
    except Exception as erro:
        st.warning(f"Não foi possível carregar a tabela de clientes: {erro}")
        clientes = None

    if clientes is not None and clientes.empty:
        st.info("Nenhum cliente encontrado no banco.")
    elif clientes is not None:
        comuns = [c for c in PARAMETROS.values() if c in clientes.columns and clientes[c].notna().any()]
        if not comuns:
            st.info("Nenhum cliente possui valores de referência cadastrados.")
        else:
            st.caption("Média da água monitorada comparada ao valor de referência de cada cliente.")
            nomes_inv = {v: k for k, v in PARAMETROS.items()}
            for i in range(0, len(comuns), 2):
                for coluna_st, col in zip(st.columns(2), comuns[i:i + 2]):
                    barras = pd.concat([
                        pd.DataFrame({"fonte": ["Monitorada (API)"], "valor": [df[col].mean()], "tipo": ["Monitorada"]}),
                        pd.DataFrame({"fonte": clientes["nomeCliente"], "valor": clientes[col], "tipo": "Cliente"}),
                    ]).dropna(subset=["valor"])
                    grafico = (
                        alt.Chart(barras)
                        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                        .encode(
                            x=alt.X("fonte:N", title=None, sort=None, axis=alt.Axis(labelAngle=-25)),
                            y=alt.Y("valor:Q", title=nomes_inv[col]),
                            color=alt.Color(
                                "tipo:N", legend=alt.Legend(title="Origem", orient="bottom"),
                                scale=alt.Scale(domain=["Monitorada", "Cliente"], range=[VERDE, "#475569"]),
                            ),
                            tooltip=["fonte", alt.Tooltip("valor:Q", format=".2f")],
                        )
                    )
                    with coluna_st, st.container(border=True):
                        st.markdown(f"**{nomes_inv[col]}**")
                        st.altair_chart(estilo(grafico, 260), use_container_width=True, theme=None)
            st.markdown("**Valores cadastrados**")
            tabela = clientes[["nomeCliente"] + comuns].rename(columns={"nomeCliente": "Cliente", **nomes_inv})
            st.dataframe(tabela, hide_index=True, use_container_width=True)

with aba_stats:
    # 1. Resumo completo por parâmetro
    st.subheader("Resumo por parâmetro")
    nomes = {c: n for n, c in PARAMETROS.items()}
    resumo = pd.DataFrame(estat.calcular_estatisticas(df)).T
    resumo.index = [estat.rotulo(i) for i in resumo.index]
    st.dataframe(resumo.rename(columns={
        "media": "Média", "mediana": "Mediana", "desvio_padrao": "Desvio",
        "q1": "Q1", "q3": "Q3", "iqr": "IQR", "minimo": "Mín", "maximo": "Máx",
        "assimetria": "Assimetria", "coef_variacao": "CV (%)"}), use_container_width=True)
    st.caption("CV = desvio ÷ média. Assimetria perto de 0 indica distribuição simétrica.")

    # 3. Conformidade com os clientes
    st.subheader("Conformidade com os clientes")
    st.caption("% de leituras dentro de ±10% do valor de referência de cada cliente.")
    try:
        conf = estat.calcular_conformidade(df, carregar_clientes())
        if conf.empty:
            st.info("Sem dados de clientes para comparar.")
        else:
            st.dataframe(conf.rename(columns={
                "cliente": "Cliente", "parametro": "Parâmetro", "referencia": "Referência",
                "media_monitorada": "Média monitorada", "pct_conforme": "% conforme"}),
                hide_index=True, use_container_width=True)
    except Exception as erro:
        st.warning(f"Não foi possível calcular a conformidade: {erro}")
