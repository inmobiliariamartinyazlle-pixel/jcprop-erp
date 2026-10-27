import streamlit as st
import pandas as pd

# Mapeo de Barrios de Salta y sus Zonas correspondientes
BARRIOS_SALTA = {
    "Centro": "Centro",
    "Macrocentro": "Macrocentro",
    "Tres Cerritos": "Norte",
    "Ciudad del Milagro": "Norte",
    "Parque Belgrano": "Norte",
    "Castañares": "Norte",
    "Intersindical": "Sur",
    "El Tribuno": "Sur",
    "Santa Ana": "Sur",
    "Las Marías": "Sur",
    "Grand Bourg": "Oeste",
    "San Martín": "Oeste",
    "Villa Las Rosas": "Este",
    "Autódromo": "Este",
    "San Lorenzo": "San Lorenzo",
    "San Lorenzo Chico": "San Lorenzo Chico",
    "El Tipal": "San Lorenzo Chico"
}

TIPOLOGIAS = [
    "Casa", 
    "Departamento", 
    "Duplex", 
    "Terreno/lote", 
    "Local Comercial", 
    "Oficina", 
    "Galpón", 
    "Campo"
]

PORTALES = ["Marketplace", "Zonaprop", "Argenprop", "Redes Sociales", "Web Propia"]

def render_modulo(supabase):
    st.title("Gestión de Propiedades 🏠")
    
    tab1, tab2 = st.tabs(["📋 Ver Inventario", "➕ Cargar Propiedad"])
    
    # ---------------- TAB 1: VER INVENTARIO ----------------
    with tab1:
        st.subheader("Inventario de Propiedades")
        
        try:
            res = supabase.table("propiedades").select("*").execute()
            datos = res.data
            
            if datos:
                df = pd.DataFrame(datos)
                
                # Filtros rápidos
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    zona_filtro = st.selectbox("Filtrar por Zona", ["Todas"] + list(df["zona"].dropna().unique()))
                with col_f2:
                    estado_filtro = st.selectbox("Filtrar por Estado", ["Todos"] + list(df["estado"].dropna().unique()))
                
                df_filtrado = df.copy()
                if zona_filtro != "Todas":
                    df_filtrado = df_filtrado[df_filtrado["zona"] == zona_filtro]
                if estado_filtro != "Todos":
                    df_filtrado = df_filtrado[df_filtrado["estado"] == estado_filtro]
                    
                st.dataframe(df_filtrado, use_container_width=True)
            else:
                st.info("No hay propiedades registradas aún en Supabase.")
        except Exception as e:
            st.error(f"Error al cargar las propiedades: {e}")

    # ---------------- TAB 2: CARGAR PROPIEDAD ----------------
    with tab2:
        st.subheader("Registro de Nueva Propiedad (JCprop)")
        
        with st.form("form_nueva_propiedad", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                tipologia = st.selectbox("Tipología", TIPOLOGIAS)
                barrio_sel = st.selectbox("Barrio", sorted(list(BARRIOS_SALTA.keys())))
                zona_auto = BARRIOS_SALTA[barrio_sel]
                st.text_input("Zona (Asignada automáticamente)", value=zona_auto, disabled=True)
                calle = st.text_input("Calle y Número Exacto")
                amoblado = st.selectbox("¿Amoblado?", ["NO", "SI"])

            with col2:
                dormitorios = st.number_input("Dormitorios", min_value=0, step=1, value=1)
                banios = st.number_input("Baños", min_value=0, step=1, value=1)
                cochera = st.selectbox("¿Cochera?", ["NO", "SI"])
                mts2 = st.number_input("Superficie (Mts2)", min_value=0.0, step=1.0, value=0.0)
                acepta_mascotas = st.selectbox("¿Acepta Mascotas?", ["NO", "SI"])

            with col3:
                precio = st.number_input("Precio ($ USD / ARS)", min_value=0.0, step=500.0, value=0.0)
                expensas = st.number_input("Expensas ($)", min_value=0.0, step=100.0, value=0.0)
                estado_contrato = st.text_input("Condición del Contrato", placeholder="Ej: 1 Año - Ajuste Trimestral IPC")
                estado = st.selectbox("Estado de la Propiedad", ["DISPONIBLE", "RESERVADA", "ALQUILADA", "VENDIDA"])
                fotos_drive = st.text_input("Link Folder Google Drive (Fotos)")

            st.markdown("---")
            st.markdown("**Publicada en:**")
            
            # Checkboxes dinámicos para portales
            publicada_en = []
            cols_portales = st.columns(len(PORTALES))
            for i, portal in enumerate(PORTALES):
                with cols_portales[i]:
                    if st.checkbox(portal, key=f"chk_{portal}"):
                        publicada_en.append(portal)

            detalles = st.text_area("Detalles y Observaciones Adicionales")

            submitted = st.form_submit_button("💾 Guardar Propiedad en Supabase")

            if submitted:
                if not calle.strip():
                    st.warning("El campo 'Calle y Número Exacto' es obligatorio.")
                else:
                    nueva_prop = {
                        "tipologia": tipologia,
                        "barrio": barrio_sel,
                        "zona": zona_auto,
                        "calle": calle,
                        "amoblado": amoblado,
                        "dormitorios": int(dormitorios),
                        "banios": int(banios),
                        "cochera": cochera,
                        "mts2": float(mts2),
                        "precio": float(precio),
                        "expensas": float(expensas),
                        "estado_contrato": estado_contrato,
                        "fotos_drive": fotos_drive,
                        "estado": estado,
                        "acepta_mascotas": acepta_mascotas,
                        "detalles": detalles,
                        "publicada_en": publicada_en
                    }
                    
                    try:
                        supabase.table("propiedades").insert(nueva_prop).execute()
                        st.success("¡Propiedad registrada con éxito en Supabase!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al intentar guardar en Supabase: {e}")
