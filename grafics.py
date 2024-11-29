import plotly.express as px
import numpy as np
# Normaliza 'valorNota' para ajustar o tamanho das bolhas
from sklearn.preprocessing import MinMaxScaler
from utils import df_rec_estado

# -------------------- GRÁFICO DE RECEITA POR ESTADO -------------------- #
'''
graf_rec_estado = px.scatter_geo(
    df_rec_estado,
    lat        = 'latitude',
    lon        = 'longitude',
    scope      = 'south america',
    size       = 'valorNota',
    template   = 'seaborn',
    hover_name = 'uf',
    hover_data = {'latitude' : False, 'longitude': False},
    title      = "RECEITA POR ESTADO"
)
'''
'''
# Adiciona uma coluna transformada para escala logarítmica
df_rec_estado['log_valorNota'] = np.log1p(df_rec_estado['valorNota'])

graf_rec_estado = px.density_mapbox(
    df_rec_estado,
    lat='latitude',
    lon='longitude',
    z='log_valorNota',
    radius=25,  # Ajusta o tamanho dos pontos
    center={"lat": -14.235, "lon": -51.925},  # Latitude e longitude aproximada do Brasil
    zoom=3,  # Nível de zoom inicial
    mapbox_style="open-street-map",  # Estilo do mapa
    title="RECEITA POR ESTADO"
)
'''
siglas_estados = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
}

# Adicionar a coluna com os nomes completos dos estados
df_rec_estado['estado_nome'] = df_rec_estado['uf'].map(siglas_estados)

# Renomear e formatar o faturamento total no formato brasileiro
df_rec_estado['Faturamento Total'] = df_rec_estado['valorNota'].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# Normaliza 'valorNota' para ajustar o tamanho das bolhas
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(5, 50))  # Ajusta o tamanho das bolhas (5 a 50 é um exemplo)
df_rec_estado['bubble_size'] = scaler.fit_transform(df_rec_estado[['valorNota']])

# Cria o mapa
graf_rec_estado = px.scatter_mapbox(
    df_rec_estado,
    lat='latitude',
    lon='longitude',
    size='bubble_size',
    color_discrete_sequence=['blue'],
    hover_name='estado_nome',  # Nome completo do estado
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
