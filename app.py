import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io
import base64
from PIL import Image

# --- GRUNDEINSTELLUNGEN ---
st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

# --- DARK DESIGN (Hintergrund Schwarz, Schrift Weiß) ---
st.markdown("""
    <style>
    /* Hintergrund der gesamten App auf Schwarz */
    .stApp { background-color: #000000; color: #ffffff; }
    
    /* Alle Texte weiß machen */
    h1, h2, h3, p, span, label, .stMarkdown, .stSelectbox label, .stTextInput label, .stTextArea label { 
        color: #ffffff !important; 
    }
    
    /* Überschrift Styling */
    .main-title { 
        font-size: 2.2rem; 
        font-weight: 800; 
        color: #004b95; 
        border-bottom: 3px solid #004b95; 
        padding-bottom: 10px; 
        margin-bottom: 25px;
    }
    
    /* Einsatz-Karten im Archiv */
    .einsatz-card { 
        background: #1a1a1a; 
        border-radius: 10px; 
        padding: 15px; 
        margin-bottom: 10px; 
        border: 1px solid #333;
        border-left: 8px solid #004b95; 
    }
    
    /* Eingabefelder anpassen damit man Text sieht */
    input, textarea, .stSelectbox div {
        background-color: #262626 !important;
        color: white !important;
        border: 1px solid #444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KONSTANTEN ---
DIENST_PW = "1234"
ADMIN_PW = "admin789"
DATEI = "zentral_archiv.csv"
STRASSEN_AUGSBURG = sorted(["Maximilianstraße", "Königsplatz", "Rathausplatz", "Moritzplatz", "Ulrichsplatz", "Annastraße", "Bahnhofstraße", "Hermanstraße", "Karlstraße", "Grottenau", "Fuggerstraße", "Konrad-Adenauer-Allee", "Elias-Holl-Platz", "Haunstetter Straße", "Gögginger Straße", "Friedberger Straße", "Berliner Allee", "Bgm.-Ackermann-Straße", "Donauwörther Straße", "Ulmer Straße", "Hirblinger Straße", "Lechhauser Straße", "Neuburger Straße", "Viktoriastraße"])

# --- FUNKTIONEN ---
def lade_daten():
    spalten = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "Dienstkraft"]
    if os.path.exists(DATEI):
        try:
            return pd.read_csv(DATEI).fillna("-").astype(str)
        except:
            return pd.DataFrame(columns=spalten)
    return pd.DataFrame(columns=spalten)

def bild_zu_base64(bild_datei):
    if bild_datei:
        img = Image.open(bild_datei)
        img.thumbnail((800, 800))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=75)
        return base64.b64encode(buffered.getvalue()).decode()
    return "-"

def erstelle_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Einsatzbericht Stadt Augsburg", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.ln(5)
    pdf.cell(0, 8, f"Ort: {row['Ort']} {row['Hausnummer']}", ln=1)
    pdf.cell(0, 8, f"Zeit: {row['Datum']} ({row['Beginn']}-{row['Ende']})", ln=1)
    pdf.cell(0, 8, f"AZ: {row['AZ']} | DK: {row['Dienstkraft']}", ln=1)
    pdf.ln(5)
    bericht_clean = str(row['Bericht']).encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 7, f"Bericht: {bericht_clean}")
    return pdf.output(dest='S').encode('latin-1')

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "is_admin" not in st.session_state: st.session_state["is_admin"] = False

if not st.session_state["auth"]:
    st.title("🚓 Dienst-Login")
    pw = st.text_input("Passwort eingeben", type="password")
    if st.button("Anmelden"):
        if pw == DIENST_PW:
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- SIDEBAR (ADMIN & LOGOUT) ---
with st.sidebar:
    st.markdown("### 🔐 Admin-Bereich")
    a_pw = st.text_input("Admin-Passwort", type="password")
    if a_pw == ADMIN_PW:
        st.session_state["is_admin"] = True
        st.success("Admin-Modus aktiv")
    else:
        st.session_state["is_admin"] = False
    
    if st.button("Abmelden"):
        st.session_state.clear()
        st.rerun()

# --- HAUPTBEREICH ---
st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()

# --- EINGABEFORMULAR ---
with st.expander("➕ NEUEN BERICHT SCHREIBEN", expanded=True):
    with st.form("einsatz_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        d = c1.date_input("Datum")
        bs = c2.time_input("Beginn")
        be = c3.time_input("Ende")
        
        o1, o2, o3 = st.columns([3,1,2])
        ort = o1.selectbox("Straße auswählen", options=STRASSEN_AUGSBURG, index=None, placeholder="Suchen...")
        if not ort: ort = o1.text_input("Ort manuell eingeben")
        hsnr = o2.text_input("Hausnr.")
        az = o3.text_input("AZ (Polizei)")
        
        zeuge = st.text_input("Beteiligte / Zeugen")
        dk = st.text_input("Dienstkraft Kürzel")
        txt = st.text_area("Sachverhalt / Bericht", height=150)
        foto = st.file_uploader("📸 Foto zur Beweissicherung", type=['jpg','png','jpeg'])
        
        if st.form_submit_button("🚀 BERICHT SPEICHERN"):
            if txt and (ort or hsnr):
                f_b64 = bild_zu_base64(foto)
                new = pd.DataFrame([[str(d), bs.strftime("%H:%M"), be.strftime("%H:%M"), str(ort), str(hsnr), str(zeuge), str(txt), str(az), f_b64, str(dk)]], columns=daten.columns)
                pd.concat([daten, new], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Bericht wurde gespeichert!"); st.rerun()

# --- ARCHIV ---
st.divider()
st.subheader("📂 Archivierte Berichte")
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        st.markdown(f"""
            <div class='einsatz-card'>
                <b style='color:#6ea8fe; font-size:1.2rem;'>📍 {row['Ort']} {row['Hausnummer']}</b><br>
                <span>📅 {row['Datum']} | 🕒 {row['Beginn']}-{row['Ende']} | 👤 DK: {row['Dienstkraft']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Details & Foto öffnen"):
            st.write(f"**Aktenzeichen:** {row['AZ']}")
            st.write(f"**Beteiligte:** {row['Zeugen']}")
            st.info(row['Bericht'])
            if row['Foto'] != "-":
                st.image(base64.b64decode(row['Foto']), width=400)
            
            # PDF Download nur für Admins
            if st.session_state["is_admin"]:
                pdf_data = erstelle_pdf(row)
                st.download_button("📄 PDF Export", data=pdf_data, file_name=f"Bericht_{row['Datum']}.pdf", key=f"pdf_{i}")
else:
    st.info("Noch keine Berichte im System.")
