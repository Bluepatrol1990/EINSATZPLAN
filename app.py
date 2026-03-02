import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# --- KONFIGURATION & STYLING ---
st.set_page_config(page_title="OA Einsatz-Dashboard", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .einsatz-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 6px solid #004b95;
    }
    .badge {
        padding: 2px 8px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-right: 4px;
        border: 1px solid;
    }
    .badge-pol { background-color: #e3f2fd; color: #0d47a1; border-color: #bbdefb; }
    .badge-rd { background-color: #ffebee; color: #b71c1c; border-color: #ffcdd2; }
    .badge-fs { background-color: #fffde7; color: #fbc02d; border-color: #fff9c4; }
    </style>
    """, unsafe_allow_html=True)

PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"
LOGO_DATEI = "logo.jpg" 

# --- DATEN-FUNKTIONEN ---
def lade_daten():
    spalten = ["Datum", "Anfang", "Ende", "Ort", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"]
    if os.path.exists(DATEI):
        try:
            df = pd.read_csv(DATEI)
            for c in spalten:
                if c not in df.columns: df[c] = "-"
            return df.fillna("-").astype(str)
        except: pass
    return pd.DataFrame(columns=spalten)

def erstelle_pdf(row):
    # PDF im Hochformat, weißer Hintergrund ist Standard
    pdf = FPDF()
    pdf.add_page()
    
    # Logo einfügen (Position oben links, Breite 35mm)
    if os.path.exists(LOGO_DATEI):
        # Wir platzieren das Logo ohne Rahmen auf das weiße Blatt
        pdf.image(LOGO_DATEI, x=10, y=10, w=35)
        pdf.ln(25) # Abstand nach unten, damit Text nicht im Logo klebt
    
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 75, 149) # Dunkelblau für die Überschrift
    pdf.cell(0, 10, txt="EINSATZPROTOKOLL - STADT AUGSBURG", ln=True, align='R')
    
    pdf.set_draw_color(0, 75, 149)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Eine Trennlinie
    pdf.ln(10)
    
    pdf.set_text_color(0, 0, 0) # Schwarz für den restlichen Text
    pdf.set_font("Arial", "B", 11)
    
    # Kompakte Datenübersicht
    details = [
        ("Datum", row['Datum']), ("Zeitspanne", f"{row['Anfang']} - {row['Ende']} Uhr"),
        ("Einsatzort", row['Ort']), ("Beteiligte", row['Zeugen']),
        ("Kräfte", f"Pol: {row['Polizei']} | RD: {row['RD']} | FS: {row['FS']} ({row['FS_Details']})")
    ]
    
    for label, value in details:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(40, 8, txt=f"{label}:", ln=0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, txt=str(value).replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss'), ln=1)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Sachverhalt / Bericht:", ln=1)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, txt=str(row['Bericht']).replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss'))
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- LOGIN ---
if "autentifiziert" not in st.session_state:
    st.session_state["autentifiziert"] = False

if not st.session_state["autentifiziert"]:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.title("🚓 Dienst-Login")
        if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, width=150)
        pw = st.text_input("Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw == PASSWORT:
                st.session_state["autentifiziert"] = True
                st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.
