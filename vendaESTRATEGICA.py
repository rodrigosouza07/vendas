import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(layout="wide", page_title="Dashboard Estratégico")

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

st.title("📊 Dashboard Estratégico de Portfólio")

if uploaded_file:

    df = carregar_dados(uploaded_file)

    # --------------------------------------------------
    # TRATAMENTOS
    # --------------------------------------------------
    df['Margem Unitária'] = df['Valor Unitário Bruto'] - df['Custo Gerencial']
    df['Prejuízo Total'] = df['Margem Unitária'] * df['Quantidade']
    df['Markup'] = df['Valor Unitário Bruto'] / df['Custo Gerencial']

    total_venda = df['Valor Total Liquido'].sum()
    total_lucro = df['Lucro'].sum()
    margem_geral = (total_lucro / total_venda) * 100 if total_venda > 0 else 0

    # --------------------------------------------------
    # VISÃO EXECUTIVA
    # --------------------------------------------------
    st.subheader("🔎 Visão Executiva")

    produtos_total = df['DESCRICAO'].nunique()
    produtos_prejuizo = df[df['Margem Unitária'] < 0]['DESCRICAO'].nunique()
    risco_carteira = (produtos_prejuizo / produtos_total) * 100 if produtos_total > 0 else 0
    impacto_prejuizo = df[df['Prejuízo Total'] < 0]['Prejuízo Total'].sum()

    abc_base = (
        df.groupby('DESCRICAO')['Valor Total Liquido']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    top5 = abc_base.head(5)['Valor Total Liquido'].sum()
    indice_concentracao = (top5 / total_venda) * 100 if total_venda > 0 else 0

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Faturamento Total", f"R$ {total_venda:,.2f}")
    c2.metric("Lucro Total", f"R$ {total_lucro:,.2f}")
    c3.metric("Margem Geral (%)", f"{margem_geral:.2f}%")
    c4.metric("Concentração Top 5 (%)", f"{indice_concentracao:.2f}%")

    c5,c6 = st.columns(2)
    c5.metric("Risco da Carteira (%)", f"{risco_carteira:.2f}%")
    c6.metric("Impacto Financeiro Negativo", f"R$ {impacto_prejuizo:,.2f}")

    st.divider()

    # --------------------------------------------------
    # CURVA ABC
    # --------------------------------------------------
    st.subheader("📈 Curva ABC")

    abc_base['% Acumulado'] = abc_base['Valor Total Liquido'].cumsum() / total_venda * 100

    def classificar_abc(p):
        if p <= 80:
            return 'A'
        elif p <= 95:
            return 'B'
        else:
            return 'C'

    abc_base['Classe ABC'] = abc_base['% Acumulado'].apply(classificar_abc)

    fig_abc = px.bar(
        abc_base.head(30),
        x='DESCRICAO',
        y='% Acumulado',
        color='Classe ABC',
        title="Classificação ABC por Faturamento"
    )
    st.plotly_chart(fig_abc, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # MATRIZ ESTRATÉGICA
    # --------------------------------------------------
    # --------------------------------------------------
# MATRIZ ESTRATÉGICA (VERSÃO ROBUSTA)
# --------------------------------------------------

    st.subheader("🧠 Matriz Estratégica de Portfólio")

    df_prod = (
        df.groupby("DESCRICAO")
        .agg({
            "Valor Total Liquido": "sum",
            "Lucro": "sum",
            "Quantidade": "sum"
        })
        .reset_index()
    )

    # Evitar divisão por zero
    df_prod = df_prod[df_prod["Valor Total Liquido"] != 0]

    df_prod["Margem %"] = (
        df_prod["Lucro"] / df_prod["Valor Total Liquido"]
    ) * 100

    # Garantir tamanho positivo
    df_prod["Quantidade Ajustada"] = df_prod["Quantidade"].abs()

    # Substituir zeros por valor mínimo para evitar erro visual
    df_prod["Quantidade Ajustada"] = df_prod["Quantidade Ajustada"].replace(0, 1)

    margem_mediana = df_prod["Margem %"].median()
    venda_mediana = df_prod["Valor Total Liquido"].median()

    def classificar(row):
        if row["Valor Total Liquido"] >= venda_mediana and row["Margem %"] >= margem_mediana:
            return "⭐ Estrela"
        elif row["Valor Total Liquido"] >= venda_mediana and row["Margem %"] < margem_mediana:
            return "🐄 Caixa"
        elif row["Valor Total Liquido"] < venda_mediana and row["Margem %"] >= margem_mediana:
            return "🚀 Oportunidade"
        else:
            return "⚠ Problema"

    df_prod["Categoria Estratégica"] = df_prod.apply(classificar, axis=1)

    fig_matriz = px.scatter(
        df_prod,
        x="Valor Total Liquido",
        y="Margem %",
        color="Categoria Estratégica",
        size="Quantidade Ajustada",
        hover_data=["DESCRICAO"],
        title="Matriz Estratégica"
    )

    st.plotly_chart(fig_matriz, use_container_width=True)


    st.divider()

        # --------------------------------------------------
        # GERADORES E DESTRUIDORES DE VALOR
        # --------------------------------------------------
    st.subheader("🏆 Top 10 Geradores de Lucro")

    top_lucro = (
            df.groupby('DESCRICAO')['Lucro']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

    fig_top = px.bar(top_lucro, x='Lucro', y='DESCRICAO',
                        orientation='h', color='Lucro')
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)

    st.subheader("⚠️ Top 10 Destruidores de Valor")

    piores = (
            df.groupby('DESCRICAO')['Prejuízo Total']
            .sum()
            .sort_values()
            .head(10)
            .reset_index()
        )

    fig_piores = px.bar(piores, x='Prejuízo Total', y='DESCRICAO',
                            orientation='h', color='Prejuízo Total',
                            color_continuous_scale='Reds')
    fig_piores.update_layout(yaxis={'categoryorder':'total ascending'})
    
    st.plotly_chart(fig_piores, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # MARGEM POR GRUPO
    # --------------------------------------------------
    st.subheader("📊 Margem por Grupo")

    grupo = (
        df.groupby('Grupo')
        .agg({'Valor Total Liquido':'sum','Lucro':'sum'})
        .reset_index()
    )

    grupo['Margem %'] = grupo['Lucro'] / grupo['Valor Total Liquido'] * 100

    fig_grupo = px.bar(grupo, x='Grupo', y='Margem %',
                       color='Margem %')

    st.plotly_chart(fig_grupo, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # INSIGHTS AUTOMÁTICOS
    # --------------------------------------------------
    st.subheader("📌 Insights Estratégicos Automáticos")

    if indice_concentracao > 50:
        st.warning("Alta concentração de receita nos Top 5 produtos. Risco estrutural elevado.")

    if risco_carteira > 20:
        st.warning("Percentual elevado de produtos com prejuízo. Revisar precificação.")

    if margem_geral < 15:
        st.warning("Margem geral abaixo de 15%. Estrutura pode estar pressionada.")

    if impacto_prejuizo < 0:
        st.error("Há destruição relevante de valor no portfólio.")
