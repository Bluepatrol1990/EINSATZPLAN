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

# --- 1. GLOBALE VARIABLEN ---
DATEI = "zentral_archiv_secure.csv"
LOGO_PFAD = "logo.png" 
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
ADMIN_PW = "admin789"
DIENST_PW = "1990" 
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!") 

# Hinterlegte Empfänger (aus deinen Anweisungen)
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

st.set_page_config(page_title="KOD Sicherheitsbereich", page_icon="🛡️", layout="wide") 

# --- 2. SICHERHEITS-CSS (VERBIRGT MENU & FOOTER) ---
st.markdown("""
    <style>
    /* Verbirgt das Streamlit Menü (Hamburger) und den Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
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
    </style>
    """, unsafe_allow_html=True) 

# --- 3. SICHERHEITS-FUNKTIONEN ---
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

# (Die PDF-Funktion bleibt unverändert wie im vorigen Schritt)
def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    # ... (Inhalt wie zuvor)
    return pdf.output(dest="S").encode("latin-1")

# --- 4. LOGIN (SAUBERE OBERFLÄCHE OHNE MENÜ) ---
if not st.session_state["auth"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("#")
        st.markdown("<h1 style='text-align: center; color: #004b95;'>🛡️ KOD Sicherheitsbereich</h1>", unsafe_allow_html=True)
        pw_input = st.text_input("Dienst-Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw_input == DIENST_PW:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Zugriff verweigert.")
    st.stop()

# --- 5. HAUPTBEREICH ---
st.title("📋 Einsatzbericht System")

# ... Hier folgt dein Berichts-Formular und das Archiv ...

# --- SIDEBAR (EINZIGER ZUGANG ZUR VERWALTUNG) ---
with st.sidebar:
    st.markdown("### 🛠️ Verwaltung")
    # Admin Anmeldung bleibt hier diskret
    with st.expander("🔑 Admin-Bereich"):
        a_pw = st.text_input("Admin-Passwort", type="password")
        if a_pw == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin-Modus aktiv")
        else:
            st.session_state["admin_auth"] = False

    if st.session_state["admin_auth"]:
        st.write("Sie haben nun Zugriff auf PDF-Exports und Löschfunktionen.")
        if st.button("System-Logout"):
            st.session_state.clear()
            st.rerun()
