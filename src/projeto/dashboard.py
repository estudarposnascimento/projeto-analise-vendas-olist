
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================================
# CONFIGURAÇÕES
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = ROOT_DIR / "database" / "olist.db"

st.set_page_config(
    page_title="Dashboard Olist",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# ESTILO
# =====================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        [data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.08);
            border: 1px solid rgba(128, 128, 128, 0.18);
            padding: 18px;
            border-radius: 12px;
        }

        [data-testid="stMetricValue"] {
            font-size: 26px;
            font-weight: 700;
        }

        h1, h2, h3 {
            font-weight: 700;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# FUNÇÕES DE ACESSO AO BANCO
# =====================================================

def read_sql(query, params=None):
    with sqlite3.connect(DATABASE_PATH) as connection:
        return pd.read_sql_query(
            query,
            connection,
            params=params,
        )


@st.cache_data(ttl=300)
def get_period():
    query = """
        SELECT
            MIN(date(purchase_date)) AS data_inicial,
            MAX(date(purchase_date)) AS data_final
        FROM gold_vendas
        WHERE order_status = 'delivered'
    """
    return read_sql(query)


@st.cache_data(ttl=300)
def get_categories():
    query = """
        SELECT DISTINCT product_category_name
        FROM gold_vendas
        WHERE order_status = 'delivered'
        ORDER BY product_category_name
    """
    return read_sql(query)["product_category_name"].dropna().tolist()


@st.cache_data(ttl=300)
def get_dashboard_data(data_inicial, data_final, categorias):
    params = [data_inicial, data_final]

    filtro_categoria = ""

    if categorias:
        placeholders = ",".join(["?"] * len(categorias))
        filtro_categoria = (
            f" AND product_category_name IN ({placeholders})"
        )
        params.extend(categorias)

    filtro = f"""
        WHERE order_status = 'delivered'
          AND date(purchase_date) BETWEEN date(?) AND date(?)
          {filtro_categoria}
    """

    # Indicadores principais
    query_kpis = f"""
        SELECT
            COUNT(DISTINCT order_id) AS pedidos,
            COUNT(*) AS itens,
            COALESCE(SUM(price), 0) AS valor_produtos,
            COALESCE(SUM(freight_value), 0) AS frete,
            COALESCE(
                SUM(price) / NULLIF(COUNT(DISTINCT order_id), 0),
                0
            ) AS ticket_medio
        FROM gold_vendas
        {filtro}
    """

    kpis = read_sql(query_kpis, params)

    # Evolução mensal
    query_mensal = f"""
        SELECT
            strftime('%Y-%m', purchase_date) AS mes,
            COUNT(DISTINCT order_id) AS pedidos,
            COUNT(*) AS itens,
            SUM(price) AS valor_produtos
        FROM gold_vendas
        {filtro}
        GROUP BY strftime('%Y-%m', purchase_date)
        ORDER BY mes
    """

    mensal = read_sql(query_mensal, params)

    # Vendas por categoria
    query_categoria = f"""
        SELECT
            product_category_name AS categoria,
            COUNT(*) AS quantidade_itens,
            SUM(price) AS valor_produtos
        FROM gold_vendas
        {filtro}
        GROUP BY product_category_name
        ORDER BY valor_produtos DESC
    """

    categorias_df = read_sql(query_categoria, params)

    # Top 10 produtos
    query_produtos = f"""
        SELECT
            product_id,
            product_category_name AS categoria,
            COUNT(*) AS quantidade_itens,
            SUM(price) AS valor_produtos
        FROM gold_vendas
        {filtro}
        GROUP BY product_id, product_category_name
        ORDER BY quantidade_itens DESC, valor_produtos DESC
        LIMIT 10
    """

    produtos = read_sql(query_produtos, params)

    return kpis, mensal, categorias_df, produtos


@st.cache_data(ttl=300)
def get_status(data_inicial, data_final):
    query = """
        SELECT
            order_status,
            COUNT(*) AS quantidade
        FROM silver_orders
        WHERE date(order_purchase_timestamp)
            BETWEEN date(?) AND date(?)
        GROUP BY order_status
        ORDER BY quantidade DESC
    """

    return read_sql(query, [data_inicial, data_final])


# =====================================================
# FORMATAÇÃO
# =====================================================

def format_brl(valor):
    valor = float(valor or 0)
    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_integer(valor):
    return f"{int(valor or 0):,}".replace(",", ".")


# =====================================================
# VERIFICAÇÃO DO BANCO
# =====================================================

if not DATABASE_PATH.exists():
    st.error(f"Banco de dados não encontrado: {DATABASE_PATH}")
    st.stop()


periodo = get_period()

if periodo.empty or pd.isna(periodo.iloc[0]["data_inicial"]):
    st.error("Não foram encontrados dados na tabela gold_vendas.")
    st.stop()


data_min = pd.to_datetime(periodo.iloc[0]["data_inicial"]).date()
data_max = pd.to_datetime(periodo.iloc[0]["data_final"]).date()


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("📊 Painel Olist")
st.sidebar.markdown("---")

st.sidebar.subheader("Filtros")

periodo_selecionado = st.sidebar.date_input(
    "Período de vendas",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
    format="DD/MM/YYYY",
)

if isinstance(periodo_selecionado, (tuple, list)):
    if len(periodo_selecionado) == 2:
        data_inicial, data_final = periodo_selecionado
    elif len(periodo_selecionado) == 1:
        data_inicial = data_final = periodo_selecionado[0]
    else:
        data_inicial, data_final = data_min, data_max
else:
    data_inicial = data_final = periodo_selecionado

categorias_disponiveis = get_categories()

categorias_selecionadas = st.sidebar.multiselect(
    "Categorias",
    options=categorias_disponiveis,
    default=categorias_disponiveis,
    help="Selecione uma ou mais categorias.",
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Fonte: Banco SQLite | Camada Gold e Silver"
)

# =====================================================
# CARREGAMENTO DOS DADOS
# =====================================================

categorias_filtro = tuple(categorias_selecionadas)

kpis, mensal, categorias_df, produtos = get_dashboard_data(
    data_inicial.isoformat(),
    data_final.isoformat(),
    categorias_filtro,
)

status_df = get_status(
    data_inicial.isoformat(),
    data_final.isoformat(),
)

if kpis.empty:
    st.error("Não foi possível calcular os indicadores.")
    st.stop()

indicadores = kpis.iloc[0]


# =====================================================
# CABEÇALHO
# =====================================================

st.title("📊 Dashboard de Análise de Vendas")
st.markdown(
    "### Brazilian E-Commerce Public Dataset — Olist"
)

st.caption(
    f"Período selecionado: "
    f"{data_inicial.strftime('%d/%m/%Y')} até "
    f"{data_final.strftime('%d/%m/%Y')}"
)

st.markdown("---")


# =====================================================
# CARTÕES DE INDICADORES
# =====================================================

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "💰 Valor vendido",
    format_brl(indicadores["valor_produtos"]),
)

col2.metric(
    "📦 Pedidos entregues",
    format_integer(indicadores["pedidos"]),
)

col3.metric(
    "🛒 Itens vendidos",
    format_integer(indicadores["itens"]),
)

col4.metric(
    "🎯 Ticket médio",
    format_brl(indicadores["ticket_medio"]),
)

col5.metric(
    "🚚 Valor do frete",
    format_brl(indicadores["frete"]),
)

st.markdown("---")


# =====================================================
# GRÁFICO 1 — EVOLUÇÃO MENSAL
# =====================================================

st.subheader("📈 Evolução mensal das vendas")

if not mensal.empty:
    fig_mensal = px.line(
        mensal,
        x="mes",
        y="valor_produtos",
        markers=True,
        labels={
            "mes": "Mês",
            "valor_produtos": "Valor vendido (R$)",
        },
        template="plotly_white",
    )

    fig_mensal.update_traces(
        line=dict(width=3),
        hovertemplate=(
            "%{x}<br>"
            "Vendas: R$ %{y:,.2f}"
            "<extra></extra>"
        ),
    )

    fig_mensal.update_layout(
        height=380,
        xaxis_title="Mês",
        yaxis_title="Valor vendido",
        hovermode="x unified",
    )

    st.plotly_chart(
        fig_mensal,
        use_container_width=True,
    )
else:
    st.info("Não existem vendas para o período selecionado.")


# =====================================================
# GRÁFICOS 2 E 3 — CATEGORIAS E STATUS
# =====================================================

col_esquerda, col_direita = st.columns(2)

with col_esquerda:
    st.subheader("🏆 Vendas por categoria")

    if not categorias_df.empty:
        top_categorias = categorias_df.head(10).sort_values(
            "valor_produtos",
            ascending=True,
        )

        fig_categorias = px.bar(
            top_categorias,
            x="valor_produtos",
            y="categoria",
            orientation="h",
            labels={
                "valor_produtos": "Valor vendido (R$)",
                "categoria": "Categoria",
            },
            template="plotly_white",
        )

        fig_categorias.update_layout(
            height=480,
            yaxis_title="",
        )

        st.plotly_chart(
            fig_categorias,
            use_container_width=True,
        )
    else:
        st.info("Sem dados de categorias.")

with col_direita:
    st.subheader("📋 Pedidos por status")

    if not status_df.empty:
        fig_status = px.pie(
            status_df,
            names="order_status",
            values="quantidade",
            hole=0.55,
            labels={
                "order_status": "Status",
                "quantidade": "Pedidos",
            },
            template="plotly_white",
        )

        fig_status.update_layout(
            height=480,
            legend_title="Status do pedido",
        )

        st.plotly_chart(
            fig_status,
            use_container_width=True,
        )
    else:
        st.info("Sem dados de status.")


# =====================================================
# GRÁFICO 4 — TOP 10 PRODUTOS
# =====================================================

st.markdown("---")
st.subheader("⭐ Top 10 produtos mais vendidos")

if not produtos.empty:
    produtos["produto_resumido"] = produtos["product_id"].str[:8]

    fig_produtos = px.bar(
        produtos.sort_values(
            "quantidade_itens",
            ascending=True,
        ),
        x="quantidade_itens",
        y="produto_resumido",
        orientation="h",
        color="valor_produtos",
        labels={
            "quantidade_itens": "Quantidade de itens",
            "produto_resumido": "Produto (ID)",
            "valor_produtos": "Valor vendido (R$)",
        },
        template="plotly_white",
        hover_data=["product_id", "categoria", "valor_produtos"],
    )

    fig_produtos.update_layout(
        height=450,
        yaxis_title="",
    )

    st.plotly_chart(
        fig_produtos,
        use_container_width=True,
    )

    st.markdown("#### Detalhamento dos produtos")

    tabela_produtos = produtos[
        [
            "product_id",
            "categoria",
            "quantidade_itens",
            "valor_produtos",
        ]
    ].copy()

    tabela_produtos["valor_produtos"] = (
        tabela_produtos["valor_produtos"].apply(format_brl)
    )

    tabela_produtos.columns = [
        "ID do produto",
        "Categoria",
        "Itens vendidos",
        "Valor vendido",
    ]

    st.dataframe(
        tabela_produtos,
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("Sem produtos para os filtros selecionados.")


# =====================================================
# RODAPÉ
# =====================================================

st.markdown("---")
st.caption(
    "Dashboard desenvolvido em Python | "
    "Streamlit + Plotly + SQLite | "
    "Projeto de Análise de Vendas Olist"
)
