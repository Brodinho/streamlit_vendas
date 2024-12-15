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

# Dicionário de mapeamento de nomes de colunas
mapeamento_colunas = {
    'sequencial': 'Sequencial',
    'tipo': 'Tipo Movimento',
    'codtra': 'Transação',
    'os': 'O.S.',
    'itemOS': 'Item O.S.',
    'codcli': 'Código Cliente',
    'cnpj': 'CNPJ',
    'razao': 'Razão Social',
    'fantasia': 'Fantasia',
    'cfop': 'CFOP',
    'data': 'Data Cadastro',
    'emissao': 'Data Emissão',
    'nota': 'Nota Número',
    'serie': 'Série',
    'chaveNfe': 'Chave NF-e',
    'item': 'Item',
    'codProduto': 'Cód. do Produto',
    'produto': 'Produto',
    'unidSaida': 'Unid. de Saída',
    'ncm': 'NCM',
    'codGrupo': 'Cód. do Grupo',
    'grupo': 'Grupo',
    'codSubGrupo': 'Cód. Sub-Grupo',
    'codVendedor': 'Cód. Vendedor',
    'vendedorRed': 'Vendedor Reduzido',
    'cidade': 'Cidade',
    'uf': 'U.F.',
    'tipoOs': 'Tipo OS',
    'descricaoTipoOs': 'Descrição Tipo OS',
    'codRegiao': 'Cód. Região',
    'valorfaturado': 'Valor Faturado',
    'quant': 'Quantidade',
    'valoripi': 'Valor IPI',
    'valoricms': 'Valor ICMS',
    'valoriss': 'Valor ISS',
    'valorSubs': 'Valor Sub. Trib.',
    'valorFrete': 'Valor do Frete',
    'valorNota': 'Valor da Nota',
    'valorContabil': 'Valor Contábil',
    'retVlrPis': 'Ret. Valor PIS',
    'retVlrCofins': 'Ret. Valor COFINS',
    'aliIpi': 'Alíquota IPI',
    'porReducaoIcms': 'Porc.Redução ICMS',
    'cstIcms': 'CST ICMS',
    'baseIcms': 'Base ICMS',
    'valorCusto': 'Valor Custo',
    'valorDesconto': 'Valor do Desconto',
    'desctra': 'Descrição da Transação',
    'servico': 'Serviço',
    'libFatura': 'Dt. Lib. Fatura',
    'latitude': 'Latitude',
    'longitude': 'Longitude'
}

def formatar_numero_br(numero):
    """Formata um número para o padrão brasileiro (ex: 1.234,56)"""
    return f"{numero:,}".replace(",", "X").replace(".", ",").replace("X", ".")

def formata_colunas_monetarias(valor):
    """Formata valores monetários para o padrão brasileiro"""
    if pd.isna(valor):
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_data(data):
    """Formata data para o padrão brasileiro"""
    if pd.isna(data):
        return ""
    return data.strftime('%d-%m-%Y')

def formatar_datetime(data):
    """Formata datetime para o padrão brasileiro"""
    if pd.isna(data):
        return ""
    return data.strftime('%d-%m-%Y %H:%M:%S')

def mostrar_dashboard():
    # Adicionar CSS e JavaScript para traduzir textos padrão
    st.markdown("""
        <style>
        /* Estilos anteriores mantidos */
        [data-testid="stNumberInput"] {
            width: 150px !important;
        }
        [data-testid="stNumberInput"] > div {
            width: 150px !important;
        }
        [data-testid="stNumberInput"] input {
            width: 150px !important;
            text-align: center;
        }
        
        /* Ocultar texto em inglês */
        .stTextInput > div[data-baseweb="input"] > div::after {
            display: none !important;
        }
        </style>
        
        <script>
        // Função para traduzir textos
        const traducoes = {
            'Press Enter to apply': 'Pressione Enter para aplicar',
            'No results': 'Sem resultados'
        };
        
        function traduzirTextos() {
            // Traduzir todos os elementos que contêm os textos específicos
            document.querySelectorAll('*').forEach(element => {
                if (element.textContent in traducoes) {
                    element.textContent = traducoes[element.textContent];
                }
            });
        }
        
        // Executar tradução inicial e configurar observador para mudanças
        document.addEventListener('DOMContentLoaded', () => {
            traduzirTextos();
            const observer = new MutationObserver(traduzirTextos);
            observer.observe(document.body, { 
                childList: true, 
                subtree: true 
            });
        });
        </script>
    """, unsafe_allow_html=True)

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
    tab_graficos, tab_dataset, tab_vendedores = st.tabs(["📊 Gráficos", "📋 Dataset", "👥 Vendedores"])

    # Aba de Gráficos
    with tab_graficos:
        # Menu lateral dos gráficos
        with st.sidebar:
            st.header('Configuração dos Gráficos')
            st.write('Selecione os gráficos que deseja visualizar:')
            
            graficos = {
                'mapa': 'Mapa de Faturamento por Estado/País',
                'barras_estado': 'Gráfico de Barras - Top 5 Estados/Países',
                'linha_mensal': 'Gráfico de Linha - Faturamento Mensal',
                'barras_categoria': 'Gráfico de Barras - Faturamento por Categoria'
            }
            
            selecao_graficos = {}
            for key, descricao in graficos.items():
                selecao_graficos[key] = st.checkbox(
                    descricao,
                    value=True,
                    key=f'check_{key}_graficos'
                )

        # Conteúdo dos gráficos
        anos_disponiveis = sorted(df['data'].dt.year.dropna().unique().astype(int))
        if anos_disponiveis:
            anos_selecionados = st.multiselect(
                'Selecione o(s) ano(s):', 
                ['Todos'] + [str(ano) for ano in anos_disponiveis],
                default=['Todos']
            )
            
            if not anos_selecionados:
                st.warning('É necessário escolher ao menos um ano ou período')
            else:
                # Filtrar dados pelos anos selecionados
                if 'Todos' in anos_selecionados:
                    df_ano = df.copy()
                else:
                    anos_int = [int(ano) for ano in anos_selecionados]
                    df_ano = df[df['data'].dt.year.isin(anos_int)]
                
                # Layout em colunas
                col1, col2 = st.columns(2)
                
                # Mapa de Faturamento por Estado
                if selecao_graficos.get('mapa', True):
                    with col1:
                        fig_map = criar_mapa_estado(df_ano)
                        st.plotly_chart(fig_map, use_container_width=True)
                
                # Gráfico de Barras - Top 5 Estados
                if selecao_graficos.get('barras_estado', True):
                    with col2:
                        fig_barras = criar_grafico_barras_estado(df_ano)
                        st.plotly_chart(fig_barras, use_container_width=True)
                
                # Gráfico de Linha - Faturamento Mensal
                if selecao_graficos.get('linha_mensal', True):
                    with col1:
                        fig_linha = criar_grafico_linha_mensal(df_ano)
                        st.plotly_chart(fig_linha, use_container_width=True)
                
                # Gráfico de Barras - Faturamento por Categoria
                if selecao_graficos.get('barras_categoria', True):
                    with col2:
                        fig_categoria = criar_grafico_barras_categoria(df_ano)
                        st.plotly_chart(fig_categoria, use_container_width=True)

    # Aba do Dataset
    with tab_dataset:
        # Menu lateral do dataset
        with st.sidebar:
            st.header("Filtros do Dataset")
            
            # Obter apenas as colunas que existem no DataFrame
            colunas_existentes = df.columns
            mapeamento_colunas_existentes = {
                col: mapeamento_colunas[col] 
                for col in colunas_existentes 
                if col in mapeamento_colunas
            }
            
            # Inicializar session_state se necessário
            if 'colunas_dataset' not in st.session_state:
                st.session_state['colunas_dataset'] = list(mapeamento_colunas_existentes.values())
            
            # Botões de Selecionar Todos e Limpar Seleção
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Selecionar Todos'):
                    st.session_state['colunas_dataset'] = list(mapeamento_colunas_existentes.values())
            with col2:
                if st.button('Limpar Seleção'):
                    st.session_state['colunas_dataset'] = []
            
            # Seleção de colunas usando nomes formatados
            todas_colunas = list(mapeamento_colunas_existentes.values())
            colunas_selecionadas = st.multiselect(
                'Selecione as colunas:',
                todas_colunas,
                default=None,  # Removido o valor default
                key='colunas_dataset'
            )
            
            # Campo de busca
            texto_busca = st.text_input('Buscar em todas as colunas:', key='busca_dataset')
            
            # Filtros de ano e mês
            col_filtro1, col_filtro2 = st.columns([1, 1])
            with col_filtro1:
                anos_disponiveis = sorted(df['emissao'].dt.year.dropna().unique())
                ano_selecionado = st.selectbox(
                    'Ano:',
                    ['Todos'] + [str(ano) for ano in anos_disponiveis],
                    key='ano_dataset'
                )
            
            with col_filtro2:
                meses = ['Todos', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                mes_selecionado = st.selectbox('Mês:', meses, key='mes_dataset')

        # Conteúdo do dataset
        if colunas_selecionadas:
            # Converter nomes formatados para nomes originais
            mapeamento_reverso = {v: k for k, v in mapeamento_colunas_existentes.items()}
            colunas_originais = [mapeamento_reverso[col] for col in colunas_selecionadas]
            
            df_filtrado = df.copy()
            
            # Aplicar filtros
            if ano_selecionado != 'Todos':
                df_filtrado = df_filtrado[df_filtrado['emissao'].dt.year == int(ano_selecionado)]
            
            if mes_selecionado != 'Todos':
                mes_numero = meses.index(mes_selecionado)
                df_filtrado = df_filtrado[df_filtrado['emissao'].dt.month == mes_numero]
            
            if texto_busca:
                mascara = pd.DataFrame(False, index=df_filtrado.index, columns=['match'])
                for coluna in df_filtrado.columns:
                    mascara['match'] |= df_filtrado[coluna].astype(str).str.contains(texto_busca, case=False, na=False)
                df_filtrado = df_filtrado[mascara['match']]

            df_exibir = df_filtrado[colunas_originais].copy()
            
            # Aplicar formatações
            for coluna in df_exibir.columns:
                # Colunas sem formatação (números inteiros)
                if coluna in ['sequencial', 'os', 'codGrupo', 'codVendedor', 'codcli', 'nota']:
                    df_exibir[coluna] = df_exibir[coluna].fillna('').astype(str).replace('\.0$', '', regex=True)
                
                # Colunas de data (sem hora)
                elif coluna in ['data', 'emissao']:
                    df_exibir[coluna] = pd.to_datetime(df_exibir[coluna]).dt.strftime('%d-%m-%Y')
                
                # Colunas de datetime (com hora)
                elif coluna in ['libFatura']:
                    df_exibir[coluna] = pd.to_datetime(df_exibir[coluna]).dt.strftime('%d-%m-%Y %H:%M:%S')
                
                # Colunas monetárias
                elif coluna in ['valorfaturado', 'valoripi', 'valoricms', 'valoriss', 
                              'valorSubs', 'valorFrete', 'valorNota', 'valorContabil',
                              'retVlrPis', 'retVlrCofins', 'baseIcms', 'valorCusto',
                              'valorDesconto']:
                    df_exibir[coluna] = df_exibir[coluna].apply(lambda x: 
                        f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                        if pd.notnull(x) else "")
            
            # Renomear colunas para exibição
            df_exibir.columns = [mapeamento_colunas_existentes[col] for col in colunas_originais]
            
            # Controles de paginação
            total_registros = len(df_exibir)
            
            col1, col2 = st.columns([2, 4])
            with col1:
                registros_por_pagina = st.select_slider(
                    'Registros por página:',
                    options=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                    value=10,
                    key='registros_dataset'
                )
            
            num_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
            pagina_atual = st.number_input(
                'Página:',
                min_value=1,
                max_value=max(1, num_paginas),
                value=1,
                key='pagina_dataset'
            )
            
            inicio = (pagina_atual - 1) * registros_por_pagina
            fim = min(inicio + registros_por_pagina, total_registros)
            
            st.write(f"Mostrando registros {inicio + 1} a {fim} de {total_registros} | Total de páginas: {num_paginas}")
            
            # Mostrar DataFrame paginado
            st.dataframe(df_exibir.iloc[inicio:fim])
        else:
            st.warning('Selecione pelo menos uma coluna para visualizar os dados.')

    # Aba de Vendedores
    with tab_vendedores:
        # Menu lateral dos vendedores
        with st.sidebar:
            st.header("Filtros de Vendedores")
            # ... resto do código dos vendedores ...
            pass

def main():
    # Inicializar o estado da sessão se necessário
    if 'pagina' not in st.session_state:
        st.session_state.pagina = 'dashboard'

    # Agora vamos direto para o dashboard
    mostrar_dashboard()

if __name__ == '__main__':
    main()

