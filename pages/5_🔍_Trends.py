import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Google Trends - Dashboard de Vendas",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Análise de Pesquisas no Google")

# Definir todas as funções primeiro
def init_pytrends():
    try:
        return TrendReq(
            hl='pt-BR',
            timeout=(10,25)
        )
    except Exception as e:
        st.error(f"Erro ao conectar com Google Trends: {str(e)}")
        return None

def preparar_termo_pesquisa(termo):
    termo = termo.strip().lower()
    palavras = termo.split()
    if len(palavras) > 2:
        termo = ' '.join(palavras[:2])
    return termo

def plot_trends_data(interest_over_time):
    if interest_over_time is None or interest_over_time.empty:
        st.error("Não há dados disponíveis para exibir")
        return
        
    try:
        # Criar figura do Plotly
        fig = go.Figure()
        
        # Adicionar linha de tendência
        fig.add_trace(
            go.Scatter(
                x=interest_over_time.index,
                y=interest_over_time['Interesse ao longo do tempo'],
                mode='lines',
                name='Interesse ao longo do tempo',
                line=dict(color='#1f77b4', width=2)
            )
        )
        
        # Calcular datas para mostrar (apenas 6 marcações)
        dates = interest_over_time.index
        n_ticks = 6
        tick_indices = np.linspace(0, len(dates)-1, n_ticks, dtype=int)
        tick_values = dates[tick_indices]
        
        # Configurar layout
        fig.update_layout(
            title='Tendência de Pesquisas no Google',
            xaxis=dict(
                title=None,
                ticktext=[d.strftime('%d/%m/%Y') for d in tick_values],
                tickvals=tick_values,
                tickangle=45,
                tickfont=dict(size=10)
            ),
            yaxis_title='Volume de Pesquisas (0-100)',
            template='plotly_dark',
            height=500,
            showlegend=True,
            hovermode='x unified',
            margin=dict(b=120, l=60, r=40, t=40)
        )
        
        # Exibir o gráfico
        st.plotly_chart(fig, use_container_width=True)
        
        # Exibir estatísticas básicas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Média de Interesse",
                f"{interest_over_time['Interesse ao longo do tempo'].mean():.1f}"
            )
        with col2:
            st.metric(
                "Máximo Interesse",
                f"{interest_over_time['Interesse ao longo do tempo'].max():.0f}"
            )
        with col3:
            st.metric(
                "Mínimo Interesse",
                f"{interest_over_time['Interesse ao longo do tempo'].min():.0f}"
            )
            
    except Exception as e:
        st.error(f"Erro ao criar o gráfico: {str(e)}")

@st.cache_data(ttl=3600)
def get_trends_data(keyword, timeframe, geo):
    try:
        # Inicializar pytrends
        pytrends = init_pytrends()
        if not pytrends:
            return None, None, None
            
        # Preparar o termo de pesquisa
        termo_pesquisa = preparar_termo_pesquisa(keyword)
        
        # Obter dados temporais
        pytrends.build_payload([termo_pesquisa], timeframe=timeframe, geo=geo)
        interest_over_time = pytrends.interest_over_time()
        
        if interest_over_time is not None and not interest_over_time.empty:
            # Remover a coluna isPartial se existir
            if 'isPartial' in interest_over_time.columns:
                interest_over_time = interest_over_time.drop('isPartial', axis=1)
            
            # Renomear a coluna
            interest_over_time = interest_over_time.rename(
                columns={termo_pesquisa: 'Interesse ao longo do tempo'}
            )
            
            return interest_over_time, None, None
            
        return None, None, None
            
    except Exception as e:
        return None, None, None

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações da Análise")
    
    # Campo para nome da empresa
    empresa = st.text_input("Nome da Empresa")
    
    # Seleção de período
    periodos = {
        'Última semana': 'now 7-d',
        'Último mês': 'today 1-m',
        'Últimos 3 meses': 'today 3-m',
        'Último ano': 'today 12-m',
        'Últimos 5 anos': 'today 5-y'
    }
    
    periodo = st.selectbox(
        "Selecione o período",
        options=list(periodos.keys()),
        index=2
    )
    
    # Região
    regiao = st.selectbox(
        "Selecione a região",
        options=['Brasil', 'Mundial'],
        index=0
    )
    
    # Botão de pesquisa
    pesquisar = st.button("🔍 Realizar Pesquisa", type="primary")

# Depois de definir todas as funções, colocar o código principal
if not empresa:
    st.info("👋 Digite o nome da empresa na barra lateral e clique em 'Realizar Pesquisa'")
elif not pesquisar:
    st.info("👆 Clique em 'Realizar Pesquisa' para ver os resultados.")
else:
    with st.spinner('Obtendo dados do Google Trends...'):
        geo = 'BR' if regiao == 'Brasil' else ''
        interest_over_time, _, _ = get_trends_data(
            empresa, 
            periodos[periodo],
            geo
        )
        
        if interest_over_time is not None:
            plot_trends_data(interest_over_time)
        else:
            st.error("Não foi possível obter dados do Google Trends")