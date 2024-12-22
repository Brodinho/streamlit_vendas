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
    
    # Remover coluna auxiliar de ordenação
    df_clientes = df_clientes.drop('Status_ordem', axis=1)

    # Adicionar filtro de status
    st.subheader("Filtrar por Status")
    status_selecionados = st.multiselect(
        'Selecione os status que deseja visualizar:',
        options=ordem_status,
        default=ordem_status,  # Todos selecionados por padrão
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
    pass  # Mantenha o código existente da análise geográfica aqui

# Aba Análise Temporal
with tab3:
    pass  # Mantenha o código existente da análise temporal aqui