import plotly.express as px
import plotly.graph_objects as go
from utils import formatar_moeda, criar_df_fat_estado
import math
import locale
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

# Dicionário para tradução dos meses
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

# Dicionário de estados
siglas_estados = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins",
    "EUA": "Estados Unidos", "COL": "Colômbia", "PER": "Peru", "ARG": "Argentina",
    "ELS": "El Salvador", "MEX": "México", "CHI": "Chile", "GUA": "Guatemala",
    "HON": "Honduras", "NIC": "Nicarágua", "PAN": "Panamá", "BOL": "Bolívia",
    "URU": "Uruguai", "PAR": "Paraguai", "CRI": "Costa Rica"
}

def criar_mapa_estado(df_filtrado):
    # Criar DataFrame com faturamento por estado
    df_fat_estado = criar_df_fat_estado(df_filtrado)
    
    # Adicionar nome do estado e formatar faturamento
    df_fat_estado['Nome_Estado'] = df_fat_estado['uf'].map(siglas_estados)
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
        color_discrete_sequence=['blue'],
        hover_name='Nome_Estado',
        hover_data={
            'bubble_size': False,
            'latitude': False,
            'longitude': False,
            'Faturamento Total': True
        },
        mapbox_style="open-street-map",
        zoom=3
    )
    
    fig.update_layout(
        coloraxis_colorbar_tickformat="R$,.2f",
        height=400
    )
    
    return fig

def criar_grafico_barras_estado(df_filtrado):
    # Filtrar apenas estados brasileiros
    df_brasil = df_filtrado[df_filtrado['uf'] != 'EX'].copy()
    
    # Preparar dados
    df_estados = df_brasil.groupby('uf')['valorfaturado'].sum().sort_values(ascending=False).head(5)
    
    # Criar gráfico
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_estados.index,
        y=df_estados.values,
        text=[formatar_moeda(valor) for valor in df_estados.values],
        textposition='auto',
        marker_color=['green' if i == 0 else '#636EFA' for i in range(len(df_estados))]
    ))
    
    # Configurar eixo Y
    max_valor = df_estados.max()
    step = 10000000  # Step de 10 milhões
    num_steps = math.ceil(max_valor / step)
    max_escala = num_steps * step
    tick_values = [i * step for i in range(num_steps + 1)]
    
    fig.update_layout(
        title='Top 5 Estados em Faturamento',
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(
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

def criar_grafico_linha_mensal(df_filtrado):
    # Configurar locale para formatação brasileira
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    
    # Remover linhas com datas nulas
    df_filtrado = df_filtrado.dropna(subset=['data'])
    
    # Criar DataFrame com as informações necessárias
    df_mensal = df_filtrado.assign(
        Ano=df_filtrado['data'].dt.year,
        Mês=df_filtrado['data'].dt.month_name().map(meses_pt),
        Num_Mês=df_filtrado['data'].dt.month
    )
    
    # Agrupar os dados usando valorNota em vez de valorfaturado
    df_mensal = df_mensal.groupby(['Mês', 'Ano', 'Num_Mês'])['valorNota'].sum().reset_index()
    df_mensal = df_mensal.sort_values(['Ano', 'Num_Mês'])
    
    # Criar lista com todos os meses em ordem
    meses_ordem = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Criar gráfico
    fig = px.line(
        df_mensal,
        x='Mês',
        y='valorNota',  # Alterado para valorNota
        color=df_mensal['Ano'].astype(str),
        markers=True,
        category_orders={'Mês': meses_ordem}
    )
    
    # Configurar eixo Y
    max_valor = df_mensal['valorNota'].max()  # Alterado para valorNota
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
        valores = df_mensal[df_mensal['Ano'].astype(str) == ano]['valorNota']  # Alterado para valorNota
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

def criar_grafico_barras_categoria(df_filtrado):
    # Preparar dados usando subGrupo em vez de grupo
    df_categoria = df_filtrado.groupby('subGrupo')['valorfaturado'].sum().sort_values(ascending=False).head(5)
    
    # Criar gráfico
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_categoria.index,
        y=df_categoria.values,
        text=[formatar_moeda(valor) for valor in df_categoria.values],
        textposition='auto',
        marker_color=['green' if i == 0 else '#636EFA' for i in range(len(df_categoria))]
    ))
    
    # Configurar eixo Y
    max_valor = df_categoria.max()
    step = 10000000  # Step de 10 milhões
    num_steps = math.ceil(max_valor / step)
    max_escala = num_steps * step
    tick_values = [i * step for i in range(num_steps + 1)]
    
    fig.update_layout(
        title='Top 5 Categorias em Faturamento',
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(
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

