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
    tab1, tab2, tab3 = st.tabs(["📊 Gráficos", "📋 Dataset", "👥 Vendedores"])

    with tab1:  # Aba de Gráficos
        # Adicionar seletor de ano com múltipla seleção e largura controlada
        anos_disponiveis = sorted(df['data'].dt.year.dropna().unique().astype(int))
        if anos_disponiveis:
            # CSS para controlar a largura dinâmica mantendo altura fixa
            st.markdown(
                """
                <style>
                /* Container principal do multiselect */
                div[data-testid="stMultiSelect"] {
                    min-width: 150px;
                    width: auto !important;
                    display: inline-block !important;
                }
                
                /* Container dos itens selecionados */
                div[data-testid="stMultiSelect"] > div {
                    width: auto !important;
                    min-width: 150px;
                    display: inline-flex !important;
                }
                
                /* Container que mostra os itens selecionados */
                div[data-testid="stMultiSelect"] > div > div {
                    height: 38px !important;
                    display: inline-flex !important;
                    flex-direction: row !important;
                    flex-wrap: nowrap !important;
                    gap: 4px;
                    overflow: visible !important;
                    width: auto !important;
                }
                
                /* Estilo para os botões individuais */
                div[data-testid="stMultiSelect"] div[role="button"] {
                    white-space: nowrap;
                    display: inline-block !important;
                }

                /* Container da coluna */
                div.stColumn {
                    width: auto !important;
                    min-width: 150px !important;
                    flex-grow: 1 !important;
                }
                </style>
                """, 
                unsafe_allow_html=True
            )
            
            # Criar uma coluna que se ajusta ao conteúdo
            col1, col2 = st.columns([3, 3])  # Proporção mais equilibrada
            with col1:
                # Adicionar opção "Todos" e permitir múltipla seleção
                opcoes_anos = ['Todos'] + [str(ano) for ano in anos_disponiveis]
                anos_selecionados = st.multiselect(
                    'Selecione o(s) Ano(s):', 
                    opcoes_anos,
                    default=['Todos']
                )
            
            # Lógica para tratar a seleção
            if 'Todos' in anos_selecionados:
                anos_filtro = anos_disponiveis
            else:
                anos_filtro = [int(ano) for ano in anos_selecionados]
                
            if not anos_selecionados:  # Se nenhum ano selecionado
                st.warning('Por favor, selecione pelo menos um ano.')
                return
        else:
            st.error('Não há dados com datas válidas disponíveis')
            return

        config = carregar_configuracoes()
        
        if config is None:
            st.error('Erro ao carregar configurações')
            st.session_state.pagina = 'config'
            st.rerun()

        if config.get('mapa', True):
            st.subheader('Mapa de Faturamento por Estado e Países')
            graf_map_estado = criar_mapa_estado(df, anos_filtro)
            if graf_map_estado is not None:
                st.plotly_chart(graf_map_estado, use_container_width=True)
            else:
                st.warning(f'Não há dados disponíveis para o(s) ano(s) selecionado(s)')

        if config.get('barras_estado', True):
            st.subheader('Estados e Países com maior faturamento (Top 5)')
            grafbar_fat_estado = criar_grafico_barras_estado(df, anos_filtro)
            if grafbar_fat_estado is not None:
                st.plotly_chart(grafbar_fat_estado, use_container_width=True)
            else:
                st.warning(f'Não há dados disponíveis para o(s) ano(s) selecionado(s)')

        if config.get('linha_mensal', True):
            st.subheader('Faturamento anual mês-a-mês')
            graflinha_fat_mensal = criar_grafico_linha_mensal(df, anos_filtro)
            if graflinha_fat_mensal is not None:
                st.plotly_chart(graflinha_fat_mensal, use_container_width=True)
            else:
                st.warning('Não há dados disponíveis para o gráfico de linha mensal')

        if config.get('barras_categoria', True):
            st.subheader('Faturamento por Sub-Categoria (Top 5)')
            graf_fat_categoria = criar_grafico_barras_categoria(df, anos_filtro)
            if graf_fat_categoria is not None:
                st.plotly_chart(graf_fat_categoria, use_container_width=True)
            else:
                st.warning('Não há dados disponíveis para o gráfico de categorias')

    with tab2:  # Aba do Dataset
        st.header("Dataset")
        
        # Inicializar df_filtrado com o DataFrame original
        df_filtrado = df.copy()
        
        # Mover filtros para a sidebar
        with st.sidebar:
            st.header("Filtros")
            
            # Obter todas as colunas disponíveis com os novos nomes
            todas_colunas = [mapeamento_colunas.get(col, col) for col in df.columns]
            
            # Inicializar o estado da sessão se necessário
            if 'colunas_selecionadas' not in st.session_state:
                st.session_state.colunas_selecionadas = todas_colunas
            
            # Criar um multiselect para seleção de colunas
            colunas_selecionadas = st.multiselect(
                'Selecione as colunas:',
                todas_colunas,
                default=st.session_state.colunas_selecionadas
            )
            
            # Criar colunas para os botões de seleção de colunas
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button('Selecionar Todas'):
                    st.session_state.colunas_selecionadas = todas_colunas
                    st.rerun()
            
            with btn_col2:
                if st.button('Limpar Seleção'):
                    st.session_state.colunas_selecionadas = []
                    st.rerun()
            
            # Adicionar campo de busca
            texto_busca = st.text_input('Buscar em todas as colunas:', '')
            
            # Adicionar CSS para controlar a largura dos dropdowns
            st.markdown("""
                <style>
                /* Container principal do selectbox */
                div[data-testid="stSelectbox"] {
                    min-width: 150px;
                    width: auto !important;
                }
                
                /* Container do selectbox em si */
                div[data-testid="stSelectbox"] > div {
                    min-width: 150px;
                    width: auto !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Filtros de ano e mês em colunas mais compactas
            col_filtro1, col_filtro2 = st.columns([1, 1])
            
            with col_filtro1:
                # Obter anos únicos da coluna Data Emissão
                anos_disponiveis = sorted(df_filtrado['emissao'].dt.year.dropna().unique())
                if anos_disponiveis:
                    ano_selecionado = st.selectbox(
                        'Ano:',
                        ['Todos'] + [str(ano) for ano in anos_disponiveis],
                        key='ano_filtro'
                    )
            
            with col_filtro2:
                # Lista de meses em português
                meses = ['Todos', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                mes_selecionado = st.selectbox('Mês:', meses, key='mes_filtro')
            
            # Adicionar expander para filtros avançados
            with st.expander("🔍 Filtros Avançados"):
                # Identificar tipos de colunas
                colunas_numericas = []
                colunas_data = []
                colunas_texto = []
                
                for col_original, col_nova in mapeamento_colunas.items():
                    if col_nova not in colunas_selecionadas:
                        continue
                        
                    if pd.api.types.is_numeric_dtype(df[col_original]):
                        colunas_numericas.append((col_original, col_nova))
                    elif pd.api.types.is_datetime64_any_dtype(df[col_original]):
                        colunas_data.append((col_original, col_nova))
                    else:
                        colunas_texto.append((col_original, col_nova))
                
                # Criar filtros para colunas numéricas
                if colunas_numericas:
                    st.subheader("Filtros Numéricos")
                    for col_original, col_nova in colunas_numericas:
                        min_val = float(df[col_original].min())
                        max_val = float(df[col_original].max())
                        
                        # Se min e max forem iguais, ajustar para criar um range válido
                        if min_val == max_val:
                            if min_val == 0:
                                max_val = float(1)  # Converter para float
                            else:
                                # Criar um pequeno range em torno do valor
                                delta = abs(min_val * 0.1)  # 10% do valor
                                min_val = float(min_val - delta)  # Converter para float
                                max_val = float(max_val + delta)  # Converter para float
                        
                        # Criar slider para cada coluna numérica
                        valores = st.slider(
                            f"Filtrar {col_nova}:",
                            min_value=float(min_val),  # Garantir que é float
                            max_value=float(max_val),  # Garantir que é float
                            value=(float(min_val), float(max_val)),  # Garantir que ambos são float
                            key=f"slider_{col_original}"
                        )
                        
                        # Aplicar filtro
                        df_filtrado = df_filtrado[
                            (df_filtrado[col_original] >= valores[0]) & 
                            (df_filtrado[col_original] <= valores[1])
                        ]
                
                # Criar filtros para colunas de data
                if colunas_data:
                    st.subheader("Filtros de Data")
                    for col_original, col_nova in colunas_data:
                        # Remover valores NaT antes de pegar min e max
                        datas_validas = df[col_original].dropna()
                        if len(datas_validas) > 0:
                            min_date = datas_validas.min()
                            max_date = datas_validas.max()
                            
                            # Criar seletor de intervalo de datas
                            datas = st.date_input(
                                f"Filtrar {col_nova}:",
                                value=(min_date, max_date),
                                min_value=min_date,
                                max_value=max_date,
                                key=f"date_{col_original}"
                            )
                            
                            if len(datas) == 2:
                                data_inicio, data_fim = datas
                                df_filtrado = df_filtrado[
                                    (df_filtrado[col_original].dt.date >= data_inicio) & 
                                    (df_filtrado[col_original].dt.date <= data_fim)
                                ]
                        else:
                            st.warning(f'Não há datas válidas na coluna {col_nova}')
                
                # Criar filtros para colunas de texto
                if colunas_texto:
                    st.subheader("Filtros de Texto")
                    for col_original, col_nova in colunas_texto:
                        # Obter valores únicos
                        valores_unicos = df[col_original].dropna().unique()
                        if len(valores_unicos) <= 50:  # Limitar para colunas com poucos valores únicos
                            valores_selecionados = st.multiselect(
                                f"Filtrar {col_nova}:",
                                options=sorted(valores_unicos),
                                key=f"multi_{col_original}"
                            )
                            
                            if valores_selecionados:
                                df_filtrado = df_filtrado[
                                    df_filtrado[col_original].isin(valores_selecionados)
                                ]
        
        # Aplicar filtros de ano e mês
        if ano_selecionado != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['emissao'].dt.year == int(ano_selecionado)]
        
        if mes_selecionado != 'Todos':
            mes_numero = meses.index(mes_selecionado)
            df_filtrado = df_filtrado[df_filtrado['emissao'].dt.month == mes_numero]
        
        # Aplicar filtro de busca
        if texto_busca:
            mascara = pd.DataFrame(False, index=df_filtrado.index, columns=['match'])
            for coluna in df_filtrado.columns:
                mascara['match'] |= df_filtrado[coluna].astype(str).str.contains(texto_busca, case=False, na=False)
            df_filtrado = df_filtrado[mascara['match']]
        
        # Mostrar total de registros após filtro
        total_filtrado = len(df_filtrado)
        total_original = len(df)
        
        # Criar uma nova linha para o slider de registros por página
        st.write("")  # Adiciona um espaço
        col_slider1, col_slider2 = st.columns([2, 4])
        
        with col_slider1:
            # Adicionar número de registros por página
            registros_por_pagina = st.select_slider(
                'Registros por página:',
                options=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                value=10,  # Valor inicial deve estar na lista de options
                key='registros_por_pagina'
            )
        
        # Mostrar o DataFrame com as colunas selecionadas
        if colunas_selecionadas:
            # Converter nomes das colunas selecionadas de volta para os nomes originais
            colunas_originais = [col for col, novo_nome in mapeamento_colunas.items() 
                               if novo_nome in colunas_selecionadas]
            
            # Reorganizar colunas (Descrição da Transação após Transação)
            if 'codtra' in colunas_originais and 'desctra' in colunas_originais:
                idx_codtra = colunas_originais.index('codtra')
                colunas_originais.remove('desctra')
                colunas_originais.insert(idx_codtra + 1, 'desctra')
            
            df_exibir = df_filtrado[colunas_originais].copy()
            
            # Aplicar formatações
            for coluna in df_exibir.columns:
                # Colunas sem formatação (números inteiros)
                if coluna in ['sequencial', 'os', 'codGrupo', 'codVendedor', 'codcli', 'nota']:
                    df_exibir[coluna] = df_exibir[coluna].fillna('').astype(str).replace('\.0$', '', regex=True)
                    # Remove formatação e converte para string, removendo o .0 dos números
                
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
            df_exibir.columns = [mapeamento_colunas.get(col, col) for col in df_exibir.columns]
            
            # Calcular número de páginas
            num_paginas = max(1, (total_filtrado + registros_por_pagina - 1) // registros_por_pagina)
            
            # Criar uma coluna estreita para o input de página
            col_pagina1, col_pagina2 = st.columns([1, 15])
            with col_pagina1:
                pagina_atual = st.number_input(
                    'Página:', 
                    min_value=1, 
                    max_value=num_paginas, 
                    value=min(1, num_paginas)
                ) - 1
            
            inicio = pagina_atual * registros_por_pagina
            fim = min(inicio + registros_por_pagina, total_filtrado)
            
            # Mostrar informações de paginação
            if total_filtrado > 0:
                st.write(f"Mostrando {formatar_numero_br(inicio+1)} a {formatar_numero_br(fim)} de {formatar_numero_br(total_filtrado)} registros | Total de páginas: {formatar_numero_br(num_paginas)}")
            else:
                st.write("Nenhum registro encontrado")
            
            # Aplicar paginação ao DataFrame
            df_pagina = df_exibir.iloc[inicio:fim]
            st.dataframe(df_pagina)
        else:
            st.warning('Por favor, selecione pelo menos uma coluna para visualizar os dados.')

    with tab3:  # Aba de Vendedores
        st.header("Vendedores")
        # Adicione aqui o código para exibir informações dos vendedores
        vendedores = df[['vendedor', 'valorNota']].groupby('vendedor').sum().sort_values('valorNota', ascending=False)
        st.dataframe(vendedores)

    # Adicionar CSS para tradução
    st.markdown("""
        <style>
        /* Tradução via CSS usando pseudo-elementos */
        div[data-baseweb="input"] div[data-testid="stTextInput"]::after {
            content: "Pressione Enter para aplicar" !important;
        }
        
        div[role="listbox"] div[role="option"][aria-selected="false"]:empty::after {
            content: "Sem resultados" !important;
        }
        
        /* Controle de largura dos inputs */
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
        </style>
    """, unsafe_allow_html=True)

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

