import pandas as pd
import streamlit as st
import plotly.express as px
from dataset import df
from PIL import Image
from utils import formata_colunas_monetarias, formatar_valor, formatar_moeda
from grafics import (criar_mapa_estado, criar_grafico_linha_mensal, 
                    criar_grafico_barras_estado, criar_grafico_barras_categoria)
from config import carregar_configuracoes

image = Image.open('imagens/sales.png')

# Definir o tema como dark
st.set_page_config(page_title="Dashboard de Vendas", layout='wide', page_icon="📊", initial_sidebar_state='expanded')

# Carregar configurações
config = carregar_configuracoes()

if config is None:
    st.error('Por favor, configure o dashboard primeiro executando: streamlit run config.py')
    st.stop()

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
    try:
        # Remover registros com data nula antes de processar os anos
        df_datas_validas = df[df['data'].notna()]
        
        # Obter anos únicos apenas de datas válidas
        anos_disponiveis = sorted(df_datas_validas['data'].dt.year.unique().astype(int).tolist())
        
        # Criar o multiselect
        anos_selecionados = st.multiselect(
            'Selecione o(s) ano(s):', 
            anos_disponiveis,
            default=anos_disponiveis,
            key='anos_select'
        )
        
        # Garantir que sempre haja pelo menos um ano selecionado
        if not anos_selecionados:
            st.warning('Por favor, selecione pelo menos um ano.')
            anos_selecionados = anos_disponiveis
        
        # Filtrar o DataFrame com base nos anos selecionados, excluindo datas nulas
        df_filtrado = df_datas_validas[df_datas_validas['data'].dt.year.isin(anos_selecionados)]
        
        coluna1, coluna2 = st.columns(2)
        with coluna1:
            total_faturamento = df_filtrado['valorNota'].sum()
            st.metric('FATURAMENTO TOTAL', formatar_moeda(total_faturamento))
            
            # Criar os gráficos com dados filtrados
            if config.get('mapa', True):
                st.subheader('Mapa de Faturamento por Estado/País')
                graf_map_estado = criar_mapa_estado(df_filtrado)
                st.plotly_chart(graf_map_estado, use_container_width=True)

            if config.get('barras_estado', True):
                st.subheader('Top 5 Estados/Países por Faturamento')
                grafbar_fat_estado = criar_grafico_barras_estado(df_filtrado)
                st.plotly_chart(grafbar_fat_estado, use_container_width=True)

            if config.get('linha_mensal', True):
                st.subheader('Faturamento Mensal')
                graflinha_fat_mensal = criar_grafico_linha_mensal(df_filtrado)
                st.plotly_chart(graflinha_fat_mensal, use_container_width=True)
            
        with coluna2:
            qtd_total_vendas = df_filtrado.groupby("nota").size().reset_index(name="qtd_vendas")
            total_vendas = f'{qtd_total_vendas["qtd_vendas"].sum()} Unidades'
            st.metric("Total de vendas: ", total_vendas)
            
            grafico_barras_categoria = criar_grafico_barras_categoria(df_filtrado)
            
            st.plotly_chart(grafico_barras_categoria, use_container_width=True)
            
    except Exception as e:
        st.error(f'Ocorreu um erro ao carregar os dados. Por favor, selecione pelo menos um ano.')
        st.error(f'Detalhes do erro: {str(e)}')

