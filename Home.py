import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide"
)

# Título
st.title("📊 Dashboard de Vendas")

# Descrição das páginas
st.markdown("""
### Navegue pelas páginas no menu lateral:

- **📊 Gráficos**: Visualize os principais indicadores em gráficos
- **📈 Métricas**: Acompanhe as métricas de vendas
- **👥 Vendedores**: Análise detalhada por vendedor
- **📊 Budget**: Análise comparativa de metas vs realizado

""")

# Mensagem no sidebar
st.sidebar.success("Selecione uma página acima.") 