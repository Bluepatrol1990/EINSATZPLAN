import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io
import base64
from PIL import Image, ImageOps
import tempfile
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="OA Augsburg Pro", page_icon="🚓", layout="wide")

# --- 2. SESSION STATE ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False

# --- 3. SICHERHEIT & SECRETS ---
try:
    DIENST_PW = st.secrets["dienst_password"]
    MASTER_KEY = st.secrets["master_key"]
except:
    DIENST_PW = "1234"
    MASTER_KEY = "AugsburgSicherheit32ZeichenCheck!"

ADMIN_PW = "admin789"

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
    "Neuburger Straße", "Viktoriastraße", "Jakoberstraße", "Vorderer Lech", "Predigerberg",
    "City-Galerie", "Oberer Graben", "Untere Jakobermauer", "Schwibbogenplatz"
])

BAUSTEINE = {
    "Auswählen...": "",
    "🚨 Ruhestörung": "Nach Eingang einer Beschwerde wurde vor Ort eine erhebliche Lärmbelästigung festgestellt. Die Verursacher wurden zur Ruhe ermahnt. Personalien wurden aufgenommen.",
    "🚫 Platzverweis": "Aufgrund aggressiven Verhaltens und Störung der öffentlichen Ordnung wurde der Person ein Platzverweis ausgesprochen. Zuwiderhandlung führt zur Gewahrsamnahme.",
    "🍺 Jugendschutz": "Im Rahmen einer Jugendschutzkontrolle wurden alkoholische Getränke bei Minderjährigen sichergestellt. Die Erziehungsberechtigten wurden informiert.",
    "🚮 Müll / Unrat": "Es wurde eine illegale Müllablagerung im öffentlichen Raum festgestellt. Beweismittel zur Identifizierung des Verursachers wurden gesichert."
}

# --- 5. AMTKLICHER PDF GENERATOR ---
class BehoerdenPDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 30)
        else:
            self.set_font("Arial", "B", 10)
            self.set_text_color(150, 150, 150)
            self.cell(30, 10, "STADTWAPPEN", ln=False)
        
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 75, 149) 
        self.set_x(50)
        self.cell(0, 10, "STADT AUGSBURG", ln=True)
        self.set_font("Arial", "", 12)
        self.set_x(50)
        self.cell(0, 7, "Ordnungsamt | Kommunaler Ordnungsdienst", ln=True)
        self.ln(10)
        self.line(10, 42, 200, 42)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Einsatzprotokoll KOD Augsburg | Seite {self.page_no()}/{{nb}}", align="C")

def erstelle_pdf(row):
    pdf = BehoerdenPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Einsatzprotokoll | AZ: {row['AZ']}", ln=True)
    pdf.ln(5)
    
    # Fakten-Tabelle
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(245, 245, 245)
    
    fields = [
        ("Datum / Zeit:", f"{row['Datum']} | {row['Beginn']} - {row['Ende']}"),
        ("Einsatzort:", f"{row['Ort']} {row['Hausnummer']}"),
        ("Kräfte:", row['Kraefte']),
        ("Beteiligte:", row['Zeugen']),
        ("GPS:", row['GPS'])
    ]
    
    for label, val in fields:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(40, 7, f" {label}", fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, f" {val}", ln=True, fill=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Sachverhalt:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 6, row['Bericht'])
    
    # --- OPTIMIERTES BILD-HANDLING ---
    if row['Foto'] != "-":
        pdf.add_page() # Bilder auf neue Seite für bessere Übersicht
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Fotodokumentation / Beweismittel", ln=True)
        pdf.ln(5)
        
        try:
            img_bytes = base64.b64decode(row['Foto'])
            img = Image.open(io.BytesIO(img_bytes))
            
            # Auto-Orientierung (Handy-Rotation korrigieren)
            img = ImageOps.exif_transpose(img)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                img.save(tmp.name, format="JPEG", quality=85)
                
                # Bildgröße berechnen (Max Breite 180mm)
                w, h = img.size
                aspect = h / w
                pdf_w = 170
                pdf_h = pdf_w * aspect
                
                # Falls Bild zu hoch für Seite, verkleinern
                if pdf_h > 220:
                    pdf_h = 220
                    pdf_w = pdf_h / aspect
                
                # Zentriert platzieren mit Rahmen
                x_pos = (210 - pdf_w) / 2
                pdf.set_draw_color(0, 75, 149)
                pdf.rect(x_pos - 1, pdf.get_y() - 1, pdf_w + 2, pdf_h + 2)
                pdf.image(tmp.name, x_pos, pdf.get_y(), pdf_w, pdf_h)
                
                os.unlink(tmp.name)
        except:
            pdf.cell(0, 10, "[Bild konnte nicht geladen werden]", ln=True)
            
    return pdf.output(dest='S').encode('latin-1')

# --- 6. LOGIN & MAIN ---
if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>🚓 Dienst Login</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        pw = st.text_input("Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw == DIENST_PW:
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

# Sidebar
with st.sidebar:
    st.header("⚙️ Admin")
    if not st.session_state["admin_auth"]:
        if st.text_input("Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.rerun()
    else:
        st.success("Admin aktiv")
        if st.button("Logout"):
            st.session_state["admin_auth"] = False
            st.rerun()

# --- Hauptformular & Archiv ---
st.title("📋 Einsatzbericht")
loc = get_geolocation()
gps_ready = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "-"

def lade_daten():
    spalten = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "Dienstkraft", "GPS", "Kraefte"]
    if os.path.exists(DATEI):
        df = pd.read_csv(DATEI).astype(str)
        for col in spalten:
            if col not in df.columns: df[col] = "-"
        for col in ["Bericht", "Zeugen", "Foto", "Kraefte"]:
            df[col] = df[col].apply(entschluesseln)
        return df[spalten]
    return pd.DataFrame(columns=spalten)

daten = lade_daten()

with st.expander("➕ NEUER BERICHT", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        d = c1.date_input("Datum")
        t1 = c2.time_input("Beginn")
        t2 = c3.time_input("Ende")
        gps = c4.text_input("GPS", value=gps_ready, disabled=True)
        
        o1, o2, o3 = st.columns([3,1,2])
        ort = o1.selectbox("Ort", STRASSEN_AUGSBURG, index=None)
        nr = o2.text_input("Nr.")
        az = o3.text_input("AZ")
        
        st.write("Kräfte:")
        ck1, ck2, ck3 = st.columns(3)
        p_on = ck1.checkbox("Polizei")
        funk = ck1.text_input("Funkstreife") if p_on else ""
        r_on = ck2.checkbox("RTW")
        f_on = ck3.checkbox("Feuerwehr")
        
        k_list = []
        if p_on: k_list.append(f"Polizei ({funk})")
        if r_on: k_list.append("RTW")
        if f_on: k_list.append("Feuerwehr")
        k_str = ", ".join(k_list) if k_list else "Keine"
        
        bericht = st.text_area("Bericht")
        z = st.text_input("Zeugen")
        f = st.file_uploader("Foto")
        
        if st.form_submit_button("Speichern"):
            f_b = "-"
            if f:
                img = Image.open(f)
                img = ImageOps.exif_transpose(img) # WICHTIG: Korrigiert Handy-Rotation
                img.thumbnail((1000, 1000))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=75)
                f_b = base64.b64encode(buf.getvalue()).decode()
            
            new_row = [str(d), t1.strftime("%H:%M"), t2.strftime("%H:%M"), str(ort), nr, verschluesseln(z), 
                       verschluesseln(bericht), az, verschluesseln(f_b), "KOD", gps_ready, verschluesseln(k_str)]
            pd.concat([pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=daten.columns), 
                       pd.DataFrame([new_row], columns=daten.columns)]).to_csv(DATEI, index=False)
            st.rerun()

st.divider()
for i, row in daten.iloc[::-1].iterrows():
    with st.expander(f"{row['Ort']} | {row['Datum']}"):
        st.write(f"Zeit: {row['Beginn']}-{row['Ende']} | Kräfte: {row['Kraefte']}")
        st.info(row['Bericht'])
        if row['Foto'] != "-": st.image(base64.b64decode(row['Foto']), width=300)
        if st.session_state["admin_auth"]:
            st.download_button("PDF Export", data=erstelle_pdf(row), file_name=f"{row['AZ']}.pdf", key=f"p{i}")
