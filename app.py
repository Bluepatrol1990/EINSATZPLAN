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

# --- 1. SICHERHEIT & VERSCHLÜSSELUNG ---
try:
    DIENST_PW = st.secrets["dienst_password"]
    ADMIN_PW = st.secrets["admin_password"]
    MASTER_KEY = st.secrets["master_key"]
except:
    # Fallback für lokale Tests
    DIENST_PW = "1234"
    ADMIN_PW = "admin789"
    MASTER_KEY = "AugsburgSicherheit32ZeichenCheck!"

def get_cipher():
    # Erzeugt den AES-Schlüssel aus dem Master-Key
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

# --- 2. KONSTANTEN & DATEN ---
DATEI = "zentral_archiv_secure.csv"
STRASSEN_AUGSBURG = sorted([
    "Maximilianstraße", "Königsplatz", "Rathausplatz", "Moritzplatz", "Ulrichsplatz", 
    "Annastraße", "Bahnhofstraße", "Hermanstraße", "Karlstraße", "Grottenau", 
    "Fuggerstraße", "Konrad-Adenauer-Allee", "Elias-Holl-Platz", "Haunstetter Straße", 
    "Gögginger Straße", "Friedberger Straße", "Berliner Allee", "Bgm.-Ackermann-Straße", 
    "Donauwörther Straße", "Ulmer Straße", "Hirblinger Straße", "Lechhauser Straße", 
    "Neuburger Straße", "Viktoriastraße", "Jakoberstraße", "Vorderer Lech"
])

BAUSTEINE = {
    "Auswählen...": "",
    "🚨 Ruhestörung": "Nach Eingang einer Beschwerde wurde vor Ort eine erhebliche Lärmbelästigung festgestellt. Die Verursacher wurden zur Ruhe ermahnt. Personalien wurden aufgenommen.",
    "🚫 Platzverweis": "Aufgrund aggressiven Verhaltens und Störung der öffentlichen Ordnung wurde der Person ein Platzverweis ausgesprochen. Zuwiderhandlung führt zur Gewahrsamnahme.",
    "🍺 Jugendschutz Maxstr.": "Im Rahmen der Jugendschutzkontrolle in der Maximilianstraße wurden alkoholische Getränke bei Minderjährigen sichergestellt. Die Erziehungsberechtigten wurden informiert.",
    "🚮 Müll / Unrat": "Es wurde eine illegale Müllablagerung im öffentlichen Raum festgestellt. Beweismittel zur Identifizierung des Verursachers wurden gesichert.",
    "🐕 Hundekontrolle": "Kontrolle der Anleinpflicht. Der Halter wurde auf die geltende Stadtsatzung hingewiesen. Keine Auffälligkeiten."
}

# --- 3. PDF GENERATOR ---
class BehoerdenPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.set_text_color(0, 75, 149) # Augsburg Blau
        self.cell(0, 10, "STADT AUGSBURG - Ordnungsamt", ln=True)
        self.ln(10); self.line(10, 25, 200, 25)

    def footer(self):
        self.set_y(-20); self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Seite {self.page_no()} | Amtlicher Bericht | Vertraulich", align="C")

def erstelle_pdf(row):
    pdf = BehoerdenPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14); pdf.set_text_color(0,0,0)
    pdf.cell(0, 10, f"Einsatzprotokoll - AZ: {row['AZ']}", ln=True); pdf.ln(5)
    
    pdf.set_font("Arial", "B", 10); pdf.cell(40, 8, "Datum/Zeit:", 1); pdf.set_font("Arial", "", 10); pdf.cell(0, 8, f"{row['Datum']} / {row['Beginn']}", 1, 1)
    pdf.set_font("Arial", "B", 10); pdf.cell(40, 8, "Ort:", 1); pdf.set_font("Arial", "", 10); pdf.cell(0, 8, f"{row['Ort']} {row['Hausnummer']}", 1, 1)
    pdf.set_font("Arial", "B", 10); pdf.cell(40, 8, "GPS:", 1); pdf.set_font("Arial", "", 10); pdf.cell(0, 8, f"{row['GPS']}", 1, 1)
    
    pdf.ln(5); pdf.set_font("Arial", "B", 11); pdf.cell(0, 8, "Sachverhalt:", ln=True)
    pdf.set_font("Arial", "", 10); pdf.multi_cell(0, 7, row['Bericht'], border=1)
    
    if row['Foto'] != "-":
        pdf.ln(5); pdf.set_text_color(0, 75, 149); pdf.cell(0, 8, "Beweisfoto:", ln=True)
        img_data = base64.b64decode(row['Foto'])
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(img_data); tmp_path = tmp.name
        pdf.set_draw_color(0, 75, 149)
        pdf.rect(60, pdf.get_y(), 82, 62) # Rahmen
        pdf.image(tmp_path, x=61, y=pdf.get_y()+1, w=80)
        os.unlink(tmp_path)
    
    pdf.set_y(-50); pdf.set_text_color(0,0,0)
    pdf.cell(90, 10, "____________________", 0, 0); pdf.cell(90, 10, "____________________", 0, 1)
    pdf.cell(90, 5, "Ort, Datum", 0, 0); pdf.cell(90, 5, f"Handzeichen {row['Dienstkraft']}", 0, 1)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. APP LOGIK ---
st.set_page_config(page_title="OA Augsburg Pro", page_icon="🚓", layout="wide")
st.markdown("<style>.stApp { background-color: #0d0d0d; color: #ffffff; }</style>", unsafe_allow_html=True)

if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🚓 Dienst-Login")
    pw = st.text_input("Passwort", type="password")
    if st.button("Anmelden"):
        if pw == DIENST_PW: st.session_state["auth"] = True; st.rerun()
        else: st.error("Falsches Passwort")
    st.stop()

# Daten laden & entschlüsseln
def lade_daten():
    spalten = ["Datum", "Beginn", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "Dienstkraft", "GPS"]
    if os.path.exists(DATEI):
        df = pd.read_csv(DATEI).astype(str)
        for col in ["Bericht", "Zeugen", "Foto"]:
            df[col] = df[col].apply(entschluesseln)
        return df
    return pd.DataFrame(columns=spalten)

daten = lade_daten()

# --- GPS BUTTON ---
st.subheader("📍 Standort fixieren")
loc = get_geolocation()
gps_ready = "-"
if loc:
    gps_ready = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}"
    st.success(f"Position erfasst: {gps_ready}")
else:
    st.info("Klicke am Handy auf 'Zulassen', um GPS zu nutzen.")

# --- FORMULAR ---
with st.expander("➕ NEUEN BERICHT SCHREIBEN", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1,1,2])
        d = c1.date_input("Datum")
        t = c2.time_input("Zeit")
        gps_field = c3.text_input("GPS-Koordinaten", value=gps_ready, disabled=True)
        
        o1, o2, o3 = st.columns([3,1,2])
        ort = o1.selectbox("Straße (Augsburg)", options=STRASSEN_AUGSBURG, index=None)
        hsnr = o2.text_input("Nr.")
        az = o3.text_input("AZ")
        
        auswahl = st.selectbox("⚡ Textbaustein (Maxstr. etc.)", options=list(BAUSTEINE.keys()))
        
        # Diktierfunktion über die Handy-Tastatur
        bericht = st.text_area("Bericht (Mikrofon-Taste auf Tastatur nutzen)", 
                               value=BAUSTEINE[auswahl] if auswahl != "Auswählen..." else "", height=150)
        
        z = st.text_input("Beteiligte / Zeugen")
        dk = st.text_input("Dienstkraft Kürzel")
        f = st.file_uploader("📸 Beweisfoto")
        
        if st.form_submit_button("🔒 VERSCHLÜSSELT SPEICHERN"):
            if bericht and ort:
                f_b = "-"
                if f:
                    img = Image.open(f); img.thumbnail((800, 800))
                    buf = io.BytesIO(); img.save(buf, format="JPEG", quality=75)
                    f_b = base64.b64encode(buf.getvalue()).decode()
                
                new_data = [str(d), t.strftime("%H:%M"), str(ort), hsnr, verschluesseln(z), 
                            verschluesseln(bericht), az, verschluesseln(f_b), dk, gps_ready]
                
                # In CSV schreiben (verschlüsselt)
                new_df = pd.DataFrame([new_data], columns=daten.columns)
                pd.concat([pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=daten.columns), new_df]).to_csv(DATEI, index=False)
                st.success("Bericht sicher in der Datenbank abgelegt!"); st.rerun()

# --- ARCHIV ---
st.divider()
st.subheader("📂 Verschlüsseltes Archiv")
for i, row in daten.iloc[::-1].iterrows():
    with st.expander(f"📍 {row['Ort']} | {row['Datum']} | AZ: {row['AZ']}"):
        st.write(f"**Zeit:** {row['Beginn']} | **GPS:** {row['GPS']}")
        st.info(row['Bericht'])
        if row['Foto'] != "-": st.image(base64.b64decode(row['Foto']), width=300)
        
        # Admin Bereich für PDF Export
        if st.sidebar.text_input(f"Admin-Key für {row['AZ']}", type="password", key=f"key_{i}") == ADMIN_PW:
            st.download_button("📄 PDF (behördlich) exportieren", data=erstelle_pdf(row), file_name=f"Bericht_{row['AZ']}.pdf")
