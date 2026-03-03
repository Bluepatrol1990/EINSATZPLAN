import streamlit as st
import pandas as pd
import os
import io
import base64
import tempfile
import urllib.parse
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageOps
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation

# --- 1. SEITEN-KONFIGURATION & DESIGN ---
st.set_page_config(page_title="KOD Augsburg Pro", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1 { color: #0054a6; border-bottom: 3px solid #0054a6; padding-bottom: 10px; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    /* Design für den E-Mail-Button */
    .mail-btn {
        background-color: #0054a6;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False

# --- 3. SICHERHEIT & SECRETS ---
# Empfänger aus deinen Vorgaben
RECIPIENTS = "Kevin.woelki@augsburg.de; kevinworlki@outlook.de"

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

# --- 4. STRASSENLISTE ---
STRASSEN_AUGSBURG = sorted([
    "Schillstr./ Dr. Schmelzingstr. - Baustellenbereich", "Hexengässchen", "Königsplatz", "Rathausplatz",
    "Maximilianstraße", "Bahnhofstraße", "Hofgarten", "Kuhsee", "Autobahnsee", "Siebentischwald",
    "Gögginger Straße", "Ulmer Straße", "Donauwörther Straße", "Haunstetter Straße", "Moritzplatz",
    "Jakoberstraße", "Elias-Holl-Platz", "Holbeinstraße", "Klinkerberg", "Predigerberg",
    "Zugspitzstraße 104 (Neuer Ostfriedhof)", "Helmut-Haller-Platz", "Oberhauser Bahnhof",
    # ... (Hier die restlichen Straßen einfügen, falls nötig)
])

# --- 5. AMTKLICHER PDF GENERATOR ---
class BehoerdenPDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 30)
        else:
            self.set_fill_color(0, 84, 166)
            self.rect(10, 8, 25, 30, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font("Arial", "B", 8)
            self.set_xy(10, 15)
            self.multi_cell(25, 4, "STADT\nAUGSBURG", align="C")

        self.set_font("Arial", "B", 16); self.set_text_color(0, 84, 166); self.set_x(45)
        self.cell(0, 10, "STADT AUGSBURG", ln=True)
        self.set_font("Arial", "B", 10); self.set_text_color(100, 100, 100); self.set_x(45)
        self.cell(0, 7, "Kommunaler Ordnungsdienst (KOD)", ln=True)
        self.ln(10); self.line(10, 42, 200, 42)

    def footer(self):
        self.set_y(-15); self.set_font("Arial", "I", 8); self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Einsatzprotokoll KOD Augsburg | Seite {self.page_no()}/{{nb}}", align="C")

def erstelle_pdf(row):
    pdf = BehoerdenPDF(); pdf.alias_nb_pages(); pdf.add_page()
    pdf.ln(5); pdf.set_font("Arial", "B", 14); pdf.cell(0, 10, f"Einsatzprotokoll | AZ: {row['AZ']}", ln=True); pdf.ln(5)
    pdf.set_font("Arial", "B", 10); pdf.set_fill_color(245, 245, 245)
    
    fields = [
        ("Datum / Zeit:", f"{row['Datum']} | {row['Beginn']} - {row['Ende']}"), 
        ("Einsatzort:", f"{row['Ort']} {row['Hausnummer']}"), 
        ("Kräfte:", row['Kraefte']), 
        ("Beteiligte:", row['Zeugen']), 
        ("GPS:", row['GPS'])
    ]
    
    for label, val in fields:
        pdf.set_font("Arial", "B", 10); pdf.cell(45, 7, f" {label}", fill=True)
        pdf.set_font("Arial", "", 10); pdf.cell(0, 7, f" {val}", ln=True, fill=True)
    
    pdf.ln(10); pdf.set_font("Arial", "B", 12); pdf.cell(0, 10, "Sachverhalt:", ln=True)
    pdf.set_font("Arial", "", 11); pdf.multi_cell(0, 6, row['Bericht'])
    
    if row['Foto'] != "-":
        pdf.add_page()
        try:
            img_data = base64.b64decode(row['Foto'])
            img = Image.open(io.BytesIO(img_data))
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                img.save(tmp.name, format="JPEG"); pdf.image(tmp.name, 10, 40, 190)
                os.unlink(tmp.name)
        except: pdf.cell(0, 10, "[Bildfehler]", ln=True)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 6. UI LOGIK ---
if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>🚓 KOD Dienst-Login</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        pw = st.text_input("Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw == DIENST_PW: st.session_state["auth"] = True; st.rerun()
    st.stop()

with st.sidebar:
    st.header("⚙️ Verwaltung")
    if not st.session_state["admin_auth"]:
        if st.text_input("Admin-Passwort", type="password") == ADMIN_PW: 
            st.session_state["admin_auth"] = True; st.rerun()
    else:
        st.success("Admin-Modus aktiv")
        if st.button("Logout"): st.session_state["admin_auth"] = False; st.rerun()

st.title("📋 Einsatzbericht")
loc = get_geolocation()
gps_ready = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "-"
DATEI = "zentral_archiv_secure.csv"

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

# --- FORMULAR ---
with st.expander("➕ NEUEN BERICHT ERSTELLEN", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        d = c1.date_input("Datum")
        t1 = c2.time_input("Beginn")
        t2 = c3.time_input("Ende")
        az = c4.text_input("Aktenzeichen (AZ)")
        
        o1, o2 = st.columns([3,1])
        ort = o1.selectbox("Straße / Ort", STRASSEN_AUGSBURG, index=None, placeholder="Straße auswählen...")
        nr = o2.text_input("Hausnummer")
        
        st.write("Kräfte / Beteiligte:")
        ck1, ck2, ck3 = st.columns(3)
        p_on = ck1.checkbox("Polizei")
        funk = ck1.text_input("Funkrufnamen") if p_on else ""
        r_on = ck2.checkbox("RTW / Sanitäter")
        f_on = ck3.checkbox("Feuerwehr")
        
        k_list = ["KOD"]
        if p_on: k_list.append(f"Polizei ({funk})")
        if r_on: k_list.append("Rettungsdienst")
        if f_on: k_list.append("Feuerwehr")
        
        bericht = st.text_area("Sachverhalt / Feststellungen")
        zeugen = st.text_input("Beteiligte Personen / Zeugen")
        foto_file = st.camera_input("Beweisfoto")
        
        if st.form_submit_button("Bericht im Archiv speichern"):
            f_b = "-"
            if foto_file:
                img = Image.open(foto_file)
                img.thumbnail((800, 800))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=70)
                f_b = base64.b64encode(buf.getvalue()).decode()
            
            new_row = [
                str(d), t1.strftime("%H:%M"), t2.strftime("%H:%M"), str(ort), nr, 
                verschluesseln(zeugen), verschluesseln(bericht), az, 
                verschluesseln(f_b), "KOD-Einsatz", gps_ready, verschluesseln(", ".join(k_list))
            ]
            
            df_save = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=daten.columns)
            pd.concat([df_save, pd.DataFrame([new_row], columns=daten.columns)]).to_csv(DATEI, index=False)
            st.success("Bericht erfolgreich gespeichert!")
            st.rerun()

# --- ARCHIV-LISTE ---
st.divider()
st.subheader("📂 Archivierte Berichte")

for i, row in daten.iloc[::-1].iterrows():
    with st.expander(f"📍 {row['Ort']} | {row['Datum']} (AZ: {row['AZ']})"):
        c_info, c_foto = st.columns([2,1])
        with c_info:
            st.write(f"**Zeit:** {row['Beginn']} - {row['Ende']}")
            st.write(f"**Kräfte:** {row['Kraefte']}")
            st.write(f"**Zeugen:** {row['Zeugen']}")
            st.info(f"**Bericht:**\n\n{row['Bericht']}")
            st.caption(f"GPS: {row['GPS']}")
        
        with c_foto:
            if row['Foto'] != "-":
                st.image(base64.b64decode(row['Foto']), use_container_width=True)
        
        # Versand & Export Sektion
        st.divider()
        col_pdf, col_mail = st.columns(2)
        
        with col_pdf:
            if st.session_state["admin_auth"]:
                st.download_button(
                    "📄 Amtliches PDF generieren", 
                    data=erstelle_pdf(row), 
                    file_name=f"KOD_Bericht_{row['AZ']}.pdf", 
                    key=f"pdf_{i}"
                )
        
        with col_mail:
            # E-Mail Link generieren
            subject = f"KOD Einsatzbericht: {row['Ort']} (AZ: {row['AZ']})"
            mail_body = (
                f"Offizielles Einsatzprotokoll KOD Augsburg\n"
                f"----------------------------------------\n"
                f"Aktenzeichen: {row['AZ']}\n"
                f"Ort: {row['Ort']} {row['Hausnummer']}\n"
                f"Zeit: {row['Datum']} ({row['Beginn']}-{row['Ende']})\n"
                f"Kräfte: {row['Kraefte']}\n\n"
                f"SACHVERHALT:\n{row['Bericht']}\n\n"
                f"GPS-Daten: {row['GPS']}\n"
                f"----------------------------------------\n"
                f"Erstellt via KOD-App Augsburg"
            )
            mailto_url = f"mailto:{RECIPIENTS}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(mail_body)}"
            
            st.markdown(f'<a href="{mailto_url}" class="mail-btn">📧 Bericht an Kevin senden</a>', unsafe_allow_html=True)
