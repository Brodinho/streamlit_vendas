import pandas as pd
import streamlit as st
import plotly.express as px
from dataset import df
from PIL import Image
from utils import formata_colunas_monetarias
from grafics import graf_rec_estado

backgroundColor = "000000"

image = Image.open('imagens/sales.png')

# st.set_page_config(layout='wide')
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
                # Aplica a formatação nas colunas monetárias
                **{col: lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for col in colunas_monetarias}
                
                # Trunca as colunas para apenas duas casas decimais
                # "valorfaturado": lambda x: f"{math.floor(x * 100) / 100:.2f}" if pd.notnull(x) else "",
                # "valorNota": lambda x: f"{math.floor(x * 100) / 100:.2f}" if pd.notnull(x) else "",
                # "valoruni": lambda x: f"{math.floor(x * 100) / 100:.2f}" if pd.notnull(x) else "",
                # "quant": lambda x: f"{math.floor(x * 100) / 100:.2f}" if pd.notnull(x) else ""
                }
            )
        )

    # st.dataframe(df)
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        total_faturamento = df['valorNota'].sum()
        st.metric('FATURAMENTO TOTAL', f"R$ {total_faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.plotly_chart(graf_rec_estado, use_container_width=True)
    with coluna2:
        qtd_vendas = df.groupby("nota").size().reset_index(name="qtd_vendas")
        total_vendas = qtd_vendas["qtd_vendas"].sum()
        st.metric("Total de vendas: ", total_vendas)

