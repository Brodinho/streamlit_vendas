import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Configuração da página
st.set_page_config(
    page_title="Google Trends - Dashboard de Vendas",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Análise de Pesquisas no Google")

# Inicializar pytrends com configuração mínima
def init_pytrends():
    try:
        return TrendReq(
            hl='pt-BR',
            timeout=(10,25)  # Aumentar timeout
        )
    except Exception as e:
        st.error(f"Erro ao conectar com Google Trends: {str(e)}")
        return None

# Função para limpar e validar o termo de pesquisa
def preparar_termo_pesquisa(termo):
    termo = termo.strip().lower()
    palavras = termo.split()
    if len(palavras) > 2:
        termo = ' '.join(palavras[:2])
    return termo

# Função para obter dados do Google Trends
@st.cache_data(ttl=3600)
def get_trends_data(keyword, timeframe, geo):
    max_retries = 3
    retry_delay = 5  # segundos
    
    for attempt in range(max_retries):
        try:
            # Inicializar nova sessão do pytrends
            pytrends = init_pytrends()
            if not pytrends:
                return None, None, None
                
            # Preparar o termo de pesquisa
            termo_pesquisa = preparar_termo_pesquisa(keyword)
            
            # Primeiro tenta com o período original
            try:
                pytrends.build_payload([termo_pesquisa], timeframe=timeframe, geo=geo)
                interest_over_time = pytrends.interest_over_time()
                
                # Se não encontrou dados, tenta com período maior
                if interest_over_time is None or interest_over_time.empty:
                    pytrends.build_payload([termo_pesquisa], timeframe='today 5-y', geo=geo)
                    interest_over_time = pytrends.interest_over_time()
                
                # Se ainda não encontrou dados
                if interest_over_time is None or interest_over_time.empty:
                    st.warning(f"""
                    Não foram encontradas pesquisas para '{keyword}'.
                    
                    Isso pode significar que:
                    1. Este termo tem pouquíssimo volume de buscas no Google
                    2. É uma marca/termo muito específico
                    3. As pessoas usam outras variações para pesquisar
                    
                    Sugestões:
                    ✓ Tente variações do nome (ex: nome completo, abreviações)
                    ✓ Pesquise termos relacionados ao seu produto/serviço
                    ✓ Para marcas, considere incluir o tipo de produto/serviço
                    """)
                    return None, None, None
                
                return interest_over_time, None, None
                
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None, None, None
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return None, None, None
    
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

# Conteúdo principal
if not empresa:
    st.info("""
    👋 **Bem-vindo à Análise de Pesquisas no Google!**
    
    Para começar:
    1. Digite o nome da sua empresa na barra lateral
    2. Selecione o período de análise
    3. Escolha a região de interesse
    4. Clique em "Realizar Pesquisa"
    
    Esta ferramenta mostrará:
    - Volume de pesquisas ao longo do tempo
    - Termos relacionados mais populares
    - Distribuição geográfica das pesquisas
    """)

elif not pesquisar:
    st.info("👆 Clique em 'Realizar Pesquisa' para ver os resultados.")

else:
    with st.spinner('Obtendo dados do Google Trends...'):
        geo = 'BR' if regiao == 'Brasil' else ''
        interest_over_time, related_queries, interest_by_region = get_trends_data(
            empresa, 
            periodos[periodo],
            geo
        )
    
    if interest_over_time is not None:
        # Criar abas para diferentes visualizações
        tab_tempo, tab_relacionadas, tab_regiao = st.tabs([
            "📈 Evolução Temporal",
            "🔤 Pesquisas Relacionadas",
            "🗺️ Distribuição Regional"
        ])
        
        # Aba de evolução temporal
        with tab_tempo:
            # Dicionário para tradução dos meses
            meses_pt = {
                'January': 'Janeiro',
                'February': 'Fevereiro',
                'March': 'Março',
                'April': 'Abril',
                'May': 'Maio',
                'June': 'Junho',
                'July': 'Julho',
                'August': 'Agosto',
                'September': 'Setembro',
                'October': 'Outubro',
                'November': 'Novembro',
                'December': 'Dezembro'
            }

            # Função para formatar as datas em português
            def formatar_data_pt(data):
                data_str = data.strftime('%d de %B de %Y')
                for mes_en, mes_pt in meses_pt.items():
                    data_str = data_str.replace(mes_en, mes_pt)
                return data_str

            # Gráfico de linha temporal
            fig_tempo = go.Figure()
            
            # Pegar o nome correto da coluna (primeira coluna após o índice)
            coluna_dados = interest_over_time.columns[0]
            
            # Selecionar datas para o eixo X
            datas_index = interest_over_time.index
            intervalo = len(datas_index) // 6
            datas_selecionadas = datas_index[::intervalo]
            datas_formatadas = [formatar_data_pt(data) for data in datas_selecionadas]

            # Preparar dados do hover
            hover_texts = [
                f"Data: {formatar_data_pt(data)}<br>Volume: {valor}" 
                for data, valor in zip(interest_over_time.index, interest_over_time[coluna_dados])
            ]

            fig_tempo.add_trace(go.Scatter(
                x=interest_over_time.index,
                y=interest_over_time[coluna_dados],
                mode='lines+markers',
                name='Volume de Pesquisas',
                line=dict(color='#2E64FE', width=2),
                marker=dict(size=6),
                hovertemplate="%{text}<extra></extra>",  # Formato personalizado do hover
                text=hover_texts  # Textos formatados para o hover
            ))
            
            fig_tempo.update_layout(
                title=f'Volume de Pesquisas para "{empresa}"',
                xaxis_title=None,  # Remove o título do eixo X
                yaxis_title="Volume Relativo de Pesquisas",
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                xaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    ticktext=datas_formatadas,
                    tickvals=datas_selecionadas,
                    tickangle=45,
                    nticks=6
                ),
                yaxis=dict(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128, 128, 128, 0.2)',
                )
            )
            
            st.plotly_chart(fig_tempo, use_container_width=True)
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            with col1:
                media = interest_over_time[coluna_dados].mean()
                st.metric("Média de Pesquisas", f"{media:.1f}")
            with col2:
                maximo = interest_over_time[coluna_dados].max()
                st.metric("Pico de Pesquisas", f"{maximo:.0f}")
            with col3:
                # Tratamento para evitar divisão por zero
                valor_inicial = interest_over_time[coluna_dados].iloc[0]
                valor_final = interest_over_time[coluna_dados].iloc[-1]
                if valor_inicial != 0:
                    tendencia = ((valor_final / valor_inicial - 1) * 100)
                    st.metric("Tendência", f"{tendencia:+.1f}%")
                else:
                    st.metric("Tendência", "N/A")
        
        # Aba de pesquisas relacionadas
        with tab_relacionadas:
            if related_queries is None:
                st.warning("Não foram encontradas pesquisas relacionadas para este termo.")
            else:
                termo_pesquisa = preparar_termo_pesquisa(empresa)
                try:
                    if termo_pesquisa not in related_queries or not related_queries[termo_pesquisa] or related_queries[termo_pesquisa]['top'] is None:
                        st.warning("Não há dados de pesquisas relacionadas disponíveis.")
                    else:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Top Pesquisas Relacionadas")
                            top_df = related_queries[termo_pesquisa]['top']
                            if top_df is not None and not top_df.empty:
                                st.dataframe(
                                    top_df.head(10),
                                    use_container_width=True
                                )
                            else:
                                st.info("Não há dados de top pesquisas relacionadas.")
                        
                        with col2:
                            st.subheader("Pesquisas em Crescimento")
                            rising_df = related_queries[termo_pesquisa]['rising']
                            if rising_df is not None and not rising_df.empty:
                                st.dataframe(
                                    rising_df.head(10),
                                    use_container_width=True
                                )
                            else:
                                st.info("Não há dados de pesquisas em crescimento.")
                except (KeyError, TypeError) as e:
                    st.warning("Não foi possível acessar os dados de pesquisas relacionadas.")
        
        # Aba de distribuição regional
        with tab_regiao:
            if interest_by_region is None:
                st.warning("Não foram encontrados dados regionais para este termo.")
            else:
                if interest_by_region.empty:
                    st.warning("Não há dados regionais suficientes para gerar o mapa.")
                else:
                    fig_regiao = go.Figure(data=go.Choropleth(
                        locations=interest_by_region.index,
                        z=interest_by_region[interest_by_region.columns[0]],
                        locationmode='country names' if geo == '' else 'ISO-3',
                        colorscale='Blues',
                        colorbar_title="Volume de Pesquisas"
                    ))
                    
                    fig_regiao.update_layout(
                        title=f'Distribuição Regional das Pesquisas',
                        height=600,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="white")
                    )
                    
                    st.plotly_chart(fig_regiao, use_container_width=True)
    
    # Adicionar explicação dos dados
    st.info("""
        **Sobre os Dados do Google Trends**
        
        📊 **Volume Relativo**: 
        - Os números representam o interesse de pesquisa relativo ao ponto mais alto do gráfico
        - 100 é o pico de popularidade do termo
        - 50 significa que o termo teve metade da popularidade
        - 0 significa que não houve dados suficientes
        
        ⚠️ **Importante**:
        - Os dados são normalizados e apresentados em uma escala de 0 a 100
        - As comparações são relativas ao período selecionado
        - Os dados podem ter uma defasagem de algumas horas
    """)