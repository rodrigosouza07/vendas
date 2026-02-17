import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(layout="wide")

# Bloco de upload
st.title('Análise de venda por PDV Grupo Adão e Eva')
st.write('Faça o upload do arquivo CSV para iniciar a análise.')

uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")

if uploaded_file is not None:
    with st.spinner('Carregando e processando os dados...'):
        data = pd.read_csv(uploaded_file, sep=',')

        data = data.drop(columns=[
            'idcaixa', 'idusuario', 'tipomovimento',
            'idabertura', 'idrecebimento', 'vallancamento',
            'valreforcocx', 'tiporeforco'
        ])

        data = data.rename(columns={
            'idempresa': 'Caixa',
            'descrrecebimento': 'Forma de Pagamento',
            'dtmovimento': 'Data Movimento',
            'nomeusuario': 'Nome Usuario'
        })

        contagem_usuarios = data['Nome Usuario'].value_counts().reset_index()
        contagem_usuarios.columns = ['Nome Usuario', 'Quantidade']

        contagem_forma_pagamento = data['Forma de Pagamento'].value_counts().reset_index()
        contagem_forma_pagamento.columns = ['Forma de Pagamento', 'Quantidade']
        contagem_forma_pagamento = contagem_forma_pagamento[contagem_forma_pagamento['Forma de Pagamento'] != 'TROCO']

        dados_pix_tef = data[data['Forma de Pagamento'] == 'PIX TEF']
        contagem_pix_tef_operador = dados_pix_tef['Nome Usuario'].value_counts().reset_index()
        contagem_pix_tef_operador.columns = ['Nome Usuario', 'Quantidade']

        total_vendas = len(data)

    # --------------------------------------
    # GRÁFICOS
    # --------------------------------------
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    grafico = alt.Chart(contagem_usuarios).mark_bar().encode(
        x='Quantidade:Q',
        y=alt.Y('Nome Usuario:N', sort='-x')
    ).properties(title='Movimentos por Usuário', height=400)

    grafico_forma_pagamento = alt.Chart(contagem_forma_pagamento).mark_bar().encode(
        x='Quantidade:Q',
        y=alt.Y('Forma de Pagamento:N', sort='-x')
    ).properties(title='Forma de Pagamento')

    grafico_pix_tef_operador = alt.Chart(contagem_pix_tef_operador).mark_bar().encode(
        x='Quantidade:Q',
        y=alt.Y('Nome Usuario:N', sort='-x')
    ).properties(title='PIX TEF por Operador')

    fig_plotly = px.pie(
        contagem_forma_pagamento,
        names='Forma de Pagamento',
        values='Quantidade',
        title='Distribuição por Forma de Pagamento',
        hole=0.4
    )
    
    col1.altair_chart(grafico, use_container_width=True)
    col2.altair_chart(grafico_forma_pagamento, use_container_width=True)
    col3.plotly_chart(fig_plotly, use_container_width=True)
    col4.altair_chart(grafico_pix_tef_operador, use_container_width=True)

    st.bar_chart(data['Caixa'].value_counts())
        
    #somando o total de vendas de todos os caixas
    total_vendas_caixas = data['Caixa'].value_counts().sum()
    st.subheader(f'Total de vendas: {total_vendas_caixas:}');
    st.success('Gráficos gerados com sucesso!')
else:
    st.warning("Envie um arquivo CSV para visualizar a análise.")

st.markdown("""Desenvolvido por [Rodrigo Souza](https://www.linkedin.com/in/rodrigo-souza-5b9016aa/)""")