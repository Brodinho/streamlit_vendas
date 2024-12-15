import streamlit as st
import pandas as pd
from dataset import df
from grafics import (criar_mapa_estado, criar_grafico_linha_mensal, 
                    criar_grafico_barras_estado, criar_grafico_barras_categoria)

# Configuração da página
st.set_page_config(
    page_title="Gráficos - Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
)

# Título da página
st.title("📊 Gráficos e Visualizações")

# Menu lateral
with st.sidebar:
    st.header('Configuração dos Gráficos')
    st.write('Selecione os gráficos que deseja visualizar:')
    
    graficos = {
        'mapa': 'Mapa de Faturamento por Estado/País',
        'barras_estado': 'Gráfico de Barras - Top 5 Estados/Países',
        'linha_mensal': 'Gráfico de Linha - Faturamento Mensal',
        'barras_categoria': 'Gráfico de Barras - Faturamento por Categoria'
    }
    
    selecao_graficos = {}
    for key, descricao in graficos.items():
        selecao_graficos[key] = st.checkbox(
            descricao,
            value=True,
            key=f'check_{key}_graficos'
        )

# Conteúdo principal
anos_disponiveis = sorted(df['data'].dt.year.dropna().unique().astype(int))
if anos_disponiveis:
    anos_selecionados = st.multiselect(
        'Selecione o(s) ano(s):', 
        ['Todos'] + [str(ano) for ano in anos_disponiveis],
        default=['Todos']
    )
    
    if not anos_selecionados:
        st.warning('É necessário escolher ao menos um ano ou período')
    else:
        # Filtrar dados pelos anos selecionados
        if 'Todos' in anos_selecionados:
            df_ano = df.copy()
        else:
            anos_int = [int(ano) for ano in anos_selecionados]
            df_ano = df[df['data'].dt.year.isin(anos_int)]
        
        # Layout em colunas
        col1, col2 = st.columns(2)
        
        # Mapa de Faturamento por Estado
        if selecao_graficos.get('mapa', True):
            with col1:
                fig_map = criar_mapa_estado(df_ano)
                st.plotly_chart(fig_map, use_container_width=True)
        
        # Gráfico de Barras - Top 5 Estados
        if selecao_graficos.get('barras_estado', True):
            with col2:
                fig_barras = criar_grafico_barras_estado(df_ano)
                st.plotly_chart(fig_barras, use_container_width=True)
        
        # Gráfico de Linha - Faturamento Mensal
        if selecao_graficos.get('linha_mensal', True):
            with col1:
                fig_linha = criar_grafico_linha_mensal(df_ano)
                st.plotly_chart(fig_linha, use_container_width=True)
        
        # Gráfico de Barras - Faturamento por Categoria
        if selecao_graficos.get('barras_categoria', True):
            with col2:
                fig_categoria = criar_grafico_barras_categoria(df_ano)
                st.plotly_chart(fig_categoria, use_container_width=True) 