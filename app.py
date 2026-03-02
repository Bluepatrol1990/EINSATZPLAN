import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
from PIL import Image

# --- KONFIGURATION & STYLING (PURE DARK MODE) ---
st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    /* Hintergrund der App auf Tiefschwarz */
    .stApp { 
        background-color: #000000; 
    }
    
    /* Alle Texte auf Reinweiß */
    h1, h2, h3, p, span, label, div, .stMarkdown {
        color: #ffffff !important;
    }

    /* Titel-Styling */
    .main-title {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 20px;
        border-bottom: 2px solid #004b95;
        padding-bottom: 10px;
    }

    /* Karten-Design im Archiv */
    .einsatz-card {
        background-color: #111111;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(255,255,255,0.05);
        border: 1px solid #333;
        border-left: 6px solid #004b95;
    }
    
    /* Eingabefelder (Dunkel mit weißer Schrift) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #444 !important;
    }

    /* Badges */
    .badge {
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 5px;
        display: inline-block;
    }
    .badge-pol { background-color: #004b95; color: white; }
    .badge-rd { background-color: #8b0000; color: white; }
    .badge-fs { background-color: #ffcc00; color: black; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid #222;
    }
    </style>
    """, unsafe_allow_html=True)

# Daten-Konstanten
PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"
LOGO_DATEI = "logo.jpg" 
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# --- FUNKTIONEN ---
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
    pdf.cell(0, 10, txt="EINSATZBERICHT - STADT AUGSBURG", ln=True, align='R')
    pdf.set_draw_color(0, 75, 149)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 11)
    details = [
        ("Datum", row['Datum']), ("Zeitspanne", f"{row['Anfang']} - {row['Ende']} Uhr"),
        ("Einsatzort", row['Ort']), ("Beteiligte", row['Zeugen']),
        ("Kraefte", f"Pol: {row['Polizei']} | RD: {row['RD']} | FS: {row['FS']}")
    ]
    for label, value in details:
        pdf.set_font("Arial", "B", 11); pdf.cell(40, 8, txt=f"{label}:", ln=0)
        pdf.set_font("Arial", "", 11); pdf.cell(0, 8, txt=str(value).replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss'), ln=1)
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
        st.markdown("<h1 style='text-align:center;'>🚓 Dienst-Login</h1>", unsafe_allow_html=True)
        if os.path.exists(LOGO_DATEI): st.image(LOGO_DATEI, width=150)
        pw = st.text_input("Dienst-Passwort", type="password")
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
    f_datum = st.date_input("Berichte filtern (Datum)", value=None)
    f_ort = st.text_input("Berichte filtern (Ort)")

# --- HAUPTBEREICH ---
st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()

# Metriken
c1, c2, c3 = st.columns(3)
c1.metric("Berichte Gesamt", len(daten))
c2.metric("Berichte Heute", len(daten[daten['Datum'] == datetime.now().strftime("%Y-%m-%d")]))
c3.metric("Status", "Einsatzbereit")

# NEUER BERICHT
with st.expander("➕ NEUEN EINSATZBERICHT SCHREIBEN", expanded=False):
    with st.form("new_entry_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        d = col1.date_input("Einsatzdatum", datetime.now())
        ts = col2.time_input("Einsatzbeginn", datetime.now().time())
        te = col3.time_input("Einsatzende", datetime.now().time())
        ort = st.text_input("Genaue Ortsangabe")
        zeuge = st.text_input("Beteiligte Personen / Zeugen")
        k1, k2, k3, k4 = st.columns([1,1,1,2])
        pol = k1.checkbox("Polizei")
        rd = k2.checkbox("Rettungsdienst")
        fs = k3.checkbox("Funkstreife")
        fsi = k4.text_input("Details Funkstreife (z.B. Name)")
        txt = st.text_area("Ausführlicher Sachverhalt", height=200)
        submit = st.form_submit_button("🚀 BERICHT ARCHIVIEREN", use_container_width=True)

    if submit:
        if txt and ort:
            new_row = pd.DataFrame([[str(d), ts.strftime("%H:%M"), te.strftime("%H:%M"), str(ort), str(zeuge), 
                                     "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", 
                                     str(fsi), str(txt)]], columns=daten.columns)
            pd.concat([daten, new_row], ignore_index=True).to_csv(DATEI, index=False)
            st.success("Bericht wurde erfolgreich gespeichert.")
            st.rerun()

# --- ARCHIV ---
st.subheader("📂 Archivierte Einsatzberichte")
if not daten.empty:
    filtered = daten.copy()
    if f_datum: filtered = filtered[filtered['Datum'] == str(f_datum)]
    if f_ort: filtered = filtered[filtered['Ort'].str.contains(f_ort, case=False)]

    for i, row in filtered.iloc[::-1].iterrows():
        # Badge-HTML
        b_html = ""
        if row['Polizei'] == "Ja": b_html += '<span class="badge badge-pol">POLIZEI</span>'
        if row['RD'] == "Ja": b_html += '<span class="badge badge-rd">RD</span>'
        if row['FS'] == "Ja": b_html += '<span class="badge badge-fs">FUNKSTREIFE</span>'

        st.markdown(f"""
            <div class="einsatz-card">
                <div style="font-weight:bold; color:#ffffff; font-size:1.2rem;">📍 {row['Ort']}</div>
                <div style="font-size:0.9rem; color:#888;">📅 {row['Datum']} | ⏰ {row['Anfang']} - {row['Ende']} Uhr</div>
                <div style="margin-top:8px;">{b_html}</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Bericht einsehen / PDF / Bearbeiten"):
            t1, t2, t3 = st.tabs(["📄 Sachverhalt", "✏️ Korrigieren", "🗑️ Entfernen"])
            with t1:
                st.write(f"**Beteiligte:** {row['Zeugen']}")
                st.info(row['Bericht'])
                st.download_button("📄 PDF HERUNTERLADEN", erstelle_pdf(row), f"Einsatz_{row['Datum']}_{i}.pdf", key=f"pdf_{i}")
            with t2:
                with st.form(f"edit_{i}"):
                    e_ort = st.text_input("Ort korrigieren", value=row['Ort'])
                    e_txt = st.text_area("Bericht korrigieren", value=row['Bericht'], height=200)
                    if st.form_submit_button("💾 ÄNDERUNGEN SPEICHERN"):
                        daten.at[i, 'Ort'] = e_ort
                        daten.at[i, 'Bericht'] = e_txt
                        daten.to_csv(DATEI, index=False)
                        st.rerun()
            with t3:
                if st.button("⚠️ BERICHT UNWIDERRUFLICH LÖSCHEN", key=f"del_{i}"):
                    daten = daten.drop(i)
                    daten.to_csv(DATEI, index=False)
                    st.rerun()
else:
    st.info("Bisher keine Berichte im Archiv vorhanden.")
