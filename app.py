import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# --- DESIGN-KONFIGURATION ---
st.set_page_config(page_title="Einsatzliste OA Nacht", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    .report-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        border-left: 6px solid #004b95;
        margin-bottom: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
    .card-header {
        font-size: 1.1rem;
        font-weight: bold;
        color: #004b95;
    }
    </style>
    """, unsafe_allow_html=True)

PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"
# WICHTIG: Hier muss exakt der Name stehen, den die Datei auf GitHub hat!
LOGO_DATEI = "logo.jpg" 

# --- DATEN-FUNKTIONEN ---
def lade_daten():
    spalten_soll = ["Datum", "Anfang", "Ende", "Ort", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"]
    if os.path.exists(DATEI):
        try:
            df = pd.read_csv(DATEI)
            for col in spalten_soll:
                if col not in df.columns: df[col] = "-"
            return df.fillna("-").astype(str)
        except: pass
    return pd.DataFrame(columns=spalten_soll)

def erstelle_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo im PDF (JPG Unterstützung)
    if os.path.exists(LOGO_DATEI):
        pdf.image(LOGO_DATEI, 10, 8, 30)
        pdf.ln(20)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="EINSATZPROTOKOLL", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    text = (f"Datum: {row['Datum']}\n"
            f"Zeitraum: {row['Anfang']} bis {row['Ende']}\n"
            f"Ort: {row['Ort']}\n"
            f"Zeugen: {row['Zeugen']}\n"
            f"Kräfte: Pol: {row['Polizei']} | RD: {row['RD']} | FS: {row['FS']}\n\n"
            f"Bericht:\n{row['Bericht']}")
    clean = text.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
    pdf.multi_cell(0, 10, txt=clean)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- LOGIN ---
if "autentifiziert" not in st.session_state:
    st.session_state["autentifiziert"] = False

if not st.session_state["autentifiziert"]:
    st.title("🔐 Login")
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, width=150)
    eingabe = st.text_input("Passwort", type="password")
    if st.button("Anmelden"):
        if eingabe == PASSWORT:
            st.session_state["autentifiziert"] = True
            st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, use_container_width=True)
    if st.button("🔴 Logout"):
        st.session_state["autentifiziert"] = False
        st.rerun()
    st.divider()
    f_datum = st.date_input("Filter Datum", value=None)
    f_ort = st.text_input("Filter Ort")

# --- HAUPTBEREICH ---
st.title("📝 Einsatzliste OA")

with st.expander("➕ Neuer Bericht", expanded=True):
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        d = c1.date_input("Datum", datetime.now())
