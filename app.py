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

# --- 1. SETTINGS & SECURITY ---
DATEI = "zentral_archiv_secure.csv"
LOGO_PFAD = "logo.png" 
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
ADMIN_PW = "admin789"
DIENST_PW = st.secrets.get("dienst_password", "1234")
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")

st.set_page_config(page_title="KOD Augsburg | Smart Report", page_icon="🚓", layout="wide") 

# --- 2. ADVANCED UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #f4f7f9; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    
    .report-card { 
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 15px; 
        padding: 25px; 
        border-left: 8px solid #004b95; 
        margin-bottom: 20px; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .report-card:hover { transform: translateY(-5px); }
    
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        background-color: #e0e7ff;
        color: #4338ca;
    }
    
    .metric-container {
        display: flex;
        gap: 15px;
        margin-top: 15px;
    }
    
    .metric-pill {
        background: #ffffff;
        padding: 8px 15px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        font-size: 0.9em;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
    """, unsafe_allow_html=True) 

# --- 3. CORE FUNCTIONS ---
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
    if os.path.exists(LOGO_PFAD):
        pdf.image(LOGO_PFAD, x=165, y=10, w=30)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 75, 149)
    pdf.cell(0, 10, "STADT AUGSBURG | ORDNUNGSAMT", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 5, "Kommunaler Ordnungsdienst (KOD)", ln=True)
    pdf.line(10, 35, 200, 35)
    pdf.ln(15)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"EINSATZPROTOKOLL - {row_data['AZ']}", ln=True, align='C')
    pdf.ln(5)

    def add_table_row(label, value):
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(240, 243, 246)
        pdf.cell(45, 10, f" {label}", border=1, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(145, 10, f" {value}", border=1, ln=True)

    add_table_row("Aktenzeichen", row_data['AZ'])
    add_table_row("Datum / Zeit", f"{row_data['Datum']} ({row_data['Beginn']} - {row_data['Ende']} Uhr)")
    add_table_row("Einsatzort", f"{row_data['Ort']} {row_data['Hausnummer']}")
    add_table_row("Kräfte vor Ort", entschluesseln(row_data['Kraefte']))
    add_table_row("GPS Ref", row_data['GPS'])
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Detaillierter Sachverhalt:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Bericht']), border='T')
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Personen / Zeugen:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Zeugen']), border='T')

    akt_foto = entschluesseln(row_data['Foto'])
    if akt_foto != "-":
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Anlage: Beweisfoto", ln=True, align='C')
        try:
            img_bytes = base64.b64decode(akt_foto)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(img_bytes)
                pdf.image(tmp.name, x=20, y=40, w=170)
                os.unlink(tmp.name) 
        except: pass

    pdf.set_y(-25)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(0, 10, f"Systemdokumentation KOD Augsburg | Empfänger: Kevin.woelki@augsburg.de", align='C')
    return pdf.output(dest="S").encode("latin-1")

# --- 4. AUTHENTICATION ---
if not st.session_state["auth"]:
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.image("https://img.icons8.com/fluency/96/police-badge.png")
        st.title("KOD Augsburg Login")
        pw = st.text_input("Dienstpasswort eingeben", type="password")
        if pw == DIENST_PW:
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# --- 5. MAIN INTERFACE ---
st.title("🚀 KOD Smart Reporting")

tab1, tab2 = st.tabs(["🆕 Neuer Bericht", "📂 Einsatzarchiv"])

with tab1:
    loc = get_geolocation()
    gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "📍 GPS wird ermittelt..."
    
    with st.form("main_form"):
        st.markdown("### 📍 Lokalisierung & Zeit")
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("Einsatzdatum")
        beginn = c2.time_input("Einsatzbeginn")
        ende = c3.time_input("Einsatzende")
        az_val = c4.text_input("Aktenzeichen (AZ)", placeholder="z.B. 2026-KOD-001")
        
        o1, o2, o3 = st.columns([3, 1, 2])
        ort_val = o1.text_input("Einsatzort", placeholder="Straße oder Platz")
        hnr_val = o2.text_input("Hausnr.")
        st.info(f"Aktueller Standort: {gps_val}")

        st.markdown("### 👮 Beteiligte Organisationen")
        k1, k2, k3 = st.columns(3)
        pol = k1.checkbox("🚔 Polizei")
        rtw = k2.checkbox("🚑 Rettungsdienst")
        fw = k3.checkbox("🚒 Feuerwehr")
        
        funkname = ""
        if pol:
            funkname = st.text_input("Funkrufname Polizei", placeholder="z.B. Augsburg 12/1")

        st.markdown("### 📝 Sachverhalt")
        inhalt = st.text_area("Berichtstext", height=200, placeholder="Was ist passiert? Wer war beteiligt?")
        beteiligte = st.text_input("Zeugen / Beteiligte Personen")
        bild = st.file_uploader("📸 Beweisfoto (Optional)", type=["jpg", "png", "jpeg"])

        if st.form_submit_button("✅ BERICHT FINALISIEREN"):
            if not az_val or not ort_val:
                st.error("Bitte Aktenzeichen und Einsatzort angeben!")
            else:
                k_list = ["KOD"]
                if pol: k_list.append(f"Polizei ({funkname})" if funkname else "Polizei")
                if rtw: k_list.append("Rettungsdienst")
                if fw: k_list.append("Feuerwehr")
                
                b64_img = "-"
                if bild:
                    img = Image.open(bild).convert("RGB")
                    img.thumbnail((1200, 1200))
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=80)
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
                st.balloons()
                st.success("Bericht erfolgreich im Hochsicherheitsarchiv gespeichert.")

with tab2:
    st.subheader("🔍 Filter & Suche")
    search_col, sort_col = st.columns([3, 1])
    suche = search_col.text_input("Suche nach AZ, Ort oder Datum...", placeholder="z.B. Rathausplatz")
    
    if os.path.exists(DATEI):
        df_archive = pd.read_csv(DATEI).astype(str)
        if suche:
            df_archive = df_archive[df_archive.apply(lambda row: suche.lower() in row.astype(str).str.lower().values, axis=1)]

        for idx, row in df_archive.iloc[::-1].iterrows():
            st.markdown(f"""
                <div class="report-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.4em; font-weight: 700; color: #004b95;">📂 {row['AZ']}</span>
                        <span class="status-badge">ERFASST</span>
                    </div>
                    <div class="metric-container">
                        <div class="metric-pill">📅 {row['Datum']}</div>
                        <div class="metric-pill">🕒 {row['Beginn']} - {row['Ende']}</div>
                        <div class="metric-pill">📍 {row['Ort']} {row['Hausnummer']}</div>
                    </div>
                    <div style="margin-top: 15px; font-size: 0.9em; color: #666;">
                        👮 <b>Kräfte:</b> {entschluesseln(row['Kraefte'])}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            c_det, c_pdf, c_del = st.columns([3, 1, 1])
            with c_det:
                with st.expander("📄 Protokoll einsehen"):
                    st.markdown(f"**Sachverhalt:**\n{entschluesseln(row['Bericht'])}")
                    st.markdown(f"**Beteiligte:** {entschluesseln(row['Zeugen'])}")
                    img_data = entschluesseln(row['Foto'])
                    if img_data != "-": st.image(base64.b64decode(img_data), width=450)
            
            with c_pdf:
                pdf_bytes = create_official_pdf(row)
                st.download_button("📥 PDF Export", pdf_bytes, f"KOD_{row['AZ']}.pdf", "application/pdf", key=f"pdf_{idx}")
            
            with c_del:
                if st.session_state["admin_auth"]:
                    if st.button("🗑️ Löschen", key=f"del_{idx}"):
                        df_archive.drop(idx).to_csv(DATEI, index=False)
                        st.rerun()

# --- 6. SIDEBAR ADMIN ---
with st.sidebar:
    st.image("https://img
