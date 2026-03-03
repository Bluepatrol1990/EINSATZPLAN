import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# --- SEITEN-STYLING ---
st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div, .stMarkdown { color: #ffffff !important; }
    .main-title { color: #ffffff; font-size: 2.2rem; font-weight: 800; border-bottom: 2px solid #004b95; padding-bottom: 10px; margin-bottom: 20px; }
    .einsatz-card { background-color: #111111; border-radius: 10px; padding: 15px; margin-bottom: 10px; border: 1px solid #333; border-left: 5px solid #004b95; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div { background-color: #1a1a1a !important; color: white !important; border: 1px solid #444 !important; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- KONSTANTEN ---
PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"
LOGO_DATEI = "logo.jpg" 
STRASSEN_DATEI = "strassen.txt"
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# --- FUNKTIONEN ---
def lade_strassen():
    """Liest die Straßennamen aus der externen Textdatei."""
    if os.path.exists(STRASSEN_DATEI):
        with open(STRASSEN_DATEI, "r", encoding="utf-8") as f:
            strassen = [line.strip() for line in f.readlines() if line.strip()]
            return sorted(list(set(strassen))) + ["📍 Manuelle Eingabe / Nicht in Liste"]
    return ["📍 Manuelle Eingabe / Nicht in Liste"]

def lade_daten():
    spalten = ["Datum", "Anfang", "Ende", "Ort", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"]
    if os.path.exists(DATEI):
        try:
            df = pd.read_csv(DATEI).fillna("-").astype(str)
            return df
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
    pdf.cell(0, 10, txt="EINSATZBERICHT - AUGSBURG", ln=True, align='R')
    pdf.set_draw_color(0, 75, 149)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 11)
    
    details = [
        ("Datum", row['Datum']), ("Zeit", f"{row['Anfang']} - {row['Ende']}"),
        ("Ort", row['Ort']), ("Beteiligte", row['Zeugen']),
        ("Kräfte", f"Pol: {row['Polizei']} | RD: {row['RD']} | FS: {row['FS']} ({row['FS_Details']})")
    ]
    for k, v in details:
        pdf.set_font("Arial", "B", 11); pdf.cell(40, 8, txt=f"{k}:", ln=0)
        pdf.set_font("Arial", "", 11); pdf.cell(0, 8, txt=str(v).replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss'), ln=1)
    
    pdf.ln(10); pdf.set_font("Arial", "B", 11); pdf.cell(0, 8, "Sachverhalt:", ln=1)
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
        st.markdown("<h2 style='text-align:center;'>🚓 Dienst-Login</h2>", unsafe_allow_html=True)
        pw = st.text_input("Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw == PASSWORT:
                st.session_state["autentifiziert"] = True
                st.rerun()
    st.stop()

# --- HAUPTBEREICH ---
st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()
strassen_liste = lade_strassen()

with st.expander("➕ NEUEN BERICHT ERFASSEN", expanded=False):
    with st.form("main_entry", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        d = col1.date_input("Datum", datetime.now())
        ts = col2.time_input("Beginn", datetime.now().time())
        te = col3.time_input("Ende", datetime.now().time())
        
        auswahl_ort = st.selectbox("Straße auswählen / suchen", options=strassen_liste)
        ort_tippen = ""
        if auswahl_ort == "📍 Manuelle Eingabe / Nicht in Liste":
            ort_tippen = st.text_input("Genaue Adresse / Ort eingeben")
        
        finaler_ort = ort_tippen if auswahl_ort == "📍 Manuelle Eingabe / Nicht in Liste" else auswahl_ort
        zeuge = st.text_input("Beteiligte / Zeugen")
        
        k1, k2, k3, k4 = st.columns([1,1,1,2])
        pol = k1.checkbox("Polizei")
        rd = k2.checkbox("RD")
        fs = k3.checkbox("FS")
        fsi = k4.text_input("Details Funkstreife")
        
        bericht_text = st.text_area("Sachverhalt", height=200)
        submit = st.form_submit_button("🚀 BERICHT SPEICHERN", use_container_width=True)

    if submit:
        if bericht_text and finaler_ort:
            neue_zeile = pd.DataFrame([[str(d), ts.strftime("%H:%M"), te.strftime("%H:%M"), str(finaler_ort), str(zeuge), 
                                         "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", 
                                         str(fsi), str(bericht_text)]], columns=daten.columns)
            pd.concat([daten, neue_zeile], ignore_index=True).to_csv(DATEI, index=False)
            st.success("Erfolgreich im Archiv gespeichert!")
            st.rerun()

# --- ARCHIV ---
st.subheader("📂 Archiv")
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        st.markdown(f"""<div class="einsatz-card"><b>📍 {row['Ort']}</b><br><small>{row['Datum']} | {row['Anfang']}-{row['Ende']} Uhr</small></div>""", unsafe_allow_html=True)
        with st.expander("Details / PDF / Bearbeiten"):
            t1, t2, t3 = st.tabs(["📄 Lesen", "✏️ Korrigieren", "🗑️ Löschen"])
            with t1:
                st.info(row['Bericht'])
                st.download_button("📄 PDF Export", erstelle_pdf(row), f"Bericht_{i}.pdf", key=f"pdf_{i}")
            with t2:
                with st.form(f"edit_{i}"):
                    u_ort = st.text_input("Ort", value=row['Ort'])
                    u_txt = st.text_area("Bericht", value=row['Bericht'], height=200)
                    if st.form_submit_button("💾 Update"):
                        daten.at[i, 'Ort'] = u_ort
                        daten.at[i, 'Bericht'] = u_txt
                        daten.to_csv(DATEI, index=False)
                        st.rerun()
            with t3:
                if st.button("❌ Bericht endgültig löschen", key=f"del_{i}"):
                    daten = daten.drop(i)
                    daten.to_csv(DATEI, index=False)
                    st.rerun()
else:
    st.info("Keine Berichte vorhanden.")
