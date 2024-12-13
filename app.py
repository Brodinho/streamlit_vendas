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
        
        # Criar colunas para organizar os controles
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Obter todas as colunas disponíveis com os novos nomes
            todas_colunas = [mapeamento_colunas.get(col, col) for col in df.columns]
            
            # Inicializar o estado da sessão se necessário
            if 'colunas_selecionadas' not in st.session_state:
                st.session_state.colunas_selecionadas = todas_colunas
            
            # Criar um multiselect para seleção de colunas
            colunas_selecionadas = st.multiselect(
                'Selecione as colunas para visualização:',
                todas_colunas,
                default=st.session_state.colunas_selecionadas
            )
            
            # Criar colunas para os botões
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button('Selecionar Todas'):
                    st.session_state.colunas_selecionadas = todas_colunas
                    st.rerun()
            
            with btn_col2:
                if st.button('Limpar Seleção'):
                    st.session_state.colunas_selecionadas = []
                    st.rerun()
        
        with col2:
            # Adicionar campo de busca para filtrar linhas
            texto_busca = st.text_input('Buscar em todas as colunas:', '')
        
        # Criar uma nova linha para o slider de registros por página
        st.write("")  # Adiciona um espaço
        col_slider1, col_slider2 = st.columns([2, 4])
        
        with col_slider1:
            # Adicionar número de registros por página
            registros_por_pagina = st.select_slider(
                'Registros por página:',
                options=[10, 25, 50, 100],
                value=25,
                key='registros_por_pagina'
            )
        
        # Filtrar o DataFrame baseado na busca
        if texto_busca:
            mascara = pd.DataFrame(False, index=df.index, columns=['match'])
            # Usar os nomes originais das colunas para a busca
            colunas_originais = [col for col, novo_nome in mapeamento_colunas.items() 
                               if novo_nome in colunas_selecionadas]
            
            for coluna in colunas_originais:  # Usar nomes originais aqui
                mascara['match'] |= df[coluna].astype(str).str.contains(texto_busca, case=False, na=False)
            df_filtrado = df[mascara['match']]
        else:
            df_filtrado = df
            
        # Mostrar o DataFrame com as colunas renomeadas
        if colunas_selecionadas:
            # Converter nomes das colunas selecionadas de volta para os nomes originais
            colunas_originais = [col for col, novo_nome in mapeamento_colunas.items() 
                               if novo_nome in colunas_selecionadas]
            
            df_exibir = df_filtrado[colunas_originais].copy()
            df_exibir.columns = [mapeamento_colunas.get(col, col) for col in df_exibir.columns]
            
            # Reordenar para colocar 'Descrição da Transação' após 'Transação'
            if 'Transação' in df_exibir.columns and 'Descrição da Transação' in df_exibir.columns:
                cols = df_exibir.columns.tolist()
                trans_idx = cols.index('Transação')
                cols.remove('Descrição da Transação')
                cols.insert(trans_idx + 1, 'Descrição da Transação')
                df_exibir = df_exibir[cols]
            
            # Formatar colunas numéricas sem separador de milhares
            colunas_sem_formato = ['Sequencial', 'O.S.', 'Cód. do Grupo', 'Cód. Vendedor']
            for col in colunas_sem_formato:
                if col in df_exibir.columns:
                    df_exibir[col] = df_exibir[col].fillna('').astype(str).replace('\.0$', '', regex=True)
            
            # Formatar colunas de data
            if 'Data Cadastro' in df_exibir.columns:
                df_exibir['Data Cadastro'] = df_exibir['Data Cadastro'].apply(formatar_data)
            if 'Data Emissão' in df_exibir.columns:
                df_exibir['Data Emissão'] = df_exibir['Data Emissão'].apply(formatar_data)
            if 'Dt. Lib. Fatura' in df_exibir.columns:
                df_exibir['Dt. Lib. Fatura'] = df_exibir['Dt. Lib. Fatura'].apply(formatar_datetime)
            
            # Formatar colunas monetárias
            colunas_monetarias = [
                'Valor Faturado', 'Valor IPI', 'Valor ICMS', 'Valor ISS', 
                'Valor Sub. Trib.', 'Valor do Frete', 'Valor da Nota', 
                'Valor Contábil', 'Ret. Valor PIS', 'Ret. Valor COFINS', 
                'Base ICMS', 'Valor Custo', 'Valor do Desconto'
            ]
            for col in colunas_monetarias:
                if col in df_exibir.columns:
                    df_exibir[col] = df_exibir[col].apply(formata_colunas_monetarias)
            
            # Mostrar informações sobre o dataset
            total_registros = len(df_exibir)
            num_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
            st.write(f'Total de registros: {formatar_numero_br(total_registros)} | Total de páginas: {formatar_numero_br(num_paginas)}')
            
            # Adicionar paginação
            if num_paginas > 1:
                # Adicionar CSS para controlar a largura do input
                st.markdown("""
                    <style>
                    [data-testid="stNumberInput"] {
                        width: 100px !important;
                    }
                    /* Ajusta o container do input */
                    [data-testid="stNumberInput"] > div {
                        width: 100px !important;
                    }
                    /* Ajusta o input em si */
                    [data-testid="stNumberInput"] input {
                        width: 100px !important;
                        text-align: center;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                # Criar uma coluna estreita para o input de página
                col_pagina1, col_pagina2 = st.columns([1, 15])
                with col_pagina1:
                    pagina_atual = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1) - 1
                
                inicio = pagina_atual * registros_por_pagina
                fim = min(inicio + registros_por_pagina, total_registros)
                
                df_pagina = df_exibir.iloc[inicio:fim]
                st.dataframe(df_pagina)
                st.write(f'Mostrando registros {formatar_numero_br(inicio+1)} a {formatar_numero_br(fim)} de {formatar_numero_br(total_registros)}')
            else:
                st.dataframe(df_exibir)
        else:
            st.warning('Por favor, selecione pelo menos uma coluna para visualizar os dados.')

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

