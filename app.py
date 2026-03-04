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

# --- 1. GLOBALE VARIABLEN & KONFIGURATION ---
DATEI = "zentral_archiv_secure.csv"
LOGO_PFAD = "logo.png" 
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
ADMIN_PW = "admin789"
DIENST_PW = "1990" 
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")

RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide") 

# --- 2. CSS STYLING (MAXIMALE SICHERHEIT) ---
st.markdown("""
    <style>
    /* ENTFERNT ALLE STANDARD-STREAMLIT ELEMENTE */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div.stDeployButton {display:none;}
    [data-testid="stDecoration"] {display:none;} /* Entfernt die "Manage App" Leiste unten */
    [data-testid="stSidebar"] {display: none;} /* Versteckt die Sidebar komplett */

    /* EIGENER FIXIERTER HEADER */
    .sticky-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #004b95;
        color: white;
        padding: 15px 25px;
        z-index: 9999;
        border-bottom: 3px solid #ffcc00;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    .main-content {
        margin-top: 80px;
    }

    .report-card { 
        background-color: #ffffff; 
        border-radius: 10px; 
        padding: 20px; 
        border-left: 10px solid #004b95; 
        margin-bottom: 15px; 
        border: 1px solid #dddddd;
    }
    .metric-box {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True) 

# --- 3. SICHERHEITSFUNKTIONEN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False 

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

# --- 4. PDF GENERIERUNG ---
def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_PFAD):
        pdf.image(LOGO_PFAD, x=160, y=10, w=35)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "STADT AUGSBURG", ln=True)
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "AMTLICHER EINSATZBERICHT", ln=True, align='C')
    
    def add_row(label, value):
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 9, f" {label}", border=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(145, 9, f" {value}", border=1, ln=True)

    add_row("AZ", row_data['AZ'])
    add_row("Datum", row_data['Datum'])
    add_row("Ort", f"{row_data['Ort']} {row_data['Hausnummer']}")
    add_row("Sachverhalt", entschluesseln(row_data['Bericht']))
    
    return pdf.output(dest="S").encode("latin-1")

# --- 5. LOGIN ---
if not st.session_state["auth"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.subheader("🔑 KOD Augsburg Login")
        pwd_input = st.text_input("Dienstpasswort", type="password")
        if pwd_input == DIENST_PW:
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- 6. HAUPTPROGRAMM ---
st.markdown("""
    <div class="sticky-header">
        <h2 style="margin:0;">📋 KOD Augsburg - Einsatzbericht</h2>
    </div>
    <div class="main-content"></div>
""", unsafe_allow_html=True)

# Bereich: Neuer Bericht
with st.expander("📝 NEUEN BERICHT ANLEGEN", expanded=True):
    loc = get_geolocation()
    gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "📍 GPS nicht erfasst"
    
    st.subheader("📍 Einsatzdetails")
    c1, c2, c3, c4 = st.columns(4)
    datum = c1.date_input("📅 Datum")
    beginn = c2.time_input("🕒 Beginn")
    ende = c3.time_input("🕒 Ende")
    az_val = c4.text_input("📂 AZ")
    
    ort_val = st.text_input("🗺️ Einsatzort")
    
    with st.form("main_form"):
        inhalt = st.text_area("✍️ Sachverhalt")
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        bild = st.file_uploader("📸 Foto", type=["jpg", "png"])
        
        if st.form_submit_button("✅ SPEICHERN"):
            b64_img = "-"
            if bild:
                img = Image.open(bild).convert("RGB")
                img.thumbnail((800, 800))
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                b64_img = base64.b64encode(buf.getvalue()).decode()

            new_entry = {
                "Datum": str(datum), "Beginn": beginn.strftime("%H:%M"), "Ende": ende.strftime("%H:%M"),
                "Ort": ort_val, "Hausnummer": "", "Zeugen": verschluesseln(beteiligte),
                "Bericht": verschluesseln(inhalt), "AZ": az_val, "Foto": verschluesseln(b64_img),
                "GPS": gps_val, "Kraefte": verschluesseln("KOD")
            }
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success("Bericht gespeichert.")
            st.rerun()

# Archiv
st.divider()
st.header("📂 Archiv")
if os.path.exists(DATEI):
    df_arch = pd.read_csv(DATEI).astype(str)
    for idx, row in df_arch.iloc[::-1].iterrows():
        with st.container():
            st.markdown(f'<div class="report-card"><b>AZ: {row["AZ"]}</b> | {row["Datum"]} | {row["Ort"]}</div>', unsafe_allow_html=True)
            if st.session_state["admin_auth"]:
                col_a, col_b = st.columns(2)
                pdf_b = create_official_pdf(row)
                col_a.download_button("📄 PDF", pdf_b, f"{row['AZ']}.pdf", key=f"p_{idx}")
                if col_b.button("🗑️ Löschen", key=f"d_{idx}"):
                    df_arch.drop(idx).to_csv(DATEI, index=False)
                    st.rerun()

# --- 7. ADMIN ANMELDUNG GANZ UNTEN ---
st.markdown("<br><br><br><hr>", unsafe_allow_html=True)
with st.expander("🛡️ Admin-Bereich (geschützt)"):
    if not st.session_state["admin_auth"]:
        admin_in = st.text_input("Admin-Passwort", type="password")
        if st.button("Anmelden"):
            if admin_in == ADMIN_PW:
                st.session_state["admin_auth"] = True
                st.success("Admin-Zugriff aktiviert.")
                st.rerun()
            else:
                st.error("Falsches Passwort.")
    else:
        st.write("✅ Sie sind als Admin angemeldet.")
        if st.button("Logout Admin"):
            st.session_state["admin_auth"] = False
            st.rerun()
