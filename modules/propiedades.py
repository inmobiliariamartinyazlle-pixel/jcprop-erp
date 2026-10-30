import streamlit as st
import pandas as pd
import re

# Mapeo de Barrios de Salta y sus Zonas correspondientes
BARRIOS_SALTA = {
    "Centro": "Centro",
    "Macrocentro": "Macrocentro",
    "Microcentro": "Centro",
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
    "El Tipal": "San Lorenzo Chico",
    "Huaico": "Norte",
    "Via Aurelia": "Oeste"
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

OPERACIONES = ["Alquiler", "Venta", "Alquiler / Venta"]
PORTALES = ["Marketplace", "Zonaprop", "Argenprop", "Redes Sociales", "Web Propia"]

# Funciones de limpieza
def limpiar_numero(val):
    if pd.isna(val) or str(val).strip() == "" or str(val).strip() == "-":
        return 0.0
    val_str = str(val).replace("$", "").replace("USD", "").replace(".", "").replace(",", ".").strip()
    match = re.search(r"[-+]?\d*\.\d+|\d+", val_str)
    return float(match.group()) if match else 0.0

def limpiar_entero(val):
    if pd.isna(val) or str(val).strip() == "" or str(val).strip() == "-":
        return 0
    val_str = str(val).upper().strip()
    if "MONO" in val_str:
        return 1
    match = re.search(r"\d+", val_str)
    return int(match.group()) if match else 1

def determinar_zona(barrio_raw):
    if pd.notna(barrio_raw):
        for b_nombre, z_nombre in BARRIOS_SALTA.items():
            if b_nombre.lower() in str(barrio_raw).lower():
                return b_nombre, z_nombre
    return "Macrocentro", "Macrocentro"

def limpiar_si_no(val):
    if pd.isna(val):
        return "NO"
    val_str = str(val).strip().upper()
    return "SI" if val_str in ["SI", "SÍ", "TRUE", "1"] else "NO"


def render_modulo(supabase):
    st.title("Gestión de Propiedades 🏠")
    
    tab1, tab2, tab3 = st.tabs(["📋 Ver Inventario", "➕ Cargar Propiedad", "📥 Carga Masiva (Excel)"])
    
    # ---------------- TAB 1: VER INVENTARIO ----------------
    with tab1:
        st.subheader("Inventario de Propiedades")
        
        try:
            res = supabase.table("propiedades").select("*").execute()
            datos = res.data
            
            if datos:
                df = pd.DataFrame(datos)
                
                # Filtros de visualización
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    op_filtro = st.selectbox("Filtrar por Operación", ["Todas"] + list(df["operacion"].dropna().unique()) if "operacion" in df.columns else ["Todas"])
                with col_f2:
                    zona_filtro = st.selectbox("Filtrar por Zona", ["Todas"] + list(df["zona"].dropna().unique()))
                with col_f3:
                    estado_filtro = st.selectbox("Filtrar por Estado", ["Todos"] + list(df["estado"].dropna().unique()))
                
                df_filtrado = df.copy()
                if op_filtro != "Todas":
                    df_filtrado = df_filtrado[df_filtrado["operacion"] == op_filtro]
                if zona_filtro != "Todas":
                    df_filtrado = df_filtrado[df_filtrado["zona"] == zona_filtro]
                if estado_filtro != "Todos":
                    df_filtrado = df_filtrado[df_filtrado["estado"] == estado_filtro]
                    
                st.dataframe(df_filtrado, use_container_width=True)
            else:
                st.info("No hay propiedades registradas aún en Supabase.")
        except Exception as e:
            st.error(f"Error al cargar las propiedades: {e}")

    # ---------------- TAB 2: CARGAR PROPIEDAD INDIVIDUAL ----------------
    with tab2:
        st.subheader("Registro de Nueva Propiedad (JCprop)")
        
        with st.form("form_nueva_propiedad", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                operacion = st.selectbox("Tipo de Operación", OPERACIONES)
                tipologia = st.selectbox("Tipología", TIPOLOGIAS)
                barrio_sel = st.selectbox("Barrio", sorted(list(BARRIOS_SALTA.keys())))
                zona_auto = BARRIOS_SALTA[barrio_sel]
                st.text_input("Zona (Asignada automáticamente)", value=zona_auto, disabled=True)

            with col2:
                calle = st.text_input("Calle y Número Exacto")
                amoblado = st.selectbox("¿Amoblado?", ["NO", "SI"])
                dormitorios = st.number_input("Dormitorios", min_value=0, step=1, value=1)
                banios = st.number_input("Baños", min_value=0, step=1, value=1)
                cochera = st.selectbox("¿Cochera?", ["NO", "SI"])

            with col3:
                precio = st.number_input("Precio ($ USD / ARS)", min_value=0.0, step=500.0, value=0.0)
                expensas = st.number_input("Expensas ($)", min_value=0.0, step=100.0, value=0.0)
                estado_contrato = st.text_input("Condición del Contrato", placeholder="Ej: 1 Año - Ajuste Trimestral IPC")
                estado = st.selectbox("Estado de la Propiedad", ["DISPONIBLE", "RESERVADA", "ALQUILADA", "VENDIDA"])

            # ---------------- CAMPOS ESPECÍFICOS / DEPARTAMENTOS ----------------
            st.markdown("---")
            st.markdown("### 🏢 Detalles Específicos y Superficies")
            
            col_dep1, col_dep2, col_dep3 = st.columns(3)
            with col_dep1:
                piso = st.text_input("Piso / Unidad (ej: 4D, 8B)")
                ubicacion = st.selectbox("Ubicación en el Edificio", ["", "Frente", "Contrafrente", "Lateral", "Interno", "Esquina"])
            with col_dep2:
                condicion = st.selectbox("Condición del Inmueble", ["", "A ESTRENAR", "EN OBRA", "NUEVO", "USADO COMO NUEVO", "USADO IMPECABLE", "BUEN ESTADO", "USADO"])
            with col_dep3:
                apto_financiacion = st.checkbox("¿Apto Financiación?")
            
            col_sup1, col_sup2, col_sup3 = st.columns(3)
            with col_sup1:
                mts2_cubiertos = st.number_input("Mts2 Cubiertos", min_value=0.0, step=1.0, format="%.2f", value=0.0)
            with col_sup2:
                mts2_semicubiertos = st.number_input("Mts2 Semicubiertos (Balcones)", min_value=0.0, step=1.0, format="%.2f", value=0.0)
            with col_sup3:
                # Si cargan cubiertos/semicubiertos se calcula solo, sino toma el general si cargan otra tipología
                mts2_calc = mts2_cubiertos + mts2_semicubiertos
                mts2_totales = st.number_input("Mts2 Totales", min_value=0.0, step=1.0, value=mts2_calc if mts2_calc > 0 else 0.0)

            detalle_financiacion = st.text_area("Detalle / Esquema de Financiación", placeholder="Ej: Anticipo del 40% y cuotas en UVAs...")
            
            col_leg1, col_leg2 = st.columns(2)
            with col_leg1:
                escritura = st.text_input("Escritura / Antecedentes", placeholder="Ej: Escritura inmediata / Boleto")
            with col_leg2:
                catastro = st.text_input("Catastro / Matrícula", placeholder="Nº de matrícula inmobiliaria")

            # ---------------- DATOS GENERALES Y EXTRAS ----------------
            st.markdown("---")
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                acepta_mascotas = st.selectbox("¿Acepta Mascotas?", ["NO", "SI"])
            with col_ex2:
                fotos_drive = st.text_input("Link Folder Google Drive (Fotos y Llaves)")

            st.markdown("**Publicada en:**")
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
                        "operacion": operacion,
                        "tipologia": tipologia,
                        "barrio": barrio_sel,
                        "zona": zona_auto,
                        "calle": calle,
                        "amoblado": amoblado,
                        "dormitorios": int(dormitorios),
                        "banios": int(banios),
                        "cochera": cochera,
                        "mts2": float(mts2_totales),
                        "precio": float(precio),
                        "expensas": float(expensas),
                        "estado_contrato": estado_contrato,
                        "fotos_drive": fotos_drive,
                        "estado": estado,
                        "acepta_mascotas": acepta_mascotas,
                        "detalles": detalles,
                        "publicada_en": publicada_en,
                        # Todos los nuevos campos mapeados correctamente
                        "piso": piso if piso else None,
                        "ubicacion": ubicacion if ubicacion else None,
                        "condicion": condicion if condicion else None,
                        "apto_financiacion": apto_financiacion,
                        "mts2_cubiertos": float(mts2_cubiertos) if mts2_cubiertos > 0 else None,
                        "mts2_semicubiertos": float(mts2_semicubiertos) if mts2_semicubiertos > 0 else None,
                        "mts2_totales": float(mts2_totales),
                        "detalle_financiacion": detalle_financiacion if detalle_financiacion else None,
                        "escritura": escritura if escritura else None,
                        "catastro": catastro if catastro else None
                    }
                    
                    try:
                        supabase.table("propiedades").insert(nueva_prop).execute()
                        st.success("¡Propiedad registrada con éxito en Supabase! 🎉")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al intentar guardar en Supabase: {e}")

    # ---------------- TAB 3: CARGA MASIVA DESDE EXCEL ----------------
    with tab3:
        st.subheader("📥 Importación Masiva desde Excel")
        st.markdown("Sube tu planilla de cálculo (`.xlsx`) para cargar el inventario de golpe.")
        
        archivo_subido = st.file_uploader("Selecciona tu archivo Excel", type=["xlsx", "xls"])
        
        if archivo_subido is not None:
            try:
                df_preview = pd.read_excel(archivo_subido)
                
                # Normalizar nombres de columnas a minúsculas y sin espacios
                df_preview.columns = [str(c).strip().lower() for c in df_preview.columns]
                
                st.info(f"📊 Columnas detectadas en tu Excel: {list(df_preview.columns)}")
                st.write("Vista previa de los datos leídos:")
                st.dataframe(df_preview.head(3), use_container_width=True)
                
                if st.button("🚀 Procesar e Importar a Supabase"):
                    propiedades_a_insertar = []
                    errores_lectura = 0
                    
                    for idx, row in df_preview.iterrows():
                        # Intentar buscar columnas de tipología y barrio de varias formas posibles
                        tipologia_raw = str(row.get("tipologia", row.get("tipo", "Departamento"))).strip()
                        barrio_raw = row.get("barrio", row.get("ubicacion", row.get("zona", "Macrocentro")))
                        calle = str(row.get("calle", row.get("direccion", "Sin dirección"))).strip()
                        
                        barrio_clean, zona_clean = determinar_zona(barrio_raw)
                        
                        # Limpieza robusta de números
                        m_cubiertos = limpiar_numero(row.get("mts2_cubiertos", row.get("cubiertos", 0)))
                        m_semicubiertos = limpiar_numero(row.get("mts2_semicubiertos", row.get("semicubiertos", 0)))
                        m_totales = limpiar_numero(row.get("mts2_totales", row.get("mts2", row.get("superficie", 0))))
                        
                        if m_totales == 0 and (m_cubiertos > 0 or m_semicubiertos > 0):
                            m_totales = m_cubiertos + m_semicubiertos

                        precio_limpio = limpiar_numero(row.get("precio", row.get("valor", 0)))
                        expensas_limpias = limpiar_numero(row.get("expensas", row.get("expensas ultimo mes", 0)))
                        dormitorios_limpios = limpiar_entero(row.get("dormitorios", row.get("dormitorioss", 1)))
                        banios_limpios = limpiar_entero(row.get("baños", row.get("banios", 1)))

                        prop = {
                            "operacion": str(row.get("operacion", "Venta")) if pd.notna(row.get("operacion")) else "Venta",
                            "tipologia": tipologia_raw if tipologia_raw != "nan" and tipologia_raw != "" else "Departamento",
                            "barrio": barrio_clean,
                            "zona": zona_clean,
                            "calle": calle if calle != "nan" and calle != "" else "Dirección no especificada",
                            "amoblado": limpiar_si_no(row.get("amoblado")),
                            "dormitorios": dormitorios_limpios,
                            "banios": banios_limpios,
                            "cochera": limpiar_si_no(row.get("cochera")),
                            "mts2": m_totales,
                            "precio": precio_limpio,
                            "expensas": expensas_limpias,
                            "estado_contrato": str(row.get("contrato", "1 Año")) if pd.notna(row.get("contrato")) else "1 Año",
                            "fotos_drive": str(row.get("fotos_drive", row.get("fotos en drive", ""))) if pd.notna(row.get("fotos_drive", row.get("fotos en drive", ""))) else "",
                            "estado": str(row.get("estado", "DISPONIBLE")) if pd.notna(row.get("estado")) else "DISPONIBLE",
                            "acepta_mascotas": limpiar_si_no(row.get("acepta_mascotas", "NO")),
                            "detalles": str(row.get("detalles", "")) if pd.notna(row.get("detalles")) else "Propiedad importada",
                            "publicada_en": ["Zonaprop"] if pd.notna(row.get("zonaprop")) else [],
                            
                            # Nuevos campos específicos
                            "piso": str(row.get("piso", "")) if pd.notna(row.get("piso")) else None,
                            "ubicacion": str(row.get("ubicacion", "")) if pd.notna(row.get("ubicacion")) else None,
                            "condicion": str(row.get("condicion", "")) if pd.notna(row.get("condicion")) else None,
                            "apto_financiacion": True if str(row.get("apto_financiacion", "")).strip().upper() in ["SI", "SÍ", "TRUE", "1"] else False,
                            "mts2_cubiertos": m_cubiertos if m_cubiertos > 0 else None,
                            "mts2_semicubiertos": m_semicubiertos if m_semicubiertos > 0 else None,
                            "mts2_totales": m_totales,
                            "detalle_financiacion": str(row.get("detalle_financiacion", "")) if pd.notna(row.get("detalle_financiacion")) else None,
                            "escritura": str(row.get("escritura", "")) if pd.notna(row.get("escritura")) else None,
                            "catastro": str(row.get("catastro", "")) if pd.notna(row.get("catastro")) else None
                        }
                        propiedades_a_insertar.append(prop)
                    
                    if propiedades_a_insertar:
                        res = supabase.table("propiedades").insert(propiedades_a_insertar).execute()
                        st.success(f"¡Se han importado exitosamente {len(propiedades_a_insertar)} propiedades a Supabase! 🎉")
                        st.balloons()
                    else:
                        st.warning("No se encontraron registros válidos para importar en el archivo.")
            except Exception as e:
                st.error(f"Ocurrió un error al procesar el archivo: {e}")
