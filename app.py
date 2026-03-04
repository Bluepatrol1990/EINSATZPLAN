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

# Deine hinterlegten Empfänger
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide") 

# --- 2. CSS STYLING (SICHERHEIT & DESIGN) ---
st.markdown("""
    <style>
    /* SICHERHEIT: Alle Streamlit-Standardelemente hart entfernen */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div.stDeployButton {display:none;}
    [data-testid="stDecoration"] {display:none !important;} 
    [data-testid="stStatusWidget"] {display:none !important;}
    [data-testid="stSidebar"] {display: none;}

    /* FIXIERTER HEADER */
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

    .main-content { margin-top: 100px; }

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
    
    /* LOGIN BOX DESIGN */
    .login-box {
        text-align: center; 
        padding: 30px; 
        border: 2px solid #004b95; 
        border-radius: 15px; 
        background-color: #f8f9fa; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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
    # Header Simulation für Stadt Augsburg
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "STADT AUGSBURG - ORDNUNGSAMT", ln=True, align='L')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "Kommunaler Ordnungsdienst (KOD)", ln=True)
    pdf.line(10, 30, 200, 30)
    pdf.ln(15)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Einsatzbericht: {row_data['AZ']}", ln=True, align='C')
    pdf.ln(5)

    def add_pdf_row(label, value):
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 8, f" {label}:", border=1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(145, 8, f" {value}", border=1, ln=True)

    add_pdf_row("Datum", row_data['Datum'])
    add_pdf_row("Zeitraum", f"{row_data['Beginn']} - {row_data['Ende']} Uhr")
    add_pdf_row("Ort", f"{row_data['Ort']} {row_data['Hausnummer']}")
    add_pdf_row("Kräfte", entschluesseln(row_data['Kraefte']))
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Sachverhalt:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Bericht']), border=1)
    
    return pdf.output(dest="S").encode("latin-1")

# --- 5. LOGIN (ZENTRIERT) ---
if not st.session_state["auth"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("""
            <div class="login-box">
                <h1 style="font-size: 3em; margin-bottom: 0;">🔑</h1>
                <h2 style="color: #004b95; margin-top: 10px;">Sicherheitsbereich</h2>
                <hr style="border: 0.5px solid #004b95; width: 50%; margin: 20px auto;">
                <p style="color: #555;">KOD Augsburg - Identifikation erforderlich</p>
            </div>
        """, unsafe_allow_html=True)
        pwd_input = st.text_input("Dienstpasswort", type="password", label_visibility="collapsed", placeholder="Passwort eingeben...")
        if pwd_input:
            if pwd_input == DIENST_PW:
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("❌ Passwort falsch.")
    st.stop()

# --- 6. HAUPTPROGRAMM ---
st.markdown("""
    <div class="sticky-header">
        <h2 style="margin:0;">📋 KOD Augsburg - Einsatzbericht</h2>
    </div>
    <div class="main-content"></div>
""", unsafe_allow_html=True)

with st.expander("📝 NEUEN BERICHT ANLEGEN", expanded=True):
    loc = get_geolocation()
    gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "📍 GPS nicht erfasst"
    
    st.subheader("📍 Einsatzdetails")
    c1, c2, c3, c4 = st.columns(4)
    datum = c1.date_input("📅 Datum")
    beginn = c2.time_input("🕒 Beginn")
    ende = c3.time_input("🕒 Ende")
    az_val = c4.text_input("📂 AZ")
    
    o1, o2 = st.columns([3, 1])
    ort_val = o1.text_input("🗺️ Einsatzort")
    hnr_val = o2.text_input("Hausnr.")

    st.subheader("👮 Beteiligte Behörden")
    k_col1, k_col2, k_col3 = st.columns(3)
    with k_col1:
        pol_check = st.checkbox("🚔 Polizei")
        funkkennung = st.text_input("🆔 Funkkennung", placeholder="Augsburg...") if pol_check else ""
    rtw_check = k_col2.checkbox("🚑 Rettungsdienst")
    fw_check = k_col3.checkbox("🚒 Feuerwehr")

    with st.form("content_form"):
        inhalt = st.text_area("✍️ Sachverhalt", height=150)
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        bild = st.file_uploader("📸 Foto hochladen", type=["jpg", "png"])

        if st.form_submit_button("✅ BERICHT SPEICHERN"):
            k_list = ["KOD"]
            if pol_check: k_list.append(f"Polizei ({funkkennung})" if funkkennung else "Polizei")
            if rtw_check: k_list.append("Rettungsdienst")
            if fw_check: k_list.append("Feuerwehr")
            
            b64_img = "-"
            if bild:
                img = Image.open(bild).convert("RGB")
                img.thumbnail((1200, 1200))
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                b64_img = base64.b64encode(buf.getvalue()).decode()

            new_data = {
                "Datum": str(datum), "Beginn": beginn.strftime("%H:%M"), "Ende": ende.strftime("%H:%M"),
                "Ort": ort_val, "Hausnummer": hnr_val, "Zeugen": verschluesseln(beteiligte),
                "Bericht": verschluesseln(inhalt), "AZ": az_val, "Foto": verschluesseln(b64_img),
                "GPS": gps_val, "Kraefte": verschluesseln(", ".join(k_list))
            }
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success(f"✅ Bericht gespeichert.")
            st.rerun()

# --- ARCHIV ---
st.divider()
st.header("📂 Einsatzarchiv")
if os.path.exists(DATEI):
    df_archive = pd.read_csv(DATEI).astype(str)
    suche = st.text_input("🔍 Suche nach AZ oder Einsatzort...")
    if suche:
        df_archive = df_archive[df_archive['AZ'].str.contains(suche, case=False) | df_archive['Ort'].str.contains(suche, case=False)]

    for idx, row in df_archive.iloc[::-1].iterrows():
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
        
        with st.expander("👁️ Details anzeigen"):
            st.info(f"**✍️ Sachverhalt:**\n{entschluesseln(row['Bericht'])}")
            st.warning(f"**👥 Beteiligte:** {entschluesseln(row['Zeugen'])}")
            img_data = entschluesseln(row['Foto'])
            if img_data != "-": st.image(base64.b64decode(img_data), width=400)
            
            # --- PDF & LÖSCHEN OPTIONEN FÜR ADMIN ---
            if st.session_state["admin_auth"]:
                st.divider()
                pdf_data = create_official_pdf(row)
                col_pdf, col_del = st.columns(2)
                col_pdf.download_button("📄 PDF Export", pdf_data, f"KOD_Bericht_{row['AZ']}.pdf", "application/pdf", key=f"pdf_{idx}")
                if col_del.button("🗑️ Bericht löschen", key=f"del_{idx}"):
                    df_archive.drop(idx).to_csv(DATEI, index=False)
                    st.rerun()
            else:
                st.info("🔒 Für PDF-Export oder Löschen bitte Admin-Login unten nutzen.")

# --- ADMIN LOGIN GANZ UNTEN ---
st.markdown("<br><br><br><hr>", unsafe_allow_html=True)
with st.expander("🛡️ Administration"):
    if not st.session_state["admin_auth"]:
        admin_pw_in = st.text_input("Admin-Passwort", type="password")
        if st.button("Admin Login"):
            if admin_pw_in == ADMIN_PW:
                st.session_state["admin_auth"] = True
                st.rerun()
    else:
        if st.button("Admin Logout"):
            st.session_state["admin_auth"] = False
            st.rerun()
