import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io
import base64
from PIL import Image
import locale

# --- SPRACHE ---
try:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
except:
    pass

st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

# --- STYLING (Helles Design mit blauen Akzenten) ---
st.markdown("""
    <style>
    .main-title { font-size: 2.5rem; font-weight: 800; color: #004b95; border-bottom: 3px solid #004b95; padding-bottom: 10px; margin-bottom: 30px; }
    .einsatz-card { background: #f9f9f9; border-radius: 12px; padding: 20px; margin-bottom: 15px; border: 1px solid #ddd; border-left: 10px solid #004b95; color: #333; }
    .card-meta { color: #666; font-size: 0.95rem; margin-top: 5px; }
    .dk-badge { background: #004b95; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- KONSTANTEN ---
DIENST_PW = "1234"
ADMIN_PW = "admin789"
DATEI = "zentral_archiv.csv"
STRASSEN_AUGSBURG = sorted([
    "Maximilianstraße", "Königsplatz", "Rathausplatz", "Moritzplatz", "Ulrichsplatz",
    "Annastraße", "Bahnhofstraße", "Hermanstraße", "Karlstraße", "Grottenau", "Fuggerstraße", 
    "Konrad-Adenauer-Allee", "Elias-Holl-Platz", "Haunstetter Straße", "Gögginger Straße", 
    "Friedberger Straße", "Berliner Allee", "Bgm.-Ackermann-Straße", "Donauwörther Straße", 
    "Ulmer Straße", "Hirblinger Straße", "Lechhauser Straße", "Neuburger Straße", "Viktoriastraße"
])

# --- FUNKTIONEN ---
def lade_daten():
    spalten = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "Dienstkraft"]
    if os.path.exists(DATEI):
        df = pd.read_csv(DATEI)
        for s in spalten:
            if s not in df.columns: df[s] = "-"
        return df[spalten].fillna("-").astype(str)
    return pd.DataFrame(columns=spalten)

def bild_zu_base64(bild_datei):
    if bild_datei:
        img = Image.open(bild_datei)
        img.thumbnail((800, 800))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=75)
        return base64.b64encode(buffered.getvalue()).decode()
    return "-"

def erstelle_behoerden_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Stadt Augsburg - Ordnungsamt", ln=True)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Einsatzbericht | AZ: {row['AZ']}", ln=True)
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Ort:", 0); pdf.set_font("Arial", "", 11); pdf.cell(0, 8, f"{row['Ort']} {row['Hausnummer']}", ln=1)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Zeitraum:", 0); pdf.set_font("Arial", "", 11); pdf.cell(0, 8, f"{row['Datum']} ({row['Beginn']} - {row['Ende']} Uhr)", ln=1)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Dienstkraft:", 0); pdf.set_font("Arial", "", 11); pdf.cell(0, 8, f"{row['Dienstkraft']}", ln=1)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Sachverhalt / Feststellungen:", ln=True)
    pdf.set_font("Arial", "", 11)
    # Umlaute-Sicherung
    txt = row['Bericht'].encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 7, txt)
    
    return pdf.output(dest='S').encode('latin-1')

# --- LOGIN & ADMIN-SESSION ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "is_admin" not in st.session_state: st.session_state["is_admin"] = False

with st.sidebar:
    st.header("🔐 Zugang")
    if not st.session_state["auth"]:
        if st.text_input("Dienst-Passwort", type="password") == DIENST_PW:
            if st.button("Einloggen"): st.session_state["auth"] = True; st
