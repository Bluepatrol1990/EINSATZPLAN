import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# --- KONFIGURATION ---
st.set_page_config(page_title="Einsatzliste OA Nacht", page_icon="🚓", layout="wide")

# CSS für das Design
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
    if os.path.exists(LOGO_DATEI):
        pdf.image(LOGO_DATEI, 10, 8, 30)
        pdf.ln(20)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="EINSATZPROTOKOLL", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    text = (f"Datum: {row['Datum']}\nZeitraum: {row['Anfang']} bis {row['Ende']}\nOrt: {row['Ort']}\n"
            f"Zeugen: {row['Zeugen']}\nKräfte: Pol: {row['Polizei']} | RD: {row['RD']} | FS: {row['FS']}\n\n"
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
    # Hier startet das Formular
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        d = c1.date_input("Datum", datetime.now())
        ts = c2.time_input("Anfang", datetime.now().time())
        te = c3.time_input("Ende", datetime.now().time())
        
        ort = st.text_input("Ort / Straße")
        zeuge = st.text_input("Zeugen")
        
        st.write("**Hinzugezogene Kräfte**")
        k1, k2, k3, k4 = st.columns([1,1,1,2])
        pol = k1.checkbox("Polizei")
        rd = k2.checkbox("RD")
        fs = k3.checkbox("FS")
        fs_i = k4.text_input("Details FS")
        
        txt_bericht = st.text_area("Bericht")
        
        # WICHTIG: Dieser Button MUSS eingerückt unter "with st.form" stehen
        submitted = st.form_submit_button("✅ Bericht speichern")

    # Logik nach dem Absenden (außerhalb des with-Blocks)
    if submitted:
        if txt_bericht:
            nz = pd.DataFrame([[str(d), ts.strftime("%H:%M"), te.strftime("%H:%M"), str(ort), str(zeuge), 
                                "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", 
                                str(fs_i), str(txt_bericht)]], 
                             columns=["Datum", "Anfang", "Ende", "Ort", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"])
            df = lade_daten()
            pd.concat([df, nz], ignore_index=True).to_csv(DATEI, index=False)
            st.success("Erfolgreich gespeichert!")
            st.rerun()
        else:
            st.error("Bitte gib einen Berichtstext ein!")

# --- ARCHIV ---
st.divider()
daten = lade_daten()
if not daten.empty:
    if f_datum: daten = daten[daten['Datum'] == str(f_datum)]
    if f_ort: daten = daten[daten['Ort'].str.contains(f_ort, case=False)]

    for i, row in daten.iloc[::-1].iterrows():
        st.markdown(f'<div class="report-card"><div class="card-header">📅 {row["Datum"]} | 📍 {row["Ort"]}</div><small>⏰ {row["Anfang"]} - {row["Ende"]}</small></div>', unsafe_allow_html=True)
        with st.expander("Bericht anzeigen"):
            st.write(f"**Kräfte:** Pol:{row['Polizei']}, RD:{row['RD']}, FS:{row['FS']} ({row['FS_Details']})")
            st.info(row['Bericht'])
            st.download_button("📄 PDF herunterladen", erstelle_pdf(row), f"Einsatz_{i}.pdf", "application/pdf", key=f"p_{i}")
