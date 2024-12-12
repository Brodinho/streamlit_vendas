import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import locale
from utils import formatar_moeda, criar_df_fat_estado
import math

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

# Normaliza 'Faturamento' para ajustar o tamanho das bolhas
from sklearn.preprocessing import MinMaxScaler
from utils import df_fat_estado, df_fat_mes, df_fat_categoria

# -------------------- GRÁFICO DE MAPA: FATURAMENTO POR MÊS -------------------- #
siglas_estados = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins",
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
    "CHI": "Chile",
    "URU": "Uruguai",
    "PAR": "Paraguai",
    "CRI": "Costa Rica"
}

# Adicionar a coluna com os nomes mesess dos estados
df_fat_estado['Nome_Estado'] = df_fat_estado['uf'].map(siglas_estados)

# Renomear e formatar o faturamento total no formato brasileiro
df_fat_estado['Faturamento Total'] = df_fat_estado['Faturamento'].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# Normaliza 'Faturamento' para ajustar o tamanho das bolhas
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(5, 50))  # Ajusta o tamanho das bolhas (5 a 50 é um exemplo)
df_fat_estado['bubble_size'] = scaler.fit_transform(df_fat_estado[['Faturamento']])

# Cria o mapa
graf_map_estado = px.scatter_mapbox(
    df_fat_estado,
    lat='latitude',
    lon='longitude',
    size='bubble_size',
    color_discrete_sequence=['blue'],
    hover_name='Nome_Estado',  # Nome meses do estado
    hover_data={
        'bubble_size': False,  # Exclui bubble_size dos rótulos
        'latitude': False,     # Exclui latitude
        'longitude': False,    # Exclui longitude
        'Faturamento Total': True  # Inclui Faturamento Total com o nome correto
    },
    # title="FATURAMENTO TOTAL POR ESTADO",
    mapbox_style="open-street-map",
    zoom=3
)

graf_map_estado.update_layout(
    coloraxis_colorbar_tickformat="R$,.2f"  # Formatação dos valores monetários no mapa
)

# -------------------- GRÁFICO DE LINHAS (FATURAMENTO POR MÊS) -------------------- #
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Máximo do faturamento
max_faturamento = df_fat_mes["Faturamento"].max()

# Criar uma nova coluna 'Mês_Ano' que combina o 'Mês' e o 'Ano' para o eixo X
df_fat_mes['Mês_Ano'] = df_fat_mes['Mês'] + ' ' + df_fat_mes['Ano'].astype(str)

'''
df_fat_mes['Faturamento'] = df_fat_mes['Faturamento'].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)
'''

# Criando o gráfico
graflinha_fat_mensal = px.line(
    df_fat_mes,
    x="Mês",
    y="Faturamento",
    color="Ano",
    markers=True,
    # title="FATURAMENTO MÊS A MÊS"
)

# Calculando os valores para o eixo Y
max_valor = df_fat_mes["Faturamento"].max()
min_valor = 0
step = 1000000  # Step de 1 milhão

# Calculando o número de milhões necessários para cobrir o valor máximo
num_milhoes = math.ceil(max_valor / step)  # Arredonda para cima
max_escala = num_milhoes * step

# Criando a sequência de valores para o eixo Y
tick_values = [i * step for i in range(num_milhoes + 1)]

# Atualizando o layout
graflinha_fat_mensal.update_layout(
    xaxis_title="",  # Remove o título do eixo X
    yaxis_title="",  # Remove o título do eixo Y
    yaxis=dict(
        tickmode="array",
        tickvals=tick_values,
        ticktext=[f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                 for x in tick_values],
        tickprefix="",
        range=[0, max_escala],
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)',
        zeroline=True
    ),
    hoverlabel=dict(
        bgcolor="rgba(68, 68, 68, 0.9)",
        font=dict(
            color="white",
            size=12
        ),
        bordercolor="rgba(68, 68, 68, 0.9)"
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color="white"
    )
)

# Formatando os valores no hover (tooltip) e nos marcadores
for i in range(len(graflinha_fat_mensal.data)):
    valores = df_fat_mes[df_fat_mes['Ano'] == int(graflinha_fat_mensal.data[i].name)]['Faturamento']
    graflinha_fat_mensal.data[i].text = ["" for _ in valores]  # Define texto vazio para os marcadores
    graflinha_fat_mensal.data[i].textposition = "top center"
    
    # Formatando os valores do hover no padrão brasileiro
    valores_formatados = [formatar_moeda(valor) for valor in valores]
    graflinha_fat_mensal.data[i].customdata = list(zip([graflinha_fat_mensal.data[i].name] * len(valores), valores_formatados))
    
    graflinha_fat_mensal.data[i].hovertemplate = (
        "<b>%{x}</b><br>" +
        "Ano: %{customdata[0]}<br>" +
        "Faturamento: %{customdata[1]}" +
        "<extra></extra>"
    )
    graflinha_fat_mensal.data[i].mode = "lines+markers"

# -------------------- GRÁFICO DE BARRAS: FATURAMENTO POR ESTADO -------------------- #
# Filtrar apenas registros com Nome_Estado válido e pegar os top 5
df_fat_estado_filtrado = df_fat_estado.dropna(subset=['Nome_Estado']).head(5)

grafbar_fat_estado = px.bar(
    df_fat_estado_filtrado,
    x='Nome_Estado',
    y='Faturamento',
    text='Faturamento',
    # title='FATURAMENTO POR ESTADO (TOP 5)'
)

# Calculando os valores para o eixo Y
max_valor = df_fat_estado_filtrado['Faturamento'].max()
min_valor = 0
step = 10000000  # Step de 10 milhões
num_steps = math.ceil(max_valor / step)
max_escala = num_steps * step

# Criando a sequência de valores para o eixo Y
tick_values = [i * step for i in range(num_steps + 1)]

# Atualizando o layout
grafbar_fat_estado.update_layout(
    xaxis_title="",  # Remove o título do eixo X
    yaxis_title="",  # Remove o título do eixo Y
    yaxis=dict(
        tickmode="array",
        tickvals=tick_values,
        ticktext=[f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                 for x in tick_values],
        range=[0, max_escala],
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)'
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color="white"
    )
)

# Formatando os valores nas barras e definindo a cor da barra mais alta
valores_formatados = [formatar_moeda(valor) for valor in df_fat_estado_filtrado['Faturamento']]
grafbar_fat_estado.update_traces(
    text=valores_formatados,
    textposition='auto',
    marker_color=['green' if x == max_valor else '#636EFA' 
                 for x in df_fat_estado_filtrado['Faturamento']],
    customdata=valores_formatados,
    hovertemplate="Estado: %{x}<br>" +
                  "Faturamento: %{customdata}" +
                  "<extra></extra>"
)

# -------------------- GRÁFICO DE BARRAS: FATURAMENTO POR SUB-GRUPO -------------------- #
# Ordenando o DataFrame antes de criar o gráfico
df_fat_categoria_ordenado = df_fat_categoria.head().sort_values('Faturamento', ascending=False)

graf_fat_categoria = px.bar(
    df_fat_categoria_ordenado,
    x="Sub Grupo",
    y="Faturamento",
    # text="Faturamento",
    # title="FATURAMENTO POR SUB-CATEGORIA (TOP 5)"
)

# Calculando os valores para o eixo Y
max_valor = df_fat_categoria_ordenado['Faturamento'].max()
min_valor = 0
step = 10000000  # Step de 10 milhões
num_steps = math.ceil(max_valor / step)
max_escala = num_steps * step

# Criando a sequência de valores para o eixo Y
tick_values = [i * step for i in range(num_steps + 1)]

# Atualizando o layout
graf_fat_categoria.update_layout(
    xaxis_title="",  # Remove o título do eixo X
    yaxis_title="",  # Remove o título do eixo Y
    yaxis=dict(
        tickmode="array",
        tickvals=tick_values,
        ticktext=[f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                 for x in tick_values],
        range=[0, max_escala],
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128, 128, 128, 0.2)'
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color="white"
    )
)

# Formatando os valores nas barras e definindo a cor da barra mais alta
valores_formatados = [formatar_moeda(valor) for valor in df_fat_categoria_ordenado['Faturamento']]
graf_fat_categoria.update_traces(
    text=valores_formatados,
    textposition='auto',
    marker_color=['green' if x == max_valor else '#636EFA' 
                 for x in df_fat_categoria_ordenado['Faturamento']],
    customdata=valores_formatados,
    hovertemplate="Sub-Categoria: %{x}<br>" +
                  "Faturamento: %{customdata}" +
                  "<extra></extra>"
)

# Exportar as funções
__all__ = ['criar_mapa_estado', 'criar_grafico_linha_mensal', 'criar_grafico_barras_estado', 'criar_grafico_barras_categoria']

def criar_mapa_estado(df, anos=None):
    # Criar DataFrame filtrado por ano(s)
    df_temp = df.copy()
    
    # Filtrar por ano(s) se especificado
    if anos is not None and anos:  # Verifica se há anos selecionados
        df_temp = df_temp[df_temp['data'].dt.year.isin(anos)]
    
    # Se não houver dados após o filtro, retornar None
    if df_temp.empty:
        return None
        
    # Criar DataFrame agregado por estado
    df_temp = df_temp.groupby("uf")[["valorNota"]].sum().reset_index()
    df_temp = df_temp.rename(columns={'valorNota': 'Faturamento'})
    
    # Adicionar a coluna com os nomes dos estados
    df_temp['Nome_Estado'] = df_temp['uf'].map(siglas_estados)

    # Renomear e formatar o faturamento total no formato brasileiro
    df_temp['Faturamento Total'] = df_temp['Faturamento'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    # Normaliza 'Faturamento' para ajustar o tamanho das bolhas
    if len(df_temp) > 0:  # Verifica se há dados antes de usar o MinMaxScaler
        scaler = MinMaxScaler(feature_range=(5, 50))
        df_temp['bubble_size'] = scaler.fit_transform(df_temp[['Faturamento']])
    else:
        df_temp['bubble_size'] = 5  # valor padrão se não houver dados

    # Adicionar coordenadas
    df_temp = df_temp.merge(
        df[['uf', 'latitude', 'longitude']].drop_duplicates(),
        on='uf',
        how='left'
    )

    # Cria o mapa
    graf_map_estado = px.scatter_mapbox(
        df_temp,
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
        # title="FATURAMENTO TOTAL POR ESTADO",
        mapbox_style="open-street-map",
        zoom=3
    )

    return graf_map_estado

def criar_grafico_linha_mensal(df, anos=None):
    # Criar DataFrame agregado por mês
    df_fat_mes = df.copy()
    
    # Filtrar por ano(s) se especificado
    if anos is not None and anos:
        df_fat_mes = df_fat_mes[df_fat_mes['data'].dt.year.isin(anos)]
    
    # Remover linhas com datas nulas
    df_fat_mes = df_fat_mes.dropna(subset=['data'])
    
    # Se não houver dados após a limpeza, retornar None
    if df_fat_mes.empty:
        return None
    
    # Converter para inteiro garantindo que não há NaN
    df_fat_mes['Ano'] = df_fat_mes['data'].dt.year.astype(int)
    df_fat_mes['Mês'] = df_fat_mes['data'].dt.month_name()
    df_fat_mes['Mês'] = df_fat_mes['Mês'].map(meses_pt)
    df_fat_mes["Num_Mês"] = df_fat_mes["data"].dt.month
    
    # Agrupar os dados
    df_fat_mes = df_fat_mes.groupby(['Mês', 'Ano', 'Num_Mês'])['valorNota'].sum().reset_index()
    df_fat_mes = df_fat_mes.rename(columns={'valorNota': 'Faturamento'})
    df_fat_mes = df_fat_mes.sort_values(['Ano', 'Num_Mês'])

    # Criar o gráfico
    grafico = px.line(
        df_fat_mes,
        x="Mês",
        y="Faturamento",
        color="Ano",
        markers=True,
        title="FATURAMENTO MÊS A MÊS"
    )

    # Calculando os valores para o eixo Y
    max_valor = df_fat_mes["Faturamento"].max()
    min_valor = 0
    step = 1000000  # Step de 1 milhão

    # Calculando o número de milhões necessários para cobrir o valor máximo
    num_milhoes = math.ceil(max_valor / step)  # Arredonda para cima
    max_escala = num_milhoes * step

    # Criando a sequência de valores para o eixo Y
    tick_values = [i * step for i in range(num_milhoes + 1)]

    # Atualizando o layout
    grafico.update_layout(
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(
            tickmode="array",
            tickvals=tick_values,
            ticktext=[f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                     for x in tick_values],
            tickprefix="",
            range=[0, max_escala],
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)',
            zeroline=True
        ),
        hoverlabel=dict(
            bgcolor="rgba(68, 68, 68, 0.9)",
            font=dict(
                color="white",
                size=12
            ),
            bordercolor="rgba(68, 68, 68, 0.9)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="white"
        ),
        showlegend=True,  # Mantém a legenda visível
        legend=dict(
            itemclick=False,  # Desabilita o clique nos itens da legenda
            itemdoubleclick=False  # Desabilita o duplo clique nos itens da legenda
        )
    )

    # Formatando os valores no hover (tooltip) e nos marcadores
    for i in range(len(grafico.data)):
        valores = df_fat_mes[df_fat_mes['Ano'] == int(grafico.data[i].name)]['Faturamento']
        grafico.data[i].text = ["" for _ in valores]  # Define texto vazio para os marcadores
        grafico.data[i].textposition = "top center"
        
        # Formatando os valores do hover no padrão brasileiro
        valores_formatados = [formatar_moeda(valor) for valor in valores]
        grafico.data[i].customdata = list(zip([grafico.data[i].name] * len(valores), valores_formatados))
        
        grafico.data[i].hovertemplate = (
            "<b>%{x}</b><br>" +
            "Ano: %{customdata[0]}<br>" +
            "Faturamento: %{customdata[1]}" +
            "<extra></extra>"
        )
        grafico.data[i].mode = "lines+markers"

    return grafico

def criar_grafico_barras_estado(df, anos=None):
    # Criar DataFrame filtrado por ano(s)
    df_temp = df.copy()
    
    # Filtrar por ano(s) se especificado
    if anos is not None and anos:  # Verifica se há anos selecionados
        df_temp = df_temp[df_temp['data'].dt.year.isin(anos)]
    
    # Se não houver dados após o filtro, retornar None
    if df_temp.empty:
        return None
        
    # Criar DataFrame agregado por estado
    df_fat_estado = df_temp.groupby("uf")[["valorNota"]].sum().reset_index()
    
    # Filtrar 'EX' antes de pegar os top 5
    df_fat_estado = df_fat_estado[df_fat_estado['uf'] != 'EX'].sort_values('valorNota', ascending=False).head(5)
    df_fat_estado = df_fat_estado.rename(columns={'valorNota': 'Faturamento'})
    df_fat_estado['Nome_Estado'] = df_fat_estado['uf'].map(siglas_estados)
    
    # Formatar os valores de faturamento para exibição
    df_fat_estado['Faturamento Total'] = df_fat_estado['Faturamento'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    
    # Criar o gráfico
    grafbar_fat_estado = px.bar(
        df_fat_estado,
        x='Nome_Estado',
        y='Faturamento',
        text='Faturamento Total',
        # title='FATURAMENTO POR ESTADO (TOP 5)'
    )
    
    # Configurar o layout do gráfico
    grafbar_fat_estado.update_traces(textposition='outside')
    grafbar_fat_estado.update_layout(
        xaxis_title="Estado",
        yaxis_title="Faturamento (R$)",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="white"
        )
    )
    
    return grafbar_fat_estado

def criar_grafico_barras_categoria(df, anos=None):
    # Criar DataFrame filtrado por ano(s)
    df_temp = df.copy()
    
    # Filtrar por ano(s) se especificado
    if anos is not None and anos:
        df_temp = df_temp[df_temp['data'].dt.year.isin(anos)]
    
    # Se não houver dados após o filtro, retornar None
    if df_temp.empty:
        return None
        
    # Criar DataFrame agregado por categoria
    df_fat_categoria = df_temp.groupby("subGrupo")[["valorNota"]].sum().reset_index()
    df_fat_categoria = df_fat_categoria.sort_values('valorNota', ascending=False).head()
    df_fat_categoria = df_fat_categoria.rename(columns={'valorNota': 'Faturamento', 'subGrupo': 'Sub Grupo'})

    # Criar o gráfico
    grafico = px.bar(
        df_fat_categoria,
        x='Sub Grupo',
        y='Faturamento',
        # title='FATURAMENTO POR SUB-CATEGORIA (TOP 5)'
    )
    
    # Calculando os valores para o eixo Y
    max_valor = df_fat_categoria['Faturamento'].max()
    min_valor = 0
    step = 10000000  # Step de 10 milhões
    num_steps = math.ceil(max_valor / step)
    max_escala = num_steps * step

    # Criando a sequência de valores para o eixo Y
    tick_values = [i * step for i in range(num_steps + 1)]

    # Atualizando o layout
    grafico.update_layout(
        xaxis_title="",  # Remove o título do eixo X
        yaxis_title="",  # Remove o título do eixo Y
        yaxis=dict(
            tickmode="array",
            tickvals=tick_values,
            ticktext=[f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                     for x in tick_values],
            range=[0, max_escala],
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.2)'
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="white"
        )
    )

    # Formatando os valores nas barras e definindo a cor da barra mais alta
    valores_formatados = [formatar_moeda(valor) for valor in df_fat_categoria['Faturamento']]
    grafico.update_traces(
        text=valores_formatados,
        textposition='auto',
        marker_color=['green' if x == max_valor else '#636EFA' 
                     for x in df_fat_categoria['Faturamento']],
        customdata=valores_formatados,
        hovertemplate="Sub-Categoria: %{x}<br>" +
                      "Faturamento: %{customdata}" +
                      "<extra></extra>"
    )

    return grafico

