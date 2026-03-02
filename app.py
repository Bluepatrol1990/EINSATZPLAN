import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# --- KONFIGURATION & STYLING (DARK MODE) ---
st.set_page_config(page_title="OA Einsatz-Dashboard", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    /* Hintergrund der gesamten App auf Schwarz/Dunkelgrau */
    .stApp { 
        background-color: #0e1117; 
    }
    
    /* Alle Texte standardmäßig auf Weiß */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #ffffff !important;
    }

    /* Karten-Design im Dark Mode */
    .einsatz-card {
        background-color: #1a1c24;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border-left: 6px solid #004b95;
        color: white;
    }
    
    /* Eingabefelder anpassen */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #262730 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }

    /* Badges für Einsatzkräfte */
    .badge {
        padding: 2px 8px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-right: 4px;
        border: 1px solid;
    }
    .badge-pol { background-color: #0d47a1; color: white; border-color: #1565c0; }
    .badge-rd { background-color: #b71c1c; color: white; border-color: #c62828; }
    .badge-fs { background-color: #fbc02d; color: black; border-color: #fdd835; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111318 !important;
    }
    </style>
    """, unsafe_allow_html=True)

PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"
LOGO_DATEI = "logo.jpg" 

# Empfänger-Info
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

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
        pdf.image(LOGO_DATEI, x=10, y=10, w=35)
        pdf.ln(25)
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 75, 149) 
    pdf.cell(0, 10, txt="EINSATZPROTOKOLL - STADT AUGSBURG", ln=True, align='R')
    pdf.set_draw_color(0, 75, 149)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 11)
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
    pdf.ln(10); pdf.set_font("Arial", "B", 11); pdf.cell(0, 8, "Bericht:", ln=1)
    pdf.set_font("Arial", "", 11); pdf.multi_cell(0, 7, txt=str(row['Bericht']).replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss'))
    pdf.ln(20); pdf.line(10, pdf.get_y(), 80, pdf.get_y()); pdf.line(120, pdf.get_y(), 190, pdf.get_y())
    pdf.set_font("Arial", "I", 8); pdf.cell(70, 5, txt="Unterschrift Ersteller", ln=0); pdf.cell(40, 5); pdf.cell(70, 5, txt="Unterschrift Kontrolle", ln=1)
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
with st.sidebar:
    if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, use_container_width=True)
    if st.button("🔴 Logout", use_container_width=True):
        st.session_state["autentifiziert"] = False
        st.rerun()
    st.divider()
    f_datum = st.date_input("Datum filtern", value=None)
    f_ort = st.text_input("Ort filtern")

# --- DASHBOARD ---
st.title("📋 Einsatz-Dashboard")
daten = lade_daten()

# Metriken (werden in Streamlit Dark Mode automatisch angepasst)
c1, c2, c3 = st.columns(3)
c1.metric("Gesamt", len(daten))
c2.metric("Heute", len(daten[daten['Datum'] == datetime.now().strftime("%Y-%m-%d")]))
c3.metric("Status", "Bereit")

# NEUER EINSATZ
with st.expander("➕ NEUEN EINSATZ ERFASSEN", expanded=False):
    with st.form("new_entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        d = col1.date_input("Datum", datetime.now())
        ts = col2.time_input("Start", datetime.now().time())
        te = col3.time_input("Ende", datetime.now().time())
        ort = st.text_input("Ort")
        zeuge = st.text_input("Beteiligte / Zeugen")
        k1, k2, k3, k4 = st.columns([1,1,1,2])
        pol = k1.checkbox("Polizei")
        rd = k2.checkbox("RD")
        fs = k3.checkbox("FS")
        fsi = k4.text_input("Details FS")
        txt = st.text_area("Bericht", height=150)
        submit = st.form_submit_button("🚀 SPEICHERN", use_container_width=True)

    if submit:
        if txt and ort:
            new_row = pd.DataFrame([[str(d), ts.strftime("%H:%M"), te.strftime("%H:%M"), str(ort), str(zeuge), 
                                     "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", 
                                     str(fsi), str(txt)]], columns=daten.columns)
            pd.concat([daten, new_row], ignore_index=True).to_csv(DATEI, index=False)
            st.success(f"Gespeichert!")
            st.rerun()

# --- ARCHIV ---
st.subheader("📚 Letzte Einsätze")
if not daten.empty:
    filtered = daten.copy()
    if f_datum: filtered = filtered[filtered['Datum'] == str(f_datum)]
    if f_ort: filtered = filtered[filtered['Ort'].str.contains(f_ort, case=False)]

    for i, row in filtered.iloc[::-1].iterrows():
        badges = ""
        if row['Polizei'] == "Ja": badges += '<span class="badge badge-pol">POL</span>'
        if row['RD'] == "Ja": badges += '<span class="badge badge-rd">RD</span>'
        if row['FS'] == "Ja": badges += '<span class="badge badge-fs">FS</span>'

        st.markdown(f"""
            <div class="einsatz-card">
                <div style="font-weight:bold; color:#6ea8fe;">📍 {row['Ort']}</div>
                <div style="font-size:0.8rem; color:#bbb;">📅 {row['Datum']} | ⏰ {row['Anfang']}-{row['Ende']}</div>
                <div style="margin-top:5px;">{badges}</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Details / Bearbeiten"):
            t1, t2, t3 = st.tabs(["📄 Lesen", "✏️ Editieren", "🗑️ Löschen"])
            with t1:
                st.info(row['Bericht'])
                st.download_button("📄 PDF", erstelle_pdf(row), f"Einsatz_{i}.pdf", key=f"pdf_{i}")
            with t2:
                with st.form(f"edit_{i}"):
                    e_ort = st.text_input("Ort", value=row['Ort'])
                    e_txt = st.text_area("Bericht", value=row['Bericht'])
                    if st.form_submit_button("💾 Update"):
                        daten.at[i, 'Ort'] = e_ort
                        daten.at[i, 'Bericht'] = e_txt
                        daten.to_csv(DATEI, index=False)
                        st.rerun()
            with t3:
                if st.button("❌ Löschen", key=f"del_{i}"):
                    daten = daten.drop(i)
                    daten.to_csv(DATEI, index=False)
                    st.rerun()
else:
    st.info("Keine Daten.")
