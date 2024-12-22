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
            ��� Visualização em mapa para melhor contexto espacial
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
