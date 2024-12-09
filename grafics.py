import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import locale
from utils import formatar_moeda
import math

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
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
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
    title="FATURAMENTO TOTAL POR ESTADO",
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
graflinha_fat_mensal.update_layout(
    yaxis=dict(
        tickmode="array",
        tickvals=tick_values,
        ticktext=[f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
                 for x in tick_values],
        tickprefix="",
        range=[0, max_escala],  # Define o intervalo do eixo Y
        showgrid=True,          # Mostra as linhas de grade
        gridwidth=1,            # Largura das linhas de grade
        gridcolor='rgba(128, 128, 128, 0.2)',  # Cor das linhas de grade
        zeroline=True          # Mostra a linha do zero
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
grafbar_fat_estado = px.bar(
    df_fat_estado.head(),
    x = 'Nome_Estado',
    y = 'Faturamento',
    text_auto=True,
    title='FATURAMENTO POR ESTADO (TOP 5)'
)

grafbar_fat_estado.update_layout(
    xaxis_title = "ESTADOS",
    # yaxis_tickformat = "R$, .2f"
    yaxis_tickformat = "TESTE ,.2f"  # Formato monetário com ponto para milhares e vírgula para decimais
)

grafbar_fat_estado.update_traces(
    hovertemplate="Faturamento: R$ %{y:,.2f}<extra></extra>"
)


# -------------------- GRÁFICO DE BARRAS: FATURAMENTO POR SUB-GRUPO -------------------- #
graf_fat_categoria = px.bar(
    df_fat_categoria.head(),
    x = "Sub Grupo",
    y = "Faturamento",
    text_auto=True,
    title="FATURAMENTO POR SUB-CATEGORIA (TOP 5)"
)

