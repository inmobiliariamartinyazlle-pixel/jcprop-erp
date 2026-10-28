import hashlib
import streamlit as st
from supabase import create_client
from modules import propiedades

# Configuración de la página
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

# Función para encriptar la contraseña (SHA-256)
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Función para validar credenciales en Supabase
def login_usuario(username, password):
    hash_p = make_hash(password)
    try:
        res = supabase.table("usuarios")\
            .select("*")\
            .eq("username", username)\
            .eq("password_hash", hash_p)\
            .execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        st.error(f"Error de conexión al autenticar: {e}")
        return None

# Manejo de sesión
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_info" not in st.session_state:
    st.session_state["usuario_info"] = None

# --- PANTALLA DE LOGIN ---
if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center;'>🏢 JCprop ERP</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Acceso Restringido - Sistema Inmobiliario M.P. 549</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            btn_login = st.form_submit_button("🔑 Iniciar Sesión", use_container_width=True)
            
            if btn_login:
                user_data = login_usuario(usuario.strip(), clave.strip())
                if user_data:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_info"] = user_data
                    st.success(f"Bienvenido/a {user_data['nombre']}")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

# --- APLICACIÓN PRINCIPAL (Sólo visible si inició sesión) ---
else:
    user_info = st.session_state["usuario_info"]
    
    # Menú Lateral
    st.sidebar.title("JCprop ERP 🏢")
    st.sidebar.caption(f"Usuario: {user_info['nombre']}")
    
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.session_state["usuario_info"] = None
        st.rerun()
        
    st.sidebar.markdown("---")
    
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
