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

# --- 4. DATEN & STRASSEN AUGSBURG ---
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
        # Logo (Falls vorhanden: logo.png im Hauptverzeichnis auf GitHub hochladen)
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 30)
        else:
            self.set_font("Arial", "B", 10)
            self.set_text_color(150, 150, 150)
            self.cell(30, 10, "[STADTWAPPEN]", ln=False)
            self.set_text_color(0, 0, 0) # Reset
        
        # Behördenkopf (Rechts daneben)
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 75, 149) # Augsburger Behördenblau
        self.set_x(50)
        self.cell(0, 10, "STADT AUGSBURG", ln=True)
        
        self.set_font("Arial", "", 12)
        self.set_x(50)
        self.cell(0, 7, "Ordnungsamt", ln=True)
        self.set_x(50)
        self.cell(0, 7, "Kommunaler Ordnungsdienst (KOD)", ln=True)
        
        self.ln(10)
        self.line(10, 45, 200, 45) # Trennlinie

    def footer(self):
        # Seitenzahl und Info unten
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 100, 100)
        titel = "Amtliches Einsatzprotokoll | KOD Augsburg"
        self.cell(0, 10, f"{titel} | Seite {self.page_no()}/{{nb}}", align="C")

def erstelle_pdf(row):
    pdf = BehoerdenPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # --- Betreff-Bereich ---
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Einsatzprotokoll | AZ: {row['AZ']}", ln=True)
    pdf.ln(8)
    
    # --- Fakten-Block (Kompakt) ---
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 240, 240) # Hellgrauer Hintergrund
    
    c_w = 40 # Label Breite
    
    pdf.cell(c_w, 7, " Datum / Zeit:", fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" {row['Datum']} | {row['Beginn']} - {row['Ende']}", ln=True, fill=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(c_w, 7, " Einsatzort:", fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" {row['Ort']} {row['Hausnummer']}", ln=True, fill=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(c_w, 7, " Kräfte vor Ort:", fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" {row['Kraefte']}", ln=True, fill=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(c_w, 7, " Beteiligte / Zeugen:", fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" {row['Zeugen']}", ln=True, fill=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(c_w, 7, " GPS Koordinate:", fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" {row['GPS']}", ln=True, fill=True)
    
    pdf.ln(10)
    
    # --- Sachverhalt ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Sachverhalt / Bericht:", ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, row['Bericht'])
    pdf.ln(10)
    
    # --- FOTO-BEREICH (In Rahmen koprimiert) ---
    if row['Foto'] != "-":
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Fotodokumentation / Beweismittel:", ln=True)
        pdf.ln(5)
        
        try:
            # Bild laden
            img_bytes = base64.b64decode(row['Foto'])
            img = Image.open(io.BytesIO(img_bytes))
            
            # Bild temporär speichern
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                img.save(tmp_file.name, format="JPEG")
                tmp_filename = tmp_file.name
                
            # WICHTIG: Rahmen zeichnen (Amtliches Blau)
            pdf.set_draw_color(0, 75, 149) # Blau
            pdf.set_line_width(1)
            # Rahmenkoordinaten (Etwas größer als das Bild)
            r_x = 12; r_y = pdf.get_y() - 2; r_w = 84; r_h = 64
            pdf.rect(r_x, r_y, r_w, r_h) 
            
            # Bild einfügen (Skaliert in den Rahmen, koprimiert)
            pdf.image(tmp_filename, r_x + 2, r_y + 2, 80, 60)
            os.unlink(tmp_filename) # Temporäre Datei löschen
            
        except Exception as e:
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 10, f"Fehler bei Bilddarstellung: {str(e)}", ln=True)
            pdf.set_text_color(0, 0, 0)
    
    # --- Unterschriften-Feld ---
    pdf.ln(20)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 10, ".....................................................", ln=False)
    pdf.cell(0, 10, ".....................................................", ln=True)
    pdf.set_font("Arial", "", 8)
    pdf.cell(90, 5, "Datum, Unterschrift Dienstkraft", ln=False)
    pdf.cell(0, 5, "Unterschrift Kevin Wölki", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# --- 6. DIENST LOGIN ---
if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>🚓 Dienst Login</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        pw = st.text_input("Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw == DIENST_PW:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Falsches Passwort")
    st.stop()

# --- 7. ADMIN BEREICH (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Verwaltung")
    if not st.session_state["admin_auth"]:
        admin_input = st.text_input("Admin-Passwort", type="password")
        if st.button("Admin Login"):
            if admin_input == ADMIN_PW:
                st.session_state["admin_auth"] = True
                st.success("Admin-Modus aktiv!")
                st.rerun()
            else:
                st.error("Falsches Passwort")
    else:
        st.success("✅ Admin-Status aktiv")
        if st.button("Admin Logout"):
            st.session_state["admin_auth"] = False
            st.rerun()
    st.divider()
    st.info("Empfänger: Kevin.woelki@augsburg.de\nkevinworlki@outlook.de")

# --- 8. HAUPTSEITE ---
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

# --- FORMULAR ---
with st.expander("➕ NEUEN BERICHT SCHREIBEN", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns([1,1,1,1])
        d = c1.date_input("Datum")
        t_start = c2.time_input("Beginn")
        t_ende = c3.time_input("Ende")
        gps_val = c4.text_input("📍 GPS", value=gps_ready, disabled=True)
        
        o1, o2, o3 = st.columns([3,1,2])
        ort_wahl = o1.selectbox("Straße / Ort (Augsburg)", options=STRASSEN_AUGSBURG, index=None, placeholder="Straße wählen...")
        hsnr = o2.text_input("Nr.")
        az = o3.text_input("AZ")

        st.write("**🚓 Eingesetzte Kräfte vor Ort:**")
        ck1, ck2, ck3 = st.columns(3)
        pol_check = ck1.checkbox("Polizei")
        funkstreife = ck1.text_input("Funkstreife", placeholder="z.B. Aux 12/1") if pol_check else ""
        rtw_check = ck2.checkbox("RTW")
        fw_check = ck3.checkbox("Feuerwehr")
        
        kraefte_liste = []
        if pol_check: kraefte_liste.append(f"Polizei ({funkstreife})")
        if rtw_check: kraefte_liste.append("RTW")
        if fw_check: kraefte_liste.append("Feuerwehr")
        kraefte_str = ", ".join(kraefte_liste) if kraefte_liste else "Keine"

        st.divider()
        auswahl = st.selectbox("⚡ Textbaustein", options=list(BAUSTEINE.keys()))
        bericht = st.text_area("Sachverhalt", value=BAUSTEINE[auswahl] if auswahl != "Auswählen..." else "", height=150)
        z = st.text_input("Beteiligte Personen / Zeugen")
        dk = st.text_input("DK Kürzel")
        f = st.file_uploader("📸 Foto hochladen")
        
        if st.form_submit_button("🔒 VERSCHLÜSSELT SPEICHERN"):
            if bericht and ort_wahl:
                f_b = "-"
                if f:
                    img = Image.open(f)
                    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                    # Automatische Komprimierung (thumbnail)
                    img.thumbnail((800, 800))
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=75)
                    f_b = base64.b64encode(buf.getvalue()).decode()
                
                new_row = [str(d), t_start.strftime("%H:%M"), t_ende.strftime("%H:%M"), 
                           str(ort_wahl), hsnr, verschluesseln(z), verschluesseln(bericht), 
                           az, verschluesseln(f_b), dk, gps_ready, verschluesseln(kraefte_str)]
                
                new_df = pd.DataFrame([new_row], columns=daten.columns)
                pd.concat([pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=daten.columns), new_df]).to_csv(DATEI, index=False)
                st.success("Bericht wurde sicher gespeichert!"); st.rerun()

# --- ARCHIV ---
st.divider()
st.subheader("📂 Verschlüsseltes Archiv")
for i, row in daten.iloc[::-1].iterrows():
    with st.expander(f"📍 {row['Ort']} | {row['Datum']} | AZ: {row['AZ']}"):
        c_arch1, c_arch2, c_arch3 = st.columns(3)
        c_arch1.write(f"**⏱ Zeitraum:** {row['Beginn']} - {row['Ende']}")
        c_arch2.write(f"**🚓 Kräfte:** {row['Kraefte']}")
        c_arch3.write(f"**👥 Beteiligte:** {row['Zeugen']}")
        st.info(row['Bericht'])
        if row['Foto'] != "-":
            st.image(base64.b64decode(row['Foto']), width=300)
        
        if st.session_state["admin_auth"]:
            # PDF Export (Amtlicher Look)
            st.download_button("📄 Amtliches PDF", data=erstelle_pdf(row), file_name=f"Bericht_{row['AZ']}.pdf", key=f"pdf_{i}")
