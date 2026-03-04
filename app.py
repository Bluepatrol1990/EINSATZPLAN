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

# --- 1. GLOBALE VARIABLEN ---
DATEI = "zentral_archiv_secure.csv"
LOGO_PFAD = "logo.png" 
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
ADMIN_PW = "admin789"
DIENST_PW = "1990" 
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")

# Registrierte Empfänger für Berichte:
# 1. Kevin.woelki@augsburg.de
# 2. kevinworlki@outlook.de

st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide") 

# --- 2. OPTIMIERTES HOCH-KONTRAST DESIGN (SCHWARZ/WEISS) ---
st.markdown("""
    <style>
    /* Hintergrund der gesamten App auf Tiefschwarz */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Erzwinge Reinweiß für alle Textelemente */
    h1, h2, h3, h4, h5, h6, p, span, label, li, .stMarkdown {
        color: #ffffff !important;
    }

    /* Spezieller Fix für Streamlit-Labels (Eingabebeschriftungen) */
    .stWidget label p {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* EINGABEFELDER: Dunkelgrau mit weißem Rahmen für Sichtbarkeit */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 5px !important;
    }

    /* Fix für Textfarbe in Eingabefeldern bei Browser-Defaults */
    input {
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Expander / Klappmenüs */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        border: 1px solid #ffffff !important;
        color: #ffffff !important;
    }

    /* Archiv-Karten Design */
    .report-card { 
        background-color: #0c0c0c; 
        border-radius: 10px; 
        padding: 20px; 
        border: 1px solid #ffffff; 
        margin-bottom: 15px; 
    }

    /* Infoboxen innerhalb der Karten */
    .metric-box {
        background-color: #222222;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #444444;
        color: #ffffff !important;
    }

    /* Checkbox-Texte explizit weiß */
    .stCheckbox label span {
        color: #ffffff !important;
    }

    /* Buttons: Blau für gute Sichtbarkeit */
    .stButton>button {
        background-color: #004b95 !important;
        color: white !important;
        border: 1px solid #ffffff !important;
        font-weight: bold;
    }

    /* Header & Menü ausblenden */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True) 

# --- 3. SICHERHEIT ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False 

def get_cipher():
    key_64 = base64.urlsafe_b64encode(MASTER_KEY[:32].encode().ljust(32))
    return Fernet(key_64) 

def verschluesseln(text):
    if not text or text == "-": return "-"
    return get_cipher().encrypt(str(text).encode()).decode() 

def entschluesseln(safe_text):
    if not safe_text or safe_text == "-": return "-"
    try: return get_cipher().decrypt(safe_text.encode()).decode()
    except: return "[DATENFEHLER]" 

# --- 4. PDF GENERIERUNG ---
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

    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Erstellt: {datetime.now().strftime('%d.%m.%Y')} | Augsburg", align='C')
    return pdf.output(dest="S").encode("latin-1")

# --- 5. LOGIN ---
if not st.session_state["auth"]:
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div style="text-align:center; margin-top:100px;"><h1>🔒</h1><h2>Sicherheitsbereich</h2></div>', unsafe_allow_html=True)
        pw_input = st.text_input("Dienstpasswort", type="password", key="login_main")
        if pw_input == DIENST_PW:
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- HAUPTAPP ---
st.title("📋 Einsatzbericht")

with st.expander("📝 NEUEN BERICHT ANLEGEN", expanded=True):
    loc = get_geolocation()
    gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "📍 GPS nicht erfasst"
    
    st.subheader("📍 Einsatzdetails")
    c1, c2, c3, c4 = st.columns(4)
    datum = c1.date_input("📅 Datum")
    beginn = c2.time_input("🕒 Beginn")
    ende = c3.time_input("🕒 Ende")
    az_val = c4.text_input("📂 AZ (Aktenzeichen)")
    
    o1, o2 = st.columns([3, 1])
    ort_val = o1.text_input("🗺️ Einsatzort")
    hnr_val = o2.text_input("Hausnr.")

    st.subheader("👮 Beteiligte Behörden")
    k_col1, k_col2, k_col3 = st.columns(3)
    with k_col1:
        pol_check = st.checkbox("🚔 Polizei")
        funkkennung = ""
        if pol_check:
            funkkennung = st.text_input("🆔 Funkkennung", placeholder="Augsburg 12/1")
    
    rtw_check = k_col2.checkbox("🚑 Rettungsdienst")
    fw_check = k_col3.checkbox("🚒 Feuerwehr")

    with st.form("content_form"):
        st.subheader("📄 Berichtsinhalt")
        inhalt = st.text_area("✍️ Sachverhalt", height=150)
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        bild = st.file_uploader("📸 Foto hochladen", type=["jpg", "png", "jpeg"])

        if st.form_submit_button("✅ BERICHT SPEICHERN"):
            k_list = ["KOD"]
            if pol_check: k_list.append(f"Polizei ({funkkennung})" if funkkennung else "Polizei")
            if rtw_check: k_list.append("Rettungsdienst")
            if fw_check: k_list.append("Feuerwehr")
            
            b64_img = "-"
            if bild:
                img = Image.open(bild).convert("RGB")
                img.thumbnail((1200, 1200))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=80)
                b64_img = base64.b64encode(buf.getvalue()).decode()

            new_data = {
                "Datum": str(datum), "Beginn": beginn.strftime("%H:%M"), "Ende": ende.strftime("%H:%M"),
                "Ort": ort_val, "Hausnummer": hnr_val, "Zeugen": verschluesseln(beteiligte),
                "Bericht": verschluesseln(inhalt), "AZ": az_val, "Foto": verschluesseln(b64_img),
                "GPS": gps_val, "Kraefte": verschluesseln(", ".join(k_list))
            }
            
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success("✅ Bericht gespeichert.")
            st.rerun()

# --- ARCHIV ---
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
                    <span style="color:white;">📂 <strong>AZ: {row['AZ']}</strong></span>
                    <span style="color:white;">📅 {row['Datum']}</span>
                </div>
                <hr style="margin: 10px 0; border-color: #ffffff;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div class="metric-box">📍 <b>Einsatzort:</b> {row['Ort']} {row['Hausnummer']}</div>
                    <div class="metric-box">🕒 <b>Zeit:</b> {row['Beginn']} - {row['Ende']}</div>
                    <div class="metric-box">👮 <b>Kräfte:</b> {entschluesseln(row['Kraefte'])}</div>
                    <div class="metric-box">🌐 <b>GPS:</b> {row['GPS']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        c_det, c_admin_only = st.columns([3, 1])
        with c_det:
            with st.expander("👁️ Details anzeigen"):
                st.info(f"**Sachverhalt:**\n{entschluesseln(row['Bericht'])}")
                st.warning(f"**Beteiligte:** {entschluesseln(row['Zeugen'])}")
                img_data = entschluesseln(row['Foto'])
                if img_data != "-": st.image(base64.b64decode(img_data), width=400)
        
        with c_admin_only:
            if st.session_state.get("admin_auth", False):
                pdf_bytes = create_official_pdf(row)
                st.download_button("📄 PDF Export", pdf_bytes, f"Bericht_{row['AZ']}.pdf", "application/pdf", key=f"pdf_{idx}")
                if st.button("🗑️ Löschen", key=f"del_{idx}"):
                    df_archive.drop(idx).to_csv(DATEI, index=False)
                    st.rerun()
            else:
                st.info("🔒 Admin-Bereich")

# --- ADMIN LOGIN GANZ UNTEN ---
st.write("")
st.divider()
c1, c2, c3 = st.columns([2, 1, 2])
with c2:
    if not st.session_state["admin_auth"]:
        if st.button("🛡️ Admin-Anmeldung"):
            st.session_state["show_admin_login"] = True
        
        if st.session_state.get("show_admin_login", False):
            adm_input = st.text_input("Admin-Passwort", type="password", key="admin_key_final")
            if adm_input == ADMIN_PW:
                st.session_state["admin_auth"] = True
                st.session_state["show_admin_login"] = False
                st.rerun()
    else:
        if st.button("🚪 Admin Logout"):
            st.session_state["admin_auth"] = False
            st.rerun()
