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

# Criar abas
tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🌎 Análise Geográfica", "📈 Análise Temporal"])

# Aba Visão Geral
with tab1:
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

    # Selecionar e ordenar colunas para exibição
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

# Aba Análise Geográfica
with tab2:
    pass  # Mantenha o código existente da análise geográfica aqui

# Aba Análise Temporal
with tab3:
    pass  # Mantenha o código existente da análise temporal aqui