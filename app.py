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

# --- MINIMALES DESIGN (Verhindert schwarzen Bildschirm) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; }
    .main-title { font-size: 2.2rem; font-weight: 800; color: #004b95; border-bottom: 2px solid #004b95; padding-bottom: 10px; }
    .einsatz-card { background: #f0f2f6; border-radius: 10px; padding: 15px; margin-bottom: 10px; border-left: 8px solid #004b95; color: #000000; }
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
    pdf.multi_cell(0, 7, f"Bericht: {row['Bericht']}".encode('latin-1', 'ignore').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "is_admin" not in st.session_state: st.session_state["is_admin"] = False

if not st.session_state["auth"]:
    st.title("🚓 Login")
    pw = st.text_input("Passwort", type="password")
    if st.button("Starten"):
        if pw == DIENST_PW:
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.write("### Admin")
    a_pw = st.text_input("Admin-Key", type="password")
    if a_pw == ADMIN_PW: st.session_state["is_admin"] = True
    if st.button("Abmelden"):
        st.session_state.clear()
        st.rerun()

# --- HAUPTTEIL ---
st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()

with st.expander("➕ NEUER BERICHT", expanded=True):
    with st.form("f"):
        c1, c2, c3 = st.columns(3)
        d = c1.date_input("Datum")
        bs = c2.time_input("Beginn")
        be = c3.time_input("Ende")
        
        o1, o2, o3 = st.columns([3,1,2])
        ort = o1.selectbox("Ort", options=STRASSEN_AUGSBURG, index=None)
        if not ort: ort = o1.text_input("Manueller Ort")
        hsnr = o2.text_input("Nr.")
        az = o3.text_input("AZ")
        
        zeuge = st.text_input("Beteiligte")
        dk = st.text_input("Kürzel DK")
        txt = st.text_area("Bericht", height=150)
        foto = st.file_uploader("Foto", type=['jpg','png','jpeg'])
        
        if st.form_submit_button("SPEICHERN"):
            f_b64 = bild_zu_base64(foto)
            new = pd.DataFrame([[str(d), bs.strftime("%H:%M"), be.strftime("%H:%M"), str(ort), str(hsnr), str(zeuge), str(txt), str(az), f_b64, str(dk)]], columns=daten.columns)
            pd.concat([daten, new], ignore_index=True).to_csv(DATEI, index=False)
            st.success("Gespeichert!"); st.rerun()

# --- ARCHIV ---
st.subheader("📂 Archiv")
for i, row in daten.iloc[::-1].iterrows():
    st.markdown(f"<div class='einsatz-card'><b>{row['Ort']} {row['Hausnummer']}</b><br>{row['Datum']} | {row['Beginn']}-{row['Ende']}</div>", unsafe_allow_html=True)
    with st.expander("Ansehen"):
        st.write(row['Bericht'])
        if row['Foto'] != "-":
            st.image(base64.b64decode(row['Foto']), width=300)
        if st.session_state["is_admin"]:
            st.download_button("📄 PDF", data=erstelle_pdf(row), file_name=f"Bericht_{i}.pdf", key=f"p{i}")
