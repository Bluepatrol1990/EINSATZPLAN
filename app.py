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

# --- 2. SICHERHEITS-STYLING & SYSTEM-SPERRE ---
st.markdown("""
    <style>
    /* Verdeckt Standard-Elemente */
    #MainMenu {visibility: hidden !important;}
    header {display: none !important;}
    footer {display: none !important;}
    
    /* Aggressives Ausblenden der Manage-App Leiste */
    [data-testid="stStatusWidget"], 
    .stAppDeployButton, 
    iframe[title="manage-app"],
    .viewerBadge_container__1QS13,
    #stConnectionStatus {
        display: none !important;
        height: 0 !important;
        width: 0 !important;
    }

    /* Der "Sichtschutz-Trick": Schiebt den Inhalt über den unteren Rand hinaus */
    .stApp {
        max-height: 100vh !important;
        overflow: hidden !important;
        margin-bottom: -100px !important;
    }

    .sticky-header {
        position: fixed; top: 0; left: 0; width: 100%;
        background-color: #004b95; color: white;
        padding: 15px 25px; z-index: 9999;
        border-bottom: 3px solid #ffcc00;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .main-content { margin-top: 100px; padding-bottom: 150px; }
    
    .login-box {
        text-align: center; padding: 40px; border: 2px solid #004b95; 
        border-radius: 15px; background-color: #f8f9fa; 
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

# --- 4. LOGIN-MASKE (BLOCKIERT ALLES ANDERE) ---
if not st.session_state["auth"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<h2 style="color: #004b95;">🔑 KOD Augsburg</h2><p>Bitte Dienstpasswort eingeben</p>', unsafe_allow_html=True)
        pwd_input = st.text_input("Passwort", type="password", label_visibility="collapsed")
        if st.button("Anmelden"):
            if pwd_input == DIENST_PW:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Falsches Passwort")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # Beendet das Skript hier, falls nicht eingeloggt

# --- 5. HAUPTBEREICH (WIRD NUR BEI LOGIN GEZEIGT) ---
st.markdown('<div class="sticky-header"><h2 style="margin:0;">📋 KOD Einsatzbericht</h2></div>', unsafe_allow_html=True)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# PDF FUNKTION
def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "STADT AUGSBURG - EINSATZBERICHT", ln=True, align='C')
    pdf.ln(10)
    for k, v in row_data.items():
        if k not in ["Foto", "Bericht", "Zeugen", "Kraefte"]:
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(40, 8, f"{k}:", border=1)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 8, f" {v}", border=1, ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "Bericht:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 8, entschluesseln(row_data['Bericht']), border=1)
    return pdf.output(dest="S").encode("latin-1")

with st.expander("📝 NEUEN BERICHT ANLEGEN", expanded=True):
    loc = get_geolocation()
    gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "📍 GPS nicht verfügbar"
    
    c1, c2, c3 = st.columns(3)
    datum = c1.date_input("Datum")
    az_val = c2.text_input("Aktenzeichen")
    ort_val = c3.text_input("Ort / Hausnummer")

    with st.form("bericht_form"):
        inhalt = st.text_area("Sachverhalt")
        beteiligte = st.text_input("Beteiligte Personen")
        bild = st.file_uploader("Beweisfoto", type=["jpg", "png"])
        
        if st.form_submit_button("✅ Bericht speichern"):
            b64_img = "-"
            if bild:
                img = Image.open(bild).convert("RGB")
                img.thumbnail((800, 800))
                buf = io.BytesIO()
                img.save(buf, format="JPEG")
                b64_img = base64.b64encode(buf.getvalue()).decode()

            new_entry = {
                "Datum": str(datum), "Beginn": "-", "Ende": "-", "Ort": ort_val, "Hausnummer": "-",
                "Zeugen": verschluesseln(beteiligte), "Bericht": verschluesseln(inhalt),
                "AZ": az_val, "Foto": verschluesseln(b64_img), "GPS": gps_val, "Kraefte": verschluesseln("KOD")
            }
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success("Bericht archiviert!")
            st.rerun()

st.divider()
st.header("📂 Archiv")
if os.path.exists(DATEI):
    df_arch = pd.read_csv(DATEI)
    for idx, row in df_arch.iloc[::-1].iterrows():
        with st.container():
            st.markdown(f'<div class="report-card"><b>AZ: {row["AZ"]}</b> | {row["Datum"]} | {row["Ort"]}</div>', unsafe_allow_html=True)
            if st.session_state["admin_auth"]:
                c_pdf, c_del = st.columns(2)
                c_pdf.download_button("PDF Export", create_official_pdf(row), f"{row['AZ']}.pdf", key=f"p_{idx}")
                if c_del.button("Löschen", key=f"d_{idx}"):
                    df_arch.drop(idx).to_csv(DATEI, index=False)
                    st.rerun()

# --- 6. ADMIN LOGIN (FÜR PDF & LÖSCHEN) ---
st.markdown("<br><hr>", unsafe_allow_html=True)
with st.expander("🛡️ Admin-Funktionen"):
    if not st.session_state["admin_auth"]:
        ad_in = st.text_input("Admin-Passwort", type="password")
        if st.button("Admin-Bereich freischalten"):
            if ad_in == ADMIN_PW:
                st.session_state["admin_auth"] = True
                st.rerun()
    else:
        if st.button("Admin-Logout"):
            st.session_state["admin_auth"] = False
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True) # Ende main-content
