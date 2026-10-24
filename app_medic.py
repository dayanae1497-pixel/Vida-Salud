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
import ssl

# --- CONEXIÓN A LA BASE DE DATOS MYSQL EN AIVEN ---
def init_connection():
    # Configuración de contexto SSL requerido por Aiven
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # O puedes cargar tu certificado CA si lo deseas

    return pymysql.connect(
        host="mysql-68077f9-viacrucis2026.d.aivencloud.com",
        user="avnadmin",
        password="AVNS_ytphqSAjobNIHWjlbex",
        database="sistema_medico_db",
        port=18358,
        cursorclass=pymysql.cursors.DictCursor,
        ssl=context
    )

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
        st.error(f"Error en la base de datos remota: {e}")
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
            
    wit
