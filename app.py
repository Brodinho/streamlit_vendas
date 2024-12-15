import streamlit as st
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Carregar imagem
image = Image.open('imagens/sales.png')

# Layout da página inicial
col1, col2 = st.columns([1, 6])
with col1:
    st.image(image, use_container_width=True)
with col2:
    st.title("Dashboard de Vendas")
    st.subheader("E m p r e s a m i x")

# Descrição do sistema
st.markdown("""
### Bem-vindo ao Dashboard de Vendas

Este sistema oferece três principais visualizações:

1. **📊 Gráficos**: Visualização de dados através de mapas e gráficos interativos
2. **📋 Dataset**: Exploração detalhada dos dados com filtros personalizados
3. **👥 Vendedores**: Análise específica do desempenho dos vendedores

Utilize o menu lateral esquerdo para navegar entre as diferentes páginas.
""")

# Métricas principais (exemplo)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total de Vendas", value="R$ 1.234.567,89")
with col2:
    st.metric(label="Número de Pedidos", value="1.234")
with col3:
    st.metric(label="Ticket Médio", value="R$ 999,99")
with col4:
    st.metric(label="Total de Clientes", value="456")

