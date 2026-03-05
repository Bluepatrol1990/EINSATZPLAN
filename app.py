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
from fpdf import FPDF # Benötigt: pip install fpdf

# --- 1. GLOBALE VARIABLEN ---
DATEI = "zentral_archiv_secure.csv"
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
ADMIN_PW = "admin789"
DIENST_PW = st.secrets.get("dienst_password", "1234")
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")

# --- 2. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide") 

st.markdown("""
    <style>
    .report-card { 
        background-color: #f0f2f6; 
        border-radius: 8px; 
        padding: 15px; 
        border-left: 8px solid #004b95; 
        margin-bottom: 10px; 
        color: #1e1e1e;
        border: 1px solid #d1d1d1;
    }
    </style>
    """, unsafe_allow_html=True) 

# --- 3. SICHERHEIT & VERSCHLÜSSELUNG ---
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

# --- 4. BEHÖRDEN-PDF LOGIK ---
def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header: Behörden-Kopf
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "STADT AUGSBURG", ln=True, align='L')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 6, "Ordnungsamt", ln=True, align='L')
    pdf.cell(0, 6, "Kommunaler Ordnungsdienst (KOD)", ln=True, align='L')
    
    pdf.line(10, 32, 200, 32)
    pdf.ln(15)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"AMTLICHER EINSATZBERICHT - AZ: {row_data['AZ']}", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, f"Zuständig: Kevin.woelki@augsburg.de | kevinworlki@outlook.de", ln=True)
    pdf.ln(2)

    # Daten-Matrix
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(230, 230, 230)
    
    def add_row(label, value):
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 8, f" {label}", border=1, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(145, 8, f" {value}", border=1, ln=True)

    add_row("Datum", row_data['Datum'])
    add_row("Einsatzzeit", f"{row_data['Beginn']} bis {row_data['Ende']} Uhr")
    add_row("Einsatzort", f"{row_data['Ort']} {row_data['Hausnummer']}")
    add_row("Kräfte", entschluesseln(row_data['Kraefte']))
    add_row("GPS", row_data['GPS'])
    
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Sachverhalt:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Bericht']), border='T')
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Beteiligte / Zeugen:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Zeugen']), border='T')

    # Foto-Anlage
    akt_foto = entschluesseln(row_data['Foto'])
    if akt_foto != "-":
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Anlage: Beweisfotos", ln=True, align='C')
        pdf.ln(10)
        try:
            img_bytes = base64.b64decode(akt_foto)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name
            pdf.image(tmp_path, x=20, y=40, w=170)
            os.unlink(tmp_path) 
        except:
            pdf.cell(0, 10, "[Bildfehler]", ln=True)

    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Erstellt am {datetime.now().strftime('%d.%m.%Y')} - KOD Augsburg", align='C')

    return pdf.output(dest="S").encode("latin-1")

# --- 5. HAUPTSEITE ---
if not st.session_state["auth"]:
    st.title("🚓 KOD Augsburg - Login")
    pw_input = st.text_input("Dienstpasswort", type="password")
    if pw_input == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

st.title("📋 Einsatzbericht")

# --- ERSTELLUNG ---
with st.expander("➕ NEUEN BERICHT ANLEGEN", expanded=True):
    loc = get_geolocation()
    gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Nicht erfasst"
    
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        pol_check = st.checkbox("🚔 Polizei")
        rtw_check = st.checkbox("🚑 Rettungsdienst")
    with col_k2:
        streife = st.text_input("Funkstreife") if pol_check else ""

    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("Datum", value=datetime.now())
        beginn = c2.time_input("Beginn")
        ende = c3.time_input("Ende")
        az_val = c4.text_input("Aktenzeichen")
        
        o1, o2 = st.columns([3, 1])
        ort_val = o1.selectbox("Einsatzort", ["Königsplatz", "Maximilianstraße", "Rathausplatz", "Oberhauser Bahnhof", "Schillstr."])
        hnr_val = o2.text_input("Nr.")

        inhalt = st.text_area("Sachverhalt", height=150)
        beteiligte = st.text_input("Beteiligte / Zeugen")
        bild = st.file_uploader("Beweisfoto", type=["jpg", "png", "jpeg"])

        if st.form_submit_button("SPEICHERN"):
            k_list = ["KOD"]
            if pol_check: k_list.append(f"Polizei ({streife})")
            if rtw_check: k_list.append("Rettungsdienst")
            
            b64_img = "-"
            if bild:
                img = Image.open(bild).convert("RGB")
                img.thumbnail((1200, 1200))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                b64_img = base64.b64encode(buf.getvalue()).decode()

            new_entry = {
                "Datum": str(datum), "Beginn": beginn.strftime("%H:%M"), "Ende": ende.strftime("%H:%M"),
                "Ort": ort_val, "Hausnummer": hnr_val, "Zeugen": verschluesseln(beteiligte),
                "Bericht": verschluesseln(inhalt), "AZ": az_val, "Foto": verschluesseln(b64_img),
                "GPS": gps_val, "Kraefte": verschluesseln(", ".join(k_list))
            }
            
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success("Bericht gespeichert!")
            st.rerun()

# --- ARCHIV ---
st.divider()
st.header("📂 Archiv")

if os.path.exists(DATEI):
    df_archive = pd.read_csv(DATEI).astype(str)
    for idx, row in df_archive.iloc[::-1].iterrows():
        with st.container():
            st.markdown(f"""
                <div class="report-card">
                    <strong>AZ: {row['AZ']}</strong> | 📅 {row['Datum']} | 📍 {row['Ort']} {row['Hausnummer']}<br>
                    <small>👮 Kräfte: {entschluesseln(row['Kraefte'])}</small>
                </div>
            """, unsafe_allow_html=True)
            
            c_det, c_pdf, c_adm = st.columns([3, 1, 1])
            with c_det:
                with st.expander("Details"):
                    st.write(f"**Sachverhalt:**\n{entschluesseln(row['Bericht'])}")
                    img_data = entschluesseln(row['Foto'])
                    if img_data != "-": st.image(base64.b64decode(img_data), width=300)
            
            with c_pdf:
                # PDF EXPORT FÜR JEDEN NUTZER
                pdf_file = create_official_pdf(row)
                st.download_button("📄 PDF", pdf_file, f"Bericht_{row['AZ']}.pdf", "application/pdf", key=f"pdf_{idx}")
            
            with c_adm:
                # NUR ADMIN DARF LÖSCHEN
                if st.session_state["admin_auth"]:
                    if st.button("🗑️", key=f"del_{idx}"):
                        df_archive.drop(idx).to_csv(DATEI, index=False)
                        st.rerun()

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.title("Verwaltung")
    if st.checkbox("🔑 Admin"):
        if st.text_input("PW", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            if st.button("🚨 ARCHIV LÖSCHEN"):
                if os.path.exists(DATEI): os.remove(DATEI)
                st.rerun()
        else: st.session_state["admin_auth"] = False
