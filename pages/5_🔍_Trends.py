import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import json
import requests
import io

# Mapeamento de estados para códigos ISO
estado_para_iso = {
    'Acre': 'BRA-AC',
    'Alagoas': 'BRA-AL',
    'Amapá': 'BRA-AP',
    'Amazonas': 'BRA-AM',
    'Bahia': 'BRA-BA',
    'Ceará': 'BRA-CE',
    'Distrito Federal': 'BRA-DF',
    'Espírito Santo': 'BRA-ES',
    'Goiás': 'BRA-GO',
    'Maranhão': 'BRA-MA',
    'Mato Grosso': 'BRA-MT',
    'Mato Grosso do Sul': 'BRA-MS',
    'Minas Gerais': 'BRA-MG',
    'Pará': 'BRA-PA',
    'Paraíba': 'BRA-PB',
    'Paraná': 'BRA-PR',
    'Pernambuco': 'BRA-PE',
    'Piauí': 'BRA-PI',
    'Rio de Janeiro': 'BRA-RJ',
    'Rio Grande do Norte': 'BRA-RN',
    'Rio Grande do Sul': 'BRA-RS',
    'Rondônia': 'BRA-RO',
    'Roraima': 'BRA-RR',
    'Santa Catarina': 'BRA-SC',
    'São Paulo': 'BRA-SP',
    'Sergipe': 'BRA-SE',
    'Tocantins': 'BRA-TO'
}

# Configuraç��������������������o da página
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
        # Remover coluna isPartial se existir
        if 'isPartial' in interest_over_time.columns:
            interest_over_time = interest_over_time.drop('isPartial', axis=1)
        
        # Pegar a primeira coluna (que contém os dados de interesse)
        coluna_dados = interest_over_time.columns[0]
        st.write("DEBUG - Usando coluna:", coluna_dados)
        
        # Criar figura do Plotly
        fig = go.Figure()
        
        # Adicionar linha de tendência
        fig.add_trace(
            go.Scatter(
                x=interest_over_time.index,
                y=interest_over_time[coluna_dados],
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
                f"{interest_over_time[coluna_dados].mean():.1f}"
            )
        with col2:
            st.metric(
                "Máximo Interesse",
                f"{interest_over_time[coluna_dados].max():.0f}"
            )
        with col3:
            st.metric(
                "Mínimo Interesse",
                f"{interest_over_time[coluna_dados].min():.0f}"
            )
            
    except Exception as e:
        st.error(f"Erro ao criar o gráfico: {str(e)}")

def retry_with_backoff(func, max_retries=3, initial_delay=5):
    """Executa uma função com retry e backoff exponencial"""
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:  # Última tentativa
                raise e
            delay = initial_delay * (2 ** i)  # Backoff exponencial
            st.write(f"DEBUG - Tentativa {i+1} falhou, aguardando {delay} segundos...")
            time.sleep(delay)
    return None

def get_trends_data(keyword, timeframe, geo):
    # Inicializar valores padrão
    interest_over_time = pd.DataFrame()
    interest_by_region = pd.DataFrame()
    related_queries = pd.DataFrame()
    related_topics = pd.DataFrame()

    try:
        pytrends = init_pytrends()
        if not pytrends:
            st.error("Não foi possível inicializar o PyTrends")
            return interest_over_time, interest_by_region, related_queries, related_topics
            
        termo_pesquisa = preparar_termo_pesquisa(keyword)
        
        # 1. Obter dados temporais
        try:
            def get_temporal():
                pytrends.build_payload([termo_pesquisa], timeframe=timeframe, geo=geo)
                return pytrends.interest_over_time()
                
            temp_data = retry_with_backoff(get_temporal, max_retries=2, initial_delay=2)
            
            if temp_data is not None and not temp_data.empty:
                if 'isPartial' in temp_data.columns:
                    temp_data = temp_data.drop('isPartial', axis=1)
                interest_over_time = temp_data
            
        except Exception as e:
            st.error(f"Erro ao obter dados temporais: {str(e)}")
            
        # 2. Obter dados regionais
        try:
            def get_regional():
                return pytrends.interest_by_region(
                    resolution='REGION',
                    inc_low_vol=True,
                    inc_geo_code=False
                )
                
            region_data = retry_with_backoff(get_regional, max_retries=2, initial_delay=2)
            
            if region_data is not None and not region_data.empty:
                region_data.index = [estado_para_iso.get(estado, estado) for estado in region_data.index]
                interest_by_region = region_data
            
        except Exception as e:
            st.error(f"Erro ao obter dados regionais: {str(e)}")
            
        # 3. Dados relacionados - temporariamente desativados
        st.info("Dados relacionados temporariamente indisponíveis")
            
    except Exception as e:
        st.error(f"Erro ao conectar com Google Trends: {str(e)}")
    
    # Garantir que todos os retornos são DataFrames válidos
    return (
        interest_over_time,
        interest_by_region,
        related_queries,  # DataFrame vazio
        related_topics   # DataFrame vazio
    )

def plot_regional_data(interest_by_region, termo):
    if interest_by_region is None or interest_by_region.empty:
        st.info("Não há dados regionais disponíveis para este termo no período selecionado.")
        return
        
    try:
        # Primeiro mostrar o quadro explicativo
        with st.expander("ℹ️ Como interpretar o Mapa de Interesse Regional", expanded=True):
            st.markdown("""
            ### 🗺️ Mapa de Calor Regional
            
            O mapa mostra o interesse relativo por região no Brasil, onde:
            
            - **Cores mais escuras** = Maior interesse
            - **Cores mais claras** = Menor interesse
            
            #### 📊 Como interpretar os valores
            - **100** = Região com maior volume de pesquisas
            - **50** = Metade do volume da região mais alta
            - **0** = Volume muito baixo ou nenhuma pesquisa
            
            #### 🔍 Detalhes importantes
            - Os valores são **normalizados** (0-100)
            - Compara o interesse **entre regiões**
            - Considera o período selecionado
            - Ajusta-se por população
            
            #### 📌 Dicas de uso
            - Passe o mouse sobre os estados para ver os valores exatos
            - Consulte a tabela abaixo do mapa para rankings
            - Compare diferentes períodos para ver mudanças de interesse
            """)
        
        # Carregar GeoJSON do Brasil
        url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        try:
            response = requests.get(url)
            brazil_states = response.json()
            
            # Mapear códigos dos estados para o formato do GeoJSON
            state_id_map = {
                'BR-AC': 'AC', 'BR-AL': 'AL', 'BR-AP': 'AP', 'BR-AM': 'AM',
                'BR-BA': 'BA', 'BR-CE': 'CE', 'BR-DF': 'DF', 'BR-ES': 'ES',
                'BR-GO': 'GO', 'BR-MA': 'MA', 'BR-MT': 'MT', 'BR-MS': 'MS',
                'BR-MG': 'MG', 'BR-PA': 'PA', 'BR-PB': 'PB', 'BR-PR': 'PR',
                'BR-PE': 'PE', 'BR-PI': 'PI', 'BR-RJ': 'RJ', 'BR-RN': 'RN',
                'BR-RS': 'RS', 'BR-RO': 'RO', 'BR-RR': 'RR', 'BR-SC': 'SC',
                'BR-SP': 'SP', 'BR-SE': 'SE', 'BR-TO': 'TO'
            }
            
            # Ajustar os códigos dos estados
            interest_by_region.index = [estado.replace('BRA-', 'BR-') for estado in interest_by_region.index]
            interest_by_region.index = [state_id_map[estado] for estado in interest_by_region.index]
            
            # Verificar dados
            coluna_dados = interest_by_region.columns[0]
            
            # Criar mapa
            fig = go.Figure()
            
            fig.add_trace(go.Choropleth(
                geojson=brazil_states,
                locations=interest_by_region.index,
                z=interest_by_region[coluna_dados],
                locationmode='geojson-id',
                colorscale='Viridis',
                showscale=True,
                colorbar_title="Interesse",
                text=[f"{estado}: {valor:.0f}" for estado, valor in interest_by_region[coluna_dados].items()],
                hovertemplate="Estado: %{text}<extra></extra>",
                featureidkey='properties.sigla'
            ))
            
            fig.update_layout(
                title=f'Interesse por Região - {termo}',
                geo=dict(
                    scope='south america',
                    showframe=False,
                    showcoastlines=True,
                    projection_type='mercator',
                    center=dict(lat=-15, lon=-55),
                    projection_scale=3
                ),
                height=600,
                template='plotly_dark',
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            # Exibir o gráfico
            st.plotly_chart(fig, use_container_width=True)
            
            # Exibir tabela com os dados
            st.write("### Dados por Estado")
            df_display = interest_by_region.copy()
            df_display.columns = ['Interesse']
            df_display = df_display.sort_values('Interesse', ascending=False)
            st.dataframe(df_display)
            
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao carregar GeoJSON: {str(e)}")
            
    except Exception as e:
        st.error(f"Erro ao criar o mapa: {str(e)}")
        st.write("DEBUG - Erro detalhado:", str(e))

def plot_related_queries(related_queries):
    try:
        if not related_queries or 'top' not in related_queries:
            return
            
        top_queries = related_queries['top']
        if top_queries is None or top_queries.empty:
            return
            
        # Limitar a 10 consultas
        top_queries = top_queries.head(10)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=top_queries['value'],
            y=top_queries['query'],
            orientation='h',
            marker_color='#1f77b4'
        ))
        
        fig.update_layout(
            title='Principais Consultas Relacionadas',
            xaxis_title='Pontuação de Relevância',
            yaxis_title=None,
            template='plotly_dark',
            height=400,
            margin=dict(l=200)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info(f"Não foi possível criar o gráfico de consultas relacionadas: {str(e)}")

def plot_related_topics(related_topics):
    try:
        if not related_topics or 'top' not in related_topics:
            return
            
        top_topics = related_topics['top']
        if top_topics is None or top_topics.empty:
            return
            
        # Limitar a 10 tópicos
        top_topics = top_topics.head(10)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=top_topics['value'],
            y=top_topics['topic_title'],
            orientation='h',
            marker_color='#2ca02c'
        ))
        
        fig.update_layout(
            title='Principais Tópicos Relacionados',
            xaxis_title='Pontuação de Relevância',
            yaxis_title=None,
            template='plotly_dark',
            height=400,
            margin=dict(l=200)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.info(f"Não foi possível criar o gráfico de tópicos relacionados: {str(e)}")

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
        interest_over_time, interest_by_region, related_queries, related_topics = get_trends_data(
            empresa, 
            periodos[periodo],
            geo
        )
        
        if interest_over_time is not None:
            # Criar abas para diferentes visualizações
            tab1, tab2, tab3, tab4 = st.tabs([
                "📈 Tendências Temporais", 
                "🗺️ Interesse por Região", 
                "🔍 Consultas Relacionadas",
                "📚 Tópicos Relacionados"
            ])
            
            with tab1:
                plot_trends_data(interest_over_time)
                
            with tab2:
                if interest_by_region is not None and not interest_by_region.empty:
                    plot_regional_data(interest_by_region, empresa)
                else:
                    st.info("Não há dados regionais disponíveis para este termo no período selecionado.")
                    
            with tab3:
                if related_queries is not None and not related_queries.empty:
                    plot_related_queries(related_queries)
                else:
                    st.info("Não há consultas relacionadas disponíveis para este termo no período selecionado.")
                    
            with tab4:
                if related_topics is not None and not related_topics.empty:
                    plot_related_topics(related_topics)
                else:
                    st.info("Não há tópicos relacionados disponíveis para este termo no período selecionado.")
        else:
            st.warning("""
                Não foi possível obter dados completos do Google Trends. 
                
                Sugestões:
                - Tente um termo mais genérico
                - Selecione um período diferente
                - Aguarde alguns minutos e tente novamente
            """)