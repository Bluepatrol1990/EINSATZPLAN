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
LOGO_PFAD = "logo.png" # Muss im selben Verzeichnis wie die App liegen
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
ADMIN_PW = "admin789"
DIENST_PW = st.secrets.get("dienst_password", "1234")
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")

# --- 2. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide") 

st.markdown("""
    <style>
    .report-card { 
        background-color: #ffffff; 
        border-radius: 5px; 
        padding: 15px; 
        border-left: 10px solid #004b95; 
        margin-bottom: 12px; 
        color: #333333;
        border: 1px solid #cccccc;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
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

# --- 4. AMTSTRÄGER-PDF FUNKTION ---
def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo hinzufügen (Falls vorhanden)
    if os.path.exists(LOGO_PFAD):
        pdf.image(LOGO_PFAD, x=160, y=10, w=35)
    
    # Briefkopf
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "STADT AUGSBURG", ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 7, "ORDNUNGSAMT", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "Kommunaler Ordnungsdienst (KOD)", ln=True)
    
    pdf.line(10, 38, 200, 38)
    pdf.ln(15)
    
    # Dokumententitel
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "AMTLICHER EINSATZBERICHT", ln=True, align='C')
    pdf.ln(5)

    # Stammdaten Tabelle
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    
    def add_table_row(label, value):
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(45, 9, f" {label}", border=1, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(145, 9, f" {value}", border=1, ln=True)

    add_table_row("Aktenzeichen (AZ)", row_data['AZ'])
    add_table_row("Datum", row_data['Datum'])
    add_table_row("Einsatzzeitraum", f"{row_data['Beginn']} - {row_data['Ende']} Uhr")
    add_table_row("Einsatzort", f"{row_data['Ort']} {row_data['Hausnummer']}")
    add_table_row("Eingesetzte Kräfte", entschluesseln(row_data['Kraefte']))
    add_table_row("GPS-Koordinaten", row_data['GPS'])
    
    # Sachverhalt
    pdf.ln(10)
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

    # Beweismittel-Anlage (Foto)
    akt_foto = entschluesseln(row_data['Foto'])
    if akt_foto != "-":
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Anlage: Beweismittelfoto", ln=True, align='C')
        pdf.ln(10)
        try:
            img_bytes = base64.b64decode(akt_foto)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name
            # Bild zentrieren und skalieren
            pdf.image(tmp_path, x=20, y=40, w=170)
            os.unlink(tmp_path) 
        except:
            pdf.cell(0, 10, "[FEHLER: Das Foto konnte nicht geladen werden]", ln=True)

    # Footer
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Dieses Dokument wurde maschinell erstellt und ist ohne Unterschrift gültig.", align='C', ln=True)
    pdf.cell(0, 5, f"Zuständige Empfänger: Kevin.woelki@augsburg.de, kevinworlki@outlook.de", align='C')

    return pdf.output(dest="S").encode("latin-1")

# --- 5. APP LOGIK ---
if not st.session_state["auth"]:
    st.title("🚓 KOD Augsburg - Systemzugang")
    if st.text_input("Dienstpasswort", type="password") == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

st.title("📋 Einsatzbericht")

# --- FORMULAR ---
with st.expander("➕ NEUEN BERICHT ANLEGEN", expanded=True):
    loc = get_geolocation()
    gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Nicht erfasst"
    
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("Einsatzdatum")
        beginn = c2.time_input("Beginn")
        ende = c3.time_input("Ende")
        az_val = c4.text_input("Aktenzeichen (AZ)")
        
        o1, o2 = st.columns([3, 1])
        ort_val = o1.selectbox("Ort", ["Königsplatz", "Maximilianstraße", "Rathausplatz", "Oberhauser Bahnhof", "Zwölf-Apostel-Platz"])
        hnr_val = o2.text_input("Hausnr.")

        k_col1, k_col2 = st.columns(2)
        pol_check = k_col1.checkbox("Polizei unterstützt")
        rtw_check = k_col1.checkbox("Rettungsdienst")
        streife = k_col2.text_input("Funkstreifename") if pol_check else ""

        inhalt = st.text_area("Detaillierter Sachverhalt", height=150)
        beteiligte = st.text_input("Beteiligte / Zeugen")
        bild = st.file_uploader("Beweisfoto (Anlage)", type=["jpg", "png", "jpeg"])

        if st.form_submit_button("BERICHT SPEICHERN"):
            k_list = ["KOD"]
            if pol_check: k_list.append(f"Polizei ({streife})")
            if rtw_check: k_list.append("Rettungsdienst")
            
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
            st.success("Einsatzbericht wurde verschlüsselt im Archiv abgelegt.")
            st.rerun()

# --- ARCHIV ---
st.divider()
st.header("📂 Einsatzarchiv")
if os.path.exists(DATEI):
    df_archive = pd.read_csv(DATEI).astype(str)
    for idx, row in df_archive.iloc[::-1].iterrows():
        st.markdown(f"""
            <div class="report-card">
                <strong>AZ: {row['AZ']}</strong> | 📅 {row['Datum']} | 📍 {row['Ort']} {row['Hausnummer']}<br>
                <small>👮 {entschluesseln(row['Kraefte'])}</small>
            </div>
        """, unsafe_allow_html=True)
        
        c_det, c_pdf, c_del = st.columns([3, 1, 1])
        with c_det:
            with st.expander("📝 Details anzeigen"):
                st.write(f"**Sachverhalt:**\n{entschluesseln(row['Bericht'])}")
                st.write(f"**Zeugen:** {entschluesseln(row['Zeugen'])}")
                img_data = entschluesseln(row['Foto'])
                if img_data != "-": st.image(base64.b64decode(img_data), width=400)
        
        with c_pdf:
            # PDF Download für alle Nutzer
            pdf_bytes = create_official_pdf(row)
            st.download_button("📄 PDF Export", pdf_bytes, f"Bericht_{row['AZ']}.pdf", "application/pdf", key=f"pdf_{idx}")
        
        with c_del:
            if st.session_state["admin_auth"]:
                if st.button("🗑️ Löschen", key=f"del_{idx}"):
                    df_archive.drop(idx).to_csv(DATEI, index=False)
                    st.rerun()

# --- ADMIN ---
with st.sidebar:
    st.title("🛡️ Verwaltung")
    if st.checkbox("Admin-Modus"):
        if st.text_input("Admin-Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            if st.button("🚨 ARCHIV KOMPLETT LEEREN"):
                if os.path.exists(DATEI): os.remove(DATEI)
                st.rerun()
        else: st.session_state["admin_auth"] = False

