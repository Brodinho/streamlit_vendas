import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from dataset import df
import locale

# Configuração da página - DEVE SER O PRIMEIRO COMANDO ST
st.set_page_config(
    page_title="Budget - Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
)

# Configurar locale para português brasileiro
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Estilo CSS personalizado
st.markdown("""
<style>
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
        flex: 1;
        min-width: 200px;
        height: 140px;
        display: flex;
        flex-direction: column;
    }
    .metric-card .label {
        color: #FFFFFF;
        font-size: 0.9em;
        margin-bottom: 10px;
    }
    .metric-card .value {
        color: #FFFFFF;
        font-size: 1.3em;
        font-weight: bold;
        word-wrap: break-word;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    .metric-card .delta {
        font-size: 0.9em;
        margin-top: auto;
        padding-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Título da página
st.title("📊 Análise de Budget vs Forecast")

# Função para formatar valores monetários
def formato_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para formatar valores monetários no padrão brasileiro
def formato_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Função para determinar cor do status
def get_status_color(realizado, meta):
    if realizado >= meta:
        return "normal"  # verde quando atinge ou supera a meta
    elif realizado >= meta * 0.9:  # 90% da meta
        return "off"     # neutro quando está próximo
    return "inverse"     # vermelho quando está abaixo

# No sidebar, adicionar input para o percentual
with st.sidebar:
    st.header("Configurações de Meta")
    percentual_meta = st.slider(
        "Percentual de aumento sobre ano anterior (%)",
        min_value=0,
        max_value=100,
        value=10,
        step=5
    )

# Preparar dados
ano_atual = pd.Timestamp.now().year
ano_anterior = ano_atual - 1

# Filtrar dados por ano
df_anterior = df[df['data'].dt.year == ano_anterior]
df_atual = df[df['data'].dt.year == ano_atual]

# Calcular faturamento total do ano anterior
faturamento_anterior = df_anterior['valorfaturado'].sum()

# Calcular meta com o percentual definido
meta_total = faturamento_anterior * (1 + percentual_meta/100)

# Calcular meta mensal (distribuída igualmente)
meta_mensal = meta_total / 12

# Preparar dados mensais
dados_anterior = df_anterior.groupby(df_anterior['data'].dt.strftime('%m'))['valorfaturado'].sum()
dados_atual = df_atual.groupby(df_atual['data'].dt.strftime('%m'))['valorfaturado'].sum()

# Calcular projeção e métricas de acompanhamento
mes_atual = pd.Timestamp.now().month
faturamento_atual_acumulado = dados_atual.sum()
media_mensal_atual = faturamento_atual_acumulado / mes_atual if mes_atual > 0 else 0
projecao_anual = faturamento_atual_acumulado + (media_mensal_atual * (12 - mes_atual))

# Calcular valores para os KPIs
# Pegar o último mês com dados
ultimo_mes_com_valor = max(dados_atual.index) if not dados_atual.empty else str(mes_atual).zfill(2)
ultimo_mes = dados_atual.get(ultimo_mes_com_valor, 0)  # Pegar o valor do último mês com dados
variacao_mensal = ((ultimo_mes/meta_mensal)-1)*100 if meta_mensal > 0 else 0
percentual_atingido = (faturamento_atual_acumulado/meta_total)*100 if meta_total > 0 else 0

# Mostrar KPIs principais em cartões
st.markdown("""
<div class="metric-container">
    <div class="metric-card">
        <div class="label">Meta Mensal</div>
        <div class="value">{}</div>
    </div>
    <div class="metric-card">
        <div class="label">Realizado Mês Atual</div>
        <div class="value">{}</div>
        <div class="delta" style="color: {}">{}</div>
    </div>
    <div class="metric-card">
        <div class="label">Projeção Anual</div>
        <div class="value">{}</div>
        <div class="delta">{}</div>
    </div>
    <div class="metric-card">
        <div class="label">% Meta Anual Atingida</div>
        <div class="value">{}</div>
    </div>
</div>
""".format(
    formato_moeda(meta_mensal),
    formato_moeda(ultimo_mes),
    'red' if variacao_mensal < 0 else 'green',
    f"{variacao_mensal:,.1f}%",
    formato_moeda(projecao_anual),
    f"{((projecao_anual/meta_total)-1)*100:,.1f}%",
    f"{percentual_atingido:,.1f}%"
), unsafe_allow_html=True)

# Mostrar apenas uma vez a informação do mês atual e último valor realizado
st.markdown(f"""
    <div style='margin: 10px 0;'>
        <div style='font-size: 0.9em;'>Mês atual: {mes_atual}</div>
        <div style='font-size: 0.9em;'>Último valor realizado: {formato_moeda(ultimo_mes)}</div>
    </div>
""", unsafe_allow_html=True)

# Criar DataFrame para o gráfico
meses = pd.date_range(start=f'{ano_atual}-01-01', periods=12, freq='M')
mes_atual = pd.Timestamp.now().month

# Preparar dados do realizado
dados_realizados = [dados_atual.get(m.strftime('%m'), 0) for m in meses[:mes_atual]]
ultimo_valor_realizado = dados_realizados[-1] if dados_realizados else 0

# Debug - Imprimir informações importantes
# st.write("Mês atual:", mes_atual)
# st.write("Último valor realizado:", ultimo_valor_realizado)

# Criar gráfico
fig = go.Figure()

# Encontrar o último mês com valor realizado
ultimo_mes_com_valor = max(dados_atual.index) if not dados_atual.empty else '00'
mes_ultimo_realizado = int(ultimo_mes_com_valor)

# Calcular o forecast para dezembro
if mes_ultimo_realizado < 12:
    ultimo_valor = dados_atual.get(ultimo_mes_com_valor, 0)
    meses_restantes = 12 - mes_ultimo_realizado
    valor_necessario_dezembro = meta_mensal + (meta_total - (dados_atual.sum() + meta_mensal))

# Dicionário de meses em português
meses_pt = {
    'jan': 'Janeiro',
    'fev': 'Fevereiro',
    'mar': 'Março',
    'abr': 'Abril',
    'mai': 'Maio',
    'jun': 'Junho',
    'jul': 'Julho',
    'ago': 'Agosto',
    'set': 'Setembro',
    'out': 'Outubro',
    'nov': 'Novembro',
    'dez': 'Dezembro'
}

# Função para converter mês em inglês para português
def converter_mes(mes_ingles):
    conversao = {
        'jan': 'jan', 'feb': 'fev', 'mar': 'mar',
        'apr': 'abr', 'may': 'mai', 'jun': 'jun',
        'jul': 'jul', 'aug': 'ago', 'sep': 'set',
        'oct': 'out', 'nov': 'nov', 'dec': 'dez'
    }
    return conversao.get(mes_ingles.lower(), mes_ingles.lower())

# Linha da Meta
fig.add_trace(go.Scatter(
    x=meses.strftime('%b').str.lower(),
    y=[meta_mensal] * 12,
    name='Meta',
    line=dict(color='gray', width=1),
    hoverinfo='skip'
))

# Linha do Realizado
valores_realizados = [dados_atual.get(m.strftime('%m'), 0) for m in meses[:mes_ultimo_realizado]]
realizado_acumulado = []
for i in range(len(valores_realizados)):
    realizado_acumulado.append(sum(valores_realizados[:i+1]))

# Preparar dados customizados para o hover
hover_data = []
for i, m in enumerate(meses[:mes_ultimo_realizado]):
    mes_abrev = converter_mes(m.strftime('%b'))
    mes_nome = meses_pt[mes_abrev]
    valor_realizado = valores_realizados[i]
    valor_acumulado = realizado_acumulado[i]
    valor_forecast = meta_total - valor_acumulado
    
    hover_text = (
        f'Mês: {mes_nome}<br>' +
        f'Realizado no mês: {formato_br(valor_realizado)}<br>' +
        f'Budget: {formato_br(meta_total)}<br>' +
        f'Forecast: {formato_br(valor_forecast)}'
    )
    
    hover_data.append(hover_text)

# Linha do Realizado
fig.add_trace(go.Scatter(
    x=meses[:mes_ultimo_realizado].strftime('%b').str.lower(),
    y=valores_realizados,
    name='Realizado',
    line=dict(color='blue', width=2),
    text=hover_data,
    hovertemplate='%{text}<extra></extra>',
    hoverinfo='text'
))

# Configurar layout
fig.update_layout(
    title=f'Análise de Meta vs Realizado {ano_atual}',
    xaxis_title=None,
    yaxis=dict(
        tickformat=",.2f",
        tickprefix="R$ ",
        separatethousands=True,
        title=None
    ),
    legend_title=None,
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    showlegend=True
)

# Adicionar anotação sobre o forecast em dezembro
fig.add_annotation(
    x=meses[-1].strftime('%b').lower(),  # Dezembro
    y=meta_mensal,
    text=f'Necessário em Dezembro: {formato_br(meta_total - sum(valores_realizados))}',
    showarrow=True,
    arrowhead=1,
    ax=0,
    ay=-40
)

st.plotly_chart(fig, use_container_width=True)

# Mostrar KPIs adicionais
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Faturamento Ano Anterior",
        value=formato_moeda(faturamento_anterior)
    )
with col2:
    st.metric(
        label="Meta Anual",
        value=formato_moeda(meta_total)
    )
with col3:
    variacao = ((faturamento_atual_acumulado/meta_total)-1)*100 if meta_total > 0 else 0
    st.metric(
        label="Realizado Atual",
        value=formato_moeda(faturamento_atual_acumulado),
        delta=f"{variacao:,.1f}%"
    )