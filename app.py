import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io
import base64
from PIL import Image
import tempfile

# --- GRUNDEINSTELLUNGEN ---
st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

# --- DARK DESIGN (Bildschirm-Ansicht) ---
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

# --- PDF PROFI-FUNKTION (Mit neuem Header-Text) ---
class BehoerdenPDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 160, 10, 35)
        self.set_font("Arial", "B", 15)
        self.set_text_color(0, 75, 149) # Augsburg Blau
        self.cell(0, 10, "STADT AUGSBURG", ln=True)
        self.set_font("Arial", "B", 12)
        self.cell(0, 7, "Ordnungsamt", ln=True) # Geänderter Text
        self.ln(12)
        self.set_draw_color(0, 75, 149)
        self.line(10, 30, 200, 30)

    def footer(self):
        self.set_y(-25)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Seite {self.page_no()} | Amtlicher Einsatzbericht | Stadt Augsburg - Ordnungsamt", align="C")

def erstelle_profi_pdf(row):
    pdf = BehoerdenPDF()
    pdf.add_page()
    
    # Header & Stammdaten
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, f"EINSATZPROTOKOLL - AZ: {row['AZ']}", ln=True)
    pdf.ln(5)

    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 10)
    
    # Tabelle für Details
    pdf.cell(30, 8, "Datum:", 1, 0, "L", True); pdf.set_font("Arial", "", 10); pdf.cell(65, 8, str(row['Datum']), 1)
    pdf.set_font("Arial", "B", 10); pdf.cell(30, 8, "Dienstkraft:", 1, 0, "L", True); pdf.set_font("Arial", "", 10); pdf.cell(65, 8, str(row['Dienstkraft']), 1, 1)
    
    pdf.set_font("Arial", "B", 10); pdf.cell(30, 8, "Beginn:", 1, 0, "L", True); pdf.set_font("Arial", "", 10); pdf.cell(65, 8, str(row['Beginn']), 1)
    pdf.set_font("Arial", "B", 10); pdf.cell(30, 8, "Ende:", 1, 0, "L", True); pdf.set_font("Arial", "", 10); pdf.cell(65, 8, str(row['Ende']), 1, 1)
    
    pdf.set_font("Arial", "B", 10); pdf.cell(30, 8, "Ort:", 1, 0, "L", True); pdf.set_font("Arial", "", 10); pdf.cell(160, 8, f"{row['Ort']} {row['Hausnummer']}", 1, 1)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Beteiligte Personen / Zeugen:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, str(row['Zeugen']), border=1)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Sachverhalt / Feststellungen:", ln=True)
    pdf.set_font("Arial", "", 10)
    bericht_clean = str(row['Bericht']).encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, bericht_clean, border=1)

    # --- BILD INTEGRATION ---
    if row['Foto'] != "-":
        pdf.ln(10)
        img_data = base64.b64decode(row['Foto'])
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(img_data)
            tmp_path = tmp.name
        
        bild_breite = 80 
        seiten_breite = pdf.w - 20 
        x_pos = (seiten_breite - bild_breite) / 2 + 10 

        if pdf.get_y() > 180: pdf.add_page()

        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(0, 75, 149)
        pdf.cell(0, 8, f"Beweisfoto / Dokumentation:", ln=True, align="C")
        pdf.ln(2)

        with Image.open(tmp_path) as img:
            real_w, real_h = img.size
            ratio = real_h / real_w
            bild_hoehe = bild_breite * ratio

        pdf.set_draw_color(0, 75, 149)
        pdf.rect(x_pos - 1, pdf.get_y() - 1, bild_breite + 2, bild_hoehe + 2)
        pdf.image(tmp_path, x=x_pos, y=pdf.get_y(), w=bild_breite)
        
        os.unlink(tmp_path)
        pdf.set_y(pdf.get_y() + bild_hoehe + 15)
    else:
        pdf.ln(20)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(95, 10, "__________________________", 0, 0)
    pdf.cell(95, 10, "__________________________", 0, 1)
    pdf.cell(95, 5, "Datum, Ort", 0, 0)
    pdf.cell(95, 5, "Handzeichen Dienstkraft", 0, 1)

    return pdf.output(dest='S').encode('latin-1')

# --- LOGIK (LOGIN, FORMULAR, ARCHIV) ---
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
        ort = o1.selectbox("Straße", options=STRASSEN_AUGSBURG, index=None, placeholder="Wählen...")
        if not ort: ort = o1.text_input("Manueller Ort")
        hsnr = o2.text_input("Hausnr.")
        az = o3.text_input("AZ")
        z = st.text_input("Beteiligte / Zeugen")
        dk = st.text_input("Dienstkraft Kürzel")
        txt = st.text_area("Bericht / Sachverhalt", height=150)
        f = st.file_uploader("📸 Foto hochladen", type=['jpg','png','jpeg'])
        if st.form_submit_button("🚀 BERICHT SPEICHERN"):
            if txt and (ort or hsnr):
                f_b = bild_zu_base64(f)
                new = pd.DataFrame([[str(d), bs.strftime("%H:%M"), be.strftime("%H:%M"), str(ort), str(hsnr), str(z), str(txt), str(az), f_b, str(dk)]], columns=daten.columns)
                pd.concat([daten, new], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Erfolgreich gespeichert!"); st.rerun()

st.divider()
for i, row in daten.iloc[::-1].iterrows():
    st.markdown(f"<div class='einsatz-card'><b>📍 {row['Ort']} {row['Hausnummer']}</b><br>{row['Datum']} | {row['Beginn']}-{row['Ende']} | AZ: {row['AZ']}</div>", unsafe_allow_html=True)
    with st.expander("Details"):
        st.write(f"**Beteiligte:** {row['Zeugen']}")
        st.info(row['Bericht'])
        if row['Foto'] != "-": st.image(base64.b64decode(row['Foto']), width=400)
        if st.session_state["is_admin"]:
            st.download_button("📄 PDF Export (Behörde)", data=erstelle_profi_pdf(row), file_name=f"Bericht_{row['AZ']}.pdf", key=f"pdf_{i}")
