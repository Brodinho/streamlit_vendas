import streamlit as st

# Primeiro comando Streamlit deve ser set_page_config
st.set_page_config(
    page_title="Clientes - Dashboard de Vendas",
    page_icon="👤",
    layout="wide",
)

# Agora as outras importações
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import locale
import math
from pathlib import Path
import sys
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Adiciona o diretório raiz ao path do Python
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

# Importações locais
from dataset import df
from utils import formatar_moeda, meses_abrev_pt, formatar_data_abrev, formatar_data_abrev_curta
from grafics import coordenadas_estados, coordenadas_paises, siglas_estados, extrair_sigla_pais

# Configurar locale para português brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Título da página
st.title("👤 Análise de Clientes")

# Sidebar com filtros
with st.sidebar:
    st.header("Filtros")
    
    # Filtro de data
    st.subheader("Período")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input(
            'Data Inicial',
            value=df['data'].min().date(),
            min_value=df['data'].min().date(),
            max_value=df['data'].max().date(),
            format="DD/MM/YYYY"
        )
    with col2:
        data_fim = st.date_input(
            'Data Final',
            value=df['data'].max().date(),
            min_value=df['data'].min().date(),
            max_value=df['data'].max().date(),
            format="DD/MM/YYYY"
        )
    
    # Filtro de estado
    estados = sorted([uf for uf in df['uf'].unique() if pd.notna(uf)])
    estados_selecionados = st.multiselect(
        'Estados',
        ['Todos'] + estados,
        default=['Todos']
    )

# Aplicar filtros
mask = (
    (df['data'].dt.date >= data_inicio) &
    (df['data'].dt.date <= data_fim)
)

if 'Todos' not in estados_selecionados:
    mask = mask & (df['uf'].isin(estados_selecionados))

df_filtrado = df.loc[mask].copy()

# Agora calcular as métricas com o df_filtrado
total_clientes = df_filtrado['razao'].nunique()
ticket_medio = df_filtrado['valorNota'].mean()
media_pedidos = df_filtrado.groupby('razao')['nota'].count().mean()
faturamento_total = df_filtrado['valorNota'].sum()

# Adicionar CSS e cards com as métricas
st.markdown(f"""
<style>
    .metric-card {{
        background-color: #2b2d3e;
        border-radius: 10px;
        padding: 15px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        text-align: center;
        height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .metric-card h3 {{
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
        margin: 0 auto;
        opacity: 0.8;
        padding: 0 5px;
        margin-bottom: 5px;
    }}
    .metric-card h2 {{
        color: #ffffff;
        font-size: 20px;
        margin: 5px auto;
        padding: 0 5px;
        white-space: nowrap;
    }}
</style>

<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 15px 0;">
    <div class="metric-card">
        <h3>Total de Clientes</h3>
        <h2>{total_clientes:,}</h2>
    </div>
    <div class="metric-card">
        <h3>Ticket Médio</h3>
        <h2>{formatar_moeda(ticket_medio)}</h2>
    </div>
    <div class="metric-card">
        <h3>Média de Pedidos</h3>
        <h2>{media_pedidos:.1f}</h2>
    </div>
    <div class="metric-card">
        <h3>Faturamento Total</h3>
        <h2>{formatar_moeda(faturamento_total)}</h2>
    </div>
</div>
""", unsafe_allow_html=True)

# Criar abas
tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🌎 Análise Geográfica", "📈 Análise Temporal"])

# Aba Visão Geral
with tab1:
    # Estilo CSS personalizado
    st.markdown("""
    <style>
        .recency-box {
            background-color: #2b2d3e;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        .recency-title {
            color: #ffffff;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .recency-intro {
            color: #ffffff;
            margin-bottom: 20px;
        }
        .recency-item {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            color: #ffffff;
        }
        .recency-conclusion {
            color: #ffffff;
            margin-top: 20px;
            font-style: italic;
        }
    </style>
    
    <div class="recency-box">
        <div class="recency-title">
            📊 Análise de Recência
        </div>
        <div class="recency-intro">
            A análise de recência é uma métrica fundamental para entender o comportamento dos clientes 
            e seu nível de engajamento com a empresa. Ela é baseada no tempo decorrido desde a última compra:
        </div>
        <div class="recency-item">
            ✅ <strong>Últimos 30 dias</strong>: Clientes ativos e engajados, que mantêm uma relação comercial recente e frequente
        </div>
        <div class="recency-item">
            ⚠️ <strong>31-90 dias</strong>: Clientes que precisam de atenção, pois estão se afastando do ciclo regular de compras
        </div>
        <div class="recency-item">
            🚨 <strong>91-180 dias</strong>: Clientes em risco de abandono, necessitando de ações de retenção
        </div>
        <div class="recency-item">
            ❗ <strong>Mais de 180 dias</strong>: Clientes inativos que precisam ser recuperados através de estratégias específicas
        </div>
        <div class="recency-conclusion">
            O gráfico abaixo mostra a distribuição dos clientes nestas categorias:
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recência
    df_recencia = df_filtrado.groupby('razao')['data'].max().apply(lambda x: (datetime.now() - x).days)
    faixas_recencia = pd.cut(df_recencia, bins=[0, 30, 90, 180, float('inf')],
                            labels=['Últimos 30 dias', '31-90 dias', '91-180 dias', 'Mais de 180 dias'])
    df_recencia = faixas_recencia.value_counts()

    fig_recencia = go.Figure(data=[
        go.Pie(
            labels=df_recencia.index,
            values=df_recencia.values,
            hole=.3
        )
    ])
    fig_recencia.update_layout(
        title='Distribuição de Recência dos Clientes',
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    # Exibir o gráfico de recência
    st.plotly_chart(fig_recencia, use_container_width=True)

    # Separador para nova seção
    st.divider()

    # Título da seção complementar
    st.markdown("""
    <style>
        .engagement-box {
            background-color: #2b2d3e;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        .engagement-title {
            color: #ffffff;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .engagement-intro {
            color: #ffffff;
            margin-bottom: 20px;
        }
    </style>
    
    <div class="engagement-box">
        <div class="engagement-title">
            📊 Indicadores de Conversão e Engajamento
        </div>
        <div class="engagement-intro">
            Análise da evolução do engajamento dos clientes e efetividade das ações de reativação.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calcular taxa de conversão de inativos para ativos
    def calcular_taxa_conversao(df):
        # Criar DataFrame com status do cliente por mês
        status_mensal = []
        
        for data in pd.date_range(df['data'].min(), df['data'].max(), freq='M'):
            # Pegar compras até o mês atual
            df_ate_mes = df[df['data'] <= data]
            
            # Calcular recência para cada cliente neste ponto no tempo
            recencia = df_ate_mes.groupby('razao')['data'].max().apply(
                lambda x: (data - x).days
            )
            
            # Classificar clientes
            inativos_anterior = set(recencia[recencia > 180].index)
            
            # Pegar compras do mês seguinte
            mes_seguinte = data + pd.DateOffset(months=1)
            df_mes_seguinte = df[
                (df['data'] > data) & 
                (df['data'] <= mes_seguinte)
            ]
            
            # Contar quantos inativos compraram no mês seguinte
            reativados = len(set(df_mes_seguinte['razao']) & inativos_anterior)
            
            status_mensal.append({
                'data': data,
                'inativos': len(inativos_anterior),
                'reativados': reativados
            })
        
        df_status = pd.DataFrame(status_mensal)
        df_status['taxa_conversao'] = (df_status['reativados'] / df_status['inativos'] * 100)
        return df_status

    # Calcular taxa de conversão
    df_conversao = calcular_taxa_conversao(df_filtrado)

    # Gráfico de taxa de conversão
    fig_conversao = go.Figure()

    fig_conversao.add_trace(go.Scatter(
        x=df_conversao['data'],
        y=df_conversao['taxa_conversao'],
        name='Taxa de Conversão',
        line=dict(color='#4169E1', width=2),
        hovertemplate='Taxa de Conversão: %{y:.1f}%<extra></extra>'
    ))

    fig_conversao.update_layout(
        title='Taxa de Conversão de Clientes Inativos para Ativos',
        xaxis_title='Período',
        yaxis_title='Taxa de Conversão (%)',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=True,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig_conversao, use_container_width=True)

    # Calcular e plotar evolução da recência média
    def calcular_recencia_media(df):
        recencia_mensal = []
        
        for data in pd.date_range(df['data'].min(), df['data'].max(), freq='M'):
            df_ate_mes = df[df['data'] <= data]
            recencia = df_ate_mes.groupby('razao')['data'].max().apply(
                lambda x: (data - x).days
            )
            
            recencia_mensal.append({
                'data': data,
                'recencia_media': recencia.mean()
            })
            
        return pd.DataFrame(recencia_mensal)

    # Calcular recência média
    df_recencia = calcular_recencia_media(df_filtrado)

    # Gráfico de evolução da recência média
    fig_recencia = go.Figure()

    fig_recencia.add_trace(go.Scatter(
        x=df_recencia['data'],
        y=df_recencia['recencia_media'],
        name='Recência Média',
        line=dict(color='#32CD32', width=2),
        hovertemplate='Recência Média: %{y:.0f} dias<extra></extra>'
    ))

    fig_recencia.update_layout(
        title='Evolução da Recência Média das Compras',
        xaxis_title='Período',
        yaxis_title='Dias desde a última compra',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=True,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig_recencia, use_container_width=True)

    # Adicionar métricas resumidas
    col1, col2 = st.columns(2)

    with col1:
        taxa_conversao_atual = df_conversao['taxa_conversao'].iloc[-1]
        st.metric(
            "Taxa de Conversão Atual", 
            f"{taxa_conversao_atual:.1f}%",
            delta=f"{taxa_conversao_atual - df_conversao['taxa_conversao'].iloc[-2]:.1f}pp"
        )

    with col2:
        recencia_atual = df_recencia['recencia_media'].iloc[-1]
        st.metric(
            "Recência Média Atual", 
            f"{recencia_atual:.0f} dias",
            delta=f"{df_recencia['recencia_media'].iloc[-2] - recencia_atual:.0f} dias",
            delta_color="inverse"
        )

    # Calcular a data mais recente do DataFrame
    data_atual = df['emissao'].max()

    # Criar função para determinar o status do cliente
    def determinar_status_cliente(ultima_compra):
        dias = (data_atual - ultima_compra).days
        if dias <= 30:
            return 'Cliente ativo e engajado'
        elif dias <= 90:
            return 'Cliente que precisa de atenção'
        elif dias <= 180:
            return 'Cliente em risco de abandono'
        else:
            return 'Cliente inativo que precisa ser recuperado'

    # Definir função para formatar documento antes de usar
    def formatar_documento(doc):
        try:
            if pd.isna(doc) or str(doc).strip() == '':
                return "Não informado"
                
            # Remove caracteres não numéricos
            doc_limpo = ''.join(filter(str.isdigit, str(doc)))
            
            # Verifica se é CPF (11 dígitos)
            if len(doc_limpo) == 11:
                return f"CPF: {doc_limpo[:3]}.{doc_limpo[3:6]}.{doc_limpo[6:9]}-{doc_limpo[9:]}"
                
            # Verifica se é CNPJ (14 dígitos)
            elif len(doc_limpo) == 14:
                return f"CNPJ: {doc_limpo[:2]}.{doc_limpo[2:5]}.{doc_limpo[5:8]}/{doc_limpo[8:12]}-{doc_limpo[12:]}"
                
            # Caso não seja nem CPF nem CNPJ
            return "Documento Inválido"
            
        except:
            return "Documento Inválido"

    # Criar DataFrame com as informações necessárias
    df_clientes = df.groupby('codcli').agg({
        'razao': 'first',
        'cnpj': 'first',
        'emissao': ['min', 'max']  # Pega a primeira e última data de compra
    }).reset_index()

    # Ajustar os nomes das colunas após o agg
    df_clientes.columns = ['Código', 'Razão Social', 'CNPJ', 'Primeira Compra', 'Última Compra']
    
    # Adicionar coluna de status baseado na última compra
    df_clientes['Status'] = df_clientes['Última Compra'].apply(determinar_status_cliente)

    # Formatar as datas
    df_clientes['Primeira Compra'] = df_clientes['Primeira Compra'].dt.strftime('%d/%m/%Y')
    df_clientes['Última Compra'] = df_clientes['Última Compra'].dt.strftime('%d/%m/%Y')

    # Formatar documento
    df_clientes['Documento'] = df_clientes['CNPJ'].apply(formatar_documento)

    # Selecionar e ordenar colunas para exibição
    df_clientes = df_clientes[[
        'Código', 
        'Razão Social', 
        'Documento', 
        'Primeira Compra',
        'Última Compra',
        'Status'
    ]]

    # Criar estilo condicional baseado no status
    def highlight_status(val):
        if val == 'Cliente ativo e engajado':
            return 'background-color: #006400; color: white'  # Verde escuro
        elif val == 'Cliente que precisa de atenção':
            return 'background-color: #CD8500; color: white'  # Laranja escuro
        elif val == 'Cliente em risco de abandono':
            return 'background-color: #8B0000; color: white'  # Vermelho escuro
        elif val == 'Cliente inativo que precisa ser recuperado':
            return 'background-color: #000000; color: #FF0000'  # Fundo preto, texto vermelho
        return ''

    # Definir ordem personalizada para os status
    ordem_status = [
        'Cliente ativo e engajado',
        'Cliente que precisa de atenção',
        'Cliente em risco de abandono',
        'Cliente inativo que precisa ser recuperado'
    ]

    # Criar categoria ordenada
    df_clientes['Status_ordem'] = pd.Categorical(
        df_clientes['Status'],
        categories=ordem_status,
        ordered=True
    )

    # Ordenar DataFrame pela ordem personalizada
    df_clientes = df_clientes.sort_values('Status_ordem')
    df_clientes = df_clientes.drop('Status_ordem', axis=1)

    # Adicionar filtro de status
    st.subheader("Filtrar por Status")
    status_selecionados = st.multiselect(
        'Selecione os status que deseja visualizar:',
        options=ordem_status,
        default=ordem_status,
        key='status_filter'
    )

    # Filtrar DataFrame baseado na seleção
    if status_selecionados:
        df_clientes_filtrado = df_clientes[df_clientes['Status'].isin(status_selecionados)]
    else:
        df_clientes_filtrado = df_clientes

    # Exibir tabela com estilo
    st.subheader("Status dos Clientes")
    st.dataframe(
        df_clientes_filtrado.style.applymap(
            highlight_status,
            subset=['Status']
        ),
        use_container_width=True,
        hide_index=True
    )

    # Atualizar métricas baseado no DataFrame filtrado
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        n_ativos = len(df_clientes_filtrado[df_clientes_filtrado['Status'] == 'Cliente ativo e engajado'])
        st.metric("Clientes Ativos", n_ativos)

    with col2:
        n_atencao = len(df_clientes_filtrado[df_clientes_filtrado['Status'] == 'Cliente que precisa de atenção'])
        st.metric("Precisam de Atenção", n_atencao)

    with col3:
        n_risco = len(df_clientes_filtrado[df_clientes_filtrado['Status'] == 'Cliente em risco de abandono'])
        st.metric("Em Risco", n_risco)

    with col4:
        n_inativos = len(df_clientes_filtrado[df_clientes_filtrado['Status'] == 'Cliente inativo que precisa ser recuperado'])
        st.metric("Inativos", n_inativos)

# Aba Análise Geográfica
with tab2:
    # Box explicativo
    st.markdown("""
    <style>
        .geo-box {
            background-color: #2b2d3e;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        .geo-title {
            color: #ffffff;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .geo-intro {
            color: #ffffff;
            margin-bottom: 20px;
        }
    </style>
    
    <div class="geo-box">
        <div class="geo-title">
            🌎 Análise Geográfica de Clientes
        </div>
        <div class="geo-intro">
            A análise geográfica permite visualizar a distribuição dos clientes por estados e países, 
            identificando concentrações regionais e oportunidades de expansão. Os dados apresentados incluem:
            <br><br>
            • Número de clientes por região<br>
            • Volume de vendas por localidade<br>
            • Visualização em mapa para melhor contexto espacial
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Criar colunas para métricas
    col1, col2, col3 = st.columns(3)

    # Métricas por localidade
    with col1:
        total_estados = df_filtrado['uf'].nunique()
        st.metric("Total de Estados", total_estados)

    with col2:
        media_clientes_estado = df_filtrado.groupby('uf')['razao'].nunique().mean()
        st.metric("Média de Clientes por Estado", f"{media_clientes_estado:.1f}")

    with col3:
        estado_mais_clientes = df_filtrado.groupby('uf')['razao'].nunique().idxmax()
        st.metric("Estado com Mais Clientes", estado_mais_clientes)

    # Distribuição de clientes por estado/país
    # Preparar dados para estados brasileiros
    df_brasil = df_filtrado[df_filtrado['uf'] != 'EX'].copy()
    df_brasil_clientes = df_brasil.groupby('uf')['razao'].nunique().reset_index()
    df_brasil_clientes['Nome_Local'] = df_brasil_clientes['uf'].map(siglas_estados)
    
    # Preparar dados para países
    df_exterior = df_filtrado[df_filtrado['uf'] == 'EX'].copy()
    df_exterior_clientes = df_exterior.groupby('pais')['razao'].nunique().reset_index()
    df_exterior_clientes['uf'] = df_exterior_clientes['pais'].apply(extrair_sigla_pais)
    df_exterior_clientes['Nome_Local'] = df_exterior_clientes['uf'].map(siglas_estados)
    
    # Combinar dados de estados e países
    df_dist_clientes = pd.concat([
        df_brasil_clientes[['uf', 'Nome_Local', 'razao']],
        df_exterior_clientes[['uf', 'Nome_Local', 'razao']]
    ], ignore_index=True)
    
    # Ordenar por número de clientes
    df_dist_clientes = df_dist_clientes.sort_values('razao', ascending=True)
    
    # Criar gráfico
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Bar(
        y=df_dist_clientes['Nome_Local'],
        x=df_dist_clientes['razao'],
        orientation='h',
        marker_color=[
            'red' if uf in coordenadas_paises.keys() else '#4169E1' 
            for uf in df_dist_clientes['uf']
        ],
        text=df_dist_clientes['razao'],
        textposition='outside',
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Qtd. Clientes: %{x:,.0f}" +
            "<extra></extra>"
        )
    ))

    fig_dist.update_layout(
        title='Distribuição de Clientes por Estado/País',
        xaxis_title='Número de Clientes',
        yaxis_title='',
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig_dist, use_container_width=True)

    # Mapa de distribuição geográfica
    def criar_mapa_clientes(df_filtrado):
        # Preparar dados para estados brasileiros
        df_brasil = df_filtrado[df_filtrado['uf'] != 'EX'].copy()
        df_brasil_clientes = df_brasil.groupby('uf')['razao'].nunique().reset_index()
        df_brasil_clientes['latitude'] = df_brasil_clientes['uf'].map(lambda x: coordenadas_estados[x]['latitude'])
        df_brasil_clientes['longitude'] = df_brasil_clientes['uf'].map(lambda x: coordenadas_estados[x]['longitude'])
        
        # Preparar dados para países
        df_exterior = df_filtrado[df_filtrado['uf'] == 'EX'].copy()
        df_exterior_clientes = df_exterior.groupby('pais')['razao'].nunique().reset_index()
        df_exterior_clientes['sigla_pais'] = df_exterior_clientes['pais'].apply(extrair_sigla_pais)
        
        # Filtrar apenas países que têm coordenadas definidas
        df_exterior_clientes = df_exterior_clientes[df_exterior_clientes['sigla_pais'].isin(coordenadas_paises.keys())]
        
        # Agora mapear as coordenadas apenas para países válidos
        df_exterior_clientes['latitude'] = df_exterior_clientes['sigla_pais'].map(lambda x: coordenadas_paises[x]['lat'])
        df_exterior_clientes['longitude'] = df_exterior_clientes['sigla_pais'].map(lambda x: coordenadas_paises[x]['lon'])
        df_exterior_clientes['uf'] = df_exterior_clientes['sigla_pais']
        
        # Combinar dados de estados e países
        df_mapa = pd.concat([
            df_brasil_clientes[['uf', 'razao', 'latitude', 'longitude']],
            df_exterior_clientes[['uf', 'razao', 'latitude', 'longitude']]
        ], ignore_index=True)
        
        # Identificar se é estado brasileiro ou país
        df_mapa['is_pais'] = df_mapa['uf'].isin(coordenadas_paises.keys())
        df_mapa['Nome_Local'] = df_mapa.apply(
            lambda x: siglas_estados.get(x['uf']) if not x['is_pais'] 
            else siglas_estados.get(x['uf'], x['uf']), axis=1
        )
        
        # Normalizar tamanho das bolhas
        scaler = MinMaxScaler(feature_range=(5, 50))
        df_mapa['bubble_size'] = scaler.fit_transform(df_mapa[['razao']])
        
        # Criar o mapa
        fig_mapa = px.scatter_mapbox(
            df_mapa,
            lat='latitude',
            lon='longitude',
            size='bubble_size',
            color='is_pais',
            color_discrete_sequence=['blue', 'red'],
            hover_name='Nome_Local',
            hover_data={
                'bubble_size': False,
                'latitude': False,
                'longitude': False,
                'is_pais': False,
                'razao': True
            },
            mapbox_style="open-street-map",
            zoom=2
        )
        
        fig_mapa.update_layout(
            title='Distribuição Geográfica de Clientes',
            height=400,
            showlegend=True,
            legend=dict(
                title="Localização",
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                itemsizing="constant"
            )
        )
        
        # Atualizar legendas
        fig_mapa.data[0].name = "Estados"
        fig_mapa.data[1].name = "Países"
        
        # Atualizar hover template
        for trace in fig_mapa.data:
            trace.hovertemplate = (
                "<b>%{hovertext}</b><br>" +
                "Qtd. Clientes: %{customdata[0]:,.0f}<br>" +
                "<extra></extra>"
            )
        
        return fig_mapa

    # Atualizar o mapa
    fig_mapa = criar_mapa_clientes(df_filtrado)
    st.plotly_chart(fig_mapa, use_container_width=True)

# Aba Análise Temporal
with tab3:
    st.markdown("""
    <style>
        .temporal-box {
            background-color: #2b2d3e;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        .temporal-title {
            color: #ffffff;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .temporal-intro {
            color: #ffffff;
            margin-bottom: 20px;
        }
    </style>
    
    <div class="temporal-box">
        <div class="temporal-title">
            📈 Evolução da Base de Clientes
        </div>
        <div class="temporal-intro">
            Análise temporal mostrando o crescimento e comportamento da base de clientes ao longo do tempo,
            incluindo número de clientes ativos, novos clientes e taxa de retenção mensal.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Preparar dados para análise temporal
    def preparar_dados_evolucao_clientes(df):
        # Criar DataFrame com data e cliente
        df_temporal = df[['data', 'razao']].copy()
        df_temporal['ano_mes'] = df_temporal['data'].dt.to_period('M')
        
        # Clientes ativos por mês
        clientes_ativos = df_temporal.groupby('ano_mes')['razao'].nunique()
        
        # Identificar primeira compra de cada cliente
        primeira_compra = df_temporal.groupby('razao')['data'].min().reset_index()
        primeira_compra['ano_mes'] = primeira_compra['data'].dt.to_period('M')
        novos_clientes = primeira_compra.groupby('ano_mes').size()
        
        # Calcular taxa de retenção
        def calcular_retencao(mes_atual, mes_anterior):
            if mes_anterior == 0:
                return 0
            return (mes_atual / mes_anterior) * 100
        
        retencao = []
        clientes_lista = list(clientes_ativos)
        for i in range(len(clientes_lista)):
            if i == 0:
                retencao.append(100)
            else:
                retencao.append(calcular_retencao(clientes_lista[i], clientes_lista[i-1]))
        
        # Criar DataFrame final
        df_evolucao = pd.DataFrame({
            'Clientes Ativos': clientes_ativos,
            'Novos Clientes': novos_clientes,
            'Taxa de Retenção (%)': retencao
        })
        
        return df_evolucao

    # Criar gráficos
    df_evolucao = preparar_dados_evolucao_clientes(df_filtrado)
    
    # Três colunas para métricas principais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ultimo_mes_ativos = df_evolucao['Clientes Ativos'].iloc[-1]
        st.metric(
            "Clientes Ativos (Último Mês)", 
            f"{ultimo_mes_ativos:,.0f}",
            f"{((ultimo_mes_ativos - df_evolucao['Clientes Ativos'].iloc[-2]) / df_evolucao['Clientes Ativos'].iloc[-2] * 100):,.1f}%"
        )
    
    with col2:
        novos_ultimo_mes = df_evolucao['Novos Clientes'].iloc[-1]
        st.metric(
            "Novos Clientes (Último Mês)", 
            f"{novos_ultimo_mes:,.0f}",
            f"{((novos_ultimo_mes - df_evolucao['Novos Clientes'].iloc[-2]) / df_evolucao['Novos Clientes'].iloc[-2] * 100):,.1f}%"
        )
    
    with col3:
        retencao_atual = df_evolucao['Taxa de Retenção (%)'].iloc[-1]
        st.metric(
            "Taxa de Retenção Atual", 
            f"{retencao_atual:.1f}%",
            f"{(retencao_atual - df_evolucao['Taxa de Retenção (%)'].iloc[-2]):,.1f}%"
        )

    # Gráfico de evolução
    fig = go.Figure()
    
    # Converter índice para string formatada
    datas_formatadas = df_evolucao.index.strftime('%Y-%m')
    
    # Adicionar linha de clientes ativos
    fig.add_trace(go.Scatter(
        x=datas_formatadas,
        y=df_evolucao['Clientes Ativos'],
        name='Clientes Ativos',
        line=dict(color='blue', width=2),
        hovertemplate='Clientes Ativos: %{y:,.0f}<extra></extra>'
    ))
    
    # Adicionar linha de novos clientes
    fig.add_trace(go.Scatter(
        x=datas_formatadas,
        y=df_evolucao['Novos Clientes'],
        name='Novos Clientes',
        line=dict(color='green', width=2),
        hovertemplate='Novos Clientes: %{y:,.0f}<extra></extra>'
    ))
    
    # Configurar layout com hover unificado
    fig.update_layout(
        title='Evolução da Base de Clientes',
        xaxis_title='Período',
        yaxis_title='Número de Clientes',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=True,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    # Formatar as datas no eixo X
    fig.update_xaxes(
        ticktext=[formatar_data_abrev(data) for data in datas_formatadas],
        tickvals=datas_formatadas
    )
    
    # Exibir gráfico
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico da taxa de retenção
    fig_retencao = go.Figure()
    
    # Converter índice para string formatada
    datas_formatadas_retencao = df_evolucao.index.strftime('%Y-%m')
    
    # Criar lista de datas formatadas para o hover
    datas_hover = [formatar_data_abrev(data) for data in datas_formatadas_retencao]
    
    # Adicionar linha de taxa de retenção
    fig_retencao.add_trace(go.Scatter(
        x=datas_formatadas_retencao,
        y=df_evolucao['Taxa de Retenção (%)'],
        name='Taxa de Retenção',
        line=dict(color='orange', width=2),
        customdata=df_evolucao['Taxa de Retenção (%)'],  # Dados para o hover
        hovertemplate='Taxa de Retenção: %{customdata:.1f}%<extra></extra>'  # Template simplificado
    ))
    
    # Configurar layout
    fig_retencao.update_layout(
        title='Taxa de Retenção Mensal',
        xaxis_title='Período',
        yaxis_title='Taxa de Retenção (%)',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=True,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    # Formatar as datas no eixo X
    fig_retencao.update_xaxes(
        ticktext=[formatar_data_abrev_curta(data) for data in datas_formatadas_retencao],
        tickvals=datas_formatadas_retencao
    )
    
    # Exibir gráfico
    st.plotly_chart(fig_retencao, use_container_width=True)

    # Separador
    st.divider()

    # Título da nova seção
    st.markdown("""
    <style>
        .freq-box {
            background-color: #2b2d3e;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        .freq-title {
            color: #ffffff;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .freq-intro {
            color: #ffffff;
            margin-bottom: 20px;
        }
    </style>
    
    <div class="freq-box">
        <div class="freq-title">
            📊 Análise de Frequência de Compras
        </div>
        <div class="freq-intro">
            Análise detalhada do comportamento de compra dos clientes, incluindo:
            <br>• Média de pedidos por cliente ao longo do tempo
            <br>• Intervalo médio entre compras
            <br>• Distribuição dos clientes por frequência
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calcular métricas de frequência
    def calcular_metricas_frequencia(df):
        # Agrupar por cliente e calcular métricas
        freq_compras = df.groupby('razao').agg({
            'data': ['count', 'min', 'max']
        }).reset_index()
        
        # Renomear colunas
        freq_compras.columns = ['Cliente', 'Total_Pedidos', 'Primeira_Compra', 'Ultima_Compra']
        
        # Calcular período ativo (em dias)
        freq_compras['Periodo_Ativo'] = (freq_compras['Ultima_Compra'] - freq_compras['Primeira_Compra']).dt.days
        
        # Calcular intervalo médio entre compras (em dias)
        freq_compras['Intervalo_Medio'] = freq_compras['Periodo_Ativo'] / (freq_compras['Total_Pedidos'] - 1)
        freq_compras['Intervalo_Medio'] = freq_compras['Intervalo_Medio'].replace([np.inf, -np.inf], 0)
        
        return freq_compras

    # Calcular métricas
    freq_compras = calcular_metricas_frequencia(df_filtrado)

    # Métricas principais em cards
    col1, col2, col3 = st.columns(3)

    with col1:
        media_pedidos = freq_compras['Total_Pedidos'].mean()
        st.metric("Média de Pedidos por Cliente", f"{media_pedidos:.1f}")

    with col2:
        intervalo_medio = freq_compras['Intervalo_Medio'].mean()
        st.metric("Intervalo Médio entre Compras", f"{intervalo_medio:.0f} dias")

    with col3:
        clientes_frequentes = len(freq_compras[freq_compras['Total_Pedidos'] > media_pedidos])
        st.metric("Clientes Acima da Média", f"{clientes_frequentes}")

    # Gráfico de evolução da média de pedidos por mês
    pedidos_mensais = df_filtrado.groupby(df_filtrado['data'].dt.to_period('M')).agg({
        'razao': 'nunique',
        'nota': 'count'
    }).reset_index()
    
    pedidos_mensais['media_pedidos'] = pedidos_mensais['nota'] / pedidos_mensais['razao']
    pedidos_mensais['data'] = pedidos_mensais['data'].astype(str)

    # Gráfico de linha para média de pedidos
    fig_media_pedidos = go.Figure()

    fig_media_pedidos.add_trace(go.Scatter(
        x=pedidos_mensais['data'],
        y=pedidos_mensais['media_pedidos'],
        name='Média de Pedidos',
        line=dict(color='#4169E1', width=2),
        customdata=pedidos_mensais['media_pedidos'],
        hovertemplate='Média de Pedidos: %{customdata:.1f}<extra></extra>'
    ))

    fig_media_pedidos.update_layout(
        title='Evolução da Média de Pedidos por Cliente',
        xaxis_title='Período',
        yaxis_title='Média de Pedidos',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=True,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    # Formatar datas no eixo X
    fig_media_pedidos.update_xaxes(
        ticktext=[formatar_data_abrev_curta(data) for data in pedidos_mensais['data']],
        tickvals=pedidos_mensais['data']
    )

    st.plotly_chart(fig_media_pedidos, use_container_width=True)

    # Distribuição de frequência de compras
    fig_dist = go.Figure()

    # Criar bins para frequência de compras
    bins = [0, 1, 2, 5, 10, float('inf')]
    labels = ['1 pedido', '2 pedidos', '3-5 pedidos', '6-10 pedidos', 'Mais de 10 pedidos']
    
    freq_compras['faixa_frequencia'] = pd.cut(freq_compras['Total_Pedidos'], bins=bins, labels=labels, right=False)
    dist_freq = freq_compras['faixa_frequencia'].value_counts().sort_index()

    fig_dist.add_trace(go.Bar(
        x=dist_freq.index,
        y=dist_freq.values,
        text=dist_freq.values,
        textposition='auto',
        marker_color='#4169E1',
        hovertemplate='Quantidade de Clientes: %{y}<extra></extra>'
    ))

    fig_dist.update_layout(
        title='Distribuição de Clientes por Frequência de Compras',
        xaxis_title='Frequência de Compras',
        yaxis_title='Número de Clientes',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=False,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig_dist, use_container_width=True)

    # Separador
    st.divider()

    # Título da nova seção
    st.markdown("""
    <style>
        .valor-box {
            background-color: #2b2d3e;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        .valor-title {
            color: #ffffff;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .valor-intro {
            color: #ffffff;
            margin-bottom: 20px;
        }
    </style>
    
    <div class="valor-box">
        <div class="valor-title">
            💰 Análise de Valor do Cliente
        </div>
        <div class="valor-intro">
            Análise do valor monetário gerado pelos clientes, incluindo:
            <br>• Evolução do ticket médio por cliente
            <br>• Valor do cliente ao longo da vida (LTV)
            <br>• Segmentação por faixa de valor
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calcular métricas de valor
    def calcular_metricas_valor(df):
        # Agrupar por cliente
        valor_clientes = df.groupby('razao').agg({
            'valorNota': ['sum', 'mean', 'count']
        }).reset_index()
        
        # Renomear colunas
        valor_clientes.columns = ['Cliente', 'Valor_Total', 'Ticket_Medio', 'Num_Compras']
        
        # Calcular LTV (valor total histórico)
        valor_clientes['LTV'] = valor_clientes['Valor_Total']
        
        return valor_clientes

    # Calcular métricas
    valor_clientes = calcular_metricas_valor(df_filtrado)

    # Métricas principais em cards
    col1, col2, col3 = st.columns(3)

    with col1:
        ticket_medio_geral = valor_clientes['Ticket_Medio'].mean()
        st.metric("Ticket Médio Geral", formatar_moeda(ticket_medio_geral))

    with col2:
        ltv_medio = valor_clientes['LTV'].mean()
        st.metric("LTV Médio", formatar_moeda(ltv_medio))

    with col3:
        clientes_alto_valor = len(valor_clientes[valor_clientes['LTV'] > ltv_medio])
        st.metric("Clientes Alto Valor", f"{clientes_alto_valor}")

    # Gráfico de evolução do ticket médio mensal
    ticket_mensal = df_filtrado.groupby(df_filtrado['data'].dt.to_period('M')).agg({
        'valorNota': 'mean'
    }).reset_index()
    
    ticket_mensal['data'] = ticket_mensal['data'].astype(str)

    # Gráfico de linha para ticket médio
    fig_ticket = go.Figure()

    fig_ticket.add_trace(go.Scatter(
        x=ticket_mensal['data'],
        y=ticket_mensal['valorNota'],
        name='Ticket Médio',
        line=dict(color='#32CD32', width=2),
        customdata=ticket_mensal['valorNota'],
        hovertemplate='Ticket Médio: R$ %{customdata:,.2f}<extra></extra>'
    ))

    fig_ticket.update_layout(
        title='Evolução do Ticket Médio',
        xaxis_title='Período',
        yaxis_title='Valor (R$)',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=True,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    # Formatar valores no eixo Y
    fig_ticket.update_yaxes(
        tickformat='R$ ,.2f'
    )

    # Formatar datas no eixo X
    fig_ticket.update_xaxes(
        ticktext=[formatar_data_abrev_curta(data) for data in ticket_mensal['data']],
        tickvals=ticket_mensal['data']
    )

    st.plotly_chart(fig_ticket, use_container_width=True)

    # Distribuição de clientes por faixa de valor (LTV)
    def definir_faixa_valor(valor):
        if valor <= 1000:
            return 'Até R$ 1.000,00'
        elif valor <= 5000:
            return 'De R$ 1.001,00 a R$ 5.000,00'
        elif valor <= 10000:
            return 'De R$ 5.001,00 a R$ 10.000,00'
        elif valor <= 50000:
            return 'De R$ 10.001,00 a R$ 50.000,00'
        else:
            return 'Acima de R$ 50.000,00'

    # Lista com a ordem correta das faixas
    ordem_faixas = [
        'Até R$ 1.000,00',
        'De R$ 1.001,00 a R$ 5.000,00',
        'De R$ 5.001,00 a R$ 10.000,00',
        'De R$ 10.001,00 a R$ 50.000,00',
        'Acima de R$ 50.000,00'
    ]

    valor_clientes['faixa_valor'] = valor_clientes['LTV'].apply(definir_faixa_valor)
    
    # Criar Series com a ordem correta
    dist_valor = pd.Series(
        index=ordem_faixas,
        data=[len(valor_clientes[valor_clientes['faixa_valor'] == faixa]) for faixa in ordem_faixas]
    )

    fig_dist_valor = go.Figure()

    fig_dist_valor.add_trace(go.Bar(
        x=dist_valor.index,
        y=dist_valor.values,
        text=dist_valor.values,
        textposition='auto',
        marker_color='#32CD32',
        hovertemplate='Quantidade de Clientes: %{y}<extra></extra>'
    ))

    fig_dist_valor.update_layout(
        title='Distribuição de Clientes por Faixa de Valor (LTV)',
        xaxis_title='Faixa de Valor',
        yaxis_title='Número de Clientes',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=False,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    st.plotly_chart(fig_dist_valor, use_container_width=True)

    # Separador
    st.divider()

    # Título da nova seção
    st.markdown("""
    <style>
        .sazon-box {
            background-color: #2b2d3e;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        .sazon-title {
            color: #ffffff;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .sazon-intro {
            color: #ffffff;
            margin-bottom: 20px;
        }
        .sazon-detail {
            color: #FFD700;
            font-style: italic;
            margin-top: 15px;
            padding: 10px;
            border-left: 3px solid #FFD700;
            background-color: rgba(255, 215, 0, 0.1);
        }
    </style>
    
    <div class="sazon-box">
        <div class="sazon-title">
            📅 Análise de Sazonalidade
        </div>
        <div class="sazon-intro">
            Análise dos padrões temporais de atividade dos clientes, incluindo:
            <br>• Variação mensal e trimestral de clientes ativos
            <br>• Períodos de maior aquisição de novos clientes
            <br>• Padrões de reativação de clientes
        </div>
        <div class="sazon-detail">
            ℹ️ Consideramos como "cliente reativado" aquele que realiza uma nova compra após um período 
            de inatividade superior a 180 dias (6 meses). Este critério nos ajuda a identificar clientes 
            que retornam após um longo período sem interação com a empresa.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Análise de clientes ativos por mês
    clientes_mes = df_filtrado.groupby(df_filtrado['data'].dt.to_period('M')).agg({
        'razao': 'nunique',
        'nota': 'count'
    }).reset_index()
    
    clientes_mes['data'] = clientes_mes['data'].astype(str)

    # Gráfico de clientes ativos por mês
    fig_ativos = go.Figure()

    fig_ativos.add_trace(go.Bar(
        x=clientes_mes['data'],
        y=clientes_mes['razao'],
        name='Clientes Ativos',
        marker_color='#4169E1',
        text=clientes_mes['razao'],
        textposition='auto',
        hovertemplate='Clientes Ativos: %{y}<extra></extra>'
    ))

    fig_ativos.update_layout(
        title='Clientes Ativos por Mês',
        xaxis_title='Período',
        yaxis_title='Número de Clientes',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=True,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    # Formatar datas no eixo X
    fig_ativos.update_xaxes(
        ticktext=[formatar_data_abrev_curta(data) for data in clientes_mes['data']],
        tickvals=clientes_mes['data']
    )

    st.plotly_chart(fig_ativos, use_container_width=True)

    # Análise de novos clientes por mês
    def identificar_novos_clientes(df):
        # Ordenar DataFrame por cliente e data
        df_sorted = df.sort_values(['razao', 'data'])
        
        # Identificar primeira compra de cada cliente
        primeira_compra = df_sorted.groupby('razao')['data'].transform('min')
        
        # Marcar como novo cliente quando a data for igual à primeira compra
        df_sorted['novo_cliente'] = df_sorted['data'] == primeira_compra
        
        return df_sorted

    df_novos = identificar_novos_clientes(df_filtrado)
    
    # Agrupar novos clientes por mês
    novos_mes = df_novos[df_novos['novo_cliente']].groupby(
        df_novos['data'].dt.to_period('M')
    )['razao'].nunique().reset_index()
    
    novos_mes['data'] = novos_mes['data'].astype(str)

    # Gráfico de novos clientes por mês
    fig_novos = go.Figure()

    fig_novos.add_trace(go.Bar(
        x=novos_mes['data'],
        y=novos_mes['razao'],
        name='Novos Clientes',
        marker_color='#32CD32',
        text=novos_mes['razao'],
        textposition='auto',
        hovertemplate='Novos Clientes: %{y}<extra></extra>'
    ))

    fig_novos.update_layout(
        title='Novos Clientes por Mês',
        xaxis_title='Período',
        yaxis_title='Número de Clientes',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=True,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    # Formatar datas no eixo X
    fig_novos.update_xaxes(
        ticktext=[formatar_data_abrev_curta(data) for data in novos_mes['data']],
        tickvals=novos_mes['data']
    )

    st.plotly_chart(fig_novos, use_container_width=True)

    # Análise de reativação de clientes
    def identificar_reativacoes(df):
        # Ordenar DataFrame por cliente e data
        df_sorted = df.sort_values(['razao', 'data'])
        
        # Calcular diferença de dias entre compras do mesmo cliente
        df_sorted['dias_ultima_compra'] = df_sorted.groupby('razao')['data'].diff().dt.days
        
        # Considerar reativação quando cliente volta após 180 dias
        df_sorted['reativacao'] = df_sorted['dias_ultima_compra'] > 180
        
        return df_sorted

    df_reativacoes = identificar_reativacoes(df_filtrado)
    
    # Agrupar reativações por mês
    reativacoes_mes = df_reativacoes[df_reativacoes['reativacao']].groupby(
        df_reativacoes['data'].dt.to_period('M')
    )['razao'].nunique().reset_index()
    
    reativacoes_mes['data'] = reativacoes_mes['data'].astype(str)

    # Gráfico de reativações por mês
    fig_reativ = go.Figure()

    fig_reativ.add_trace(go.Bar(
        x=reativacoes_mes['data'],
        y=reativacoes_mes['razao'],
        name='Clientes Reativados',
        marker_color='#FFD700',
        text=reativacoes_mes['razao'],
        textposition='auto',
        hovertemplate='Clientes Reativados: %{y}<extra></extra>'
    ))

    fig_reativ.update_layout(
        title='Reativação de Clientes por Mês',
        xaxis_title='Período',
        yaxis_title='Número de Clientes',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        showlegend=True,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    # Formatar datas no eixo X
    fig_reativ.update_xaxes(
        ticktext=[formatar_data_abrev_curta(data) for data in reativacoes_mes['data']],
        tickvals=reativacoes_mes['data']
    )

    st.plotly_chart(fig_reativ, use_container_width=True)