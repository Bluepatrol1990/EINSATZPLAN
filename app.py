import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io
import base64
from PIL import Image
import tempfile
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation

# --- 1. SEITEN-KONFIGURATION (Muss als allererstes kommen!) ---
st.set_page_config(page_title="OA Augsburg Pro", page_icon="🚓", layout="wide")

# --- 2. SESSION STATE INITIALISIEREN ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

# --- 3. SICHERHEIT & VERSCHLÜSSELUNG ---
try:
    DIENST_PW = st.secrets["dienst_password"]
    ADMIN_PW = st.secrets["admin_password"]
    MASTER_KEY = st.secrets["master_key"]
except:
    DIENST_PW = "1234"
    ADMIN_PW = "admin789"
    MASTER_KEY = "AugsburgSicherheit32ZeichenCheck!"

def get_cipher():
    key_64 = base64.urlsafe_b64encode(MASTER_KEY[:32].encode().ljust(32))
    return Fernet(key_64)

def verschluesseln(text):
    if not text or text == "-": return "-"
    return get_cipher().encrypt(text.encode()).decode()

def entschluesseln(safe_text):
    if not safe_text or safe_text == "-": return "-"
    try:
        return get_cipher().decrypt(safe_text.encode()).decode()
    except:
        return "[Entschlüsselungsfehler]"

# --- 4. DATEN & STRASSEN ---
DATEI = "zentral_archiv_secure.csv"
STRASSEN_AUGSBURG = sorted([
    "Maximilianstraße", "Königsplatz", "Rathausplatz", "Moritzplatz", "Ulrichsplatz", 
    "Annastraße", "Bahnhofstraße", "Hermanstraße", "Karlstraße", "Grottenau", 
    "Fuggerstraße", "Konrad-Adenauer-Allee", "Elias-Holl-Platz", "Haunstetter Straße", 
    "Gögginger Straße", "Friedberger Straße", "Berliner Allee", "Bgm.-Ackermann-Straße", 
    "Donauwörther Straße", "Ulmer Straße", "Hirblinger Straße", "Lechhauser Straße", 
    "Neuburger Straße", "Viktoriastraße", "Jakoberstraße", "Vorderer Lech", "Predigerberg"
])

BAUSTEINE = {
    "Auswählen...": "",
    "🚨 Ruhestörung": "Nach Eingang einer Beschwerde wurde vor Ort eine erhebliche Lärmbelästigung festgestellt. Die Verursacher wurden zur Ruhe ermahnt. Personalien wurden aufgenommen.",
    "🚫 Platzverweis": "Aufgrund aggressiven Verhaltens und Störung der öffentlichen Ordnung wurde der Person ein Platzverweis ausgesprochen. Zuwiderhandlung führt zur Gewahrsamnahme.",
    "🍺 Jugendschutz": "Im Rahmen einer Jugendschutzkontrolle wurden alkoholische Getränke bei Minderjährigen sichergestellt. Die Erziehungsberechtigten wurden informiert.",
    "🚮 Müll / Unrat": "Es wurde eine illegale Müllablagerung im öffentlichen Raum festgestellt. Beweismittel zur Identifizierung des Verursachers wurden gesichert."
}

# --- 5. PDF GENERATOR ---
class BehoerdenPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.set_text_color(0, 75, 149) 
        self.cell(0, 10, "STADT AUGSBURG - Ordnungsamt", ln=True)
        self.ln(10); self.line(10, 25, 200, 25)

def erstelle_pdf(row):
    pdf = BehoerdenPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Einsatzprotokoll - AZ: {row['AZ']}", ln=True); pdf.ln(5)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 7, f"Datum: {row['Datum']}\nOrt: {row['Ort']} {row['Hausnummer']}\nGPS: {row['GPS']}\n\nBericht:\n{row['Bericht']}")
    return pdf.output(dest='S').encode('latin-1')

# --- 6. LOGIN LOGIK ---
if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>🚓 Dienst Login</h1>", unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            pw = st.text_input("Dienst-Passwort", type="password")
            if st.button("Anmelden", use_container_width=True):
                if pw == DIENST_PW:
                    st.session_state["auth"] = True
                    st.rerun()
                else:
                    st.error("Falsches Passwort")
    st.stop()

# --- 7. HAUPTSEITE (Erscheint nach Login) ---
st.markdown("<style>.stApp { background-color: #0d0d0d; color: #ffffff; }</style>", unsafe_allow_html=True)
st.title("📋 Mobiler Einsatzbericht")

# GPS abrufen
loc = get_geolocation()
gps_ready = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "-"

# Daten laden
def lade_daten():
    if os.path.exists(DATEI):
        df = pd.read_csv(DATEI).astype(str)
        for col in ["Bericht", "Zeugen", "Foto"]:
            df[col] = df[col].apply(entschluesseln)
        return df
    return pd.DataFrame(columns=["Datum", "Beginn", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "Dienstkraft", "GPS"])

daten = lade_daten()

# --- FORMULAR ---
with st.expander("➕ NEUEN BERICHT SCHREIBEN", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1,1,2])
        d = c1.date_input("Datum")
        t = c2.time_input("Zeit")
        gps_val = c3.text_input("📍 Standort fixiert", value=gps_ready, disabled=True)
        
        o1, o2, o3 = st.columns([3,1,2])
        ort_wahl = o1.selectbox("Straße / Ort (Augsburg)", options=STRASSEN_AUGSBURG, index=None)
        hsnr = o2.text_input("Nr.")
        az = o3.text_input("AZ")
        
        auswahl = st.selectbox("⚡ Textbaustein wählen", options=list(BAUSTEINE.keys()))
        bericht = st.text_area("Sachverhalt (Nutze Mikrofon auf Tastatur)", 
                               value=BAUSTEINE[auswahl] if auswahl != "Auswählen..." else "", height=150)
        
        z = st.text_input("Beteiligte / Zeugen")
        dk = st.text_input("DK Kürzel")
        f = st.file_uploader("📸 Foto hochladen")
        
        if st.form_submit_button("🔒 VERSCHLÜSSELT SPEICHERN"):
            if bericht and ort_wahl:
                f_b = "-"
                if f:
                    img = Image.open(f); img.thumbnail((800, 800))
                    buf = io.BytesIO(); img.save(buf, format="JPEG")
                    f_b = base64.b64encode(buf.getvalue()).decode()
                
                new_row = [str(d), t.strftime("%H:%M"), str(ort_wahl), hsnr, verschluesseln(z), 
                           verschluesseln(bericht), az, verschluesseln(f_b), dk, gps_ready]
                
                new_df = pd.DataFrame([new_row], columns=daten.columns)
                pd.concat([pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=daten.columns), new_df]).to_csv(DATEI, index=False)
                st.success("Gespeichert!"); st.rerun()

# --- ARCHIV ---
st.divider()
st.subheader("📂 Sicherer Archiv-Zugriff")
for i, row in daten.iloc[::-1].iterrows():
    with st.expander(f"📍 {row['Ort']} | {row['Datum']} | AZ: {row['AZ']}"):
        st.write(f"**Bericht:** {row['Bericht']}")
        if row['Foto'] != "-":
            st.image(base64.b64decode(row['Foto']), width=300)
        
        # Admin Sperre für PDF
        if st.sidebar.text_input(f"Admin-Freigabe {row['AZ']}", type="password", key=f"adm_{i}") == ADMIN_PW:
            st.download_button("📄 PDF Export", data=erstelle_pdf(row), file_name=f"Bericht_{row['AZ']}.pdf")
