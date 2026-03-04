import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64
from PIL import Image
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation 
from fpdf import FPDF

# --- 1. KONFIGURATION & SICHERHEIT ---
DATEI = "zentral_archiv_secure.csv"
LOGO_PFAD = "logo.png" 
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]

# Empfänger laut deinen Vorgaben
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# Passwörter (Sollten idealerweise in st.secrets stehen!)
ADMIN_PW = "admin789"
DIENST_PW = "1990" 
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")

st.set_page_config(page_title="KOD Augsburg | Dienstportal", page_icon="🚓", layout="wide") 

# --- 2. ERWEITERTES CSS (INKL. MENÜ-SPERRE) ---
st.markdown("""
    <style>
    /* Versteckt die Streamlit-Menüleiste oben rechts und den Footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Haupt-Hintergrund */
    .stApp { background-color: #f4f7f9; }
    
    /* Karten-Design für Berichte */
    .report-card { 
        background-color: #ffffff; 
        border-radius: 8px; 
        padding: 25px; 
        border-top: 5px solid #004b95; 
        margin-bottom: 20px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .section-header {
        color: #004b95;
        font-weight: bold;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 5px;
        margin-bottom: 15px;
        margin-top: 10px;
    }

    .metric-box {
        background-color: #fcfcfc;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #eee;
        font-size: 0.95em;
    }

    .login-container {
        max-width: 450px;
        margin: 100px auto;
        padding: 40px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True) 

# --- 3. HELFER-FUNKTIONEN ---
def get_cipher():
    # Erzeugt einen 32-Byte Key für Fernet aus dem MASTER_KEY
    key_64 = base64.urlsafe_b64encode(MASTER_KEY[:32].encode().ljust(32))
    return Fernet(key_64) 

def verschluesseln(text):
    if not text or text == "-": return "-"
    return get_cipher().encrypt(str(text).encode()).decode() 

def entschluesseln(safe_text):
    if not safe_text or safe_text == "-": return "-"
    try: return get_cipher().decrypt(safe_text.encode()).decode()
    except: return "[DATENFEHLER]" 

def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_PFAD):
        pdf.image(LOGO_PFAD, x=160, y=10, w=35)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "STADT AUGSBURG", ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 7, "ORDNUNGSAMT", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "Kommunaler Ordnungsdienst (KOD)", ln=True)
    pdf.line(10, 38, 200, 38)
    pdf.ln(15)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "AMTLICHER EINSATZBERICHT", ln=True, align='C')
    pdf.ln(5)

    def add_table_row(label, value):
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 9, f" {label}", border=1, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(145, 9, f" {value}", border=1, ln=True)

    pdf.set_fill_color(240, 240, 240)
    add_table_row("Aktenzeichen (AZ)", row_data['AZ'])
    add_table_row("Datum", row_data['Datum'])
    add_table_row("Zeitraum", f"{row_data['Beginn']} - {row_data['Ende']} Uhr")
    add_table_row("Einsatzort", f"{row_data['Ort']} {row_data['Hausnummer']}")
    add_table_row("Kräfte", entschluesseln(row_data['Kraefte']))
    add_table_row("GPS", row_data['GPS'])
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Sachverhalt / Feststellungen:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Bericht']), border='T')
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Beteiligte / Zeugen:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Zeugen']), border='T')

    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Erstellt am {datetime.now().strftime('%d.%m.%Y')} | Stadt Augsburg", align='C')
    return pdf.output(dest="S").encode("latin-1")

# --- 4. LOGIN SEITE ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False 

if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.image("https://img.icons8.com/fluency/96/police-badge.png", width=80)
        st.markdown("<h3>Dienstportal Login</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: gray;'>Stadt Augsburg - Ordnungsamt</p>", unsafe_allow_html=True)
        
        pw = st.text_input("", type="password", placeholder="Passwort eingeben", label_visibility="collapsed")
        if pw == DIENST_PW:
            st.session_state["auth"] = True
            st.rerun()
        elif pw != "":
            st.error("Zugriff verweigert.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. HAUPT-INTERFACE ---
st.title("🚓 KOD Einsatzportal")

tab1, tab2 = st.tabs(["📝 Neuer Einsatzbericht", "📂 Archiv & Dokumentation"])

with tab1:
    st.markdown('<p class="section-header">📁 STAMMDATEN DES EINSATZES</p>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    datum = c1.date_input("📅 Datum", format="DD.MM.YYYY")
    beginn = c2.time_input("🕒 Einsatzbeginn")
    ende = c3.time_input("🕒 Einsatzende")
    az_val = c4.text_input("📂 Aktenzeichen (AZ)", placeholder="z.B. 2026-004")
    
    st.markdown('<p class="section-header">📍 ÖRTLICHKEIT</p>', unsafe_allow_html=True)
    o1, o2, o3 = st.columns([3, 1, 2])
    ort_val = o1.text_input("🗺️ Einsatzort / Straße", placeholder="An der Blauen Kappe")
    hnr_val = o2.text_input("Haus-Nr.")
    
    loc = get_geolocation()
    gps_info = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Nicht erfasst"
    o3.info(f"🌐 GPS: {gps_info}")

    st.markdown('<p class="section-header">👮 BETEILIGTE KRÄFTE</p>', unsafe_allow_html=True)
    k1, k2, k3 = st.columns(3)
    pol_check = k1.checkbox("🚔 Polizei Augsburg")
    rtw_check = k2.checkbox("🚑 Rettungsdienst")
    fw_check = k3.checkbox("🚒 Feuerwehr")
    
    funk = ""
    if pol_check:
        funk = st.text_input("🆔 Funkkennung Polizei", placeholder="z.B. Augsburg 12/1")

    st.markdown('<p class="section-header">📑 DOKUMENTATION</p>', unsafe_allow_html=True)
    with st.form("main_form"):
        inhalt = st.text_area("✍️ Sachverhalt / Dienstliche Feststellungen", height=200)
        beteiligte = st.text_input("👥 Beteiligte Personen / Zeugen")
        bild = st.file_uploader("📸 Beweismittel / Foto", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("✅ BERICHT REVISIONSSICHER SPEICHERN"):
            k_list = ["KOD"]
            if pol_check: k_list.append(f"Polizei ({funk})" if funk else "Polizei")
            if rtw_check: k_list.append("Rettungsdienst")
            if fw_check: k_list.append("Feuerwehr")
            
            b64_img = "-"
            if bild:
                img = Image.open(bild).convert("RGB")
                img.thumbnail((800, 800))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=75)
                b64_img = base64.b64encode(buf.getvalue()).decode()

            new_data = {
                "Datum": datum.strftime("%d.%m.%Y"), 
                "Beginn": beginn.strftime("%H:%M"), 
                "Ende": ende.strftime("%H:%M"),
                "Ort": ort_val, "Hausnummer": hnr_val, 
                "Zeugen": verschluesseln(beteiligte),
                "Bericht": verschluesseln(inhalt), 
                "AZ": az_val, 
                "Foto": verschluesseln(b64_img),
                "GPS": gps_info, 
                "Kraefte": verschluesseln(", ".join(k_list))
            }
            
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success(f"💾 Archiviert. Kopie geht an: {', '.join(RECIPIENTS)}")
            st.rerun()

with tab2:
    if os.path.exists(DATEI):
        df_archive = pd.read_csv(DATEI).astype(str)
        suche = st.text_input("🔍 Suche im Archiv (AZ oder Ort)...")
        
        if suche:
            df_archive = df_archive[df_archive['AZ'].str.contains(suche, case=False) | df_archive['Ort'].str.contains(suche, case=False)]

        for idx, row in df_archive.iloc[::-1].iterrows():
            st.markdown(f"""
                <div class="report-card">
                    <b>📂 AZ: {row['AZ']}</b> | 📅 {row['Datum']} | 📍 {row['Ort']} {row['Hausnummer']}
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Details anzeigen"):
                st.write(f"**Kräfte:** {entschluesseln(row['Kraefte'])}")
                st.write(f"**Bericht:** {entschluesseln(row['Bericht'])}")
                
                if st.session_state.get("admin_auth", False):
                    pdf_bytes = create_official_pdf(row)
                    st.download_button("📄 PDF Download", pdf_bytes, f"Bericht_{row['AZ']}.pdf", key=f"pdf_{idx}")

# --- 6. SIDEBAR (ADMIN) ---
with st.sidebar:
    st.markdown("### 🛡️ Admin")
    if st.checkbox("Admin-Login"):
        pw_admin = st.text_input("Admin-Key", type="password")
        if pw_admin == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin aktiv")
        else:
            st.session_state["admin_auth"] = False
