import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Análise Adão e Eva")

# --------------------------------------------------
# FUNÇÃO PARA CARREGAR E TRATAR DADOS
# --------------------------------------------------
@st.cache_data
def carregar_dados(uploaded_file):
    data = pd.read_excel(uploaded_file)

    # Remover colunas desnecessárias
    cols_to_drop = [
        'IDSUBPRODUTO', 'REFERENCIA',
        'IDSECAO', 'IDSUBGRUPO'
    ]
    #se não encontrar a coluna, não lançar erro
    data = data.drop(columns=cols_to_drop, errors='ignore')

    # Renomear colunas
    data = data.rename(columns={
        'QTDPRODUTO': 'Quantidade',
        'LUCRO': 'Lucro',
        'CUSTOGERENCIAL': 'Custo Gerencial',
        'CUSTONOTAFISCAL': 'Custo Nota Fiscal',
        'VALTOTLIQUIDO': 'Valor Total Liquido',
        'VALUNITBRUTO': 'Valor Unitário Bruto',
        'DESCRSECAO': 'Seção',
        'IDPRODUTO': 'Código Produto',
        'DESCRGRUPO': 'Grupo',
    })

    return data

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.image("logo.png", width=200)
    st.header("Configurações de Dados")

    uploaded_file = st.file_uploader(
        "Faça upload da planilha Excel (.xlsx)",
        type=['xlsx']
    )

    if uploaded_file:
        st.success("Arquivo pronto para análise!")
    else:
        st.info("Aguardando arquivo...")
        
    mostrar_prejuizo = st.checkbox("Mostrar apenas produtos com prejuízo")

# --------------------------------------------------
# ÁREA PRINCIPAL
# --------------------------------------------------
st.title("Análise de Venda Gerencial - Grupo Adão e Eva")

if uploaded_file is not None:
    try:
        data = carregar_dados(uploaded_file)

        # ---------------- FILTROS ----------------
        with st.sidebar:
            st.divider()
            st.subheader("Filtros Avançados")

            descricao = st.multiselect(
                "Descrição",
                options=data['DESCRICAO'].unique()
            )

            secao = st.multiselect(
                "Seção",
                options=data['Seção'].unique()
            )

            grupo = st.multiselect(
                "Grupo",
                options=data['Grupo'].unique()
            )

        df_filtrado = data.copy()

        if descricao:
            df_filtrado = df_filtrado[df_filtrado['DESCRICAO'].isin(descricao)]
        if secao:
            df_filtrado = df_filtrado[df_filtrado['Seção'].isin(secao)]
        if grupo:
            df_filtrado = df_filtrado[df_filtrado['Grupo'].isin(grupo)]

        # ---------------- MÉTRICAS ----------------
        st.subheader("Resumo Geral")

        total_venda = df_filtrado['Valor Total Liquido'].sum()
        total_lucro = df_filtrado['Lucro'].sum()
        total_qtd = df_filtrado['Quantidade'].sum()

        lucratividade = (
            (total_lucro / total_venda) * 100
            if total_venda > 0 else 0
        )

        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Faturamento Total", f"R$ {total_venda:,.2f}")
        m2.metric("Lucro Total", f"R$ {total_lucro:,.2f}")
        m3.metric("Qtd Itens Vendidos", f"{total_qtd:,.0f}")
        m4.metric("Lucratividade %", f"{lucratividade:.2f}%")
        
        st.divider()

      # ---------------- Prejuizo ----------------
        if mostrar_prejuizo:
            df_filtrado = df_filtrado[
            df_filtrado["Valor Unitário Bruto"] <
            df_filtrado["Custo Gerencial"]
    ]
      
        # ---------------- TOP 10 ----------------
        st.subheader("Performance Positiva")

        top_produtos = (
            df_filtrado
            .groupby('DESCRICAO')['Valor Total Liquido']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig_top = px.bar(
            top_produtos,
            x='Valor Total Liquido',
            y='DESCRICAO',
            orientation='h',
            color='Valor Total Liquido',
            color_continuous_scale='Blues'
        )

        fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)

        st.divider()

        # ---------------- PIORES PRODUTOS ----------------
        st.subheader("Análise de Baixo Desempenho")

        piores_produtos = (
            df_filtrado
            .groupby('DESCRICAO')['Valor Total Liquido']
            .sum()
            .sort_values()
            .head(10)
            .reset_index()
        )

        fig_piores = px.bar(
            piores_produtos,
            x='Valor Total Liquido',
            y='DESCRICAO',
            orientation='h',
            color='Valor Total Liquido',
            color_continuous_scale='Reds'
        )

        fig_piores.update_layout(yaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig_piores, use_container_width=True)

        st.divider()

        # ---------------- GRÁFICOS DE LUCRATIVIDADE ----------------
        col1, col2 = st.columns(2)

        # Lucratividade por Seção
        with col1:
            st.subheader("Lucratividade por Seção")

            df_secao = (
                df_filtrado
                .groupby("Seção")
                .agg({"Valor Total Liquido": "sum", "Lucro": "sum"})
                .reset_index()
            )

            df_secao["Lucratividade %"] = (
                df_secao["Lucro"] /
                df_secao["Valor Total Liquido"]
            ) * 100

            fig_secao = px.pie(
                df_secao,
                names="Seção",
                values="Lucratividade %",
                hole=0.4
            )

            st.plotly_chart(fig_secao, use_container_width=True)

        # Lucratividade por Grupo
        with col2:
            st.subheader("Lucratividade por Grupo")

            df_grupo = (
                df_filtrado
                .groupby("Grupo")
                .agg({"Valor Total Liquido": "sum", "Lucro": "sum"})
                .reset_index()
            )

            df_grupo["Lucratividade %"] = (
                df_grupo["Lucro"] /
                df_grupo["Valor Total Liquido"]
            ) * 100

            fig_grupo = px.pie(
                df_grupo,
                names="Grupo",
                values="Lucratividade %",
                hole=0.4
            )
            
            st.plotly_chart(fig_grupo, use_container_width=True)
            
        st.divider()

        # ---------------- ANÁLISE CUSTO X VALOR UNITÁRIO ----------------
        st.subheader("Análise: Custo Gerencial vs Valor Unitário")

        df_scatter = df_filtrado.copy()

        # Remover valores nulos ou zero
        df_scatter = df_scatter[
            (df_scatter["Valor Unitário Bruto"] > 0) &
            (df_scatter["Custo Gerencial"] > 0)
        ]

        fig_scatter = px.scatter(
            df_scatter,
            x="Valor Unitário Bruto",
            y="Custo Gerencial",
            color="Grupo",  # pode trocar para "Seção" se preferir
            hover_data=["DESCRICAO", "Lucro"],
            title="Dispersão - Custo Gerencial vs Valor Unitário"
        )

        # Linha de referência (Custo = Valor)
        max_val = max(
            df_scatter["Valor Unitário Bruto"].max(),
            df_scatter["Custo Gerencial"].max()
        )

        fig_scatter.add_shape(
            type="line",
            x0=0, y0=0,
            x1=max_val, y1=max_val,
            line=dict(color="red", dash="dash"),
        )

        fig_scatter.update_layout(
            xaxis_title="Valor Unitário Bruto",
            yaxis_title="Custo Gerencial"
        )

        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.divider()
        st.subheader("Indicadores Estratégicos de Margem")

        df_margem = df_filtrado.copy()

        df_margem["Margem Unitária"] = (
            df_margem["Valor Unitário Bruto"] - df_margem["Custo Gerencial"]
        )

        df_margem["Status"] = df_margem["Margem Unitária"].apply(
            lambda x: "Prejuízo" if x < 0 else "Saudável"
        )

        total_produtos = df_margem["DESCRICAO"].nunique()
        produtos_prejuizo = df_margem[df_margem["Status"] == "Prejuízo"]["DESCRICAO"].nunique()

        percentual_risco = (
            (produtos_prejuizo / total_produtos) * 100
            if total_produtos > 0 else 0
        )

        c1, c2, c3 = st.columns(3)

        c1.metric("Produtos Únicos", total_produtos)
        c2.metric("Produtos com Prejuízo", produtos_prejuizo)
        c3.metric("Risco da Carteira (%)", f"{percentual_risco:.2f}%")

        st.divider()
        st.subheader("Top 10 Maiores Prejuízos Unitários")

        ranking_prejuizo = (
                df_margem[df_margem["Margem Unitária"] < 0]
                .groupby("DESCRICAO")["Margem Unitária"]
                .mean()
                .sort_values()
                .head(10)
                .reset_index()
            )

        fig_ranking = px.bar(
                ranking_prejuizo,
                x="Margem Unitária",
                y="DESCRICAO",
                orientation="h",
                color="Margem Unitária",
                color_continuous_scale="Reds"
            )

        fig_ranking.update_layout(
                yaxis={'categoryorder': 'total ascending'}
            )

        st.plotly_chart(fig_ranking, use_container_width=True)

        st.subheader("Impacto Financeiro dos Produtos com Prejuízo")

        df_prejuizo_total = df_margem.copy()
        df_prejuizo_total["Prejuízo Total"] = (
                df_prejuizo_total["Margem Unitária"] * df_prejuizo_total["Quantidade"]
            )

        impacto_total = df_prejuizo_total[
                df_prejuizo_total["Prejuízo Total"] < 0
            ]["Prejuízo Total"].sum()

        st.metric("Impacto Financeiro Total (R$)", f"R$ {impacto_total:,.2f}")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")