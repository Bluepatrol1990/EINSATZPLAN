import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64
import tempfile
from PIL import Image
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation 
from fpdf import FPDF 

# --- 1. KONFIGURATION & SICHERHEIT ---
DIENST_PW = "1990" 
# Nutze Secrets falls vorhanden, sonst Fallback
ADMIN_PW = st.secrets.get("admin_password", "admin789")
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")

# Hinterlegte Empfänger (Kevin Woelki) - Gemäß Anweisung hinzugefügt
EMAIL_RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

DATEI = "zentral_archiv_secure.csv"
LOGO_PFAD = "logo.png" 
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]

st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide") 

# --- 2. UI SCHUTZ & STYLING (Verbessert) ---
st.markdown("""
    <style>
    /* Versteckt Streamlit Branding & 'Manage App' */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    
    /* Login Container Design */
    .login-box {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 50px;
    }
    
    /* Archiv Karten Design */
    .report-card { 
        background-color: #ffffff; 
        border-radius: 10px; 
        padding: 20px; 
        border-left: 10px solid #004b95; 
        margin-bottom: 15px; 
        color: #333333;
        border: 1px solid #dddddd;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True) 

# --- 3. SESSION STATE INITIALISIERUNG ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False 

# --- 4. KRYPTOGRAPHIE ---
def get_cipher():
    # Erzeugt einen validen 32-Byte Base64 Key aus dem MASTER_KEY
    key_64 = base64.urlsafe_b64encode(MASTER_KEY[:32].encode().ljust(32))
    return Fernet(key_64) 

def verschluesseln(text):
    if not text or text == "-": return "-"
    return get_cipher().encrypt(str(text).encode()).decode() 

def entschluesseln(safe_text):
    if not safe_text or safe_text == "-": return "-"
    try: return get_cipher().decrypt(safe_text.encode()).decode()
    except: return "[DATENFEHLER]" 

# --- 5. PDF GENERIERUNG ---
def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    # Header & Logo (Logo muss im Verzeichnis liegen)
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
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(45, 9, f" {label}", border=1, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(145, 9, f" {value}", border=1, ln=True) 

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
    
    # Foto-Anlage falls vorhanden
    akt_foto = entschluesseln(row_data['Foto'])
    if akt_foto != "-":
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Anlage: Beweismittelfoto", ln=True, align='C')
        try:
            img_bytes = base64.b64decode(akt_foto)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name
            pdf.image(tmp_path, x=20, y=40, w=170)
            os.unlink(tmp_path) 
        except: pass 

    return pdf.output(dest="S").encode("latin-1") 

# --- 6. DIENST-LOGIN (HAUPTSEITE) ---
if not st.session_state["auth"]:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://www.augsburg.de/typo3conf/ext/mag_site/Resources/Public/Images/Logo/augsburg_logo.svg", width=180)
        st.subheader("🔒 KOD Sicherheitsbereich")
        pw_input = st.text_input("Dienstpasswort", type="password", label_visibility="collapsed", placeholder="Passwort eingeben...")
        if st.button("Anmelden", use_container_width=True) or (pw_input == DIENST_PW and pw_input != ""):
            if pw_input == DIENST_PW:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Ungültiges Kennwort.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop() 

# --- 7. SIDEBAR (ADMIN-LOGIN & INFO) ---
with st.sidebar:
    st.image("https://www.augsburg.de/typo3conf/ext/mag_site/Resources/Public/Images/Logo/augsburg_logo.svg", width=150)
    st.title("🛡️ Admin-Bereich")
    
    if not st.session_state["admin_auth"]:
        admin_pw_input = st.text_input("Admin-Passwort", type="password")
        if st.button("Admin Login"):
            if admin_pw_input == ADMIN_PW:
                st.session_state["admin_auth"] = True
                st.success("Erfolgreich als Admin angemeldet.")
                st.rerun()
            else:
                st.error("Falsches Passwort.")
    else:
        st.success("✅ Admin-Modus aktiv")
        if st.button("Logout Admin"):
            st.session_state["admin_auth"] = False
            st.rerun()
    
    st.divider()
    st.info(f"📧 **Berichts-Empfänger:**\n{EMAIL_RECIPIENTS[0]}\n{EMAIL_RECIPIENTS[1]}")

# --- 8. BERICHTS-EINGABE ---
st.title("📋 Einsatzbericht Erfassung")

with st.expander("📝 NEUEN BERICHT ANLEGEN", expanded=True):
    loc = get_geolocation()
    gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "📍 GPS nicht erfasst"
    
    c1, c2, c3, c4 = st.columns(4)
    datum = c1.date_input("📅 Datum")
    beginn = c2.time_input("🕒 Beginn")
    ende = c3.time_input("🕒 Ende")
    az_val = c4.text_input("📂 AZ (Aktenzeichen)")
    
    o1, o2 = st.columns([3, 1])
    ort_val = o1.text_input("🗺️ Einsatzort")
    hnr_val = o2.text_input("Hausnr.") 

    with st.form("content_form"):
        st.subheader("📄 Berichtsinhalt")
        inhalt = st.text_area("✍️ Sachverhalt", height=150)
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        bild = st.file_uploader("📸 Foto hochladen", type=["jpg", "png", "jpeg"]) 

        if st.form_submit_button("✅ BERICHT SPEICHERN"):
            # (Speicherlogik wie gehabt)
            b64_img = "-"
            if bild:
                img = Image.open(bild).convert("RGB")
                img.thumbnail((1000, 1000))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=75)
                b64_img = base64.b64encode(buf.getvalue()).decode() 

            new_data = {
                "Datum": str(datum), "Beginn": beginn.strftime("%H:%M"), "Ende": ende.strftime("%H:%M"),
                "Ort": ort_val, "Hausnummer": hnr_val, "Zeugen": verschluesseln(beteiligte),
                "Bericht": verschluesseln(inhalt), "AZ": az_val, "Foto": verschluesseln(b64_img),
                "GPS": gps_val, "Kraefte": verschluesseln("KOD Augsburg")
            }
            
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success("✅ Bericht erfolgreich archiviert.")
            st.rerun() 

# --- 9. ARCHIV ---
st.divider()
st.header("📂 Einsatzarchiv")
if os.path.exists(DATEI):
    df_archive = pd.read_csv(DATEI).astype(str)
    suche = st.text_input("🔍 Suche nach AZ oder Einsatzort...")
    
    if suche:
        df_archive = df_archive[df_archive['AZ'].str.contains(suche, case=False) | df_archive['Ort'].str.contains(suche, case=False)] 

    for idx, row in df_archive.iloc[::-1].iterrows():
        st.markdown(f"""
            <div class="report-card">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-size: 1.2em;">📂 <strong>AZ: {row['AZ']}</strong></span>
                    <span>📅 {row['Datum']}</span>
                </div>
                <div style="font-size: 0.9em; margin-top: 5px;">📍 {row['Ort']} {row['Hausnummer']} | 🕒 {row['Beginn']} - {row['Ende']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        c_det, c_admin_only = st.columns([3, 1])
        with c_det:
            with st.expander("👁️ Details anzeigen"):
                st.write(f"**Bericht:** {entschluesseln(row['Bericht'])}")
                st.write(f"**Beteiligte:** {entschluesseln(row['Zeugen'])}")
        
        with c_admin_only:
            if st.session_state["admin_auth"]:
                pdf_bytes = create_official_pdf(row)
                st.download_button("📄 PDF", pdf_bytes, f"Bericht_{row['AZ']}.pdf", "application/pdf", key=f"pdf_{idx}")
                if st.button("🗑️ Löschen", key=f"del_{idx}"):
                    # Löschfunktion
                    df_temp = pd.read_csv(DATEI)
                    df_temp.drop(idx).to_csv(DATEI, index=False)
                    st.rerun()
            else:
                st.info("🔒 Admin-Rechte nötig")
