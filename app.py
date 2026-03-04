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

# Empfänger: Kevin.woelki@augsburg.de, kevinworlki@outlook.de

st.set_page_config(page_title="KOD Augsburg", page_icon="🚓", layout="wide") 

# --- 2. ULTIMATIVES KONTRAST-DESIGN (HARDCORE BLACK & WHITE) ---
st.markdown("""
    <style>
    /* 1. Hintergrund absolut Schwarz */
    .stApp {
        background-color: #000000 !important;
    }

    /* 2. Alle Texte absolut Reinweiß */
    h1, h2, h3, h4, h5, h6, p, span, label, div, .stMarkdown, .stCheckbox {
        color: #ffffff !important;
        font-family: 'Arial', sans-serif !important;
    }

    /* 3. Eingabefelder: Schwarzer Grund, Weißer Rahmen (Kontrast!) */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important; /* Dickerer weißer Rand */
        border-radius: 0px !important;
    }

    /* Fix für Eingabetext (verhindert Browser-Grau) */
    input { -webkit-text-fill-color: #ffffff !important; }

    /* 4. Buttons: Weiß mit schwarzer Schrift (Invertiert für Action) */
    .stButton>button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #ffffff !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        width: 100%;
        border-radius: 0px !important;
    }
    
    .stButton>button:hover {
        background-color: #cccccc !important;
        color: #000000 !important;
    }

    /* 5. Archiv-Karten: Weißer Rahmen, kein Schnickschnack */
    .report-card { 
        background-color: #000000; 
        border: 2px solid #ffffff; 
        padding: 20px; 
        margin-bottom: 20px; 
    }

    /* 6. Expander / Menüs */
    .streamlit-expanderHeader {
        background-color: #000000 !important;
        border: 1px solid #ffffff !important;
        border-radius: 0px !important;
    }

    /* 7. Radio & Checkbox Fix */
    div[data-baseweb="checkbox"] div {
        border-color: #ffffff !important;
    }

    /* Verstecke Streamlit-Elemente */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
    """, unsafe_allow_html=True) 

# --- 3. SICHERHEITSKERN ---
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

# --- 4. PDF LOGIK ---
def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "STADT AUGSBURG - ORDNUNGSAMT", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "Kommunaler Ordnungsdienst (KOD)", ln=True)
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Bericht AZ: {row_data['AZ']}", ln=True)
    
    for key in ["Datum", "Beginn", "Ende", "Ort", "GPS"]:
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(40, 8, f"{key}:", 1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 8, f" {row_data[key]}", 1, ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, "Sachverhalt:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, entschluesseln(row_data['Bericht']), border=1)

    return pdf.output(dest="S").encode("latin-1")

# --- 5. LOGIN ---
if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.write("# 🔐 LOGIN")
        pw = st.text_input("Dienstpasswort", type="password")
        if pw == DIENST_PW:
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- HAUPTAPP ---
st.title("🚓 KOD EINSATZPROTOKOLL")

# GPS Tracking
loc = get_geolocation()
gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Wartet auf GPS..."

with st.container():
    st.subheader("📝 DATENERFASSUNG")
    c1, c2 = st.columns(2)
    az = c1.text_input("Aktenzeichen (AZ)")
    ort = c2.text_input("Einsatzort / Straße")
    
    c3, c4, c5 = st.columns(3)
    dat = c3.date_input("Datum")
    beg = c4.time_input("Beginn")
    end = c5.time_input("Ende")

    pol = st.checkbox("🚔 Polizei vor Ort")
    funk = ""
    if pol: funk = st.text_input("Funkkennung Polizei")

    bericht = st.text_area("Sachverhalt / Maßnahmen", height=200)
    zeugen = st.text_input("Beteiligte Personen / Zeugen")
    foto = st.file_uploader("📸 Beweisfoto", type=["jpg", "png"])

    if st.button("💾 BERICHT FINALISIEREN UND SPEICHERN"):
        b64_img = "-"
        if foto:
            img = Image.open(foto).convert("RGB")
            img.thumbnail((1000, 1000))
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            b64_img = base64.b64encode(buf.getvalue()).decode()

        k_list = ["KOD"]
        if pol: k_list.append(f"Polizei {funk}")

        new_entry = {
            "Datum": str(dat), "Beginn": beg.strftime("%H:%M"), "Ende": end.strftime("%H:%M"),
            "Ort": ort, "Hausnummer": "", "Zeugen": verschluesseln(zeugen),
            "Bericht": verschluesseln(bericht), "AZ": az, "Foto": verschluesseln(b64_img),
            "GPS": gps_val, "Kraefte": verschluesseln(", ".join(k_list))
        }
        
        df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(DATEI, index=False)
        st.success("✅ GESPEICHERT!")
        st.rerun()

# --- ARCHIV ---
st.divider()
st.subheader("📂 ARCHIV")
if os.path.exists(DATEI):
    df_archive = pd.read_csv(DATEI).astype(str)
    for idx, row in df_archive.iloc[::-1].iterrows():
        st.markdown(f"""
            <div class="report-card">
                <h3>AZ: {row['AZ']} | {row['Datum']}</h3>
                <p><b>Ort:</b> {row['Ort']} | <b>Zeit:</b> {row['Beginn']}-{row['Ende']}</p>
                <p><b>Kräfte:</b> {entschluesseln(row['Kraefte'])}</p>
                <p style="font-size: 0.8em; color: #aaa !important;">GPS: {row['GPS']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("DETAILS ÖFFNEN"):
            st.write(f"**Bericht:** {entschluesseln(row['Bericht'])}")
            st.write(f"**Zeugen:** {entschluesseln(row['Zeugen'])}")
            if st.session_state["admin_auth"]:
                pdf = create_official_pdf(row)
                st.download_button("📄 PDF DOWNLOAD", pdf, f"{row['AZ']}.pdf", key=f"dl_{idx}")
                if st.button("🗑 LÖSCHEN", key=f"del_{idx}"):
                    df_archive.drop(idx).to_csv(DATEI, index=False)
                    st.rerun()

# --- ADMIN ---
st.divider()
if not st.session_state["admin_auth"]:
    if st.button("🛠 ADMIN LOGIN"):
        ad_pw = st.text_input("Admin-Passwort", type="password")
        if ad_pw == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.rerun()
else:
    if st.button("🔓 ADMIN LOGOUT"):
        st.session_state["admin_auth"] = False
        st.rerun()
