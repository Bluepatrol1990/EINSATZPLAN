import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io
import base64
from PIL import Image
import locale

# --- SPRACHE ---
try:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
except:
    pass

st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

# --- STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div, .stMarkdown { color: #ffffff !important; }
    .main-title { font-size: 2.5rem; font-weight: 800; border-bottom: 3px solid #004b95; padding-bottom: 10px; margin-bottom: 30px; }
    .einsatz-card { background: #151515; border-radius: 12px; padding: 20px; margin-bottom: 15px; border: 1px solid #333; border-left: 10px solid #004b95; }
    .card-meta { color: #888; font-size: 0.95rem; margin-top: 5px; }
    .dk-badge { background: #004b95; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
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
        df = pd.read_csv(DATEI)
        for s in spalten:
            if s not in df.columns: df[s] = "-"
        return df[spalten].fillna("-").astype(str)
    return pd.DataFrame(columns=spalten)

def bild_zu_base64(bild_datei):
    if bild_datei:
        img = Image.open(bild_datei)
        img.thumbnail((800, 800))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=75)
        return base64.b64encode(buffered.getvalue()).decode()
    return "-"

def erstelle_behoerden_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 75, 149)
    pdf.cell(0, 10, "Ordnungsamt Stadt Augsburg", ln=True)
    pdf.set_font("Arial", "B", 10); pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Einsatzbericht | AZ: {row['AZ']}", ln=True)
    pdf.ln(10); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Ort:"); pdf.set_font("Arial", "", 11); pdf.cell(0, 8, f"{row['Ort']} {row['Hausnummer']}", ln=1)
    pdf.set_font("Arial", "B", 11); pdf.cell(40, 8, "Zeit:"); pdf.set_font("Arial", "", 11); pdf.cell(0, 8, f"{row['Datum']} ({row['Beginn']}-{row['Ende']})", ln=1)
    pdf.ln(5); pdf.set_font("Arial", "B", 11); pdf.cell(0, 10, "Sachverhalt:", ln=1)
    pdf.set_font("Arial", "", 11)
    safe_text = str(row['Bericht']).encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 7, safe_text)
    return pdf.output(dest='S')

# --- LOGIN & ADMIN-CHECK ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "is_admin" not in st.session_state: st.session_state["is_admin"] = False

with st.sidebar:
    st.header("🔑 Login")
    if not st.session_state["auth"]:
        if st.text_input("Dienst-Passwort", type="password") == DIENST_PW:
            st.session_state["auth"] = True; st.rerun()
    else:
        st.success("Angemeldet")
        if st.text_input("Admin-Passwort", type="password") == ADMIN_PW:
            st.session_state["is_admin"] = True
            st.warning("🔓 Admin-Rechte aktiv")
        if st.button("Logout"): st.session_state["auth"] = False; st.rerun()

if not st.session_state["auth"]: st.stop()

# --- HAUPTBEREICH ---
st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()

# --- FORMULAR ---
with st.expander("➕ NEUEN BERICHT SCHREIBEN", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        d = c1.date_input("Datum", datetime.now())
        u_s = c2.time_input("Beginn", datetime.now().time())
        u_e = c3.time_input("Ende", datetime.now().time())
        dk = c4.text_input("Dienstkraft")
        
        o1, o2, o3 = st.columns([3, 1, 2])
        ort_wahl = o1.selectbox("Straße", options=STRASSEN_AUGSBURG, index=None, placeholder="Suchen...")
        if not ort_wahl: ort_wahl = o1.text_input("Manueller Ort")
        hsnr = o2.text_input("Hausnr.")
        az = o3.text_input("AZ (Polizei)")
        
        zeuge = st.text_input("Zeugen/Beteiligte")
        txt = st.text_area("Sachverhalt", height=200)
        foto = st.file_uploader("📸 Foto", type=['jpg', 'jpeg', 'png'])
        
        if st.form_submit_button("🚀 SPEICHERN"):
            if txt and ort_wahl:
                foto_b64 = bild_zu_base64(foto)
                new = pd.DataFrame([[str(d), u_s.strftime("%H:%M"), u_e.strftime("%H:%M"), str(ort_wahl), str(hsnr), str(zeuge), str(txt), str(az), foto_b64, str(dk)]], columns=daten.columns)
                pd.concat([daten, new], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Gespeichert!"); st.rerun()

# --- ARCHIV ---
st.subheader("📂 Archiv")
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        st.markdown(f"""
            <div class="einsatz-card">
                <b>📍 {row['Ort']} {row['Hausnummer']}</b> <span class="dk-badge">{row['Dienstkraft']}</span><br>
                <span class="card-meta">📅 {row['Datum']} | 🕒 {row['Beginn']}-{row['Ende']} | AZ: {row['AZ']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Details anzeigen"):
            st.write(f"**Beteiligte:** {row['Zeugen']}")
            st.info(row['Bericht'])
            if row['Foto'] != "-":
                st.image(base64.b64decode(row['Foto']), width=400)
            
            # HIER WAR DER FEHLER: Der Button muss IN die Schleife
            if st.session_state["is_admin"]:
                pdf_bytes = erstelle_behoerden_pdf(row)
                st.download_button("📄 PDF Export", data=pdf_bytes, file_name=f"Bericht_{row['Datum']}.pdf", key=f"pdf_{i}")
