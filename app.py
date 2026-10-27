import streamlit as st
from supabase import create_client
from modules import propiedades

# Configuración de página
st.set_page_config(
    page_title="JCprop ERP - Gestión Inmobiliaria",
    page_icon="🏠",
    layout="wide"
)

# Inicializar conexión a Supabase usando st.secrets
@st.cache_resource
def init_supabase():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

# Menú Lateral
st.sidebar.title("JCprop ERP 🏢")
st.sidebar.caption("M.P. 549 - Salta, Argentina")

opcion = st.sidebar.radio(
    "Navegación",
    [
        "Propiedades",
        "Clientes (Próximamente)",
        "Operaciones (Próximamente)",
        "Agenda (Próximamente)",
        "Comisiones (Próximamente)",
        "Reportes (Próximamente)"
    ]
)

# Enrutamiento de módulos
if opcion == "Propiedades":
    propiedades.render_modulo(supabase)
else:
    st.title(f"Módulo: {opcion}")
    st.info("Este módulo se activará en la siguiente fase de desarrollo.")
