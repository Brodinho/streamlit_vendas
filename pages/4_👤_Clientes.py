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