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
    .stApp { background-color: #f4f7f9; }
    .einsatz-card {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 8px solid #004b95;
    }
    .badge {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 5px;
    }
    .badge-pol { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    .badge-rd { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .badge-fs { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
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
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_DATEI):
        pdf.image(LOGO_DATEI, 10, 8, 30)
        pdf.ln(20)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="EINSATZPROTOKOLL - STADT AUGSBURG", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    
    fields = [("Datum", row['Datum']), ("Zeit", f"{row['Anfang']}-{row['Ende']}"), ("Ort", row['Ort']), ("Zeugen", row['Zeugen'])]
    for k, v in fields:
        pdf.set_font("Arial", "B", 11); pdf.cell(40, 8, f"{k}:", 0); pdf.set_font("Arial", "", 11); pdf.cell(0, 8, str(v).replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss'), 1)
    
    pdf.ln(10); pdf.set_font("Arial", "B", 11); pdf.cell(0, 8
