import streamlit as st
import pymysql
import pandas as pd
import requests
from datetime import date
import io
import os
import base64

# Librerías para exportar a PDF con ReportLab
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Configurar la página en modo ancho
st.set_page_config(
    page_title="VIDACLINIC - Tu salud, nuestra prioridad",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- RUTAS DE IMÁGENES Y CONVERSIÓN A BASE64 ---
PATH_FONDO = "imagenes/fondo.jpg"
PATH_LOGO = "imagenes/logo.jpg"
PATH_MASCOTA = "imagenes/mascota.png"

def obtener_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

b64_fondo = obtener_base64(PATH_FONDO)
b64_logo = obtener_base64(PATH_LOGO)
b64_mascota = obtener_base64(PATH_MASCOTA)

# --- INYECCIÓN DE ESTILOS CSS GLOBALES DE ALTA PRECISIÓN ---
def aplicar_estilos_maqueta():
    bg_style = f"""
        background: linear-gradient(rgba(242, 249, 245, 0.85), rgba(242, 249, 245, 0.85)),
                    url("data:image/jpeg;base64,{b64_fondo}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    """ if b64_fondo else "background-color: #F2F9F5;"

    css = f"""
    <style>
    /* Ocultar elementos innecesarios de Streamlit */
    #MainMenu, header, footer {{ visibility: hidden; }}
    
    /* Fondo principal */
    .stApp {{
        {bg_style}
        color: #15432A !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    /* BARRA LATERAL (SIDEBAR) EXACTA A LA MAQUETA */
    section[data-testid="stSidebar"] {{
        background-color: #2D8A5E !important;
        width: 280px !important;
    }}
    
    section[data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}

    /* Opciones de Radio del Sidebar */
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
        background-color: transparent !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        margin-bottom: 4px !important;
    }}

    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
        background-color: rgba(255, 255, 255, 0.15) !important;
    }}

    /* CAMPOS DE ENTRADA (INPUTS VERDE MENTA) */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
        background-color: #72C79B !important;
        color: #15432A !important;
        border-radius: 25px !important;
        border: 2px solid #2D8A5E !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 10px 18px !important;
    }}

    .stTextInput input::placeholder {{
        color: #15432A !important;
        opacity: 0.7;
    }}

    /* BOTONES VERDES INSTITUCIONALES REDONDEADOS */
    .stButton>button, div[data-testid="stFormSubmitButton"]>button {{
        background-color: #2D8A5E !important;
        color: #FFFFFF !important;
        border-radius: 25px !important;
        font-weight: 800 !important;
        font-size: 17px !important;
        border: none !important;
        padding: 12px 28px !important;
        width: 100% !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15) !important;
    }}

    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {{
        background-color: #15432A !important;
        color: #FFFFFF !important;
    }}

    /* PESTAÑAS (TABS) MAQUETADAS */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: #72C79B !important;
        color: #15432A !important;
        border-radius: 20px 20px 0 0 !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #2D8A5E !important;
        color: #FFFFFF !important;
    }}

    /* TABLAS VERDES */
    div[data-testid="stDataFrame"] {{
        background-color: rgba(114, 199, 155, 0.85) !important;
        border-radius: 15px !important;
        border: 2px solid #2D8A5E !important;
        padding: 8px !important;
    }}

    div[data-testid="stDataFrame"] * {{
        color: #15432A !important;
        font-weight: 600 !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

aplicar_estilos_maqueta()

# --- HEADER / BANNER EXACTO A LA MAQUETA ---
def render_header(subtitulo="Portal de Acceso Restringido"):
    logo_html = f'<img src="data:image/jpeg;base64,{b64_logo}" style="height: 90px; margin-bottom: 5px;">' if b64_logo else '<h1 style="color:#15432A; margin:0;">💊 VIDACLINIC</h1>'
    
    st.markdown(f"""
        <div style="background-color: #FFFFFF; border-bottom: 6px solid #2D8A5E; border-top: 6px solid #2D8A5E; padding: 15px 0; text-align: center; margin-bottom: 25px;">
            {logo_html}
            <h2 style="color: #15432A; margin: 5px 0 0 0; font-weight: 800; font-size: 26px; text-transform: uppercase;">{subtitulo}</h2>
        </div>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A LA BASE DE DATOS MYSQL ---
def init_connection():
    return pymysql.connect
        password_db = st.secrets.get("password", "AVNS_ytphqSAjobNIHWjlbex")
        conn = mysql.connector.connect(
        host="mysql-68077f9-viacrucis2026.d.aivencloud.com",
        user="avnadmin",
        password=password_db,
        port=18358,
        database="sistema_medico_db",
        connect_timeout=3  # Timeout corto para activar contingencia rápido si no hay red
        )
        st.session_state['modo_offline'] = False
        return conn
    except Exception:
        st.session_state['modo_offline'] = True
        return None

# --- VERIFICACIÓN SEGURA DE COLUMNAS ---
def run_query(query, params=None, fetch=True):
    try:
        connection = init_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
                connection.close()
                return result
            else:
                connection.commit()
                last_id = cursor.lastrowid
                connection.close()
                return last_id
    except Exception as e:
        st.error(f"Error en la base de datos: {e}")
        return None

# --- VERIFICACIÓN SEGURA DE COLUMNAS ---
def asegurar_columnas_sistema():
    try:
        query_check = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'sistema_medico_db' 
              AND TABLE_NAME = 'cita_medica'
        """
        columnas_existentes = [row['COLUMN_NAME'] for row in (run_query(query_check) or [])]
        
        if 'moneda_pago' not in columnas_existentes:
            run_query("ALTER TABLE cita_medica ADD COLUMN moneda_pago VARCHAR(50) DEFAULT 'Dólares (USD)'", fetch=False)
        if 'comprobante' not in columnas_existentes:
            run_query("ALTER TABLE cita_medica ADD COLUMN comprobante VARCHAR(100) DEFAULT 'N/A'", fetch=False)
        if 'estado_pago' not in columnas_existentes:
            run_query("ALTER TABLE cita_medica ADD COLUMN estado_pago VARCHAR(20) DEFAULT 'Pendiente'", fetch=False)
        if 'estado_cita' not in columnas_existentes:
            run_query("ALTER TABLE cita_medica ADD COLUMN estado_cita VARCHAR(20) DEFAULT 'Pendiente'", fetch=False)
        if 'total_honorario_usd' not in columnas_existentes:
            run_query("ALTER TABLE cita_medica ADD COLUMN total_honorario_usd DECIMAL(10,2) DEFAULT 0.00", fetch=False)
        if 'total_honorario_cop' not in columnas_existentes:
            run_query("ALTER TABLE cita_medica ADD COLUMN total_honorario_cop DECIMAL(10,2) DEFAULT 0.00", fetch=False)
        if 'total_consultorio_usd' not in columnas_existentes:
            run_query("ALTER TABLE cita_medica ADD COLUMN total_consultorio_usd DECIMAL(10,2) DEFAULT 0.00", fetch=False)
        if 'total_consultorio_cop' not in columnas_existentes:
            run_query("ALTER TABLE cita_medica ADD COLUMN total_consultorio_cop DECIMAL(10,2) DEFAULT 0.00", fetch=False)
        if 'total_equipo_usd' not in columnas_existentes:
            run_query("ALTER TABLE cita_medica ADD COLUMN total_equipo_usd DECIMAL(10,2) DEFAULT 0.00", fetch=False)
        if 'total_equipo_cop' not in columnas_existentes:
            run_query("ALTER TABLE cita_medica ADD COLUMN total_equipo_cop DECIMAL(10,2) DEFAULT 0.00", fetch=False)
    except Exception:
        pass

asegurar_columnas_sistema()

# --- FUNCIÓN PARA GENERAR PDF DE AUDITORÍA CONSOLIDADA Y MAESTRA ---
def generar_pdf_auditoria_master(df_citas, df_dividendos, df_infraestructura, totales_dict):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor('#15432A'), spaceAfter=4)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], fontSize=8.5, textColor=colors.HexColor('#2D8A5E'), spaceAfter=5)
    cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=6, leading=7, textColor=colors.HexColor('#1F2926'), alignment=1)
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=6.5, leading=8, textColor=colors.whitesmoke, fontName='Helvetica-Bold', alignment=1)
    
    elements.append(Paragraph(f"FARMAVIDA - INFORME COMPLETO DE AUDITORÍA Y CIERRE DE CICLO", title_style))
    elements.append(Paragraph(f"<b>Fecha de Cierre:</b> {date.today()} | <b>Estado:</b> Consolidado Inmutable", subtitle_style))
    elements.append(Spacer(1, 4))
    
    resumen_data = [
        [Paragraph("Concepto / Moneda", header_style), Paragraph("Total USD", header_style), Paragraph("Total COP", header_style), Paragraph("Total VES", header_style)],
        [Paragraph("Balance Real Caja", cell_style), Paragraph(f"${totales_dict['usd']:,.2f}", cell_style), Paragraph(f"${totales_dict['cop']:,.2f}", cell_style), Paragraph(f"Bs. {totales_dict['ves']:,.2f}", cell_style)],
        [Paragraph("Ingresos Clínica (Consultorios + Equipos)", cell_style), Paragraph(f"${totales_dict['clinica_usd']:,.2f}", cell_style), Paragraph(f"${totales_dict['clinica_cop']:,.2f}", cell_style), Paragraph("-", cell_style)],
        [Paragraph("Honorarios Médicos", cell_style), Paragraph(f"${totales_dict['medicos_usd']:,.2f}", cell_style), Paragraph(f"${totales_dict['medicos_cop']:,.2f}", cell_style), Paragraph("-", cell_style)]
    ]
    t_resumen = Table(resumen_data, colWidths=[220, 180, 180, 182])
    t_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A5235')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2D8A5E')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F2F9F5')),
    ]))
    elements.append(t_resumen)
    elements.append(Spacer(1, 6))

    if not df_infraestructura.empty:
        headers_inf = [Paragraph(str(col), header_style) for col in df_infraestructura.columns.tolist()]
        data_inf = [headers_inf]
        for row in df_infraestructura.astype(str).values.tolist():
            data_inf.append([Paragraph(cell, cell_style) for cell in row])
        t_inf = Table(data_inf, colWidths=[762 / len(df_infraestructura.columns)] * len(df_infraestructura.columns))
        t_inf.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A5235')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2D8A5E')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F2F9F5')),
        ]))
        elements.append(t_inf)

    doc.build(elements)
    buffer.seek(0)
    return buffer

def generar_pdf_reporte(titulo, df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor('#15432A'), spaceAfter=8)
    cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=6.5, leading=8, textColor=colors.HexColor('#1F2926'), alignment=1)
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=7, leading=9, textColor=colors.whitesmoke, fontName='Helvetica-Bold', alignment=1)
    
    elements.append(Paragraph(f"FARMAVIDA - {titulo}", title_style))
    elements.append(Spacer(1, 5))
    
    headers = [Paragraph(str(col), header_style) for col in df.columns.tolist()]
    data = [headers]
    for row in df.astype(str).values.tolist():
        data.append([Paragraph(cell, cell_style) for cell in row])
    
    table = Table(data, colWidths=[762 / len(df.columns)] * len(df.columns))
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A5235')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F2F9F5')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2D8A5E')),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def actualizar_tasa_bcv_automatico():
    hoy = date.today()
    tasa_hoy = run_query("SELECT * FROM tasa_cambio WHERE fecha = %s", (hoy,))
    if tasa_hoy:
        return tasa_hoy[0]['id_tasa'], float(tasa_hoy[0]['tasa_usd_ves'])
    
    tasa_valor = None
    try:
        url = "https://ve.dolarapi.com/v1/dolares/oficial"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            tasa_valor = float(data['price'])
    except Exception:
        pass

    if not tasa_valor:
        ultima_tasa = run_query("SELECT tasa_usd_ves FROM tasa_cambio ORDER BY fecha DESC LIMIT 1")
        if ultima_tasa:
            tasa_valor = float(ultima_tasa[0]['tasa_usd_ves'])
        else:
            tasa_valor = 881.876

    query_insert_tasa = """
        INSERT INTO tasa_cambio (fecha, tasa_usd_ves, fuente) 
        VALUES (%s, %s, 'BCV') 
        ON DUPLICATE KEY UPDATE tasa_usd_ves = VALUES(tasa_usd_ves)
    """
    run_query(query_insert_tasa, (hoy, tasa_valor), fetch=False)
    
    res = run_query("SELECT id_tasa FROM tasa_cambio WHERE fecha = %s", (hoy,))
    if res:
        return res[0]['id_tasa'], tasa_valor
    return 1, tasa_valor

# --- INICIALIZACIÓN DE SESIÓN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None

if "nav_menu" not in st.session_state:
    st.session_state.nav_menu = "🏠 Inicio (Portal Principal)"

# ==========================================
# 1. PANTALLA DE LOGIN (IDENTICA A IMAGEN 1)
# ==========================================
if not st.session_state.logged_in:
    render_header("Portal de Acceso Restringido")

    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("""
            <div style="background-color: #FFFFFF; border: 3px solid #2D8A5E; border-radius: 20px; padding: 25px 30px; box-shadow: 0px 8px 20px rgba(0,0,0,0.1); margin-top: 10px;">
                <h2 style="color: #15432A; text-align: center; margin-top: 0; font-weight: 800; font-size: 24px;">Credenciales de Acceso</h2>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("<p style='color: #15432A; font-weight: bold; margin-bottom: 2px;'>Usuario</p>", unsafe_allow_html=True)
            username = st.text_input("Usuario", placeholder="", label_visibility="collapsed")
            
            st.markdown("<p style='color: #15432A; font-weight: bold; margin-bottom: 2px; margin-top: 10px;'>Contraseña</p>", unsafe_allow_html=True)
            password = st.text_input("Contraseña", type="password", placeholder="", label_visibility="collapsed")
            
            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            submit_login = st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True)
            
            if submit_login:
                query = """
                    SELECT u.*, r.descripcion as rol_nombre 
                    FROM usuario u 
                    JOIN rol r ON u.id_rol = r.id_rol 
                    WHERE u.nombre_usuario = %s AND u.clave = %s
                """
                user_record = run_query(query, (username, password))
                if user_record:
                    st.session_state.logged_in = True
                    st.session_state.user = user_record[0]['nombre_usuario']
                    st.session_state.role = user_record[0]['rol_nombre']
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Verifica tus datos.")
        st.stop()

# ==========================================
# 2. PANEL PRINCIPAL CON SIDEBAR EXACTO (IMAGEN 2)
# ==========================================
st.sidebar.markdown(f"""
    <div style="margin-bottom: 15px;">
        <h3 style="margin:0; font-size: 22px; font-weight: 800;">👤 {st.session_state.user}</h3>
        <p style="margin:2px 0 0 0; color: #80D8B6 !important; font-weight: bold;">Rol: {st.session_state.role}</p>
    </div>
    <hr style="border: 1px solid #72C79B; margin-bottom: 15px;">
    <p style="font-weight: 800; font-size: 18px; margin-bottom: 10px;">Navegación:</p>
""", unsafe_allow_html=True)

menu_options = ["🏠 Inicio", "📋 Agendar Cita", "📅 Citas Agendadas"]
if st.session_state.role == 'Administrativo':
    menu_options.append("📊 Panel Administrativo")
    menu_options.append("💰 Pago a Médicos")

menu_options.append("🔒 Cerrar Sesión")

selected_menu = st.sidebar.radio("Navegación", menu_options, key="nav_menu_radio", label_visibility="collapsed")

# Mascota en la parte inferior del sidebar
if b64_mascota:
    st.sidebar.markdown(f"""
        <div style="text-align: center; margin-top: 30px;">
            <img src="data:image/png;base64,{b64_mascota}" style="width: 140px; height: auto;">
        </div>
    """, unsafe_allow_html=True)

if st.session_state.get("force_nav"):
    selected_menu = st.session_state.force_nav
    st.session_state.force_nav = None

if selected_menu == "🔒 Cerrar Sesión":
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

# Banner Principal del Dashboard
render_header("Sistema Unificado de Gestión Médica y Control Financiero.")

# ------------------------------------------
# MÓDULO 1: INICIO
# ------------------------------------------
if selected_menu == "🏠 Inicio":
    st.markdown("<h1 style='color: #15432A; font-size: 36px; font-weight: 900; margin-bottom: 15px;'>Información General:</h1>", unsafe_allow_html=True)
    
    tab_m, tab_h, tab_e = st.tabs(["Médicos Especialistas", "Horario Disponible", "Equipos Médicos"])
    
    with tab_m:
        df_med = pd.DataFrame(run_query("SELECT m.nombre, m.apellido, e.nombre_especialidad FROM medicos m JOIN especialidades e ON m.id_especialidad = e.id_especialidad"))
        if not df_med.empty:
            df_med.columns = ['Nombre', 'Apellido', 'Especialidad']
            st.dataframe(df_med, use_container_width=True)
            
    with tab_h:
        medicos_list_h = run_query("SELECT id_medico, CONCAT(nombre, ' ', apellido) as medico FROM medicos")
        if medicos_list_h:
            medico_dict_h = {m['medico']: m['id_medico'] for m in medicos_list_h}
            medico_seleccionado = st.selectbox(
                "Seleccione un Médico para ver sus horarios disponibles:", 
                options=list(medico_dict_h.keys()), 
                key="filtro_medico_horario"
            )
            
            id_med_seleccionado = medico_dict_h[medico_seleccionado]
            
            citas_ocupadas_query = """
                SELECT id_horario 
                FROM cita_medica 
                WHERE id_medico = %s AND COALESCE(estado_cita, 'Pendiente') = 'Pendiente'
            """
            citas_ocupadas = run_query(citas_ocupadas_query, (id_med_seleccionado,))
            ids_horarios_ocupados = [c['id_horario'] for c in citas_ocupadas] if citas_ocupadas else []
            
            horarios_query = """
                SELECT 
                    h.id_horario, 
                    d.Descripción as dia, 
                    CAST(h.hora_inicio AS CHAR) as hora_inicio, 
                    CAST(h.hora_fin AS CHAR) as hora_fin 
                FROM horario h 
                JOIN dias d ON h.id_dia = d.id_dia
                ORDER BY d.id_dia, h.hora_inicio
            """
            todos_horarios = run_query(horarios_query)
            
            if todos_horarios:
                horarios_disponibles = [h for h in todos_horarios if h['id_horario'] not in ids_horarios_ocupados]
                if horarios_disponibles:
                    df_disp = pd.DataFrame(horarios_disponibles)
                    st.markdown(f"#### 📅 Horarios Libres para el Dr(a). **{medico_seleccionado}**")
                    dias_disponibles = df_disp['dia'].unique()
                    
                    for dia_item in dias_disponibles:
                        st.markdown(f"##### 📌 **{dia_item}**")
                        df_dia = df_disp[df_disp['dia'] == dia_item][['hora_inicio', 'hora_fin']]
                        df_dia.columns = ['Hora de Inicio', 'Hora de Cierre']
                        st.dataframe(df_dia, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"El Dr(a). {medico_seleccionado} no tiene horarios disponibles.")
            else:
                st.info("No hay horarios configurados en el sistema.")

    with tab_e:
        query_equipos_esp = """
            SELECT 
                eq.descripcion as 'Descripción del Equipo / Examen',
                COALESCE(es.nombre_especialidad, 'General / Sin Asignar') as 'Especialidad Pertenece'
            FROM equipo eq
            LEFT JOIN especialidades es ON eq.id_especialidad = es.id_especialidad
            ORDER BY es.nombre_especialidad, eq.descripcion
        """
        df_eq = pd.DataFrame(run_query(query_equipos_esp))
        if not df_eq.empty:
            st.dataframe(df_eq, use_container_width=True, hide_index=True)
        else:
            st.info("No hay equipos registrados en el sistema.")

# ------------------------------------------
# MÓDULO 2: AGENDAR CITA
# ------------------------------------------
elif selected_menu == "📋 Agendar Cita":
    st.markdown("<h1 style='color: #15432A; font-size: 36px; font-weight: 900;'>Agendar Citas</h1>", unsafe_allow_html=True)

    if "calculated_cita" not in st.session_state:
        st.session_state.calculated_cita = None

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1: 
        st.markdown("<p style='color: #15432A; font-weight: bold; margin:0;'>Nombre</p>", unsafe_allow_html=True)
        nombre_p = st.text_input("Nombre", key="c_nombre", label_visibility="collapsed")
    with col_p2: 
        st.markdown("<p style='color: #15432A; font-weight: bold; margin:0;'>Apellido</p>", unsafe_allow_html=True)
        apellido_p = st.text_input("Apellido", key="c_apellido", label_visibility="collapsed")
    with col_p3: 
        st.markdown("<p style='color: #15432A; font-weight: bold; margin:0;'>Edad</p>", unsafe_allow_html=True)
        edad_p = st.number_input("Edad", min_value=0, max_value=120, value=30, key="c_edad", label_visibility="collapsed")
    
    st.markdown("<p style='color: #15432A; font-weight: bold; margin-top:10px; margin-bottom:0;'>Motivo de Consulta / Síntomas</p>", unsafe_allow_html=True)
    padecimiento_p = st.text_area("Motivo de Consulta", height=70, key="c_padecimiento", label_visibility="collapsed")
   
    tipo_servicio = st.radio("Seleccione Servicio", ["Consulta General", "Examen Especializado"], horizontal=True)

    col_s1, col_s2 = st.columns(2)
    medicos_list = run_query("SELECT id_medico, nombre, apellido FROM medicos")
    medico_dict = {f"{m['nombre']} {m['apellido']}": m['id_medico'] for m in medicos_list}
    with col_s1: 
        st.markdown("<p style='color: #15432A; font-weight: bold; margin:0;'>Seleccione Médico</p>", unsafe_allow_html=True)
        medico_sel = st.selectbox("Seleccione Médico", options=list(medico_dict.keys()), key="c_medico", label_visibility="collapsed")

    horarios_list = run_query("""
        SELECT h.id_horario, d.Descripción as dia, h.hora_inicio, h.hora_fin 
        FROM horario h JOIN dias d ON h.id_dia = d.id_dia
    """)
    horario_dict = {f"{h['dia']} [{h['hora_inicio']} - {h['hora_fin']}]": h['id_horario'] for h in horarios_list}
    with col_s2: 
        st.markdown("<p style='color: #15432A; font-weight: bold; margin:0;'>Seleccione Horario</p>", unsafe_allow_html=True)
        horario_sel = st.selectbox("Seleccione Horario", options=list(horario_dict.keys()), key="c_horario", label_visibility="collapsed")

    equipo_sel_id = None
    consultorio_asignado_id = None

    if tipo_servicio == "Examen Especializado":
        equipos_list = run_query("SELECT id_equipo, descripcion FROM equipo")
        equipo_dict = {eq['descripcion']: eq['id_equipo'] for eq in equipos_list}
        st.markdown("<p style='color: ##000000; font-weight: bold; margin:0;'>Seleccione Equipo</p>", unsafe_allow_html=True)
        equipo_sel_str = st.selectbox("Seleccione Equipo", options=list(equipo_dict.keys()), key="c_equipo_unico", label_visibility="collapsed")
        equipo_sel_id = equipo_dict[equipo_sel_str]

        res_exam = run_query("SELECT id_consultorio FROM examen_esp WHERE id_equipo = %s", (equipo_sel_id,))
        consultorio_asignado_id = res_exam[0]['id_consultorio'] if res_exam else 1
    else:
        res_cons = run_query("SELECT id_consultorio FROM consulta_normal LIMIT 1")
        consultorio_asignado_id = res_cons[0]['id_consultorio'] if res_cons else 1

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("CALCULAR TOTAL A PAGAR", use_container_width=True):
        if not nombre_p or not apellido_p:
            st.warning("Por favor ingrese el nombre y apellido del paciente.")
        else:
            id_tasa_activo, tasa_actual = actualizar_tasa_bcv_automatico()
            id_med = medico_dict[medico_sel]
            id_hor = horario_dict[horario_sel]

            m_data = run_query("SELECT honorario_usd FROM medicos WHERE id_medico = %s", (id_med,))[0]
            c_data = run_query("SELECT costo_usd FROM consultorio WHERE id_consultorio = %s", (consultorio_asignado_id,))[0]

            honorario_usd = float(m_data['honorario_usd'])
            consultorio_usd = float(c_data['costo_usd'])

            equipo_usd_total = 0.0
            if equipo_sel_id:
                eq_db = run_query("SELECT costo_usd FROM equipo WHERE id_equipo = %s", (equipo_sel_id,))[0]
                equipo_usd_total = float(eq_db['costo_usd'])

            total_usd = honorario_usd + consultorio_usd + equipo_usd_total
            total_cop = total_usd * 3100.0
            total_ves = total_usd * float(tasa_actual)

            st.session_state.calculated_cita = {
                "nombre": nombre_p, "apellido": apellido_p, "edad": edad_p, "padecimiento": padecimiento_p,
                "id_med": id_med, "id_con": consultorio_asignado_id, "id_hor": id_hor, "id_tasa": id_tasa_activo,
                "tasa": tasa_actual, 
                "honorario_usd": honorario_usd, "honorario_cop": honorario_usd * 3100.0,
                "consultorio_usd": consultorio_usd, "consultorio_cop": consultorio_usd * 3100.0,
                "equipo_usd": equipo_usd_total, "equipo_cop": equipo_usd_total * 3100.0,
                "total_usd": total_usd, "total_cop": total_cop, "total_ves": total_ves
            }

    if st.session_state.get("calculated_cita"):
        data = st.session_state.calculated_cita
        st.markdown(f"""
            <div style='background-color: #FFFFFF; padding: 20px; border-radius: 15px; border: 2px solid #2D8A5E; color: #15432A; margin-top: 15px;'>
                <h3 style='margin:0;'>💰 Resumen Total a Pagar para el Paciente:</h3>
                <p style='margin:5px 0;'><b>Total USD:</b> ${data['total_usd']:.2f} USD | <b>Total COP:</b> ${data['total_cop']:,.2f} COP</p>
                <p style='font-size: 18px; margin:0;'><b>Total Bolívares:</b> Bs. {data['total_ves']:,.2f} VES</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("form_confirmar_pago"):
            col_m1, col_m2 = st.columns(2)
            with col_m1: moneda_pago = st.selectbox("Moneda con la que Cancela", ["Dólares (USD)", "Pesos Colombianos (COP)", "Bolívares (VES)"])
            with col_m2: comprobante_ves = st.text_input("Número de Comprobante / Referencia")

            btn_registrar = st.form_submit_button("REGISTRAR CITA Y PAGO", use_container_width=True)

            if btn_registrar:
                if moneda_pago == "Bolívares (VES)" and not comprobante_ves:
                    st.error("¡Atención! Para pagos en bolívares debe ingresar la referencia.")
                else:
                    conflicto = run_query("""
                        SELECT * FROM cita_medica 
                        WHERE id_horario = %s 
                          AND (id_medico = %s OR id_consultorio = %s)
                          AND COALESCE(estado_cita, 'Pendiente') = 'Pendiente'
                    """, (data['id_hor'], data['id_med'], data['id_con']))

                    if conflicto:
                        st.error("❌ ¡Error de Disponibilidad! Médico o Consultorio ocupados en este horario.")
                    else:
                        id_paciente = run_query("INSERT INTO paciente (nombre, apellido, edad, padecimiento) VALUES (%s, %s, %s, %s)", (data['nombre'], data['apellido'], data['edad'], data['padecimiento']), fetch=False)
                        comp_guardar = comprobante_ves if comprobante_ves else "N/A"

                        query_insert_cita = """
                            INSERT INTO cita_medica (
                                id_paciente, id_medico, id_consultorio, id_horario, id_tasa, padecimiento,
                                total_honorario_usd, total_honorario_cop,
                                total_consultorio_usd, total_consultorio_cop,
                                total_equipo_usd, total_equipo_cop,
                                costo_total_usd, costo_total_cop, costo_total_ves,
                                moneda_pago, comprobante, estado_pago, estado_cita
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pendiente', 'Pendiente')
                        """
                        run_query(query_insert_cita, (
                            id_paciente, data['id_med'], data['id_con'], data['id_hor'], data['id_tasa'], data['padecimiento'],
                            data['honorario_usd'], data['honorario_cop'],
                            data['consultorio_usd'], data['consultorio_cop'],
                            data['equipo_usd'], data['equipo_cop'],
                            data['total_usd'], data['total_cop'], data['total_ves'],
                            moneda_pago, comp_guardar
                        ), fetch=False)

                        st.success("¡Cita agendada con éxito!")
                        st.session_state.calculated_cita = None
                        st.session_state.force_nav = "🏠 Inicio"
                        st.rerun()

# ------------------------------------------
# MÓDULO 3: CITAS AGENDADAS
# ------------------------------------------
elif selected_menu == "📅 Citas Agendadas":
    st.markdown("<h1 style='color: #15432A; font-size: 36px; font-weight: 900;'>Citas Agendadas</h1>", unsafe_allow_html=True)

    citas_esp_query = """
        SELECT 
            cm.id_cita, es.nombre_especialidad as especialidad,
            CONCAT(p.nombre, ' ', p.apellido) as paciente,
            CONCAT(m.nombre, ' ', m.apellido) as medico,
            co.descripcion as consultorio,
            CONCAT(d.Descripción, ' (', h.hora_inicio, ' - ', h.hora_fin, ')') as horario,
            cm.costo_total_usd as total_usd, 
            cm.costo_total_cop as total_cop,
            cm.costo_total_ves as total_ves,
            COALESCE(cm.moneda_pago, 'Dólares (USD)') as moneda_pago,
            COALESCE(cm.estado_cita, 'Pendiente') as estado_cita
        FROM cita_medica cm
        JOIN paciente p ON cm.id_paciente = p.id_paciente
        JOIN medicos m ON cm.id_medico = m.id_medico
        JOIN especialidades es ON m.id_especialidad = es.id_especialidad
        JOIN consultorio co ON cm.id_consultorio = co.id_consultorio
        JOIN horario h ON cm.id_horario = h.id_horario
        JOIN dias d ON h.id_dia = d.id_dia
        WHERE COALESCE(cm.estado_cita, 'Pendiente') = 'Pendiente'
        ORDER BY es.nombre_especialidad
    """
    df_citas_esp = pd.DataFrame(run_query(citas_esp_query))

    if not df_citas_esp.empty:
        especialidades = df_citas_esp['especialidad'].unique().tolist()
        filtro_esp = st.selectbox("Filtrar por Especialidad", ["Todas"] + especialidades)

        df_filtrado = df_citas_esp.copy()
        if filtro_esp != "Todas":
            df_filtrado = df_filtrado[df_filtrado['especialidad'] == filtro_esp]

        if st.session_state.role == 'Administrativo':
            df_mostrar_tabla = df_filtrado[['id_cita', 'especialidad', 'paciente', 'medico', 'consultorio', 'horario', 'total_usd', 'total_cop', 'total_ves', 'moneda_pago']].copy()
            df_mostrar_tabla.insert(0, 'Completar', False)
            df_mostrar_tabla.columns = ['Completar', 'ID', 'Especialidad', 'Paciente', 'Médico', 'Consultorio', 'Horario', 'Total (USD)', 'Total (COP)', 'Total (VES)', 'Moneda Pago']
        else:
            df_mostrar_tabla = df_filtrado[['id_cita', 'especialidad', 'paciente', 'medico', 'consultorio', 'horario', 'moneda_pago']].copy()
            df_mostrar_tabla.insert(0, 'Completar', False)
            df_mostrar_tabla.columns = ['Completar', 'ID', 'Especialidad', 'Paciente', 'Médico', 'Consultorio', 'Horario', 'Moneda Pago']

        edited_df = st.data_editor(df_mostrar_tabla, use_container_width=True, hide_index=True)

        if st.button("MARCAR SELECCIONADAS COMO CUMPLIDAS", use_container_width=True):
            filas_seleccionadas = edited_df[edited_df['Completar'] == True]
            if not filas_seleccionadas.empty:
                for idx, row in filas_seleccionadas.iterrows():
                    id_cita_item = row['ID']
                    run_query("UPDATE cita_medica SET estado_cita = 'Cumplida' WHERE id_cita = %s", (id_cita_item,), fetch=False)
                st.success("¡Citas completadas!")
                st.rerun()

        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            pdf_data = generar_pdf_reporte("Citas Pendientes por Especialidad", df_mostrar_tabla.drop(columns=['Completar']))
            st.download_button("📄 Descargar Reporte en PDF", data=pdf_data, file_name="citas_especialidad.pdf", mime="application/pdf", use_container_width=True)
        with col_exp2:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_mostrar_tabla.drop(columns=['Completar']).to_excel(writer, index=False, sheet_name='Citas')
            excel_buffer.seek(0)
            st.download_button("📊 Descargar Reporte en Excel", data=excel_buffer, file_name="citas_especialidad.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    else:
        st.info("🎉 ¡No hay citas pendientes!")

# ------------------------------------------
# MÓDULO 4: PANEL ADMINISTRATIVO
# ------------------------------------------
elif selected_menu == "📊 Panel Administrativo" and st.session_state.role == 'Administrativo':
    st.markdown("<h1 style='color: #15432A; font-size: 36px; font-weight: 900;'>Panel Administrativo</h1>", unsafe_allow_html=True)

    citas_query = """
        SELECT 
            cm.id_cita, 
            CONCAT(p.nombre, ' ', p.apellido) as paciente,
            CONCAT(m.nombre, ' ', m.apellido) as medico, 
            co.descripcion as consultorio,
            COALESCE(eq.descripcion, 'Consulta General') as servicio_examen,
            CONCAT(d.Descripción, ' (', h.hora_inicio, ' - ', h.hora_fin, ')') as horario,
            COALESCE(cm.moneda_pago, 'Dólares (USD)') as moneda_pago,
            COALESCE(cm.comprobante, 'N/A') as comprobante,
            cm.costo_total_usd,
            cm.costo_total_cop,
            cm.costo_total_ves,
            COALESCE(NULLIF(cm.total_honorario_usd, 0), m.honorario_usd) as honorarios_medicos_usd,
            COALESCE(NULLIF(cm.total_honorario_cop, 0), m.honorario_usd * 3100.0) as honorarios_medicos_cop,
            (cm.costo_total_usd - COALESCE(NULLIF(cm.total_honorario_usd, 0), m.honorario_usd)) as ingresos_clinica_usd,
            ((cm.costo_total_usd - COALESCE(NULLIF(cm.total_honorario_usd, 0), m.honorario_usd)) * 3100.0) as ingresos_clinica_cop
        FROM cita_medica cm
        JOIN paciente p ON cm.id_paciente = p.id_paciente
        JOIN medicos m ON cm.id_medico = m.id_medico
        JOIN consultorio co ON cm.id_consultorio = co.id_consultorio
        JOIN horario h ON cm.id_horario = h.id_horario
        JOIN dias d ON h.id_dia = d.id_dia
        LEFT JOIN examen_esp ee ON co.id_consultorio = ee.id_consultorio
        LEFT JOIN equipo eq ON ee.id_equipo = eq.id_equipo
        WHERE cm.estado_pago = 'Pendiente'
    """
    df_citas = pd.DataFrame(run_query(citas_query))

    if not df_citas.empty:
        df_mostrar = df_citas[[
            'id_cita', 'paciente', 'medico', 'consultorio', 'servicio_examen', 'horario', 
            'moneda_pago', 'comprobante', 'costo_total_usd', 'costo_total_cop', 'costo_total_ves',
            'honorarios_medicos_usd', 'honorarios_medicos_cop', 'ingresos_clinica_usd', 'ingresos_clinica_cop'
        ]].copy()
        
        df_mostrar.columns = [
            'ID', 'Paciente', 'Médico', 'Consultorio', 'Servicio / Examen', 'Horario', 
            'Moneda', 'Ref', 'Total USD', 'Total COP', 'Total VES', 
            'Honorarios USD', 'Honorarios COP', 'Clínica USD', 'Clínica COP'
        ]
        
        st.dataframe(df_mostrar, use_container_width=True)

        total_usd_real = float(df_citas[df_citas['moneda_pago'] == 'Dólares (USD)']['costo_total_usd'].sum())
        total_cop_real = float(df_citas[df_citas['moneda_pago'] == 'Pesos Colombianos (COP)']['costo_total_cop'].sum())
        total_ves_real = float(df_citas[df_citas['moneda_pago'] == 'Bolívares (VES)']['costo_total_ves'].sum())

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1: st.metric("Real en Dólares (USD)", f"${total_usd_real:,.2f}")
        with col_b2: st.metric("Real en Pesos (COP)", f"${total_cop_real:,.2f}")
        with col_b3: st.metric("Real en Bolívares (VES)", f"Bs. {total_ves_real:,.2f}")

        infra_query = "SELECT descripcion as 'Descripción / Infraestructura', costo_usd as 'Costo USD', (costo_usd * 3100.0) as 'Costo COP' FROM consultorio UNION SELECT descripcion as 'Descripción / Infraestructura', costo_usd as 'Costo USD', (costo_usd * 3100.0) as 'Costo COP' FROM equipo"
        df_infraestructura = pd.DataFrame(run_query(infra_query))

        med_div_query = "SELECT m.id_medico as 'ID', CONCAT(m.nombre, ' ', m.apellido) as 'Médico', COUNT(cm.id_cita) as 'Citas', SUM(COALESCE(NULLIF(cm.total_honorario_usd, 0), m.honorario_usd)) as 'Hon. USD', SUM(COALESCE(NULLIF(cm.total_honorario_cop, 0), m.honorario_usd * 3100.0)) as 'Hon. COP' FROM medicos m JOIN cita_medica cm ON m.id_medico = cm.id_medico WHERE cm.estado_pago = 'Pendiente' GROUP BY m.id_medico"
        df_div_cierre = pd.DataFrame(run_query(med_div_query))

        totales_dict = {
            "usd": total_usd_real, "cop": total_cop_real, "ves": total_ves_real,
            "clinica_usd": float(df_citas['ingresos_clinica_usd'].sum()),
            "clinica_cop": float(df_citas['ingresos_clinica_cop'].sum()),
            "medicos_usd": float(df_citas['honorarios_medicos_usd'].sum()),
            "medicos_cop": float(df_citas['honorarios_medicos_cop'].sum())
        }

        pdf_master_buffer = generar_pdf_auditoria_master(df_mostrar, df_div_cierre, df_infraestructura, totales_dict)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.download_button(label="📄 Descargar PDF Auditor Completo", data=pdf_master_buffer, file_name=f"informe_auditoria_{date.today()}.pdf", mime="application/pdf", use_container_width=True)
        with col_c2:
            if st.button("🔄 EFECTUAR CIERRE DE CICLO", use_container_width=True):
                run_query("UPDATE cita_medica SET estado_pago = 'Pagado' WHERE estado_pago = 'Pendiente'", fetch=False)
                st.success("¡Cierre completado con éxito!")
                st.rerun()
    else:
        st.info("🎉 ¡No hay operaciones pendientes!")

# ------------------------------------------
# MÓDULO 5: PAGO A MÉDICOS
# ------------------------------------------
elif selected_menu == "💰 Pago a Médicos" and st.session_state.role == 'Administrativo':
    st.markdown("<h1 style='color: #15432A; font-size: 36px; font-weight: 900;'>Pago a Médicos</h1>", unsafe_allow_html=True)

    med_query = "SELECT m.id_medico, CONCAT(m.nombre, ' ', m.apellido) as medico, COUNT(cm.id_cita) as total_consultas, SUM(COALESCE(NULLIF(cm.total_honorario_usd, 0), m.honorario_usd)) as acumulado_usd, SUM(COALESCE(NULLIF(cm.total_honorario_cop, 0), m.honorario_usd * 3100.0)) as acumulado_cop, SUM(cm.costo_total_ves) as acumulado_ves_aprox FROM medicos m JOIN cita_medica cm ON m.id_medico = cm.id_medico WHERE cm.estado_pago = 'Pendiente' GROUP BY m.id_medico"
    df_div = pd.DataFrame(run_query(med_query))

    if not df_div.empty:
        df_div.columns = ['ID Médico', 'Médico Especialista', 'Total Citas Pendientes', 'Pendiente (USD)', 'Pendiente (COP)', 'Pendiente (VES)']
        st.dataframe(df_div, use_container_width=True)

        medico_pago_sel = st.selectbox("Seleccione el Médico a liquidar", df_div['Médico Especialista'].tolist())
        row_medico = df_div[df_div['Médico Especialista'] == medico_pago_sel].iloc[0]
        id_med_sel = row_medico['ID Médico']
        monto_usd = row_medico['Pendiente (USD)']
        monto_cop = row_medico['Pendiente (COP)']
        monto_ves = row_medico['Pendiente (VES)']

        moneda_entrega_medico = st.selectbox("Seleccione la moneda de cancelación", ["Dólares (USD)", "Pesos Colombianos (COP)", "Bolívares (VES)"])
        
        if st.button("PROCESAR LIQUIDACIÓN Y GENERAR RECIBO", use_container_width=True):
            citas_detalle_query = "SELECT cm.id_cita as ID, CONCAT(p.nombre, ' ', p.apellido) as Paciente, co.descripcion as Consultorio, CONCAT(d.Descripción, ' (', h.hora_inicio, ')') as Horario, COALESCE(NULLIF(cm.total_honorario_usd, 0), m.honorario_usd) as Hon_USD, COALESCE(NULLIF(cm.total_honorario_cop, 0), m.honorario_usd * 3100.0) as Hon_COP, cm.costo_total_ves as Hon_VES FROM cita_medica cm JOIN paciente p ON cm.id_paciente = p.id_paciente JOIN medicos m ON cm.id_medico = m.id_medico JOIN consultorio co ON cm.id_consultorio = co.id_consultorio JOIN horario h ON cm.id_horario = h.id_horario JOIN dias d ON h.id_dia = d.id_dia WHERE cm.id_medico = %s AND cm.estado_pago = 'Pendiente'"
            df_detalles = pd.DataFrame(run_query(citas_detalle_query, (id_med_sel,)))
            run_query("UPDATE cita_medica SET estado_pago = 'Pagado' WHERE id_medico = %s AND estado_pago = 'Pendiente'", (id_med_sel,), fetch=False)
            
            st.success(f"¡Pago a {medico_pago_sel} procesado con éxito!")

            buffer_recibo = io.BytesIO()
            doc_recibo = SimpleDocTemplate(buffer_recibo, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=25, bottomMargin=25)
            elementos = []
            styles = getSampleStyleSheet()
            h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=12, textColor=colors.HexColor('#15432A'), spaceAfter=4)
            normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#1F2926'), spaceAfter=3)
            
            elementos.append(Paragraph(f"<b>FARMAVIDA</b> - Comprobante de Pago de Honorarios Médicos", h1))
            elementos.append(Paragraph(f"<b>Médico:</b> {medico_pago_sel} | <b>Fecha:</b> {date.today()}", normal))
            elementos.append(Paragraph(f"<b>Moneda de Cancelación:</b> {moneda_entrega_medico}", normal))
            elementos.append(Spacer(1, 5))
            
            data_tabla = [df_detalles.columns.tolist()] + df_detalles.astype(str).values.tolist()
            data_tabla.append(["", "", "", "TOTALES:", f"${monto_usd:,.2f}", f"${monto_cop:,.2f}", f"Bs. {monto_ves:,.2f}"])
            
            t_recibo = Table(data_tabla)
            t_recibo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A5235')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2D8A5E'))
            ]))
            
            elementos.append(t_recibo)
            doc_recibo.build(elementos)
            buffer_recibo.seek(0)
            
            st.download_button(label="📥 Descargar Recibo de Pago (PDF)", data=buffer_recibo, file_name=f"recibo_pago_{id_med_sel}.pdf", mime="application/pdf", use_container_width=True)
    else:
        st.info("🎉 ¡No hay dividendos pendientes!")
