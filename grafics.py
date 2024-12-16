import streamlit as st
import pandas as pd
import plotly.express as px
import locale
from datetime import datetime
from utils import formatar_moeda

# Configurar locale para português brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Dicionário para tradução dos meses
meses = {
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

# Configuração da página
st.set_page_config(page_title="Vendedores", page_icon="👥", layout="wide")

# Título da página
st.title("Análise de Vendedores")

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_parquet('dados/dados_vendas.parquet')
    df['data'] = pd.to_datetime(df['data'])
    return df

df = load_data()

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
        help="Selecione o período desejado",
        locale="pt_BR"
    )
    
    if len(dates) == 2:
        start_date, end_date = dates
        mask = (df['data'].dt.date >= start_date) & (df['data'].dt.date <= end_date)
        df_filtrado = df.loc[mask].copy()
    else:
        df_filtrado = df.copy()

# Criar métricas por vendedor
df_metricas = df_filtrado.groupby('vendedor', as_index=False).agg({
    'nf': 'count',
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

