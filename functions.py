import pandas as pd
import math

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

    
