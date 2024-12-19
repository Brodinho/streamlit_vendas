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

# Gráficos
st.subheader("Análise Gráfica")

# Top 10 clientes
df_top_clientes = df_filtrado.groupby('razao')['valorNota'].sum().sort_values(ascending=True).tail(10)

fig_top_clientes = go.Figure()
fig_top_clientes.add_trace(go.Bar(
    y=df_top_clientes.index,
    x=df_top_clientes.values,
    text=[formatar_moeda(val) for val in df_top_clientes.values],
    textposition='outside',
    orientation='h',
    marker_color=['green' if i == len(df_top_clientes)-1 else '#636EFA' for i in range(len(df_top_clientes))]
))

# Configurar eixo X (valores monetários)
max_valor = df_top_clientes.max()
step = 1000000  # Step de 1 milhão
num_steps = math.ceil(max_valor / step)
max_escala = num_steps * step
tick_values = [i * step for i in range(num_steps + 1)]

fig_top_clientes.update_layout(
    title='Top 10 Clientes por Faturamento',
    xaxis_title="",
    yaxis_title="",
    xaxis=dict(
        tickmode="array",
        tickvals=tick_values,
        ticktext=[formatar_moeda(x) for x in tick_values],
        range=[0, max_escala],
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)'
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    height=400,
    showlegend=False
)

# Exibir gráfico
st.plotly_chart(fig_top_clientes, use_container_width=True)

# Análise de Recência
st.subheader("Análise de Recência")

# Adicionar texto explicativo
st.info("""
    **O que é Análise de Recência?**
    
    A recência indica há quanto tempo cada cliente realizou sua última compra:
    - **Últimos 30 dias**: Clientes que compraram no último mês
    - **31-90 dias**: Clientes que compraram entre 1 e 3 meses atrás
    - **91-180 dias**: Clientes que compraram entre 3 e 6 meses atrás
    - **Mais de 180 dias**: Clientes que não compram há mais de 6 meses
""")

# Calcular última compra de cada cliente
ultima_compra = df_filtrado.groupby('razao')['data'].max()
data_atual = df_filtrado['data'].max()
recencia = (data_atual - ultima_compra).dt.days

# Criar faixas de recência
def categorizar_recencia(dias):
    if dias <= 30:
        return 'Últimos 30 dias'
    elif dias <= 90:
        return '31-90 dias'
    elif dias <= 180:
        return '91-180 dias'
    else:
        return 'Mais de 180 dias'

recencia_categorizada = recencia.apply(categorizar_recencia)
contagem_recencia = recencia_categorizada.value_counts()

# Criar gráfico de pizza diretamente com os dados
fig_recencia = px.pie(
    values=contagem_recencia.values,
    names=contagem_recencia.index,
    title='Distribuição de Clientes por Recência de Compra'
)

# Customizar o hover
fig_recencia.update_traces(
    hovertemplate="<br>".join([
        "Período: %{label}",
        "Quantidade de Clientes: %{value:,.0f}",
        "<extra></extra>"
    ])
)

fig_recencia.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white")
)

# Exibir gráfico
st.plotly_chart(fig_recencia, use_container_width=True)

# Análise Geográfica
st.subheader("Distribuição Geográfica")

# Criar duas colunas para os gráficos
col1, col2 = st.columns(2)

with col1:
    # Dicionário de estados
    estados_dict = {
        'AC': 'Acre',
        'AL': 'Alagoas',
        'AP': 'Amapá',
        'AM': 'Amazonas',
        'BA': 'Bahia',
        'CE': 'Ceará',
        'DF': 'Distrito Federal',
        'ES': 'Espírito Santo',
        'GO': 'Goiás',
        'MA': 'Maranhão',
        'MT': 'Mato Grosso',
        'MS': 'Mato Grosso do Sul',
        'MG': 'Minas Gerais',
        'PA': 'Pará',
        'PB': 'Paraíba',
        'PR': 'Paraná',
        'PE': 'Pernambuco',
        'PI': 'Piauí',
        'RJ': 'Rio de Janeiro',
        'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul',
        'RO': 'Rondônia',
        'RR': 'Roraima',
        'SC': 'Santa Catarina',
        'SP': 'São Paulo',
        'SE': 'Sergipe',
        'TO': 'Tocantins',
        'EX': 'EX'  # Mantido como está
    }
    
    # Análise por Estado
    df_estados = df_filtrado.groupby('uf')['razao'].nunique().sort_values(ascending=True)
    
    # Criar gráfico de barras horizontais
    fig_estados = go.Figure()
    fig_estados.add_trace(go.Bar(
        y=df_estados.index,
        x=df_estados.values,
        text=df_estados.values,
        textposition='outside',
        orientation='h',
        marker_color=['green' if i == len(df_estados)-1 else '#636EFA' for i in range(len(df_estados))],
        hovertemplate="<br>".join([
            "Estado: %{customdata}",
            "Quantidade de Clientes: %{x:,.0f}",
            "<extra></extra>"
        ]),
        customdata=[estados_dict.get(uf, uf) for uf in df_estados.index]
    ))
    
    # Configurar layout
    fig_estados.update_layout(
        title='Número de Clientes por Estado',
        xaxis_title="",
        yaxis_title="",
        showlegend=False,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            dtick=20
        )
    )
    
    st.plotly_chart(fig_estados, use_container_width=True)

with col2:
    # Dicionário de coordenadas das capitais
    coordenadas = {
        'AC': {'lat': -9.975377, 'lon': -67.824897, 'regiao': 'Norte'},
        'AL': {'lat': -9.665972, 'lon': -35.735117, 'regiao': 'Nordeste'},
        'AP': {'lat': 0.034934, 'lon': -51.066753, 'regiao': 'Norte'},
        'AM': {'lat': -3.119028, 'lon': -60.021731, 'regiao': 'Norte'},
        'BA': {'lat': -12.971606, 'lon': -38.501587, 'regiao': 'Nordeste'},
        'CE': {'lat': -3.731862, 'lon': -38.526669, 'regiao': 'Nordeste'},
        'DF': {'lat': -15.794229, 'lon': -47.882166, 'regiao': 'Centro-Oeste'},
        'ES': {'lat': -20.310055, 'lon': -40.296432, 'regiao': 'Sudeste'},
        'GO': {'lat': -16.686882, 'lon': -49.264789, 'regiao': 'Centro-Oeste'},
        'MA': {'lat': -2.532621, 'lon': -44.298914, 'regiao': 'Nordeste'},
        'MT': {'lat': -15.601411, 'lon': -56.097892, 'regiao': 'Centro-Oeste'},
        'MS': {'lat': -20.464146, 'lon': -54.615895, 'regiao': 'Centro-Oeste'},
        'MG': {'lat': -19.916681, 'lon': -43.934493, 'regiao': 'Sudeste'},
        'PA': {'lat': -1.455833, 'lon': -48.490277, 'regiao': 'Norte'},
        'PB': {'lat': -7.119496, 'lon': -34.845016, 'regiao': 'Nordeste'},
        'PR': {'lat': -25.427337, 'lon': -49.273356, 'regiao': 'Sul'},
        'PE': {'lat': -8.057838, 'lon': -34.882897, 'regiao': 'Nordeste'},
        'PI': {'lat': -5.089967, 'lon': -42.809588, 'regiao': 'Nordeste'},
        'RJ': {'lat': -22.906847, 'lon': -43.172897, 'regiao': 'Sudeste'},
        'RN': {'lat': -5.794478, 'lon': -35.211675, 'regiao': 'Nordeste'},
        'RS': {'lat': -30.034647, 'lon': -51.217658, 'regiao': 'Sul'},
        'RO': {'lat': -8.761160, 'lon': -63.901089, 'regiao': 'Norte'},
        'RR': {'lat': 2.819725, 'lon': -60.672683, 'regiao': 'Norte'},
        'SC': {'lat': -27.596910, 'lon': -48.549172, 'regiao': 'Sul'},
        'SP': {'lat': -23.550520, 'lon': -46.633308, 'regiao': 'Sudeste'},
        'SE': {'lat': -10.916206, 'lon': -37.077466, 'regiao': 'Nordeste'},
        'TO': {'lat': -10.249091, 'lon': -48.324285, 'regiao': 'Norte'}
    }
    
    # Cores para cada região (tons mais escuros)
    cores_regiao = {
        'Norte': '#FF4D4D',      # Vermelho mais escuro
        'Nordeste': '#2E64FE',   # Azul mais escuro
        'Centro-Oeste': '#8000FF', # Roxo mais escuro
        'Sudeste': '#088A4B',    # Verde mais escuro
        'Sul': '#FF8C00'         # Laranja mais escuro
    }
    
    # Preparar dados para o mapa
    df_mapa = df_filtrado[df_filtrado['uf'] != 'EX'].groupby('uf')['razao'].nunique().reset_index()
    
    # Adicionar coordenadas e região ao DataFrame
    df_mapa['lat'] = df_mapa['uf'].map(lambda x: coordenadas[x]['lat'])
    df_mapa['lon'] = df_mapa['uf'].map(lambda x: coordenadas[x]['lon'])
    df_mapa['regiao'] = df_mapa['uf'].map(lambda x: coordenadas[x]['regiao'])
    df_mapa['cor'] = df_mapa['regiao'].map(cores_regiao)
    
    # Criar mapa
    fig_mapa = px.scatter_mapbox(
        df_mapa,
        lat='lat',
        lon='lon',
        size='razao',
        color='regiao',
        color_discrete_map=cores_regiao,
        hover_name='uf',
        hover_data={
            'regiao': True,
            'razao': True,
            'lat': False,
            'lon': False
        },
        zoom=3,
        title='Distribuição Geográfica de Clientes por Região'
    )
    
    # Configurar layout do mapa
    fig_mapa.update_layout(
        mapbox=dict(
            style="open-street-map",
            zoom=3,
            center=dict(lat=-15.7801, lon=-47.9292),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Customizar hover
    fig_mapa.update_traces(
        hovertemplate="<br>".join([
            "Estado: %{hovertext}",
            "Região: %{customdata[0]}",
            "Quantidade de Clientes: %{customdata[1]:,.0f}",
            "<extra></extra>"
        ])
    )
    
    st.plotly_chart(fig_mapa, use_container_width=True)

# Calcular concentração por região para o texto informativo
df_regiao_concentracao = df_filtrado[df_filtrado['uf'] != 'EX'].groupby('regiao')['razao'].nunique()

# Adicionar métricas de concentração
st.info("""
    **Análise de Concentração Geográfica**
    - O estado com maior número de clientes representa {:.1%} do total
    - As três principais regiões concentram {:.1%} dos clientes
""".format(
    df_estados.max() / df_estados.sum(),
    df_regiao_concentracao.nlargest(3).sum() / df_regiao_concentracao.sum()
)) 

# Análise de Produtos
st.subheader("Análise de Produtos")

# Criar duas colunas para os gráficos
col1, col2 = st.columns(2)

with col1:
    # Top 10 grupos mais vendidos
    df_grupos = df_filtrado.groupby('grupo')['valorNota'].sum().sort_values(ascending=True).tail(10)
    
    # Criar gráfico de barras horizontais para grupos
    fig_grupos = go.Figure()
    fig_grupos.add_trace(go.Bar(
        y=df_grupos.index,
        x=df_grupos.values,
        text=[formatar_moeda(val) for val in df_grupos.values],
        textposition='outside',
        orientation='h',
        marker_color=['green' if i == len(df_grupos)-1 else '#636EFA' for i in range(len(df_grupos))]
    ))
    
    # Configurar layout
    fig_grupos.update_layout(
        title='Top 10 Grupos de Produtos por Faturamento',
        xaxis_title="",
        yaxis_title="",
        showlegend=False,
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            tickformat=',.0f'
        )
    )
    
    # Customizar hover
    fig_grupos.update_traces(
        hovertemplate="<br>".join([
            "Grupo: %{y}",
            "Faturamento: %{text}",
            "<extra></extra>"
        ])
    )
    
    st.plotly_chart(fig_grupos, use_container_width=True)

with col2:
    # Análise de subgrupos com treemap
    df_hierarquia = df_filtrado.groupby(['grupo', 'subGrupo'])['valorNota'].sum().reset_index()
    
    # Criar treemap
    fig_treemap = px.treemap(
        df_hierarquia,
        path=[px.Constant("Todos"), 'grupo', 'subGrupo'],
        values='valorNota',
        title='Distribuição de Vendas por Grupo e Subgrupo',
        custom_data=['valorNota']  # Adicionar valor como custom_data
    )
    
    # Configurar layout
    fig_treemap.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=400
    )
    
    # Customizar hover
    fig_treemap.update_traces(
        hovertemplate="<br>".join([
            "Categoria: %{label}",
            "Valor: R$ %{value:,.2f}",
            "Percentual do Total: %{percentRoot:.1%}",
            "<extra></extra>"
        ])
    )
    
    st.plotly_chart(fig_treemap, use_container_width=True)

# Adicionar insights sobre produtos
st.info("""
    **Análise de Concentração de Produtos**
    - O grupo de produtos mais vendido representa {:.1%} do faturamento total
    - Os três principais grupos concentram {:.1%} das vendas
    - Existem {} subgrupos ativos de produtos
""".format(
    df_grupos.max() / df_filtrado['valorNota'].sum(),
    df_grupos.nlargest(3).sum() / df_filtrado['valorNota'].sum(),
    df_filtrado['subGrupo'].nunique()
)) 

# Análise Temporal
st.subheader("Análise Temporal")

# Criar duas colunas para os gráficos
col1, col2 = st.columns(2)

with col1:
    # Evolução mensal de clientes ativos
    df_evolucao = df_filtrado.groupby(pd.Grouper(key='data', freq='M'))['razao'].nunique().reset_index()
    df_evolucao['data'] = df_evolucao['data'].dt.strftime('%b/%Y')
    
    # Criar gráfico de linha
    fig_evolucao = go.Figure()
    fig_evolucao.add_trace(go.Scatter(
        x=df_evolucao['data'],
        y=df_evolucao['razao'],
        mode='lines+markers',
        name='Clientes Ativos',
        line=dict(color='#2E64FE', width=3),
        marker=dict(size=8)
    ))
    
    # Configurar layout
    fig_evolucao.update_layout(
        title='Evolução Mensal de Clientes Ativos',
        xaxis_title="",
        yaxis_title="Número de Clientes",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            tickangle=45
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
        )
    )
    
    # Customizar hover
    fig_evolucao.update_traces(
        hovertemplate="<br>".join([
            "Período: %{x}",
            "Clientes Ativos: %{y:,.0f}",
            "<extra></extra>"
        ])
    )
    
    st.plotly_chart(fig_evolucao, use_container_width=True)

with col2:
    # Sazonalidade por mês
    df_filtrado['mes_num'] = df_filtrado['data'].dt.month  # Número do mês
    df_filtrado['mes'] = df_filtrado['data'].dt.month_name()  # Nome do mês em inglês
    
    # Mapear nomes dos meses para português
    meses_ordem = {
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
    
    # Traduzir os meses
    df_filtrado['mes'] = df_filtrado['mes'].map(meses_ordem)
    
    # Calcular sazonalidade usando o número do mês para garantir a ordem correta
    df_sazonalidade = df_filtrado.groupby(['mes_num', 'mes'])['valorNota'].sum().reset_index()
    df_sazonalidade = df_sazonalidade.sort_values('mes_num')
    
    # Criar gráfico de barras
    fig_sazonalidade = go.Figure()
    
    # Definir cores baseadas nos valores
    cores = ['#2E64FE'] * len(df_sazonalidade)  # Cor padrão azul
    idx_max = df_sazonalidade['valorNota'].values.argmax()
    idx_min = df_sazonalidade['valorNota'].values.argmin()
    cores[idx_max] = 'green'  # Maior valor em verde
    cores[idx_min] = '#FF4D4D'  # Menor valor em vermelho
    
    fig_sazonalidade.add_trace(go.Bar(
        x=df_sazonalidade['mes'],
        y=df_sazonalidade['valorNota'],
        text=[formatar_moeda(val) for val in df_sazonalidade['valorNota']],
        textposition='outside',
        marker_color=cores
    ))
    
    # Configurar layout
    fig_sazonalidade.update_layout(
        title='Sazonalidade de Vendas por Mês',
        xaxis_title="",
        yaxis_title="Faturamento",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            tickangle=45
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            tickformat=',.0f'
        )
    )
    
    # Customizar hover
    fig_sazonalidade.update_traces(
        hovertemplate="<br>".join([
            "Mês: %{x}",
            "Faturamento: %{text}",
            "<extra></extra>"
        ])
    )
    
    st.plotly_chart(fig_sazonalidade, use_container_width=True)

# Adicionar insights sobre temporalidade
st.info("""
    **Análise de Sazonalidade**
    - O mês com maior número de clientes ativos é {:.0f}% superior à média mensal
    - O período de {} a {} concentra {:.1%} do faturamento anual
""".format(
    (df_evolucao['razao'].max() / df_evolucao['razao'].mean() - 1) * 100,
    df_sazonalidade.nlargest(3, 'valorNota')['mes'].iloc[0],
    df_sazonalidade.nlargest(3, 'valorNota')['mes'].iloc[2],
    df_sazonalidade.nlargest(3, 'valorNota')['valorNota'].sum() / df_sazonalidade['valorNota'].sum()
)) 

# Análise de Segmentação por Valor
st.subheader("Segmentação por Valor")

# Criar duas colunas para os gráficos
col1, col2 = st.columns(2)

with col1:
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
        return faixas[-1][2]  # Última categoria para valores maiores
    
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
    
    # Criar gráfico de barras
    fig_faixas = go.Figure()
    
    # Adicionar barras para número de clientes
    fig_faixas.add_trace(go.Bar(
        name='Número de Clientes',
        x=df_stats['faixa'],
        y=df_stats['num_clientes'],
        text=df_stats['num_clientes'],
        textposition='outside',
        yaxis='y',
        offsetgroup=1
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
    
    # Configurar layout
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
    
    st.plotly_chart(fig_faixas, use_container_width=True)

with col2:
    # Adicionar explicação do gráfico de Pareto
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
    
    # Configurar layout
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
    
    st.plotly_chart(fig_pareto, use_container_width=True)

# Adicionar insights sobre segmentação
percentual_80 = df_pareto[df_pareto['valor_acumulado'] <= 80]['cliente_percentual'].max()
st.info("""
    **Análise de Concentração de Clientes**
    - {:.1f}% dos clientes representam 80% do faturamento
    - A faixa de maior valor concentra {:.1f}% do faturamento total
    - {:.1f}% dos clientes estão na faixa até R$ 10 mil
""".format(
    percentual_80,
    df_stats['valor_total'].max() / df_stats['valor_total'].sum() * 100,
    df_stats[df_stats['faixa'] == 'Até R$ 10 mil']['num_clientes'].iloc[0] / df_stats['num_clientes'].sum() * 100
))