import pandas as pd
import math
from dataset import df

# -------------------- FUNÇÃO PARA FORMATAR COLUNAS MONTÁRIAS -------------------- #
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

# -------------------- FUNÇÃO PARA GERAR O DATAFRAME DE FATURAMENTO POR ESTADO -------------------- #
df_rec_estado = df.groupby("uf")[["valorNota"]].sum()
df_rec_estado = df.drop_duplicates(subset="uf")[["uf", "latitude", "longitude"]].merge(df_rec_estado, left_on="uf", right_index=True).sort_values("valorNota", ascending=False)
print("df_rec_estado")
print(df_rec_estado)