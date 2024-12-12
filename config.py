import streamlit as st
import json
import os

def salvar_configuracoes(config):
    with open('config_dashboard.json', 'w') as f:
        json.dump(config, f)

def carregar_configuracoes():
    if os.path.exists('config_dashboard.json'):
        with open('config_dashboard.json', 'r') as f:
            return json.load(f)
    return None

def configurar_dashboard():
    st.title('Configuração do Dashboard')
    st.write('Selecione os gráficos que deseja visualizar:')

    # Lista de gráficos disponíveis
    graficos = {
        'mapa': 'Mapa de Faturamento por Estado/País',
        'barras_estado': 'Gráfico de Barras - Top 5 Estados/Países',
        'linha_mensal': 'Gráfico de Linha - Faturamento Mensal',
        # Adicione outros gráficos aqui
    }

    # Criar checkboxes para cada gráfico
    selecao_graficos = {}
    for key, descricao in graficos.items():
        selecao_graficos[key] = st.checkbox(descricao, value=True)  # True para começar marcado

    # Botão para salvar configurações
    if st.button('Salvar Configurações e Iniciar Dashboard'):
        salvar_configuracoes(selecao_graficos)
        st.success('Configurações salvas! Você pode fechar esta janela e iniciar o dashboard.')
        
    st.write('---')
    st.write('Para aplicar as alterações, reinicie o dashboard após salvar as configurações.')

if __name__ == '__main__':
    configurar_dashboard() 