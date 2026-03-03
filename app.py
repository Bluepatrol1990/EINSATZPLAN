import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io

# --- KONFIGURATION & MODERNES STYLING ---
st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div, .stMarkdown { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; }
    .main-title { color: #ffffff; font-size: 2.5rem; font-weight: 800; border-bottom: 3px solid #004b95; padding-bottom: 15px; margin-bottom: 30px; }
    .einsatz-card { background: #151515; border-radius: 12px; padding: 20px; margin-bottom: 15px; border: 1px solid #333; border-left: 10px solid #004b95; }
    .card-header { font-size: 1.4rem; font-weight: 800; color: #6ea8fe !important; margin-bottom: 2px; }
    .card-sub { font-size: 0.9rem; color: #888888 !important; margin-bottom: 12px; font-weight: 500; }
    .card-zeugen { font-size: 0.95rem; color: #cccccc !important; background: #222; padding: 8px; border-radius: 5px; margin-top: 10px; }
    .badge { padding: 5px 12px; border-radius: 5px; font-size: 0.75rem; font-weight: 900; margin-right: 10px; display: inline-block; }
    .b-pol { background-color: #004b95; color: white; }
    .b-rd { background-color: #8b0000; color: white; }
    .b-fs { background-color: #ffcc00; color: black; }
    /* Formular-Styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div { background-color: #1a1a1a !important; color: white !important; border-radius: 8px !important; border: 1px solid #444 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- KONSTANTEN ---
DIENST_PW = "1234"
ADMIN_PW = "admin789"
DATEI = "zentral_archiv.csv"
# GEÄNDERT: Von 'logo.jpg' auf 'logo.png'
LOGO_DATEI = "logo.png" 
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# --- PDF GENERATOR MIT PNG-LOGO ---
def erstelle_behoerden_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    
    # PNG-Logo hinzufügen (falls vorhanden)
    if os.path.exists(LOGO_DATEI):
        # Das PNG wird automatisch mit Transparenz geladen
        # w=40 bedeutet: Breite 40mm, Höhe wird automatisch berechnet
        pdf.image(LOGO_DATEI, x=10, y=8, w=40)
        pdf.ln(20) # Abstand nach unten schaffen
    
    # Überschrift (Augsburg Blau)
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 75, 149) 
    pdf.cell(0, 10, "Ordnungsamt Stadt Augsburg", ln=True, align='R')
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Amtlicher Einsatzbericht / Protokollfuehrung", ln=True, align='R')
    
    # Trennlinie
    pdf.set_draw_color(0, 75, 149)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(15)
    
    # Einsatzdetails
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Einsatzort:", ln=0)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"{row['Ort']} {row['Zusatz']}", ln=1)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Datum/Zeit:", ln=0)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"{row['Datum']} | {row['Anfang']} - {row['Ende']} Uhr", ln=1)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Beteiligte:", ln=0)
    pdf.set_font("Arial", "", 11)
    # Bereinigen von Umlauten für FPDF (WICHTIG!)
    pdf.multi_cell(0, 8, str(row['Zeugen']).replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss'))
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, "Sachverhalt / Bericht:", ln=1)
    pdf.set_font("Arial", "", 11)
    
    # Berichtstext bereinigen
    text = str(row['Bericht']).replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
    pdf.multi_cell(0, 7, text)
    
    # Unterschriftenbereich
    pdf.ln(40)
    pdf.line(10, pdf.get_y(), 90, pdf.get_y())
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 5, "Datum, Unterschrift Dienstkraft (Sachbearbeiter)", ln=True)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- DATEN LADEN & SPEICHERN ---
def lade_daten():
    spalten = ["Datum", "Anfang", "Ende", "Ort", "Zusatz", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"]
    if os.path.exists(DATEI):
        try:
            df = pd.read_csv(DATEI)
            for s in spalten:
                if s not in df.columns: df[s] = "-"
            return df[spalten].fillna("-").astype(str)
        except: return pd.DataFrame(columns=spalten)
    return pd.DataFrame(columns=spalten)

# --- LOGIN & SIDEBAR (ADMIN) ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "is_admin" not in st.session_state: st.session_state["is_admin"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("<h1 style='text-align:center;'>🚓 Dienst-Login</h1>", unsafe_allow_html=True)
        if st.text_input("Dienst-Passwort", type="password") == DIENST_PW:
            if st.button("Anmelden", use_container_width=True):
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

with st.sidebar:
    st.title("⚙️ Admin-Bereich")
    if st.text_input("Admin-Passwort", type="password") == ADMIN_PW:
        st.session_state["is_admin"] = True
        st.success("🔓 Admin-Modus AKTIV")
    else: st.session_state["is_admin"] = False
    st.divider()
    if st.button("🔴 Logout"):
        st.session_state["auth"] = False
        st.rerun()

# --- HAUPTBEREICH: EINSATZ-DASHBOARD ---
st.markdown("<div class='main-title'>📋 Einsatz-Dashboard</div>", unsafe_allow_html=True)
daten = lade_daten()

# Neuen Bericht erfassen (für alle)
with st.expander("➕ NEUEN EINSATZBERICHT SCHREIBEN", expanded=True):
    with st.form("entry_form"):
        # (Formularfelder hier einfügen... Datum, Ort, Zeugen, etc.)
        st.info("Formular ausfüllen...")
        if st.form_submit_button("Bericht speichern"): pass

# --- MODERNES ARCHIV ---
st.subheader("📂 Archivierte Berichte")
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        b_p = f'<span class="badge b-pol">POL</span>' if row['Polizei'] == "Ja" else ""
        b_r = f'<span class="badge b-rd">RD</span>' if row['RD'] == "Ja" else ""
        b_f = f'<span class="badge b-fs">FS</span>' if row['FS'] == "Ja" else ""
        
        st.markdown(f"""
            <div class="einsatz-card">
                <div class="card-header">📍 {row['Ort']} {row['Zusatz']}</div>
                <div class="card-sub">🕒 {row['Datum']} | {row['Anfang']} Uhr</div>
                <div class="card-zeugen">👥 <b>Beteiligte:</b> {row['Zeugen']}</div>
                <div style="margin-top:10px;">{b_p}{b_r}{b_f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Vollständigen Bericht & Export"):
            st.markdown(f"**Berichtstext:**\n\n{row['Bericht']}")
            
            # PDF NUR FÜR ADMIN
            if st.session_state["is_admin"]:
                st.divider()
                st.download_button(
                    label="📄 Behördliches PDF generieren",
                    data=erstelle_behoerden_pdf(row),
                    file_name=f"Einsatz_{row['Datum']}_{row['Ort']}.pdf",
                    mime="application/pdf",
                    key=f"pdf_{i}"
                )
                if st.button("🗑️ Bericht löschen", key=f"del_{i}"):
                    daten.drop(i).to_csv(DATEI, index=False)
                    st.rerun()
else:
    st.info("Das Archiv ist leer.")
