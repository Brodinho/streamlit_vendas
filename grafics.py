import streamlit as st
import pandas as pd
import plotly.express as px
import locale
from datetime import datetime
from utils import formatar_moeda
from dataset import df  # Importar o DataFrame diretamente do dataset.py
import plotly.graph_objects as go
from utils import formatar_moeda, criar_df_fat_estado
import math
from sklearn.preprocessing import MinMaxScaler

# Configurar locale para português brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Dicionário para tradução dos meses (mantendo o nome como meses_pt)
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

# Datas mínima e máxima para o filtro
min_date = df['data'].min().date()
max_date = df['data'].max().date()

# Configuração do estilo do calendário
st.markdown("""
    <style>
        .stDateInput {
            font-family: 'Arial';
        }
        .stDateInput input {
            text-align: center;
        }
        div[data-baseweb="calendar"] {
            font-family: 'Arial';
        }
        div[data-baseweb="calendar"] button {
            font-family: 'Arial';
        }
    </style>
""", unsafe_allow_html=True)

# Filtros na sidebar
with st.sidebar:
    st.header("Filtros")
    
    # Filtro de data com formato brasileiro
    dates = st.date_input(
        "Filtros de vendedores",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY",
        key="date_filter",
        help="Selecione o período desejado"
    )
    
    if len(dates) == 2:
        start_date, end_date = dates
        mask = (df['data'].dt.date >= start_date) & (df['data'].dt.date <= end_date)
        df_filtrado = df.loc[mask].copy()
    else:
        df_filtrado = df.copy()

# Criar métricas por vendedor
df_metricas = df_filtrado.groupby('vendedor', as_index=False).agg({
    'nota': 'count',
    'valorNota': ['sum', 'mean']
})

# Achatar as colunas multi-índice
df_metricas.columns = ['Vendedor', 'Pedidos', 'Valor Total', 'Ticket Médio']

# Ordenar por Pedidos (decrescente)
df_metricas = df_metricas.sort_values('Pedidos', ascending=False)

# Resetar índice começando do 1
df_metricas.index = range(1, len(df_metricas) + 1)

# Formatar valores monetários
df_metricas['Valor Total'] = df_metricas['Valor Total'].apply(formatar_moeda)
df_metricas['Ticket Médio'] = df_metricas['Ticket Médio'].apply(formatar_moeda)

# Exibir métricas com índice começando em 1
st.subheader("Métricas por Vendedor")
st.dataframe(
    df_metricas,
    use_container_width=True,
    hide_index=False
)

# Preparar dados para o gráfico de barras
df_graph = df_filtrado.groupby('vendedor', as_index=False)['valorNota'].sum()
df_graph = df_graph.sort_values('valorNota', ascending=False)
df_graph.columns = ['vendedor', 'valor']

# Criar gráfico
fig = px.bar(
    df_graph,
    x='vendedor',
    y='valor',
    title='Análise Gráfica'
)

# Configurar formato brasileiro para os valores do eixo Y
def formato_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Atualizar layout do gráfico
fig.update_layout(
    xaxis_title="Vendedor",
    yaxis_title="Valor Total",
    showlegend=False,
    height=400,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    yaxis=dict(
        tickformat=",",
        ticktext=[formato_br(val) for val in fig.layout.yaxis.tickvals] if fig.layout.yaxis.tickvals else []
    )
)

# Formatar valores nas barras
fig.update_traces(
    text=[formato_br(val) for val in df_graph['valor']],
    textposition='outside',
    texttemplate='%{text}'
)

# Exibir gráfico
st.plotly_chart(fig, use_container_width=True)

# Dicionário de estados
siglas_estados = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins",
    "EUA": "Estados Unidos", "COL": "Colômbia", "PER": "Peru", "ARG": "Argentina",
    "ELS": "El Salvador", "MEX": "México", "CHI": "Chile", "GUA": "Guatemala",
    "HON": "Honduras", "NIC": "Nicarágua", "PAN": "Panamá", "BOL": "Bolívia",
    "URU": "Uruguai", "PAR": "Paraguai", "CRI": "Costa Rica"
}

def criar_mapa_estado(df_filtrado):
    # Criar DataFrame com faturamento por estado
    df_fat_estado = criar_df_fat_estado(df_filtrado)
    
    # Adicionar nome do estado e formatar faturamento
    df_fat_estado['Nome_Estado'] = df_fat_estado['uf'].map(siglas_estados)
    df_fat_estado['Faturamento Total'] = df_fat_estado['valorfaturado'].apply(formatar_moeda)
    
    # Normalizar tamanho das bolhas
    scaler = MinMaxScaler(feature_range=(5, 50))
    df_fat_estado['bubble_size'] = scaler.fit_transform(df_fat_estado[['valorfaturado']])
    
    # Criar o mapa
    fig = px.scatter_mapbox(
        df_fat_estado,
        lat='latitude',
        lon='longitude',
        size='bubble_size',
        color_discrete_sequence=['blue'],
        hover_name='Nome_Estado',
        hover_data={
            'bubble_size': False,
            'latitude': False,
            'longitude': False,
            'Faturamento Total': True
        },
        mapbox_style="open-street-map",
        zoom=3
    )
    
    fig.update_layout(
        coloraxis_colorbar_tickformat="R$,.2f",
        height=400
    )
    
    return fig

def criar_grafico_linha_mensal(df_filtrado):
    # Configurar locale para formatação brasileira
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    
    # Remover linhas com datas nulas
    df_filtrado = df_filtrado.dropna(subset=['data'])
    
    # Criar DataFrame com as informações necessárias
    df_mensal = df_filtrado.assign(
        Ano=df_filtrado['data'].dt.year,
        Mês=df_filtrado['data'].dt.month_name().map(meses_pt),
        Num_Mês=df_filtrado['data'].dt.month
    )
    
    # Agrupar os dados usando valorNota
    df_mensal = df_mensal.groupby(['Mês', 'Ano', 'Num_Mês'])['valorNota'].sum().reset_index()
    df_mensal = df_mensal.sort_values(['Ano', 'Num_Mês'])
    
    # Criar lista com todos os meses em ordem
    meses_ordem = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Criar gráfico
    fig = px.line(
        df_mensal,
        x='Mês',
        y='valorNota',
        color=df_mensal['Ano'].astype(str),
        markers=True,
        category_orders={'Mês': meses_ordem}
    )
    
    # Configurar eixo Y
    max_valor = df_mensal['valorNota'].max()
    step = 1000000  # Step de 1 milhão
    num_milhoes = math.ceil(max_valor / step)
    max_escala = num_milhoes * step
    tick_values = [i * step for i in range(num_milhoes + 1)]
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(
            tickmode="array",
            tickvals=tick_values,
            ticktext=[formatar_moeda(x) for x in tick_values],
            range=[0, max_escala],
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            zeroline=True
        ),
        hoverlabel=dict(
            bgcolor="rgba(68, 68, 68, 0.9)",
            font=dict(color="white", size=12),
            bordercolor="rgba(68, 68, 68, 0.9)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=400,
        showlegend=True,
        legend=dict(
            itemclick=False,
            itemdoubleclick=False
        )
    )
    
    # Formatar hover
    for i in range(len(fig.data)):
        ano = fig.data[i].name
        valores = df_mensal[df_mensal['Ano'].astype(str) == ano]['valorNota']
        valores_formatados = [formatar_moeda(valor) for valor in valores]
        fig.data[i].customdata = list(zip([ano] * len(valores), valores_formatados))
        fig.data[i].hovertemplate = (
            "<b>%{x}</b><br>" +
            "Ano: %{customdata[0]}<br>" +
            "Faturamento: %{customdata[1]}" +
            "<extra></extra>"
        )
        fig.data[i].mode = "lines+markers"
    
    return fig

def criar_grafico_barras_estado(df_filtrado):
    # Filtrar apenas estados brasileiros
    df_brasil = df_filtrado[df_filtrado['uf'] != 'EX'].copy()
    
    # Preparar dados
    df_estados = df_brasil.groupby('uf')['valorfaturado'].sum().sort_values(ascending=True).head(5)
    
    # Criar gráfico
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_estados.index,
        x=df_estados.values,
        text=[formatar_moeda(valor) for valor in df_estados.values],
        textposition='auto',
        marker_color=['green' if i == 4 else '#636EFA' for i in range(len(df_estados))],
        orientation='h'
    ))
    
    # Configurar eixo X (valores monetários)
    max_valor = df_estados.max()
    step = 100000  # Step de 100 mil
    num_steps = math.ceil(max_valor / step)
    max_escala = num_steps * step
    tick_values = [i * step for i in range(num_steps + 1)]
    
    fig.update_layout(
        title='Top 5 Estados em Faturamento',
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
    
    return fig

def criar_grafico_barras_categoria(df_filtrado):
    # Preparar dados usando subGrupo
    df_categoria = df_filtrado.groupby('subGrupo')['valorfaturado'].sum().sort_values(ascending=True).head(5)
    
    # Criar gráfico
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_categoria.index,
        x=df_categoria.values,
        text=[formatar_moeda(valor) for valor in df_categoria.values],
        textposition='auto',
        marker_color=['green' if i == 4 else '#636EFA' for i in range(len(df_categoria))],
        orientation='h'
    ))
    
    # Configurar eixo X (valores monetários)
    max_valor = df_categoria.max()
    step = 1000  # Step de 1 mil
    num_steps = math.ceil(max_valor / step)
    max_escala = num_steps * step
    tick_values = [i * step for i in range(num_steps + 1)]
    
    fig.update_layout(
        title='Top 5 Categorias em Faturamento',
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
    
    return fig