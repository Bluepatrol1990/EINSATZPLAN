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

# --- DARK DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }
    .main-title { font-size: 2.2rem; font-weight: 800; color: #004b95; border-bottom: 3px solid #004b95; padding-bottom: 10px; margin-bottom: 25px; }
    .einsatz-card { background: #1a1a1a; border-radius: 10px; padding: 15px; margin-bottom: 10px; border: 1px solid #333; border-left: 8px solid #004b95; }
    input, textarea, .stSelectbox div { background-color: #262626 !important; color: white !important; border: 1px solid #444 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- KONSTANTEN ---
DIENST_PW = "1234"
ADMIN_PW = "admin789"
DATEI = "zentral_archiv.csv"
STRASSEN_AUGSBURG = sorted(["Maximilianstraße", "Königsplatz", "Rathausplatz", "Moritzplatz", "Ulrichsplatz", "Annastraße", "Bahnhofstraße", "Hermanstraße", "Karlstraße", "Grottenau", "Fuggerstraße", "Konrad-Adenauer-Allee", "Elias-Holl-Platz", "Haunstetter Straße", "Gögginger Straße", "Friedberger Straße", "Berliner Allee", "Bgm.-Ackermann-Straße", "Donauwörther Straße", "Ulmer Straße", "Hirblinger Straße", "Lechhauser Straße", "Neuburger Straße", "Viktoriastraße"])

# --- PDF PROFI-FUNKTION ---
class BehoerdenPDF(FPDF):
    def header(self):
        # Logo (falls logo.png im Ordner existiert)
        if os.path.exists("logo.png"):
            self.image("logo.png", 160, 10, 35)
        
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 75, 149)
        self.cell(0, 10, "STADT AUGSBURG", ln=True)
        self.set_font("Arial", "I", 10)
        self.cell(0, 5, "Ordnungsreferat - Kommunaler Ordnungsdienst", ln=True)
        self.ln(15)
        self.set_draw_color(0, 75, 149)
        self.line(10, 32, 200, 32)

    def footer(self):
        self.set_y(-25)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Seite {self.page_no()} | Automatisch generierter Einsatzbericht | Vertrauliche Dienstsache", align="C")

def erstelle_profi_pdf(row):
    pdf = BehoerdenPDF()
    pdf.add_page()
    
    # Titel
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, f"EINSATZPROTOKOLL - AZ: {row['AZ']}", ln=True, align="L")
    pdf.ln(5)

    # Stammdaten-Tabelle
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 10)
    
    data = [
        ["Datum:", row['Datum'], "Dienstkraft:", row['Dienstkraft']],
        ["Beginn:", row['Beginn'], "Ende:", row['Ende']],
        ["Ort:", f"{row['Ort']} {row['Hausnummer']}", "", ""]
    ]
    
    for r in data:
        pdf.cell(30, 8, r[0], 1, 0, "L", True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(65, 8, str(r[1]), 1)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(30, 8, r[2], 1, 0, "L", True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(65, 8, str(r[3]), 1)
        pdf.ln()

    pdf.ln(10)
    
    # Zeugen / Beteiligte
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, "Beteiligte Personen / Zeugen:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, str(row['Zeugen']), border="B")
    pdf.ln(5)

    # Sachverhalt
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, "Sachverhalt / Feststellungen:", ln=True)
    pdf.set_font("Arial", "", 10)
    bericht_clean = str(row['Bericht']).encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 7, bericht_clean)
    
    # Abschluss
    pdf.ln(20)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(95, 10, "__________________________", 0, 0)
    pdf.cell(95, 10, "__________________________", 0, 1)
    pdf.cell(95, 5, "Datum, Ort", 0, 0)
    pdf.cell(95, 5, "Unterschrift Dienstkraft", 0, 1)

    return pdf.output(dest='S').encode('latin-1')

# --- LOGIK (Rest wie vorher) ---
def lade_daten():
    spalten = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "Dienstkraft"]
    if os.path.exists(DATEI):
        try: return pd.read_csv(DATEI).fillna("-").astype(str)
        except: return pd.DataFrame(columns=spalten)
    return pd.DataFrame(columns=spalten)

def bild_zu_base64(bild_datei):
    if bild_datei:
        img = Image.open(bild_datei); img.thumbnail((800, 800))
        buf = io.BytesIO(); img.save(buf, format="JPEG", quality=75)
        return base64.b64encode(buf.getvalue()).decode()
    return "-"

if "auth" not in st.session_state: st.session_state["auth"] = False
if "is_admin" not in st.session_state: st.session_state["is_admin"] = False

if not st.session_state["auth"]:
    st.title("🚓 Dienst-Login")
    if st.text_input("Passwort", type="password") == DIENST_PW:
        if st.button("Anmelden"): st.session_state["auth"] = True; st.rerun()
    st.stop()

with st.sidebar:
    st.markdown("### 🔐 Admin")
    if st.text_input("Admin-Passwort", type="password") == ADMIN_PW:
        st.session_state["is_admin"] = True; st.success("Admin aktiv")
    else: st.session_state["is_admin"] = False
    if st.button("Abmelden"): st.session_state.clear(); st.rerun()

st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()

with st.expander("➕ NEUEN BERICHT SCHREIBEN", expanded=True):
    with st.form("e_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        d = c1.date_input("Datum")
        bs = c2.time_input("Beginn")
        be = c3.time_input("Ende")
        o1, o2, o3 = st.columns([3,1,2])
        ort = o1.selectbox("Straße", options=STRASSEN_AUGSBURG, index=None)
        if not ort: ort = o1.text_input("Manueller Ort")
        hsnr = o2.text_input("Hausnr.")
        az = o3.text_input("AZ")
        z = st.text_input("Beteiligte")
        dk = st.text_input("Dienstkraft")
        txt = st.text_area("Bericht", height=150)
        f = st.file_uploader("Foto", type=['jpg','png','jpeg'])
        if st.form_submit_button("🚀 SPEICHERN"):
            if txt:
                f_b = bild_zu_base64(f)
                new = pd.DataFrame([[str(d), bs.strftime("%H:%M"), be.strftime("%H:%M"), str(ort), str(hsnr), str(z), str(txt), str(az), f_b, str(dk)]], columns=daten.columns)
                pd.concat([daten, new], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Gespeichert!"); st.rerun()

st.divider()
for i, row in daten.iloc[::-1].iterrows():
    st.markdown(f"<div class='einsatz-card'><b>📍 {row['Ort']} {row['Hausnummer']}</b><br>{row['Datum']} | AZ: {row['AZ']}</div>", unsafe_allow_html=True)
    with st.expander("Details"):
        st.info(row['Bericht'])
        if row['Foto'] != "-": st.image(base64.b64decode(row['Foto']), width=400)
        if st.session_state["is_admin"]:
            st.download_button("📄 PDF Behörden-Export", data=erstelle_profi_pdf(row), file_name=f"Einsatz_{row['AZ']}.pdf", key=f"pdf_{i}")
