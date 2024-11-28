import pandas as pd
import streamlit as st
import plotly.express as px
from dataset import df
from PIL import Image
from functions import formata_colunas_monetarias

backgroundColor = "000000"

image = Image.open('imagens/sales-64x64.png')

# st.set_page_config(layout='wide')
# Definir o tema como dark
st.set_page_config(page_title="Dashboard de Vendas", layout='wide', initial_sidebar_state='expanded')
st.image(image)
st.title("Dashboard de Vendas")

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

    # Deixar datas no formato pt-br
    st.dataframe(
        df.style.format(
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
        # st.metric('FATURAMENTO TOTAL', f"R$ {df['valorNota'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

