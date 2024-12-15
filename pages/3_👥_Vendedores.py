import streamlit as st
import pandas as pd
from dataset import df

# Configuração da página
st.set_page_config(
    page_title="Vendedores - Dashboard de Vendas",
    page_icon="👥",
    layout="wide",
)

# Título da página
st.title("👥 Análise de Vendedores")

# Menu lateral
with st.sidebar:
    st.header("Filtros de Vendedores")
    
    # Obter lista de vendedores únicos (excluindo nulos)
    vendedores = sorted([v for v in df['vendedor'].unique() if pd.notna(v)])
    
    # Multiselect para vendedores
    vendedores_selecionados = st.multiselect(
        'Selecione os vendedores:',
        vendedores,
        default=vendedores[:5] if len(vendedores) > 0 else None
    )
    
    # Filtro de período
    st.subheader("Período")
    col1, col2 = st.columns(2)
    with col1:
        min_date = df['data'].min().date()
        max_date = df['data'].max().date()
        data_inicio = st.date_input('Data Inicial', value=min_date, min_value=min_date, max_value=max_date)
    with col2:
        data_fim = st.date_input('Data Final', value=max_date, min_value=min_date, max_value=max_date)

# Conteúdo principal
if vendedores_selecionados:
    # Filtrar dados
    df_vendedores = df[df['vendedor'].isin(vendedores_selecionados)].copy()
    
    if data_inicio and data_fim:
        df_vendedores = df_vendedores[
            (df_vendedores['data'].dt.date >= data_inicio) &
            (df_vendedores['data'].dt.date <= data_fim)
        ]
    
    # Verificar se há dados após a filtragem
    if len(df_vendedores) > 0:
        # Calcular métricas por vendedor
        metricas_vendedores = df_vendedores.groupby('vendedor').agg({
            'valorfaturado': 'sum',
            'os': 'count'
        }).reset_index()
        
        metricas_vendedores['ticket_medio'] = metricas_vendedores['valorfaturado'] / metricas_vendedores['os']
        
        # Formatar valores monetários
        metricas_vendedores['valorfaturado_fmt'] = metricas_vendedores['valorfaturado'].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        metricas_vendedores['ticket_medio_fmt'] = metricas_vendedores['ticket_medio'].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        
        # Criar DataFrame para exibição
        df_exibir = pd.DataFrame({
            'Vendedor': metricas_vendedores['vendedor'],
            'Total Faturado': metricas_vendedores['valorfaturado_fmt'],
            'Quantidade de Pedidos': metricas_vendedores['os'],
            'Ticket Médio': metricas_vendedores['ticket_medio_fmt']
        })
        
        # Exibir tabela de métricas
        st.subheader("Métricas por Vendedor")
        st.dataframe(df_exibir, use_container_width=True)
        
        # Gráficos de análise
        st.subheader("Análise Gráfica")
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras - Faturamento por vendedor
            chart_data = pd.DataFrame({
                'Vendedor': metricas_vendedores['vendedor'],
                'Faturamento': metricas_vendedores['valorfaturado']
            }).set_index('Vendedor')
            st.bar_chart(chart_data)
            st.caption("Faturamento por Vendedor")
        
        with col2:
            # Gráfico de linha - Evolução mensal
            df_line = df_vendedores.copy()
            df_line['ano_mes'] = df_line['data'].dt.strftime('%Y-%m')
            evolucao_mensal = df_line.groupby('ano_mes')['valorfaturado'].sum().reset_index()
            evolucao_mensal.columns = ['Período', 'Faturamento']
            chart_data = evolucao_mensal.set_index('Período')
            st.line_chart(chart_data)
            st.caption("Evolução Mensal do Faturamento")
    else:
        st.warning('Não há dados para o período e vendedores selecionados.')
else:
    st.warning('Selecione pelo menos um vendedor para visualizar os dados.') 