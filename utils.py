import pandas as pd
import math
from dataset import df
import numpy as np
import locale

# -------------------- FUNÇÕES: INÍCIO -------------------- #
# Função para converter os valores das colunas monetárias para numeric
def formata_colunas_monetarias(df, colunas):
    for coluna in colunas:
        # Força a conversão da coluna para tipo numérico (float), caso estejam como string
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce')  
        '''
        # Aplica a formatação, considerando valores nulos
        df[coluna] = df[coluna].apply(
            lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
            if pd.notnull(x) else ""
        )
        '''
    return df

# Função para formatar valores no padrão brasileiro nos rótulos dos gráficos
def formatar_valor(valor):
    return locale.format_string("R$ %.2f", valor, grouping=True)

# Formatar moeda
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para formatar valores monetários no padrão brasileiro
def formatar_valor_monetario(valor):
    return locale.currency(valor, grouping=True)

# Função para extrair a sigla do país
def extrair_sigla_pais(pais):
    mapeamento_paises = {
        'COLOMBIA': 'COL',
        'PERU': 'PER',
        'ARGENTINA': 'ARG',
        'ESTADOS UNIDOS': 'EUA',
        'EL SALVADOR': 'ELS'
        # Adicione outros países conforme necessário
    }
    return mapeamento_paises.get(str(pais).upper(), 'EX')

# Adicionar dicionário com as coordenadas dos países
coordenadas_paises = {
    'EUA': {'lat': 37.0902, 'lon': -95.7129},    # Estados Unidos
    'COL': {'lat': 4.5709, 'lon': -74.2973},     # Colômbia
    'PER': {'lat': -9.1900, 'lon': -75.0152},    # Peru
    'ARG': {'lat': -38.4161, 'lon': -63.6167},   # Argentina
    'ELS': {'lat': 13.7942, 'lon': -88.8965},    # El Salvador
    'MEX': {'lat': 23.6345, 'lon': -102.5528},   # México
    'CHI': {'lat': -35.6751, 'lon': -71.5430},   # Chile
    'GUA': {'lat': 15.7835, 'lon': -90.2308},    # Guatemala
    'HON': {'lat': 15.2000, 'lon': -86.2419},    # Honduras
    'NIC': {'lat': 12.8654, 'lon': -85.2072},    # Nicarágua
    'PAN': {'lat': 8.5380, 'lon': -80.7821},     # Panamá
    'BOL': {'lat': -16.2902, 'lon': -63.5887},   # Bolívia
    'URU': {'lat': -32.5228, 'lon': -55.7658},   # Uruguai
    'PAR': {'lat': -23.4425, 'lon': -58.4438},   # Paraguai
    'CRI': {'lat': 9.7489, 'lon': -83.7534},     # Costa Rica
}

# Modificação na construção do df_fat_estado
def criar_df_fat_estado(df):
    # Dicionário com as coordenadas dos estados
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
    
    # Agrupa por estado e soma o valor faturado
    df_temp = df.groupby('uf')['valorfaturado'].sum().reset_index()
    
    # Adiciona as coordenadas
    df_temp['latitude'] = df_temp['uf'].map(lambda x: coordenadas_estados.get(x, {}).get('latitude'))
    df_temp['longitude'] = df_temp['uf'].map(lambda x: coordenadas_estados.get(x, {}).get('longitude'))
    
    return df_temp

# -------------------- FUNÕES: FIM -------------------- #



# -------------------- DATAFRAME DE FATURAMENTO POR ESTADO -------------------- #

df_fat_estado = criar_df_fat_estado(df)

# -------------------- DATAFRAME DE FATURAMENTO POR MÊS-A-MÊS E ANO -------------------- #
data_inicio = df["data"].min()  # Menor data diretamente da coluna 'data'
ano_inicio = data_inicio.year   # Ano correspondente à menor data
data_atual = df["data"].max()   # Maior data diretamente da coluna 'data'

# Simulação de dados (substitua com sua lógica real de extração)
data = pd.date_range(start=data_inicio, end=data_atual, freq="M")
# valorNota = np.random.uniform(2000, 200000, len(data))
# df = pd.DataFrame({"data": data, "valorNota": valorNota})

# Mapeamento dos meses do inglês para o português
meses_pt = {
    "January"  : "Janeiro",
    "February" : "Fevereiro",
    "March"    : "Março",
    "April"    : "Abril",
    "May"      : "Maio",
    "June"     : "Junho",
    "July"     : "Julho",
    "August"   : "Agosto",
    "September": "Setembro",
    "October"  : "Outubro",
    "November" : "Novembro",
    "December" : "Dezembro"
}
# set_index('emissao'): Define a coluna emissao como índice para a operação de agrupamento.
# groupby(pd.Grouper(freq='M')): Agrupa os dados por mês, usando pd.Grouper com a frequência mensal ('M').
# ['valorNota']: Acessa diretamente a coluna valorNota para aplicar a soma.
# .sum(): Soma os valores da coluna valorNota para cada grupo.
# .reset_index(): Reseta o índice para transformar o resultado em um DataFrame padrão.
df_fat_mes = (
    df.set_index("data")
    .groupby(pd.Grouper(freq="M"))["valorNota"]
    .sum()
    .reset_index()
)



df_fat_mes['Mês'] = df_fat_mes['data'].dt.month_name()  # Obtém o nome do mês a partir da coluna 'data'
df_fat_mes['Ano'] = df_fat_mes['data'].dt.year  # Obtém o ano a partir da coluna 'data'

# Substituindo os nomes dos meses para português
df_fat_mes['Mês'] = df_fat_mes['Mês'].map(meses_pt)

# Adicionar uma coluna com o número do mês
df_fat_mes["Num_Mês"] = df_fat_mes["data"].dt.month

# Renomeando a coluna valorNota
df_fat_mes = df_fat_mes.rename(columns={'valorNota' : 'Faturamento'})

# Ordenar o DataFrame pelo ano e pelo número do mês
df_fat_mes = df_fat_mes.sort_values(["Ano", "Num_Mês"])

# -------------------- DATAFRAME DE CATEGORIAS DE PRODUTOS -------------------- #

df_fat_categoria = df.groupby("subGrupo")[["valorNota"]].sum().sort_values("valorNota", ascending=False)

# Garantir que todos os subgrupos estejam presentes (incluindo os que não têm vendas)
all_subgrupos = df['subGrupo'].unique()  # Pega todos os subgrupos existentes no dataframe original
df_fat_categoria = df_fat_categoria.reindex(all_subgrupos)  # Reindexa para garantir que todos os subgrupos apareçam

df_fat_categoria = df_fat_categoria.fillna(0.00).astype(float)
# Resetando o índice para que 'subGrupo' seja uma coluna novamente
df_fat_categoria = df_fat_categoria.reset_index()
df_fat_categoria = df_fat_categoria.rename(columns={"valorNota" : "Faturamento", "subGrupo" : "Sub Grupo"})

print('Dataframe: df_fat_categoria:')
print(df_fat_categoria.head())


