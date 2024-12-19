import streamlit as st
import pandas as pd
import plotly.express as px
from dataset import df
import locale
import math

# Configurar locale para português brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Configuração da página
st.set_page_config(
    page_title="Vendedores - Dashboard de Vendas",
    page_icon="👥",
    layout="wide",
)

# Configuração do estilo do calendário para português
st.markdown("""
    <style>
        /* Tradução dos meses no calendário */
        div[data-baseweb="calendar"] div[role="grid"] div[role="columnheader"] {
            color: black !important;
        }
        
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:first-child div[role="cell"]:first-child::before {
            content: "Janeiro" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:first-child div[role="cell"]:nth-child(2)::before {
            content: "Fevereiro" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:first-child div[role="cell"]:nth-child(3)::before {
            content: "Março" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:first-child div[role="cell"]:nth-child(4)::before {
            content: "Abril" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:nth-child(2) div[role="cell"]:first-child::before {
            content: "Maio" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:nth-child(2) div[role="cell"]:nth-child(2)::before {
            content: "Junho" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:nth-child(2) div[role="cell"]:nth-child(3)::before {
            content: "Julho" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:nth-child(2) div[role="cell"]:nth-child(4)::before {
            content: "Agosto" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:nth-child(3) div[role="cell"]:first-child::before {
            content: "Setembro" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:nth-child(3) div[role="cell"]:nth-child(2)::before {
            content: "Outubro" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:nth-child(3) div[role="cell"]:nth-child(3)::before {
            content: "Novembro" !important;
        }
        div[data-baseweb="calendar"] div[role="grid"] div[role="row"]:nth-child(3) div[role="cell"]:nth-child(4)::before {
            content: "Dezembro" !important;
        }
        
        /* Esconder texto original em inglês */
        div[data-baseweb="calendar"] div[role="grid"] div[role="cell"] span {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

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
        data_inicio = st.date_input(
            'Data Inicial', 
            value=min_date, 
            min_value=min_date, 
            max_value=max_date,
            format="DD/MM/YYYY",
            key="data_inicio"
        )
    with col2:
        data_fim = st.date_input(
            'Data Final', 
            value=max_date, 
            min_value=min_date, 
            max_value=max_date,
            format="DD/MM/YYYY",
            key="data_fim"
        )

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
        
        # Criar DataFrame para exibição e ordenar por Quantidade de Pedidos
        df_exibir = pd.DataFrame({
            'Vendedor': metricas_vendedores['vendedor'],
            'Total Faturado': metricas_vendedores['valorfaturado_fmt'],
            'Quantidade de Pedidos': metricas_vendedores['os'],
            'Ticket Médio': metricas_vendedores['ticket_medio_fmt']
        })
        df_exibir = df_exibir.sort_values('Quantidade de Pedidos', ascending=False)
        # Resetar índice começando em 1
        df_exibir.index = range(1, len(df_exibir) + 1)
        
        # Exibir tabela de métricas
        st.subheader("Métricas por Vendedor")
        st.dataframe(df_exibir, use_container_width=True)
        
        # Gráficos de análise
        st.subheader("Análise Gráfica")
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras - Faturamento por vendedor
            df_graph = df_vendedores.groupby('vendedor', as_index=False)['valorNota'].sum()
            df_graph = df_graph.sort_values('valorNota', ascending=True)  # Ordenação ascendente para visualização correta
            df_graph.columns = ['vendedor', 'valor']
            
            # Criar gráfico
            fig = px.bar(
                df_graph,
                y='vendedor',
                x='valor',
                title='Análise Gráfica',
                orientation='h'
            )
            
            # Configurar formato brasileiro para os valores do eixo X
            def formato_br(valor):
                return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            # Calcular valores para o eixo X
            max_valor = df_graph['valor'].max()
            step = 3000000  # Step de 3 milhões
            num_steps = math.ceil(max_valor / step)
            max_escala = num_steps * step
            tick_values = [i * step for i in range(num_steps + 1)]
            
            # Atualizar layout do gráfico
            fig.update_layout(
                xaxis_title="",
                yaxis_title="",
                showlegend=False,
                height=400,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                xaxis=dict(
                    tickmode="array",
                    tickvals=tick_values,
                    ticktext=[formato_br(val) for val in tick_values],
                    range=[0, max_escala],
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='rgba(128, 128, 128, 0.2)'
                )
            )
            
            # Formatar valores nas barras
            fig.update_traces(
                text=[formato_br(val) for val in df_graph['valor']],
                textposition='outside',  # Forçar texto para fora das barras
                texttemplate='%{text}',
                textangle=0  # Manter texto na horizontal
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfico de linha - Evolução mensal
            df_line = df_vendedores.copy()
            df_line['ano_mes'] = pd.to_datetime(df_line['data']).dt.strftime('%Y-%m')
            df_line['mes_abrev'] = pd.to_datetime(df_line['data']).dt.strftime('%b-%Y').str.lower()
            
            evolucao_mensal = (df_line.groupby(['ano_mes', 'mes_abrev'])['valorfaturado']
                              .sum()
                              .reset_index()
                              .sort_values('ano_mes'))
            
            fig_line = px.line(
                evolucao_mensal,
                x='mes_abrev',
                y='valorfaturado',
                title='Evolução Mensal do Faturamento'
            )
            
            # Calcular intervalo para o eixo y do gráfico de linha
            max_valor_linha = evolucao_mensal['valorfaturado'].max()
            
            # Ajustar o intervalo baseado no valor máximo
            if max_valor_linha <= 500_000:
                intervalo_linha = 50_000
            elif max_valor_linha <= 1_000_000:
                intervalo_linha = 100_000
            else:
                intervalo_linha = 200_000
            
            # Criar array de valores para o eixo y
            y_ticks_linha = []
            current_value = 0
            
            # Encontrar o próximo valor da escala acima do máximo
            proximo_valor_escala = ((max_valor_linha // intervalo_linha) + 1) * intervalo_linha
            
            # Se o valor máximo estiver muito próximo do próximo valor da escala (diferença menor que 5%),
            # ajustar para usar o próximo valor da escala
            if (proximo_valor_escala - max_valor_linha) / max_valor_linha < 0.05:
                max_valor_linha = proximo_valor_escala
            
            while current_value <= max_valor_linha:
                y_ticks_linha.append(current_value)
                current_value += intervalo_linha
            
            fig_line.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                yaxis=dict(
                    tickmode='array',
                    ticktext=[formato_br(val) for val in y_ticks_linha],
                    tickvals=y_ticks_linha,
                    range=[0, max_valor_linha * 1.1],  # Volta para 10% de margem
                    tickfont=dict(size=10)
                )
            )
            st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning('Não há dados para o período e vendedores selecionados.')
else:
    st.warning('Selecione pelo menos um vendedor para visualizar os dados.') 