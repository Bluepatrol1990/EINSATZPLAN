import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64
import tempfile
from PIL import Image
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation 
from fpdf import FPDF 

# --- 1. KONFIGURATION & SICHERHEIT ---
DIENST_PW = "1990" 
ADMIN_PW = st.secrets.get("admin_password", "admin789")
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")

DATEI = "zentral_archiv_secure.csv"
LOGO_PFAD = "logo.png" 
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]

st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide") 

# --- 2. UI SCHUTZ & STYLING (Zurückgesetzt & Optimiert) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stStatusWidget"] {display: none;}
    
    .login-box {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 50px;
    }
    
    /* ORIGINAL ARCHIV DESIGN */
    .report-card { 
        background-color: #ffffff; 
        border-radius: 10px; 
        padding: 20px; 
        border-left: 10px solid #004b95; 
        margin-bottom: 15px; 
        color: #333333;
        border: 1px solid #dddddd;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-box {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True) 

if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False 

# --- 3. KRYPTOGRAPHIE ---
def get_cipher():
    key_64 = base64.urlsafe_b64encode(MASTER_KEY[:32].encode().ljust(32))
    return Fernet(key_64) 

def verschluesseln(text):
    if not text or text == "-": return "-"
    return get_cipher().encrypt(str(text).encode()).decode() 

def entschluesseln(safe_text):
    if not safe_text or safe_text == "-": return "-"
    try: return get_cipher().decrypt(safe_text.encode()).decode()
    except: return "[DATENFEHLER]" 

# --- 4. PDF FUNKTION ---
def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_PFAD): pdf.image(LOGO_PFAD, x=160, y=10, w=35)
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "STADT AUGSBURG", ln=True)
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 7, "ORDNUNGSAMT", ln=True)
    pdf.line(10, 38, 200, 38); pdf.ln(15)
    pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "AMTLICHER EINSATZBERICHT", ln=True, align='C')
    pdf.ln(5)
    return pdf.output(dest="S").encode("latin-1")

# --- 5. LOGIN ---
if not st.session_state["auth"]:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://www.augsburg.de/typo3conf/ext/mag_site/Resources/Public/Images/Logo/augsburg_logo.svg", width=180)
        st.subheader("🔒 KOD Sicherheitsbereich")
        pw_input = st.text_input("Dienstpasswort", type="password", label_visibility="collapsed")
        if st.button("Anmelden", use_container_width=True) or (pw_input == DIENST_PW and pw_input != ""):
            if pw_input == DIENST_PW:
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Falsch.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop() 

# --- 6. SIDEBAR (FIXED ADMIN LOGIN) ---
with st.sidebar:
    st.image("https://www.augsburg.de/typo3conf/ext/mag_site/Resources/Public/Images/Logo/augsburg_logo.svg", width=150)
    st.title("🛡️ Administration")
    if st.checkbox("🔑 Admin-Modus aktivieren"):
        admin_pw_input = st.text_input("Admin-Passwort", type="password")
        if admin_pw_input == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin aktiv")
        else: st.session_state["admin_auth"] = False
    else: st.session_state["admin_auth"] = False

# --- 7. HAUPTSEITE & ARCHIV ---
st.title("📋 Einsatzbericht")

# Formular-Bereich (gekürzt für Übersicht)
with st.expander("📝 NEUEN BERICHT ANLEGEN"):
    st.write("Eingabemaske hier...")

st.divider()
st.header("📂 Einsatzarchiv")
if os.path.exists(DATEI):
    df_archive = pd.read_csv(DATEI).astype(str)
    for idx, row in df_archive.iloc[::-1].iterrows():
        # WIEDERHERGESTELLTES LAYOUT
        st.markdown(f"""
            <div class="report-card">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 1.2em;">📂 <strong>AZ: {row['AZ']}</strong></span>
                    <span>📅 {row['Datum']}</span>
                </div>
                <hr style="margin: 10px 0;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="metric-box">📍 <b>Einsatzort:</b> {row['Ort']} {row['Hausnummer']}</div>
                    <div class="metric-box">🕒 <b>Zeit:</b> {row['Beginn']} - {row['Ende']}</div>
                    <div class="metric-box">👮 <b>Kräfte:</b> {entschluesseln(row['Kraefte'])}</div>
                    <div class="metric-box">🌐 <b>GPS:</b> {row['GPS']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        c_det, c_admin = st.columns([3, 1])
        with c_det:
            with st.expander("👁️ Details anzeigen"):
                st.info(f"**Sachverhalt:** {entschluesseln(row['Bericht'])}")
        
        with c_admin:
            if st.session_state.get("admin_auth", False):
                st.download_button("📄 PDF Export", create_official_pdf(row), f"Bericht_{row['AZ']}.pdf", key=f"p_{idx}")
                if st.button("🗑️ Löschen", key=f"d_{idx}"):
                    pd.read_csv(DATEI).drop(idx).to_csv(DATEI, index=False)
                    st.rerun()
