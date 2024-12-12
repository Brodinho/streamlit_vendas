import pandas as pd
import streamlit as st
import plotly.express as px
from dataset import df
from PIL import Image
from utils import formata_colunas_monetarias, formatar_valor, formatar_moeda
from grafics import (criar_mapa_estado, criar_grafico_linha_mensal, 
                    criar_grafico_barras_estado, criar_grafico_barras_categoria)
from config import carregar_configuracoes, salvar_configuracoes

# Configuração da página - deve ser a primeira chamada Streamlit
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

image = Image.open('imagens/sales.png')

def mostrar_configuracao():
    st.title('Configuração do Dashboard')
    st.write('Selecione os gráficos que deseja visualizar:')

    # Lista completa de gráficos disponíveis
    graficos = {
        'mapa': 'Mapa de Faturamento por Estado/País',
        'barras_estado': 'Gráfico de Barras - Top 5 Estados/Países',
        'linha_mensal': 'Gráfico de Linha - Faturamento Mensal',
        'barras_categoria': 'Gráfico de Barras - Faturamento por Categoria'
    }

    # Carregar configurações salvas (se existirem)
    config_salva = carregar_configuracoes()
    
    # Criar checkboxes para cada gráfico
    selecao_graficos = {}
    for key, descricao in graficos.items():
        # Use a configuração salva se existir, caso contrário use True como padrão
        valor_padrao = config_salva.get(key, True) if config_salva else True
        selecao_graficos[key] = st.checkbox(descricao, value=valor_padrao)

    # Botão para salvar configurações
    if st.button('Salvar Configurações e Visualizar Dashboard'):
        salvar_configuracoes(selecao_graficos)
        st.session_state.pagina = 'dashboard'
        st.rerun()

def mostrar_dashboard():
    # Botão para voltar à configuração
    if st.button('⚙️ Configurar Gráficos'):
        st.session_state.pagina = 'config'
        st.rerun()

    # Dividir o layout em duas colunas
    col1, col2 = st.columns([1, 6])
    with col1:
        st.image(image, use_container_width=True)
    with col2:
        st.title("Dashboard de Vendas")
        st.subheader("E m p r e s a m i x")

    # Criar abas
    tab1, tab2, tab3 = st.tabs(["📊 Gráficos", "📋 Dataset", "👥 Vendedores"])

    with tab1:  # Aba de Gráficos
        # Adicionar seletor de ano - com tratamento para NaN
        anos_disponiveis = sorted(df['data'].dt.year.dropna().unique().astype(int))
        if anos_disponiveis:  # Verifica se há anos disponíveis
            ano_selecionado = st.selectbox('Selecione o Ano:', 
                                         anos_disponiveis, 
                                         index=len(anos_disponiveis)-1)
        else:
            st.error('Não há dados com datas válidas disponíveis')
            return

        config = carregar_configuracoes()
        
        if config is None:
            st.error('Erro ao carregar configurações')
            st.session_state.pagina = 'config'
            st.rerun()

        if config.get('mapa', True):
            st.subheader('Mapa de Faturamento por Estado/País')
            graf_map_estado = criar_mapa_estado(df, ano_selecionado)
            if graf_map_estado is not None:
                st.plotly_chart(graf_map_estado, use_container_width=True)
            else:
                st.warning(f'Não há dados disponíveis para o ano {ano_selecionado}')

        if config.get('barras_estado', True):
            st.subheader('Top 5 Estados/Países por Faturamento')
            grafbar_fat_estado = criar_grafico_barras_estado(df, ano_selecionado)
            if grafbar_fat_estado is not None:
                st.plotly_chart(grafbar_fat_estado, use_container_width=True)
            else:
                st.warning(f'Não há dados disponíveis para o ano {ano_selecionado}')

        if config.get('linha_mensal', True):
            st.subheader('Faturamento Mensal')
            graflinha_fat_mensal = criar_grafico_linha_mensal(df)
            if graflinha_fat_mensal is not None:
                st.plotly_chart(graflinha_fat_mensal, use_container_width=True)
            else:
                st.warning('Não há dados disponíveis para o gráfico de linha mensal')

        if config.get('barras_categoria', True):
            st.subheader('Faturamento por Categoria')
            graf_fat_categoria = criar_grafico_barras_categoria(df)
            if graf_fat_categoria is not None:
                st.plotly_chart(graf_fat_categoria, use_container_width=True)
            else:
                st.warning('Não há dados disponíveis para o gráfico de categorias')

    with tab2:  # Aba do Dataset
        st.header("Dataset")
        # Adicione aqui o código para exibir o dataset
        st.dataframe(df)

    with tab3:  # Aba de Vendedores
        st.header("Vendedores")
        # Adicione aqui o código para exibir informações dos vendedores
        vendedores = df[['vendedor', 'valorNota']].groupby('vendedor').sum().sort_values('valorNota', ascending=False)
        st.dataframe(vendedores)

def main():
    # Inicializar o estado da sessão se necessário
    if 'pagina' not in st.session_state:
        st.session_state.pagina = 'config'

    # Mostrar a página apropriada
    if st.session_state.pagina == 'config':
        mostrar_configuracao()
    else:
        mostrar_dashboard()

if __name__ == '__main__':
    main()

