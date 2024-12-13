import pandas as pd
import json
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, to_timestamp, date_format, round 
from datetime import datetime, timedelta
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, DateType, TimestampType

# Inicializando uma sessão no Spark
spark = SparkSession.builder \
    .appName("Vendas") \
    .getOrCreate()
# spark = SparkSession.builder.appName('processamento').getOrCreate()

# url com os dados
url = '


# Fazer a requisição
response = requests.get(url)

# Converter a resposta json, em um dicionário python
if response.status_code == 200:
    print('Dados carregados com sucesso.')
    dados = response.json()
else:
    raise Exception(f"Falha ao carregar dados. Erro: {response.status_code}")

# Cria um DataFrame PySpark a partir dos dados JSON
df_spark = spark.read.json(spark.sparkContext.parallelize([json.dumps(dados)]))

# Converter as colunas para oa formatos correto:
# Colunas de data
df_spark = (
        df_spark
       .withColumn("data", to_date(col("data"), "yyyy-MM-dd"))
       .withColumn("emissao", to_date(col("emissao"), "yyyy-MM-dd"))
       .withColumn("libfatura", to_timestamp(col("libfatura"),"yyyy-MM-dd HH:mm:ss"))
)

data_atual = datetime.now()
ano_inicio = data_atual.year -5
data_inicio = datetime(ano_inicio, 1, 1)  # 1º de janeiro do ano calculado

# Exibir a data de início para verificação
print(f"Filtrando dados a partir de: {data_inicio}")

df_spark = df_spark.filter(col("emissao") >= data_inicio)

# Carregar lista com as colunas string
colunas_string = ["filial"]

# Carregar lista com as colunas do tipo integer
colunas_integer = ["sequencial", "tipo", "codtra", "os", "itemOs", "item", "codGrupo", "codSubGrupo",
                    "codVendedor", "tipoOs", "codRegiao", "servico"
]

# Fazer a conversão
for col_int in colunas_integer:
    df_spark = df_spark.withColumn(col_int, col(col_int).cast(IntegerType()))

# Preencher as colunas integer com valor padrão, caso elas contenham valor null
df_spark = df_spark.fillna(0, subset=colunas_integer)

# Carregar lista com as colunas do tipo double
colunas_double = ["valorfaturado", "quant", "valoruni", "valoripi", "valoricms", "valoriss", "valorSubs",
                    "valorNota", "valorFrete", "valorContabil", "retVlrPis", "retVlrCofins", "retVlrCsll",
                    "valorPis", "valorCofins", "aliqIpi", "aliqIcms", "porcReducaoIcms", "baseIcms", "valorCusto",
                    "valorDesconto"
]
df_spark = df_spark.fillna(0.00, subset=colunas_double)
df_spark = df_spark.withColumn("valorfaturado", round(col("valorfaturado"), 2))

# Fazer a conversão
for col_double in colunas_double:
    df_spark =  df_spark.withColumn(col_double, col(col_double).cast(DoubleType()))



# Ordena as colunas de acordo com a ordenação do banco de dados
ordem_colunas = [
    "sequencial", "tipo", "filial", "codtra", "os", "itemOs", "codcli", "cnpj", "razao", "fantasia",
    "cfop", "data", "emissao", "nota", "serie", "chaveNfe", "item", "codProduto", "produto",
    "unidSaida", "ncm", "codGrupo", "grupo", "codSubGrupo", "subGrupo", "codVendedor", "vendedor",
    "vendedorRed", "cidade", "uf", "tipoOs", "descricaoTipoOs", "codRegiao", "regiao",
    "valorfaturado", "quant", "valoruni", "valoripi", "valoricms", "valoriss", "valorSubs",
    "valorFrete", "valorNota", "valorContabil", "retVlrPis", "retVlrCofins", "retVlrCsll",
    "valorPis", "valorCofins", "aliqIpi", "aliqIcms", "porcReducaoIcms", "cstIcms", "baseIcms",
    "valorCusto", "valorDesconto", "desctra", "servico", "libFatura"
]

# Reordene as colunas no dataframe spark
df_spark = df_spark.select([col(c) for c in ordem_colunas])

# df_spark.printSchema()

# Converter para Pandas DataFrame
df = df_spark.toPandas()

# Dicionário contendo todos os Estados do Brasil e suas respectivas coordenadas.
coordenadas = {
    "AC": {"latitude": -8.77, "longitude": -70.55},
    "AL": {"latitude": -9.62, "longitude": -36.82},
    "AP": {"latitude": 1.41, "longitude": -51.77},
    "AM": {"latitude": -3.47, "longitude": -65.10},
    "BA": {"latitude": -12.96, "longitude": -38.51},
    "CE": {"latitude": -3.71, "longitude": -38.54},
    "DF": {"latitude": -15.83, "longitude": -47.86},
    "ES": {"latitude": -19.19, "longitude": -40.34},
    "GO": {"latitude": -16.64, "longitude": -49.31},
    "MA": {"latitude": -2.55, "longitude": -44.30},
    "MT": {"latitude": -12.64, "longitude": -55.42},
    "MS": {"latitude": -20.44, "longitude": -54.65},
    "MG": {"latitude": -18.10, "longitude": -44.38},
    "PA": {"latitude": -3.13, "longitude": -52.29},
    "PB": {"latitude": -7.06, "longitude": -35.55},
    "PR": {"latitude": -24.89, "longitude": -51.55},
    "PE": {"latitude": -8.28, "longitude": -35.07},
    "PI": {"latitude": -8.28, "longitude": -43.68},
    "RJ": {"latitude": -22.84, "longitude": -43.15},
    "RN": {"latitude": -5.22, "longitude": -36.52},
    "RS": {"latitude": -30.01, "longitude": -51.22},
    "RO": {"latitude": -11.22, "longitude": -62.80},
    "RR": {"latitude": 1.89, "longitude": -61.22},
    "SC": {"latitude": -27.33, "longitude": -49.44},
    "SP": {"latitude": -23.55, "longitude": -46.63},
    "SE": {"latitude": -10.90, "longitude": -37.07},
    "TO": {"latitude": -10.18, "longitude": -48.33},
}

# Inserindo as colunas de latitude e longitude no DataFrame com base na coluna 'uf'
# Obs.: O método map do Pandas serve para aplicar o mapeamento linha por linha, ou seja,
# ele aplica uma função (ou mapeamento) para cada valor da coluna uf.
df['latitude'] = df['uf'].map(lambda x: coordenadas[x]['latitude'] if x in coordenadas else None)
df['longitude'] = df['uf'].map(lambda x: coordenadas[x]['longitude'] if x in coordenadas else None)


df.index = df.index + 1
df.style.set_properties(**{'text-align':'center'}, subset=['valoruni'])

# Remover pontuação das colunas que não precisam de separdores
df["sequencial"] = pd.to_numeric(df["sequencial"].apply(lambda x: str(x).replace(",", "")), errors="coerce", downcast="integer")
df["os"] = pd.to_numeric(df["os"].apply(lambda x: str(x).replace(",", "")), errors="coerce", downcast="integer")

# Padronizar os valores
df["itemOs"]    = pd.to_numeric(df["itemOs"], errors="coerce")
df["codGrupo"]  = pd.to_numeric(df["codGrupo"], errors="coerce")

# Substituir valor none por n/c
df["valoriss"] = df["valoriss"].replace('nan', '0,00')  # Caso 'nan' seja string
df["valorfaturado"] = df["valorfaturado"].replace('NaN', 0.00)
df["grupo"]    = df["grupo"].replace('none', 'N/C')

# Garantir que as colunas 'data' e 'emissao' sejam convertidas para o tipo datetime no Pandas
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df['emissao'] = pd.to_datetime(df['emissao'], errors='coerce')

print('Estrutura do DataFrame df:')
print(df[["cidade", "uf","regiao", "latitude", "longitude"]].head(100))

response.close()
spark.stop()