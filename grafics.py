import streamlit as st
import pandas as pd
import plotly.express as px
import locale
from datetime import datetime
from utils import formatar_moeda
from dataset import df  # Importar o DataFrame diretamente do dataset.py
import plotly.graph_objects as go
from utils import formatar_moeda, criar_df_fat_estado
import math
from sklearn.preprocessing import MinMaxScaler

# Mover as definições globais para aqui
coordenadas_estados = {
    'AC': {'latitude': -8.77, 'longitude': -70.55},
    'AL': {'latitude': -9.71, 'longitude': -35.73},
    'AM': {'latitude': -3.07, 'longitude': -61.66},
    'AP': {'latitude': 1.41, 'longitude': -51.77},
    'BA': {'latitude': -12.96, 'longitude': -38.51},
    'CE': {'latitude': -3.71, 'longitude': -38.54},
    'DF': {'latitude': -15.78, 'longitude': -47.92},
    'ES': {'latitude': -20.31, 'longitude': -40.31},
    'GO': {'latitude': -16.64, 'longitude': -49.31},
    'MA': {'latitude': -2.55, 'longitude': -44.30},
    'MG': {'latitude': -19.92, 'longitude': -43.93},
    'MS': {'latitude': -20.44, 'longitude': -54.64},
    'MT': {'latitude': -15.60, 'longitude': -56.10},
    'PA': {'latitude': -1.45, 'longitude': -48.50},
    'PB': {'latitude': -7.12, 'longitude': -34.86},
    'PE': {'latitude': -8.05, 'longitude': -34.92},
    'PI': {'latitude': -5.09, 'longitude': -42.80},
    'PR': {'latitude': -25.42, 'longitude': -49.27},
    'RJ': {'latitude': -22.91, 'longitude': -43.20},
    'RN': {'latitude': -5.79, 'longitude': -35.20},
    'RO': {'latitude': -8.76, 'longitude': -63.90},
    'RR': {'latitude': 2.82, 'longitude': -60.67},
    'RS': {'latitude': -30.03, 'longitude': -51.23},
    'SC': {'latitude': -27.59, 'longitude': -48.54},
    'SE': {'latitude': -10.90, 'longitude': -37.07},
    'SP': {'latitude': -23.55, 'longitude': -46.63},
    'TO': {'latitude': -10.17, 'longitude': -48.33}
}

coordenadas_paises = {
    'EUA': {'lat': 37.0902, 'lon': -95.7129},
    'COL': {'lat': 4.5709, 'lon': -74.2973},
    'PER': {'lat': -9.1900, 'lon': -75.0152},
    'ARG': {'lat': -38.4161, 'lon': -63.6167},
    'ELS': {'lat': 13.7942, 'lon': -88.8965},
    'MEX': {'lat': 23.6345, 'lon': -102.5528},
    'CHI': {'lat': -35.6751, 'lon': -71.5430},
    'GUA': {'lat': 15.7835, 'lon': -90.2308},
    'HON': {'lat': 15.2000, 'lon': -86.2419},
    'NIC': {'lat': 12.8654, 'lon': -85.2072},
    'PAN': {'lat': 8.5380, 'lon': -80.7821},
    'BOL': {'lat': -16.2902, 'lon': -63.5887},
    'URU': {'lat': -32.5228, 'lon': -55.7658},
    'PAR': {'lat': -23.4425, 'lon': -58.4438},
    'CRI': {'lat': 9.7489, 'lon': -83.7534}
}

siglas_estados = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
    "EUA": "Estados Unidos",
    "COL": "Colômbia",
    "PER": "Peru",
    "ARG": "Argentina",
    "ELS": "El Salvador",
    "MEX": "México",
    "CHI": "Chile",
    "GUA": "Guatemala",
    "HON": "Honduras",
    "NIC": "Nicarágua",
    "PAN": "Panamá",
    "BOL": "Bolívia",
    "URU": "Uruguai",
    "PAR": "Paraguai",
    "CRI": "Costa Rica"
}

def extrair_sigla_pais(pais):
    return mapeamento_paises.get(str(pais).upper(), 'EX')

# Encapsular qualquer configuração do Streamlit em funções
def setup_streamlit():
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    
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

# Dicionário para tradução dos meses (mantendo o nome como meses_pt)
meses_pt = {
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

# Datas mínima e máxima para o filtro
min_date = df['data'].min().date()
max_date = df['data'].max().date()

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
        help="Selecione o período desejado"
    )
    
    if len(dates) == 2:
        start_date, end_date = dates
        mask = (df['data'].dt.date >= start_date) & (df['data'].dt.date <= end_date)
        df_filtrado = df.loc[mask].copy()
    else:
        df_filtrado = df.copy()

# Criar métricas por vendedor
df_metricas = df_filtrado.groupby('vendedor', as_index=False).agg({
    'nota': 'count',
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

# Mapeamento de países para suas siglas
mapeamento_paises = {
    'COLOMBIA': 'COL',
    'PERU': 'PER',
    'ARGENTINA': 'ARG',
    'ESTADOS UNIDOS': 'EUA',
    'EL SALVADOR': 'ELS',
    'MEXICO': 'MEX',
    'CHILE': 'CHI',
    'GUATEMALA': 'GUA',
    'HONDURAS': 'HON',
    'NICARAGUA': 'NIC',
    'PANAMA': 'PAN',
    'BOLIVIA': 'BOL',
    'URUGUAI': 'URU',
    'PARAGUAI': 'PAR',
    'COSTA RICA': 'CRI'
}

def criar_df_fat_estado(df):
    # Separar dados do Brasil e do exterior
    df_brasil = df[df['uf'] != 'EX'].copy()
    df_exterior = df[df['uf'] == 'EX'].copy()
    
    # Processar dados do Brasil
    df_brasil_fat = df_brasil.groupby('uf')['valorfaturado'].sum().reset_index()
    df_brasil_fat['latitude'] = df_brasil_fat['uf'].map(lambda x: coordenadas_estados.get(x, {}).get('latitude'))
    df_brasil_fat['longitude'] = df_brasil_fat['uf'].map(lambda x: coordenadas_estados.get(x, {}).get('longitude'))
    
    # Processar dados do exterior
    df_exterior_fat = df_exterior.groupby('pais')['valorfaturado'].sum().reset_index()
    df_exterior_fat['sigla_pais'] = df_exterior_fat['pais'].apply(extrair_sigla_pais)
    df_exterior_fat['latitude'] = df_exterior_fat['sigla_pais'].map(lambda x: coordenadas_paises.get(x, {}).get('lat'))
    df_exterior_fat['longitude'] = df_exterior_fat['sigla_pais'].map(lambda x: coordenadas_paises.get(x, {}).get('lon'))
    df_exterior_fat['uf'] = df_exterior_fat['sigla_pais']  # Usar sigla do país como UF
    
    # Combinar dados do Brasil e exterior
    df_fat_estado = pd.concat([
        df_brasil_fat[['uf', 'valorfaturado', 'latitude', 'longitude']],
        df_exterior_fat[['uf', 'valorfaturado', 'latitude', 'longitude']]
    ], ignore_index=True)
    
    return df_fat_estado

def criar_mapa_estado(df_filtrado):
    # Criar DataFrame com faturamento por estado/país
    df_fat_estado = criar_df_fat_estado(df_filtrado)
    
    # Identificar se é estado brasileiro ou país
    df_fat_estado['is_pais'] = df_fat_estado['uf'].isin(coordenadas_paises.keys())
    df_fat_estado['Nome_Local'] = df_fat_estado.apply(
        lambda x: siglas_estados.get(x['uf']) if not x['is_pais'] 
        else siglas_estados.get(x['uf'], x['uf']), axis=1
    )
    
    df_fat_estado['Faturamento Total'] = df_fat_estado['valorfaturado'].apply(formatar_moeda)
    
    # Normalizar tamanho das bolhas
    scaler = MinMaxScaler(feature_range=(5, 50))
    df_fat_estado['bubble_size'] = scaler.fit_transform(df_fat_estado[['valorfaturado']])
    
    # Criar o mapa
    fig = px.scatter_mapbox(
        df_fat_estado,
        lat='latitude',
        lon='longitude',
        size='bubble_size',
        color='is_pais',  # Diferenciar países de estados por cor
        color_discrete_sequence=['blue', 'red'],  # Azul para estados, vermelho para países
        hover_name='Nome_Local',
        hover_data={
            'bubble_size': False,
            'latitude': False,
            'longitude': False,
            'is_pais': False,
            'Faturamento Total': True
        },
        mapbox_style="open-street-map",
        zoom=2  # Zoom mais aberto para mostrar todos os países
    )
    
    fig.update_layout(
        coloraxis_colorbar_tickformat="R$,.2f",
        height=400,
        showlegend=True,
        legend=dict(
            title="Localização",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            itemsizing="constant"
        )
    )
    
    # Atualizar legendas
    fig.data[0].name = "Estados"
    fig.data[1].name = "Países"
    
    return fig

def criar_grafico_linha_mensal(df_filtrado):
    # Remover linhas com datas nulas
    df_filtrado = df_filtrado.dropna(subset=['data'])
    
    # Criar DataFrame com as informações necessárias
    df_mensal = df_filtrado.assign(
        Ano=df_filtrado['data'].dt.year,
        Mês=df_filtrado['data'].dt.month_name().map(meses_pt),
        Num_Mês=df_filtrado['data'].dt.month
    )
    
    # Agrupar os dados usando valorNota
    df_mensal = df_mensal.groupby(['Mês', 'Ano', 'Num_Mês'])['valorNota'].sum().reset_index()
    df_mensal = df_mensal.sort_values(['Ano', 'Num_Mês'])
    
    # Criar lista com todos os meses em ordem
    meses_ordem = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Criar gráfico
    fig = px.line(
        df_mensal,
        x='Mês',
        y='valorNota',
        color=df_mensal['Ano'].astype(str),
        markers=True,
        category_orders={'Mês': meses_ordem}
    )
    
    # Configurar eixo Y
    max_valor = df_mensal['valorNota'].max()
    step = 1000000  # Step de 1 milhão
    num_milhoes = math.ceil(max_valor / step)
    max_escala = num_milhoes * step
    tick_values = [i * step for i in range(num_milhoes + 1)]
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(
            tickmode="array",
            tickvals=tick_values,
            ticktext=[formatar_moeda(x) for x in tick_values],
            range=[0, max_escala],
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            zeroline=True
        ),
        hoverlabel=dict(
            bgcolor="rgba(68, 68, 68, 0.9)",
            font=dict(color="white", size=12),
            bordercolor="rgba(68, 68, 68, 0.9)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=400,
        showlegend=True,
        legend=dict(
            itemclick=False,
            itemdoubleclick=False
        )
    )
    
    # Formatar hover
    for i in range(len(fig.data)):
        ano = fig.data[i].name
        valores = df_mensal[df_mensal['Ano'].astype(str) == ano]['valorNota']
        valores_formatados = [formatar_moeda(valor) for valor in valores]
        fig.data[i].customdata = list(zip([ano] * len(valores), valores_formatados))
        fig.data[i].hovertemplate = (
            "<b>%{x}</b><br>" +
            "Ano: %{customdata[0]}<br>" +
            "Faturamento: %{customdata[1]}" +
            "<extra></extra>"
        )
        fig.data[i].mode = "lines+markers"
    
    return fig

def criar_grafico_barras_estado(df_filtrado):
    # Preparar dados para estados brasileiros
    df_brasil = df_filtrado[df_filtrado['uf'] != 'EX'].copy()
    df_brasil_fat = df_brasil.groupby('uf')['valorfaturado'].sum().reset_index()
    df_brasil_fat['Nome_Local'] = df_brasil_fat['uf'].map(siglas_estados)
    
    # Preparar dados para países
    df_exterior = df_filtrado[df_filtrado['uf'] == 'EX'].copy()
    df_exterior_fat = df_exterior.groupby('pais')['valorfaturado'].sum().reset_index()
    df_exterior_fat['uf'] = df_exterior_fat['pais'].apply(extrair_sigla_pais)
    df_exterior_fat['Nome_Local'] = df_exterior_fat['uf'].map(siglas_estados)
    
    # Combinar dados de estados e países
    df_combinado = pd.concat([
        df_brasil_fat[['uf', 'Nome_Local', 'valorfaturado']],
        df_exterior_fat[['uf', 'Nome_Local', 'valorfaturado']]
    ], ignore_index=True)
    
    # Ordenar e pegar top 5 (ordem decrescente)
    df_top5 = df_combinado.nlargest(5, 'valorfaturado').sort_values('valorfaturado', ascending=True)
    
    # Criar gráfico
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_top5['Nome_Local'],
        x=df_top5['valorfaturado'],
        text=[formatar_moeda(valor) for valor in df_top5['valorfaturado']],
        textposition='outside',
        marker_color=[
            'red' if uf in coordenadas_paises.keys() else '#636EFA' 
            for uf in df_top5['uf']
        ],
        orientation='h',
        hovertemplate='%{y}<br>' +  # Nome do Estado/País
                      '%{customdata}<br>' +  # Valor formatado em R$
                      '<extra></extra>',  # Remove informações extras
        customdata=[formatar_moeda(valor) for valor in df_top5['valorfaturado']]
    ))
    
    # Simplificar o eixo X usando menos divisões
    max_valor = df_top5['valorfaturado'].max()
    num_divisoes = 5  # Reduzir número de divisões
    step = math.ceil(max_valor / num_divisoes / 1000000) * 1000000  # Arredondar para milhões
    tick_values = [i * step for i in range(num_divisoes + 1)]
    
    fig.update_layout(
        title='Top 5 Estados/Países em Faturamento',
        xaxis=dict(
            tickmode="array",
            tickvals=tick_values,
            ticktext=[formatar_moeda(x) for x in tick_values],
            range=[0, max(tick_values)],
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)'
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=400,
        showlegend=False,
        margin=dict(l=150)  # Aumentar margem esquerda para acomodar nomes longos
    )
    
    return fig

def criar_grafico_barras_categoria(df_filtrado):
    # Preparar dados usando subGrupo
    df_categoria = df_filtrado.groupby('subGrupo')['valorfaturado'].sum().sort_values(ascending=True).head(5)
    
    # Criar gráfico
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_categoria.index,
        x=df_categoria.values,
        text=[formatar_moeda(valor) for valor in df_categoria.values],
        textposition='auto',
        marker_color=['green' if i == 4 else '#636EFA' for i in range(len(df_categoria))],
        orientation='h'
    ))
    
    # Configurar eixo X (valores monetários)
    max_valor = df_categoria.max()
    step = 1000  # Step de 1 mil
    num_steps = math.ceil(max_valor / step)
    max_escala = num_steps * step
    tick_values = [i * step for i in range(num_steps + 1)]
    
    fig.update_layout(
        title='Top 5 Categorias em Faturamento',
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(
            tickmode="array",
            tickvals=tick_values,
            ticktext=[formatar_moeda(x) for x in tick_values],
            range=[0, max_escala],
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)'
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=400,
        showlegend=False
    )
    
    return fig

def criar_grafico_taxa_conversao(df_conversao):
    fig = go.Figure()
    
    # Formatar datas para o hover (apenas mês e ano em português)
    datas_formatadas = []
    
    # Dicionário de meses em português (invertido)
    meses_pt_invertido = {
        'janeiro': 'Janeiro',
        'fevereiro': 'Fevereiro',
        'março': 'Março',
        'abril': 'Abril',
        'maio': 'Maio',
        'junho': 'Junho',
        'julho': 'Julho',
        'agosto': 'Agosto',
        'setembro': 'Setembro',
        'outubro': 'Outubro',
        'novembro': 'Novembro',
        'dezembro': 'Dezembro'
    }
    
    for data in df_conversao['data']:
        mes = data.strftime('%B').lower()  # Pega o mês em português minúsculo
        mes_formatado = meses_pt_invertido.get(mes, mes.capitalize())  # Traduz para o formato desejado
        ano = data.strftime('%Y')  # Pega o ano
        data_formatada = f"{mes_formatado}/{ano}"
        datas_formatadas.append(data_formatada)

    fig.add_trace(go.Scatter(
        x=df_conversao['data'],
        y=df_conversao['taxa_conversao'],
        mode='lines',
        line=dict(color='#1f77b4'),
        customdata=list(zip(datas_formatadas, df_conversao['taxa_conversao'])),
        hoverinfo='text',
        # Formatação do hover com data em destaque
        hovertext=[f"<b>{data}</b><br><br>Taxa de Conversão: {taxa:.1f}%" 
                  for data, taxa in zip(datas_formatadas, df_conversao['taxa_conversao'])],
        showlegend=False
    ))

    fig.update_layout(
        title='Taxa de Conversão de Clientes Inativos para Ativos',
        # xaxis_title='Período',
        yaxis_title='Taxa de Conversão (%)',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        xaxis=dict(
            showspikes=False,
            showline=True,
            showgrid=True
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=400
    )
    
    return fig

def criar_grafico_recencia_media(df_recencia):
    fig = go.Figure()
    
    # Formatar datas para o hover (apenas mês e ano em português)
    datas_formatadas = []
    
    # Dicionário de meses em português (invertido) - IGUAL ao do gráfico de taxa de conversão
    meses_pt_invertido = {
        'janeiro': 'Janeiro',
        'fevereiro': 'Fevereiro',
        'março': 'Março',
        'abril': 'Abril',
        'maio': 'Maio',
        'junho': 'Junho',
        'julho': 'Julho',
        'agosto': 'Agosto',
        'setembro': 'Setembro',
        'outubro': 'Outubro',
        'novembro': 'Novembro',
        'dezembro': 'Dezembro'
    }
    
    for data in df_recencia['data']:
        mes = data.strftime('%B').lower()  # Pega o mês em português minúsculo
        mes_formatado = meses_pt_invertido.get(mes, mes.capitalize())  # Traduz para o formato desejado
        ano = data.strftime('%Y')  # Pega o ano
        data_formatada = f"{mes_formatado}/{ano}"
        datas_formatadas.append(data_formatada)

    fig.add_trace(go.Scatter(
        x=df_recencia['data'],
        y=df_recencia['recencia_media'],
        mode='lines',
        line=dict(color='#00FF00'),
        customdata=list(zip(datas_formatadas, df_recencia['recencia_media'])),
        hoverinfo='text',
        hovertext=[f"<b>{data}</b><br><br>Recência Média: {recencia:.0f} dias" 
                  for data, recencia in zip(datas_formatadas, df_recencia['recencia_media'])],
        name='Recência Média'
    ))

    fig.update_layout(
        title='Evolução da Recência Média das Compras',
        # xaxis_title='Período',
        yaxis_title='Dias desde a última compra',
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="rgba(0,0,0,0.8)",
            font_size=14
        ),
        xaxis=dict(
            showspikes=False,
            showline=True,
            showgrid=True
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=400
    )
    
    return fig