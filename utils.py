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

# -------------------- FUNÇÕES: FIM -------------------- #



# -------------------- DATAFRAME DE FATURAMENTO POR ESTADO -------------------- #

df_fat_estado = df.groupby("uf")[["valorNota"]].sum()
df_fat_estado = df.drop_duplicates(subset="uf")[["uf", "latitude", "longitude"]].merge(df_fat_estado, left_on="uf", right_index=True).sort_values("valorNota", ascending=False)

# Renomeando a coluna valorNota
df_fat_estado = df_fat_estado.rename(columns={'valorNota': 'Faturamento'})

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


