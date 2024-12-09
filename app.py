import pandas as pd
import streamlit as st
import plotly.express as px
from dataset import df
from PIL import Image
from utils import formata_colunas_monetarias, formatar_valor, formatar_moeda
from grafics import graf_map_estado, graflinha_fat_mensal, grafbar_fat_estado, graf_fat_categoria

image = Image.open('imagens/sales.png')

# Definir o tema como dark
st.set_page_config(page_title="Dashboard de Vendas", layout='wide', page_icon="📊", initial_sidebar_state='expanded')

# Dividir o layout em duas colunas
col1, col2 = st.columns([1, 6])  # Ajuste os pesos das colunas conforme necessário
with col1:
    st.image(image, use_container_width=True)
with col2:
    st.title("Dashboard de Vendas")
    st.subheader("E m p r e s a m i x")

colunas_monetarias = ["valorfaturado", "valoruni", "valoripi", "valoruni", "valoricms", "valoriss", "valorSubs", "valorFrete",
                      "valorNota", "valorContabil", "retVlrPis", "retVlrCofins", "retVlrCsll", "valorPis", "valorCofins",
                      "baseIcms", "valorCusto", "valorDesconto"
                      ]

aba1, aba2, aba3 = st.tabs(['DATAFRAME', 'VENDAS', 'VENDEDORES'])
df = formata_colunas_monetarias(df,colunas_monetarias)
with aba1:

    # Remove os separadores de milhar do dataframe, onde não há necessidade.
    df["sequencial"] = df["sequencial"].apply(lambda x: f"{x}" if pd.notnull(x) else "")
    df["os"] = df["os"].apply(lambda x: f"{x}" if pd.notnull(x) else "") 

    # Preencher célula com N/C quando for null
    df["grupo"]       = df["grupo"].fillna("N/C")
    df["subGrupo"]    = df["subGrupo"].fillna("N/C")
    df["vendedor"]    = df["vendedor"].fillna("N/C")
    df["vendedorRed"] = df["vendedorRed"].fillna("N/C")
    df["descricaoTipoOs"] = df["descricaoTipoOs"].fillna("N/C")
    df["regiao"]      = df["regiao"].fillna("N/C")

# Aplicando o CSS para ajustar a largura do input

    st.markdown("""
        <style>
        /* Ajusta a largura do input completo */
        input {
            width: 150px;  /* Ajuste a largura conforme necessário */
        }
        </style>
        """, unsafe_allow_html=True)

    # Configuração da paginação
    linhas_por_pagina = st.number_input("Linhas por página", min_value=5, max_value=50, value=10, step=5)
    total_paginas = (len(df) // linhas_por_pagina) + (1 if len(df) % linhas_por_pagina != 0 else 0)
    pagina = st.number_input("Página", min_value=1, max_value=(len(df) // linhas_por_pagina) + 1, value=1, step=1)
    st.write(f"Total de páginas: {total_paginas}")
    inicio = (pagina - 1) * linhas_por_pagina
    fim = inicio + linhas_por_pagina

    # Exibição da página atual
    pagina_df = df.iloc[inicio:fim]

    # Aplicar estilos no formato pt-br no dataframe
    st.dataframe(
        pagina_df.style.format(
            {
                # Aplica a formatação nas colunas data
                "data": lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else "",
                "emissao": lambda x: x.strftime("%d/%m/%Y") if pd.notnull(x) else "",
                }
            )
        )

    # st.dataframe(df)
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        total_faturamento = df['valorNota'].sum()
        st.metric('FATURAMENTO TOTAL', formatar_moeda(total_faturamento))
        st.plotly_chart(graf_map_estado, use_container_width=True)
        st.plotly_chart(grafbar_fat_estado, use_container_width=True)
    with coluna2:
        qtd_total_vendas = df.groupby("nota").size().reset_index(name="qtd_vendas")
        total_vendas = f'{qtd_total_vendas["qtd_vendas"].sum()} Unidades'
        st.metric("Total de vendas: ", total_vendas)
        st.plotly_chart(graflinha_fat_mensal, use_container_width=True)
        st.plotly_chart(graf_fat_categoria, use_container_width=True)

