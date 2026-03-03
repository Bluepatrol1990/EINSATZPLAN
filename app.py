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
st.set_page_config(page_title="KOD Augsburg - Behördensystem", page_icon="🚓", layout="wide") 

# CSS für modernes Interface
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
    .stButton>button { width: 100%; }
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
    
    # Horizontale Linie
    pdf.line(10, 32, 200, 32)
    pdf.ln(15)
    
    # Titel & AZ
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"AMTLICHER EINSATZBERICHT - AZ: {row_data['AZ']}", ln=True, align='C')
    pdf.ln(5)
    
    # Empfänger-Info (Interner Vermerk)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 5, f"Zuständige Sachbearbeiter: Kevin.woelki@augsburg.de | kevinworlki@outlook.de", ln=True)
    pdf.ln(2)

    # Daten-Matrix (Tabellarisch)
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
    add_row("Eingesetzte Kräfte", entschluesseln(row_data['Kraefte']))
    add_row("GPS-Referenz", row_data['GPS'])
    
    # Sachverhalt
    pdf.ln(8)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Sachverhalt und Feststellungen:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Bericht']), border='T')
    
    # Beteiligte
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Beteiligte Personen / Zeugen:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Zeugen']), border='T')

    # Foto-Anlage (Falls vorhanden)
    akt_foto = entschluesseln(row_data['Foto'])
    if akt_foto != "-":
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Anlage: Fotodokumentation", ln=True, align='C')
        pdf.ln(10)
        
        try:
            img_bytes = base64.b64decode(akt_foto)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name
            
            # Bild skalieren (max Breite 170mm)
            pdf.image(tmp_path, x=20, y=40, w=170)
            os.unlink(tmp_path) 
        except:
            pdf.cell(0, 10, "[FEHLER: Foto konnte nicht gerendert werden]", ln=True)

    # Fußzeile (Automatisch auf jeder Seite durch FPDF möglich, hier manuell am Ende)
    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Erstellt am {datetime.now().strftime('%d.%m.%Y um %H:%M')} - KOD Augsburg", align='C')

    return pdf.output(dest="S").encode("latin-1")

# --- 5. HAUPTPROGRAMM ---
if not st.session_state["auth"]:
    st.title("🚓 KOD Augsburg - Systemzugang")
    pw_input = st.text_input("Dienstpasswort eingeben", type="password")
    if pw_input == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

# Menüführung
st.title("📋 Einsatzmanagement KOD")

# --- ERSTELLUNG ---
with st.expander("➕ NEUEN BERICHT ANLEGEN", expanded=True):
    loc = get_geolocation()
    gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Manuelle Erfassung"
    
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        pol_check = st.checkbox("🚨 Polizei vor Ort")
        rtw_check = st.checkbox("🚑 Rettungsdienst vor Ort")
    with col_k2:
        streife = st.text_input("Streifename/Nummer") if pol_check else ""

    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("Datum", value=datetime.now())
        beginn = c2.time_input("Beginn")
        ende = c3.time_input("Ende")
        az_val = c4.text_input("Aktenzeichen", placeholder="z.B. 2026-KOD-001")
        
        o1, o2 = st.columns([3, 1])
        ort_val = o1.selectbox("Einsatzort", ["Königsplatz", "Maximilianstraße", "Rathausplatz", "Oberhauser Bahnhof", "Schillstr."])
        hnr_val = o2.text_input("Nr.")

        inhalt = st.text_area("Sachverhalt / Feststellung", height=150)
        beteiligte = st.text_input("Beteiligte / Zeugen / Personalien")
        bild = st.file_uploader("Beweisfoto hochladen", type=["jpg", "png", "jpeg"])

        if st.form_submit_button("BERICHT REVISIONSSICHER SPEICHERN"):
            # Kräfte verarbeiten
            k_list = ["KOD"]
            if pol_check: k_list.append(f"Polizei ({streife})")
            if rtw_check: k_list.append("Rettungsdienst")
            
            # Bild verarbeiten
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
            st.success("Bericht wurde im Archiv verschlüsselt hinterlegt!")
            st.rerun()

# --- ARCHIV ---
st.divider()
st.header("📂 Zentrales Archiv")
suche = st.text_input("🔍 Filter nach Aktenzeichen oder Ort")

if os.path.exists(DATEI):
    df_archive = pd.read_csv(DATEI).astype(str)
    if suche:
        df_archive = df_archive[df_archive['AZ'].str.contains(suche, case=False) | df_archive['Ort'].str.contains(suche, case=False)]

    for idx, row in df_archive.iloc[::-1].iterrows():
        with st.container():
            st.markdown(f"""
                <div class="report-card">
                    <strong>AZ: {row['AZ']}</strong> | 📅 {row['Datum']} | 📍 {row['Ort']} {row['Hausnummer']}<br>
                    <small>👮 Kräfte: {entschluesseln(row['Kraefte'])}</small>
                </div>
            """, unsafe_allow_html=True)
            
            c_det, c_adm = st.columns([4, 1])
            with c_det:
                with st.expander("📝 Details einsehen"):
                    st.write(f"**Sachverhalt:**\n{entschluesseln(row['Bericht'])}")
                    st.write(f"**Zeugen:** {entschluesseln(row['Zeugen'])}")
                    img_data = entschluesseln(row['Foto'])
                    if img_data != "-": st.image(base64.b64decode(img_data), width=400)
            
            with c_adm:
                if st.session_state["admin_auth"]:
                    # PDF EXPORT
                    pdf_file = create_official_pdf(row)
                    st.download_button("📄 PDF Export", pdf_file, f"Bericht_{row['AZ']}.pdf", "application/pdf", key=f"pdf_{idx}")
                    if st.button("🗑️ Löschen", key=f"del_{idx}"):
                        df_archive.drop(idx).to_csv(DATEI, index=False)
                        st.rerun()
                else:
                    st.info("PDF: Nur Admin")

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.image("https://www.augsburg.de/typo3conf/ext/pp_site_augsburg/Resources/Public/img/logo-stadt-augsburg.svg", width=150) # Optional: Logo Link
    st.title("Verwaltung")
    if st.checkbox("🔑 Admin-Login"):
        if st.text_input("Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin-Modus aktiv")
        else:
            st.error("Falsches Passwort")
