import pandas as pd
import requests

# URL da API
url = "http://tecnolife.empresamix.info:8077/POWERBI/?CLIENTE=TECNOLIFE&ID=XIOPMANA&VIEW=CUBO_FATURAMENTO"

# Fazer requisição GET para a API
response = requests.get(url)
data = response.json()

# Converter para DataFrame
df = pd.DataFrame(data)

# Mapeamento de nomes de colunas
mapeamento_colunas = {
    'sequencial': 'Sequencial',
    'os': 'Ordem de Serviço',
    'data': 'Data',
    'emissao': 'Data de Emissão',
    'codGrupo': 'Código do Grupo',
    'grupo': 'Grupo',
    'codVendedor': 'Código do Vendedor',
    'vendedor': 'Vendedor',
    'codcli': 'Código do Cliente',
    'cliente': 'Cliente',
    'nota': 'Nota Fiscal',
    'valorfaturado': 'Valor Faturado',
    'valoripi': 'Valor IPI',
    'valoricms': 'Valor ICMS',
    'valoriss': 'Valor ISS',
    'valorSubs': 'Valor Substituição',
    'valorFrete': 'Valor Frete',
    'valorNota': 'Valor da Nota',
    'valorContabil': 'Valor Contábil',
    'retVlrPis': 'Retenção PIS',
    'retVlrCofins': 'Retenção COFINS',
    'baseIcms': 'Base ICMS',
    'valorCusto': 'Valor Custo',
    'valorDesconto': 'Valor Desconto',
    'libFatura': 'Liberação Fatura'
}

# Converter colunas de data
date_columns = ['data', 'emissao', 'libFatura']
for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Tratar valores nulos na coluna vendedor
df['vendedor'] = df['vendedor'].fillna('Não Informado')