import pandas as pd
import json
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, to_timestamp, date_format 
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DoubleType, DateType, TimestampType

# Inicializando uma sessão no Spark
spark = SparkSession.builder \
    .appName("Vendas") \
    .getOrCreate()
# spark = SparkSession.builder.appName('processamento').getOrCreate()

# url com os dados
url = 'http://tecnolife.empresamix.info:8077/POWERBI/?CLIENTE=TECNOLIFE&ID=XIOPMANA&VIEW=CUBO_FATURAMENTO'

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

       # Converter as datas para o formato pt-br
       .withColumn("data", date_format(col("data"), "dd-MM-yyyy"))
       .withColumn("emissao", date_format(col("emissao"), "dd-MM-yyyy"))
       .withColumn("libfatura", date_format(col("libfatura"), "dd-MM-yyyy HH:mm:ss"))
)

# Carregar lista com as colunas do tipo integer
colunas_integer = ["sequencial", "tipo", "codtra", "os", "itemOs", "item", "codGrupo", "codSubGrupo",
                    "codVendedor", "tipoOs", "codRegiao", "servico"
]

# Fazer a conversão
for col_int in colunas_integer:
    df_spark = df_spark.withColumn(col_int, col(col_int).cast(IntegerType()))

# Carregar lista com as colunas do tipo double
colunas_double = ["valorfaturado", "quant", "valoruni", "valoripi", "valoricms", "valoriss", "valorSubs",
                    "valorNota", "valorFrete", "valorContabil", "retVlrPis", "retVlrCofins", "retVlrCsll",
                    "valorPis", "valorCofins", "aliqIpi", "aliqIcms", "porcReducaoIcms", "baseIcms", "valorCusto",
                    "valorDesconto"
]

# Fazer a conversão
for col_double in colunas_double:
    df_spark =  df_spark.withColumn(col_double, col(col_double).cast(DoubleType()))



# Ordena as colunas de acordo com a ordenação do banco de dados
column_order = [
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
df_spark = df_spark.select([col(c) for c in column_order])

df_spark.printSchema()
# df.show(n=5, truncate=False)

# Converter para Pandas DataFrame
df = df_spark.toPandas()

print(df[['sequencial','filial','razao','data', 'emissao','libFatura']].head(20))

response.close()
spark.stop()