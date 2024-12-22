import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import locale
import math
from pathlib import Path
import sys

# Adiciona o diretório raiz ao path do Python
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from dataset import df
from utils import formatar_moeda

# Configurar locale para português brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Configuração da página
st.set_page_config(
    page_title="Clientes - Dashboard de Vendas",
    page_icon="👤",
    layout="wide",
)

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
    estados = sorted([uf for uf in df['uf'].unique() if pd.notna(uf)])  # Remove valores nulos
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

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

# Total de clientes únicos
total_clientes = df_filtrado['razao'].nunique()
with col1:
    st.metric("Total de Clientes", f"{total_clientes:,}".replace(",", "."))

# Ticket médio por cliente
ticket_medio = df_filtrado['valorNota'].mean()
with col2:
    st.metric("Ticket Médio", formatar_moeda(ticket_medio))

# Média de pedidos por cliente
media_pedidos = df_filtrado.groupby('razao')['nota'].count().mean()
with col3:
    st.metric("Média de Pedidos/Cliente", f"{media_pedidos:.1f}")

# Faturamento total
faturamento_total = df_filtrado['valorNota'].sum()
with col4:
    st.metric("Faturamento Total", formatar_moeda(faturamento_total))

# Preparar dados para os gráficos
# Top Clientes
df_top_clientes = df_filtrado.groupby('razao')['valorNota'].sum().sort_values(ascending=True).tail(10)
fig_top_clientes = go.Figure(data=[
    go.Bar(
        x=df_top_clientes.values,
        y=df_top_clientes.index,
        orientation='h',
        marker_color='#2E64FE'
    )
])
fig_top_clientes.update_layout(
    title='Top 10 Clientes por Faturamento',
    xaxis_title="Faturamento",
    yaxis_title="Cliente",
    height=400,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white")
)

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

# Criar DataFrame com as informações necessárias
df_clientes = df.groupby('codcli').agg({
    'razao': 'first',
    'cnpj': 'first',
    'emissao': 'max'  # Pega a data mais recente de compra
}).reset_index()

# Adicionar coluna de status
df_clientes['Status'] = df_clientes['emissao'].apply(determinar_status_cliente)

# Ordenar por data de última compra (mais recente primeiro)
df_clientes = df_clientes.sort_values('emissao', ascending=False)

# Formatar documento
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

# Atualizar o DataFrame com a nova formatação
df_clientes['Documento'] = df_clientes['cnpj'].apply(formatar_documento)

# Renomear colunas para exibição
df_clientes = df_clientes.rename(columns={
    'codcli': 'Código',
    'razao': 'Razão Social',
})

# Selecionar e ordenar colunas para exibição (atualizado para usar "Documento")
df_clientes = df_clientes[['Código', 'Razão Social', 'Documento', 'Status']]

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

# Exibir tabela com estilo
st.subheader("Status dos Clientes")
st.dataframe(
    df_clientes.style.applymap(
        highlight_status,
        subset=['Status']
    ),
    use_container_width=True,
    hide_index=True
)

# Adicionar métricas resumidas
col1, col2, col3, col4 = st.columns(4)

with col1:
    n_ativos = len(df_clientes[df_clientes['Status'] == 'Cliente ativo e engajado'])
    st.metric("Clientes Ativos", n_ativos)

with col2:
    n_atencao = len(df_clientes[df_clientes['Status'] == 'Cliente que precisa de atenção'])
    st.metric("Precisam de Atenção", n_atencao)

with col3:
    n_risco = len(df_clientes[df_clientes['Status'] == 'Cliente em risco de abandono'])
    st.metric("Em Risco", n_risco)

with col4:
    n_inativos = len(df_clientes[df_clientes['Status'] == 'Cliente inativo que precisa ser recuperado'])
    st.metric("Inativos", n_inativos)

# Análise Geográfica
df_estados = df_filtrado.groupby('uf')['razao'].nunique().sort_values(ascending=True)
fig_estados = go.Figure(data=[
    go.Bar(
        x=df_estados.values,
        y=df_estados.index,
        orientation='h',
        marker_color='#2E64FE'
    )
])
fig_estados.update_layout(
    title='Distribuição de Clientes por Estado',
    xaxis_title="Número de Clientes",
    yaxis_title="Estado",
    height=400,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white")
)

# Análise Geográfica - Mapa
# Dicionário com coordenadas dos estados
coordenadas_estados = {
    'AC': (-9.0238, -70.812),
    'AL': (-9.5713, -36.782),
    'AM': (-3.4168, -65.8561),
    'AP': (1.4085, -51.7957),
    'BA': (-12.9718, -38.5011),
    'CE': (-3.7172, -38.5433),
    'DF': (-15.7975, -47.8919),
    'ES': (-20.3155, -40.3128),
    'GO': (-16.6864, -49.2643),
    'MA': (-2.5297, -44.3028),
    'MG': (-19.9167, -43.9345),
    'MS': (-20.4428, -54.6464),
    'MT': (-15.601, -56.0974),
    'PA': (-1.4554, -48.4898),
    'PB': (-7.115, -34.8631),
    'PE': (-8.0476, -34.8770),
    'PI': (-5.0892, -42.8019),
    'PR': (-25.4195, -49.2646),
    'RJ': (-22.9068, -43.1729),
    'RN': (-5.7945, -35.2120),
    'RO': (-8.7619, -63.9039),
    'RR': (2.8235, -60.6758),
    'RS': (-30.0346, -51.2177),
    'SC': (-27.5954, -48.5480),
    'SE': (-10.9091, -37.0677),
    'SP': (-23.5505, -46.6333),
    'TO': (-10.2128, -48.3603)
}

# Criar DataFrame com dados do mapa
df_estados = df_filtrado.groupby('uf')['razao'].nunique().reset_index()

# Adicionar coordenadas de forma mais segura
def get_latitude(uf):
    coords = coordenadas_estados.get(uf)
    return coords[0] if coords else None

def get_longitude(uf):
    coords = coordenadas_estados.get(uf)
    return coords[1] if coords else None

df_estados['latitude'] = df_estados['uf'].apply(get_latitude)
df_estados['longitude'] = df_estados['uf'].apply(get_longitude)

# Remover estados sem coordenadas
df_estados = df_estados.dropna(subset=['latitude', 'longitude'])

# Criar mapa
fig_mapa = px.scatter_mapbox(
    df_estados,
    lat='latitude',
    lon='longitude',
    size='razao',  # Tamanho dos pontos baseado no número de clientes
    hover_name='uf',
    hover_data={'latitude': False, 'longitude': False, 'razao': True},
    color='razao',  # Cor baseada no número de clientes
    color_continuous_scale='Blues',
    labels={'razao': 'Número de Clientes'},
    zoom=3,
    title='Distribuição Geográfica de Clientes'
)

# Configurar layout do mapa
fig_mapa.update_layout(
    mapbox_style="carto-darkmatter",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=30, b=0),
    height=400,
    font=dict(color="white"),
    coloraxis_colorbar=dict(
        title="Número de Clientes",
        titleside="right",
        ticks="outside",
        tickcolor="white",
        tickfont=dict(color="white")
    )
)

# Análise Temporal
df_evolucao = df_filtrado.groupby(pd.Grouper(key='data', freq='M'))['razao'].nunique()
fig_evolucao = go.Figure(data=[
    go.Scatter(
        x=df_evolucao.index,
        y=df_evolucao.values,
        mode='lines+markers',
        line=dict(color='#2E64FE', width=2),
        marker=dict(size=8)
    )
])
fig_evolucao.update_layout(
    title='Evolução Mensal de Clientes Ativos',
    xaxis_title="Período",
    yaxis_title="Número de Clientes",
    height=400,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white")
)

# Análise de Sazonalidade
# Preparar dados de sazonalidade
df_sazonalidade = df_filtrado.copy()
df_sazonalidade['mes'] = df_sazonalidade['data'].dt.strftime('%B')  # Nome do mês
df_sazonalidade['mes_num'] = df_sazonalidade['data'].dt.month  # Número do mês

# Agrupar por mês
df_sazonalidade = df_sazonalidade.groupby(['mes', 'mes_num'])['valorNota'].agg([
    ('valorNota', 'sum'),
    ('num_clientes', 'count')
]).reset_index()

# Ordenar por mês
df_sazonalidade = df_sazonalidade.sort_values('mes_num')

# Criar gráfico de sazonalidade
fig_sazonalidade = go.Figure()

# Adicionar barras para número de clientes
fig_sazonalidade.add_trace(go.Bar(
    name='Número de Vendas',
    x=df_sazonalidade['mes'],
    y=df_sazonalidade['num_clientes'],
    yaxis='y',
    marker_color='#2E64FE',
    text=df_sazonalidade['num_clientes'],
    textposition='outside'
))

# Adicionar linha para valor total
fig_sazonalidade.add_trace(go.Scatter(
    name='Valor Total',
    x=df_sazonalidade['mes'],
    y=df_sazonalidade['valorNota'],
    yaxis='y2',
    line=dict(color='green', width=2),
    mode='lines+markers+text',
    marker=dict(size=8),
    text=[formatar_moeda(val) for val in df_sazonalidade['valorNota']],
    textposition='top center'
))

# Configurar layout
fig_sazonalidade.update_layout(
    title='Sazonalidade de Vendas',
    xaxis_title='Mês',
    yaxis=dict(
        title='Número de Vendas',
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)',
    ),
    yaxis2=dict(
        title='Valor Total',
        overlaying='y',
        side='right',
        showgrid=False,
        tickformat=',.0f'
    ),
    height=400,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ),
    xaxis=dict(tickangle=45)
)

# Segmentação por Valor
# Calcular faturamento total por cliente
df_faturamento_cliente = df_filtrado.groupby('razao')['valorNota'].sum().sort_values(ascending=True)

# Definir faixas de valor
faixas = [
    (0, 10000, 'Até R$ 10 mil'),
    (10000, 50000, 'R$ 10 mil a R$ 50 mil'),
    (50000, 100000, 'R$ 50 mil a R$ 100 mil'),
    (100000, 500000, 'R$ 100 mil a R$ 500 mil'),
    (500000, float('inf'), 'Acima de R$ 500 mil')
]

# Categorizar clientes
def categorizar_cliente(valor):
    for min_val, max_val, label in faixas:
        if min_val <= valor < max_val:
            return label
    return faixas[-1][2]

df_faixas = pd.DataFrame({
    'faixa': [categorizar_cliente(valor) for valor in df_faturamento_cliente.values],
    'valor': df_faturamento_cliente.values
})

# Calcular estatísticas por faixa
df_stats = df_faixas.groupby('faixa').agg({
    'valor': ['count', 'sum']
}).reset_index()
df_stats.columns = ['faixa', 'num_clientes', 'valor_total']

# Ordenar faixas
ordem_faixas = [faixa[2] for faixa in faixas]
df_stats['faixa'] = pd.Categorical(df_stats['faixa'], categories=ordem_faixas, ordered=True)
df_stats = df_stats.sort_values('faixa')

# Criar gráfico de faixas
fig_faixas = go.Figure()

# Adicionar barras para número de clientes
fig_faixas.add_trace(go.Bar(
    name='Número de Clientes',
    x=df_stats['faixa'],
    y=df_stats['num_clientes'],
    text=df_stats['num_clientes'],
    textposition='outside',
    yaxis='y',
    offsetgroup=1,
    marker_color='#2E64FE'
))

# Adicionar linha para valor total
fig_faixas.add_trace(go.Scatter(
    name='Valor Total',
    x=df_stats['faixa'],
    y=df_stats['valor_total'],
    text=[formatar_moeda(val) for val in df_stats['valor_total']],
    mode='lines+markers+text',
    textposition='top center',
    yaxis='y2',
    line=dict(color='green', width=2),
    marker=dict(size=8)
))

# Configurar layout do gráfico de faixas
fig_faixas.update_layout(
    title='Distribuição de Clientes por Faixa de Valor',
    xaxis_title="",
    yaxis=dict(
        title="Número de Clientes",
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)',
    ),
    yaxis2=dict(
        title="Valor Total",
        overlaying='y',
        side='right',
        showgrid=False,
        tickformat=',.0f'
    ),
    height=400,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ),
    xaxis=dict(tickangle=45)
)

# Análise de Pareto
df_pareto = pd.DataFrame({
    'cliente': df_faturamento_cliente.index,
    'valor': df_faturamento_cliente.values
})

# Calcular percentuais acumulados
df_pareto['valor_percentual'] = df_pareto['valor'] / df_pareto['valor'].sum() * 100
df_pareto['valor_acumulado'] = df_pareto['valor_percentual'].cumsum()
df_pareto['cliente_percentual'] = range(1, len(df_pareto) + 1)
df_pareto['cliente_percentual'] = df_pareto['cliente_percentual'] / len(df_pareto) * 100

# Criar gráfico de Pareto
fig_pareto = go.Figure()

# Adicionar linha de Pareto
fig_pareto.add_trace(go.Scatter(
    x=df_pareto['cliente_percentual'],
    y=df_pareto['valor_acumulado'],
    mode='lines',
    name='% Acumulado do Faturamento',
    line=dict(color='#2E64FE', width=3)
))

# Adicionar linha de referência 80/20
fig_pareto.add_trace(go.Scatter(
    x=[0, 20, 20],
    y=[0, 80, 100],
    mode='lines',
    name='Referência 80/20',
    line=dict(color='red', width=2, dash='dash')
))

# Configurar layout do gráfico de Pareto
fig_pareto.update_layout(
    title='Análise de Pareto (80/20)',
    xaxis_title="% Acumulado de Clientes",
    yaxis_title="% Acumulado do Faturamento",
    height=400,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ),
    xaxis=dict(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)',
        range=[0, 100]
    ),
    yaxis=dict(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)',
        range=[0, 100]
    )
)

# Calcular percentual para insights
percentual_80 = df_pareto[df_pareto['valor_acumulado'] <= 80]['cliente_percentual'].max()

# Criar abas
tab_visao_geral, tab_geografica, tab_temporal, tab_segmentacao = st.tabs([
    "📊 Visão Geral",
    "🗺️ Análise Geográfica", 
    "📅 Análise Temporal",
    "💰 Segmentação"
])

# Aba de Visão Geral
with tab_visao_geral:
    st.subheader("Top Clientes")
    st.plotly_chart(fig_top_clientes, use_container_width=True, key="top_clientes")
    
    st.subheader("Análise de Recência")
    st.info("""
    **O que é Análise de Recência?**
    
    A análise de recência mostra o padrão de compra dos clientes com base em sua última interação:
    
    🟦 **Últimos 30 dias**: Clientes ativos e engajados
    🟨 **31-90 dias**: Clientes que precisam de atenção
    🟧 **91-180 dias**: Clientes em risco de abandono
    🟥 **Mais de 180 dias**: Clientes inativos que precisam ser recuperados
    
    Esta análise ajuda a identificar oportunidades de reativação e retenção de clientes.
    """)
    st.plotly_chart(fig_recencia, use_container_width=True, key="recencia")

# Aba de Análise Geográfica
with tab_geografica:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_estados, use_container_width=True, key="estados")
    with col2:
        st.plotly_chart(fig_mapa, use_container_width=True, key="mapa")
    
    st.info("""
    **Análise de Concentração Geográfica**
    
    A distribuição geográfica dos clientes revela importantes insights:
    
    📍 **Concentração Regional**: 
    - {:.1f}% dos clientes estão concentrados nos 3 principais estados
    - O estado de maior concentração representa {:.1f}% da base
    
    🎯 **Oportunidades**:
    - Estados com baixa penetração podem indicar potencial de crescimento
    - Regiões de alta concentração podem necessitar de estratégias de proteção da base
    
    💡 **Implicações Estratégicas**:
    - Adequação de estratégias comerciais por região
    - Planejamento logístico e de atendimento
    """.format(
        df_estados['razao'].nlargest(3).sum() / df_estados['razao'].sum() * 100,
        df_estados['razao'].max() / df_estados['razao'].sum() * 100
    ))

# Aba de Análise Temporal
with tab_temporal:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_evolucao, use_container_width=True, key="evolucao")
    with col2:
        st.plotly_chart(fig_sazonalidade, use_container_width=True, key="sazonalidade")
    
    st.info("""
    **Análise de Sazonalidade**
    
    O comportamento temporal das vendas apresenta padrões importantes:
    
    📈 **Evolução Mensal**:
    - Crescimento médio mensal de {:.1f}% no número de clientes ativos
    - Pico de {:.0f} clientes ativos em {}
    
    📅 **Sazonalidade**:
    - Maior volume de vendas entre {} e {}
    - Período de baixa entre {} e {}
    
    💡 **Recomendações**:
    - Preparação antecipada para períodos de alta demanda
    - Estratégias específicas para períodos de baixa temporada
    """.format(
        ((df_evolucao.iloc[-1] / df_evolucao.iloc[0]) ** (1/len(df_evolucao)) - 1) * 100,
        df_evolucao.max(),
        df_evolucao.idxmax().strftime('%B/%Y'),
        df_sazonalidade.nlargest(3, 'num_clientes')['mes'].iloc[0],
        df_sazonalidade.nlargest(3, 'num_clientes')['mes'].iloc[-1],
        df_sazonalidade.nsmallest(3, 'num_clientes')['mes'].iloc[0],
        df_sazonalidade.nsmallest(3, 'num_clientes')['mes'].iloc[-1]
    ))

# Aba de Segmentação
with tab_segmentacao:
    st.info("""
    **Como interpretar o Gráfico de Pareto (80/20)?**
    
    Este gráfico mostra como o faturamento está distribuído entre os clientes:
    
    📊 **Linha Azul**: 
    - Mostra o percentual acumulado do faturamento
    - Clientes ordenados do maior para o menor
    - Quanto mais curvada, maior a concentração em poucos clientes
    
    📏 **Linha Vermelha**: 
    - Referência ideal onde 20% dos clientes representam 80% do faturamento
    - Serve como comparação para análise de concentração
    
    💡 **Como usar**: 
    - Encontre no eixo X a % de clientes que você quer analisar
    - O valor no eixo Y mostra quanto esses clientes representam do faturamento total
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_faixas, use_container_width=True, key="faixas")
    with col2:
        st.plotly_chart(fig_pareto, use_container_width=True, key="pareto")
    
    st.info("""
    **Análise de Concentração de Clientes**
    
    A segmentação por valor revela importantes insights sobre a base de clientes:
    
    💰 **Distribuição do Faturamento**:
    - {:.1f}% dos clientes representam 80% do faturamento
    - A faixa de maior valor concentra {:.1f}% do faturamento total
    - {:.1f}% dos clientes estão na faixa até R$ 10 mil
    
    🎯 **Implicações Estratégicas**:
    - Necessidade de estratégias diferenciadas por segmento
    - Foco em proteção dos principais clientes
    - Oportunidades de desenvolvimento da base
    
    ⚠️ **Pontos de Atenção**:
    - Alta dependência de poucos clientes pode representar risco
    - Potencial de crescimento em clientes de menor valor
    """.format(
        percentual_80,
        df_stats['valor_total'].max() / df_stats['valor_total'].sum() * 100,
        df_stats[df_stats['faixa'] == 'Até R$ 10 mil']['num_clientes'].iloc[0] / df_stats['num_clientes'].sum() * 100
    ))