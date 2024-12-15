import streamlit as st
import pandas as pd
from dataset import df, mapeamento_colunas

# Configuração da página
st.set_page_config(
    page_title="Dataset - Dashboard de Vendas",
    page_icon="📋",
    layout="wide",
)

# Título da página
st.title("📋 Análise do Dataset")

# Menu lateral
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
        default=None,
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

# Conteúdo principal
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
    df_exibir.index = df_exibir.index + 1
    st.dataframe(df_exibir.iloc[inicio:fim])
else:
    st.warning('Selecione pelo menos uma coluna para visualizar os dados.') 