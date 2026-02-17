import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide", page_title="Dashboard Estratégico CEO")

# --------------------------------------------------
# FUNÇÃO DE CARGA
# --------------------------------------------------
@st.cache_data
def carregar_dados(uploaded_file):
    data = pd.read_excel(uploaded_file)

    cols_to_drop = ['IDSUBPRODUTO','REFERENCIA','IDSECAO','IDSUBGRUPO']
    data = data.drop(columns=cols_to_drop, errors='ignore')

    data = data.rename(columns={
        'QTDPRODUTO': 'Quantidade',
        'LUCRO': 'Lucro',
        'CUSTOGERENCIAL': 'Custo Gerencial',
        'VALTOTLIQUIDO': 'Valor Total Liquido',
        'VALUNITBRUTO': 'Valor Unitário Bruto',
        'DESCRSECAO': 'Seção',
        'DESCRGRUPO': 'Grupo'
    })

    return data

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.image("logo.png", width=200)
    st.header("Upload de Dados")
    uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])

# --------------------------------------------------
# INÍCIO
# --------------------------------------------------
st.title("📊 Dashboard Estratégico - Visão CEO")

if uploaded_file:

    df = carregar_dados(uploaded_file)

    # --------------------------------------------------
    # VISÃO EXECUTIVA
    # --------------------------------------------------

    total_venda = df['Valor Total Liquido'].sum()
    total_lucro = df['Lucro'].sum()
    total_qtd = df['Quantidade'].sum()
    margem_geral = (total_lucro / total_venda) * 100 if total_venda > 0 else 0

    df['Margem Unitária'] = df['Valor Unitário Bruto'] - df['Custo Gerencial']
    df['Prejuízo Total'] = df['Margem Unitária'] * df['Quantidade']

    produtos_total = df['DESCRICAO'].nunique()
    produtos_prejuizo = df[df['Margem Unitária'] < 0]['DESCRICAO'].nunique()
    risco_carteira = (produtos_prejuizo / produtos_total) * 100 if produtos_total > 0 else 0
    impacto_prejuizo = df[df['Prejuízo Total'] < 0]['Prejuízo Total'].sum()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Faturamento Total", f"R$ {total_venda:,.2f}")
    c2.metric("Lucro Total", f"R$ {total_lucro:,.2f}")
    c3.metric("Margem Geral (%)", f"{margem_geral:.2f}%")
    c4.metric("Risco da Carteira (%)", f"{risco_carteira:.2f}%")

    st.metric("💣 Impacto Financeiro do Prejuízo", f"R$ {impacto_prejuizo:,.2f}")

    st.divider()

    # --------------------------------------------------
    # CURVA ABC
    # --------------------------------------------------

    st.subheader("📈 Curva ABC - Produtos")

    abc = (
        df.groupby('DESCRICAO')['Valor Total Liquido']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    abc['% Acumulado'] = abc['Valor Total Liquido'].cumsum() / abc['Valor Total Liquido'].sum() * 100

    def classificar_abc(p):
        if p <= 80:
            return 'A'
        elif p <= 95:
            return 'B'
        else:
            return 'C'

    abc['Classe ABC'] = abc['% Acumulado'].apply(classificar_abc)

    fig_abc = px.bar(
        abc.head(30),
        x='DESCRICAO',
        y='% Acumulado',
        color='Classe ABC',
        title="Classificação ABC por Faturamento"
    )

    st.plotly_chart(fig_abc, use_container_width=True)

    colA, colB, colC = st.columns(3)

    colA.metric("Produtos Classe A", abc[abc['Classe ABC'] == 'A'].shape[0])
    colB.metric("Produtos Classe B", abc[abc['Classe ABC'] == 'B'].shape[0])
    colC.metric("Produtos Classe C", abc[abc['Classe ABC'] == 'C'].shape[0])

    st.divider()

    # --------------------------------------------------
    # TOP PRODUTOS POR LUCRO (DECISÃO REAL)
    # --------------------------------------------------

    st.subheader("🏆 Top 10 Produtos por Lucro")

    top_lucro = (
        df.groupby('DESCRICAO')['Lucro']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig_top_lucro = px.bar(
        top_lucro,
        x='Lucro',
        y='DESCRICAO',
        orientation='h',
        color='Lucro'
    )

    fig_top_lucro.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_lucro, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # PRODUTOS QUE DESTROEM VALOR
    # --------------------------------------------------

    st.subheader("⚠️ Top 10 Produtos que Mais Destruíram Lucro")

    piores = (
        df.groupby('DESCRICAO')['Prejuízo Total']
        .sum()
        .sort_values()
        .head(10)
        .reset_index()
    )

    fig_piores = px.bar(
        piores,
        x='Prejuízo Total',
        y='DESCRICAO',
        orientation='h',
        color='Prejuízo Total',
        color_continuous_scale='Reds'
    )

    fig_piores.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_piores, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # ANÁLISE ESTRUTURAL DE MARGEM
    # --------------------------------------------------

    st.subheader("📊 Margem por Grupo")

    grupo = (
        df.groupby('Grupo')
        .agg({'Valor Total Liquido':'sum','Lucro':'sum'})
        .reset_index()
    )

    grupo['Margem %'] = (grupo['Lucro'] / grupo['Valor Total Liquido']) * 100

    fig_grupo = px.bar(
        grupo,
        x='Grupo',
        y='Margem %',
        color='Margem %'
    )

    st.plotly_chart(fig_grupo, use_container_width=True)
