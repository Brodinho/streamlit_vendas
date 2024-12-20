import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Configuração da página deve ser a primeira chamada Streamlit
st.set_page_config(
    page_title="Gráficos - Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
)

# Adiciona o diretório raiz ao path do Python
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from dataset import df
from grafics import (criar_mapa_estado, criar_grafico_linha_mensal, 
                    criar_grafico_barras_estado, criar_grafico_barras_categoria)

# Título da página
st.title("📊 Gráficos e Visualizações")

# Dicionário com todos os gráficos disponíveis
graficos = {
    'mapa': {
        'titulo': 'Mapa de Faturamento por Estado/País',
        'funcao': criar_mapa_estado
    },
    'barras_estado': {
        'titulo': 'Gráfico de Barras - Top 5 Estados/Países',
        'funcao': criar_grafico_barras_estado
    },
    'linha_mensal': {
        'titulo': 'Gráfico de Linha - Faturamento Mensal',
        'funcao': criar_grafico_linha_mensal
    },
    'barras_categoria': {
        'titulo': 'Gráfico de Barras - Top 5 Categorias',
        'funcao': criar_grafico_barras_categoria
    }
}

# Menu lateral
with st.sidebar:
    st.header('Configuração dos Gráficos')
    st.write('Selecione os gráficos que deseja visualizar:')
    
    selecao_graficos = {}
    for key, info in graficos.items():
        selecao_graficos[key] = st.checkbox(
            info['titulo'],
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
        
        # Criar lista de gráficos selecionados
        graficos_ativos = [
            (key, info) for key, info in graficos.items() 
            if selecao_graficos.get(key, True)
        ]
        
        # Organizar gráficos em colunas
        if graficos_ativos:
            # Criar colunas
            col1, col2 = st.columns(2)
            colunas = [col1, col2]
            
            # Distribuir gráficos nas colunas
            for i, (key, info) in enumerate(graficos_ativos):
                with colunas[i % 2]:
                    fig = info['funcao'](df_ano)
                    st.plotly_chart(fig, use_container_width=True) 