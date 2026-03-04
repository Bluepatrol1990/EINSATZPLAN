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

# ... (Konfiguration & Empfänger)
# region INITIALISIERUNG
DATEI = "zentral_archiv_secure.csv"
LOGO_PFAD = "logo.png" 
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
ADMIN_PW = "admin789"
DIENST_PW = "1990" 
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]
# endregion

st.set_page_config(page_title="KOD Augsburg", page_icon="🚓", layout="wide") 

# --- STYLING ---
st.markdown("""
    <style>
    .report-card { background-color: #ffffff; border-radius: 10px; padding: 20px; border-left: 10px solid #004b95; margin-bottom: 15px; border: 1px solid #dddddd; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .metric-box { background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #eee; }
    .login-box { text-align: center; padding: 30px; border: 2px solid #004b95; border-radius: 15px; background-color: #f8f9fa; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True) 

# --- HILFSFUNKTIONEN ---
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

def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_PFAD): pdf.image(LOGO_PFAD, x=160, y=10, w=35)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "STADT AUGSBURG", ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 7, "ORDNUNGSAMT", ln=True)
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "AMTLICHER EINSATZBERICHT", ln=True, align='C')
    # ... (Rest der PDF Logik identisch)
    return pdf.output(dest="S").encode("latin-1")

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False 

if not st.session_state["auth"]:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown('<div class="login-box"><h1>🔑</h1><h2>Sicherheitsbereich</h2><hr></div>', unsafe_allow_html=True)
        pwd_input = st.text_input("Dienstpasswort", type="password", label_visibility="collapsed", placeholder="Passwort...")
        if pwd_input == DIENST_PW:
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- HAUPTBEREICH ---
st.title("📋 Einsatzbericht")

with st.expander("📝 NEUEN BERICHT ANLEGEN", expanded=True):
    loc = get_geolocation()
    gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "📍 GPS nicht erfasst"
    
    c1, c2, c3, c4 = st.columns(4)
    datum = c1.date_input("📅 Datum")
    beginn = c2.time_input("🕒 Beginn")
    ende = c3.time_input("🕒 Ende")
    az_val = c4.text_input("📂 AZ")
    
    o1, o2 = st.columns([3, 1])
    ort_val = o1.text_input("🗺️ Einsatzort")
    hnr_val = o2.text_input("Hausnr.")

    st.subheader("👮 Beteiligte Behörden")
    k_col1, k_col2, k_col3 = st.columns(3)
    with k_col1:
        pol_check = st.checkbox("🚔 Polizei")
        funkkennung = st.text_input("🆔 Funkkennung") if pol_check else ""
    rtw_check = k_col2.checkbox("🚑 Rettungsdienst")
    fw_check = k_col3.checkbox("🚒 Feuerwehr")

    with st.form("content_form"):
        inhalt = st.text_area("✍️ Sachverhalt", height=150)
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        bild = st.file_uploader("📸 Foto", type=["jpg", "png", "jpeg"])

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
st.header("📂 Archiv")
if os.path.exists(DATEI):
    df_archive = pd.read_csv(DATEI).astype(str)
    suche = st.text_input("🔍 Suche...")
    if suche:
        df_archive = df_archive[df_archive['AZ'].str.contains(suche, case=False) | df_archive['Ort'].str.contains(suche, case=False)]

    for idx, row in df_archive.iloc[::-1].iterrows():
        st.markdown(f'<div class="report-card"><b>AZ: {row["AZ"]}</b> | 📅 {row["Datum"]} | 📍 {row["Ort"]}</div>', unsafe_allow_html=True)
        
        with st.expander("👁️ Details"):
            st.write(f"**Bericht:** {entschluesseln(row['Bericht'])}")
            if st.session_state["admin_auth"]:
                st.download_button("📄 PDF Export", create_official_pdf(row), f"Bericht_{row['AZ']}.pdf", key=f"pdf_{idx}")
                if st.button("🗑️ Löschen", key=f"del_{idx}"):
                    pd.read_csv(DATEI).drop(idx).to_csv(DATEI, index=False)
                    st.rerun()

# --- ADMIN LOGIN GANZ UNTEN ---
st.markdown("<br><br><br><hr>", unsafe_allow_html=True)
with st.expander("🛡️ Administration"):
    if not st.session_state["admin_auth"]:
        admin_in = st.text_input("Admin-Passwort", type="password")
        if admin_in == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.rerun()
    else:
        st.success("Admin-Modus aktiv")
        if st.button("Logout Admin"):
            st.session_state["admin_auth"] = False
            st.rerun()
