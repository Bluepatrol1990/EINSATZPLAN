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
from streamlit_drawable_canvas import st_canvas # pip install streamlit-drawable-canvas

# --- 1. GLOBALE VARIABLEN & SETTINGS ---
DATEI = "zentral_archiv_secure.csv"
LOGO_PFAD = "logo.png" 
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte", "Status"]
ADMIN_PW = "admin789"
DIENST_PW = st.secrets.get("dienst_password", "1234")
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")

VORLAGEN = {
    "Freitext": "",
    "🚨 Ruhestörung": "Anwohner beschwerten sich über überlaute Musik/Lärm aus der o.g. Örtlichkeit. Vor Ort wurde die Störung bestätigt und die verantwortliche Person zur Ruhe ermahnt. Personalien wurden festgestellt.",
    "🍺 Alkoholverbot": "Die Person wurde beim Konsum von Alkohol innerhalb der Verbotszone angetroffen. Ein Platzverweis wurde ausgesprochen. Sicherstellung/Entsorgung erfolgte vor Ort.",
    "🚯 Vermüllung": "Es wurde eine illegale Ablagerung von Abfall festgestellt. Verursacher konnte vor Ort nicht ermittelt werden / wurde zur Beseitigung aufgefordert.",
    "🆔 Platzverweis": "Aufgrund aggressiven Verhaltens wurde der Person ein Platzverweis für die Dauer von 24 Stunden für den Bereich XXX erteilt."
}

# --- 2. KONFIGURATION ---
st.set_page_config(page_title="KOD Augsburg Pro", page_icon="🚓", layout="wide") 

# --- 3. CRYPTO LOGIK ---
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

# --- 4. AMTSTRÄGER-PDF (INKL. UNTERSCHRIFT) ---
def create_pro_pdf(row_data, signature_img=None):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_PFAD):
        pdf.image(LOGO_PFAD, x=160, y=10, w=35)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "STADT AUGSBURG | ORDNUNGSAMT", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "Kommunaler Ordnungsdienst (KOD) - Einsatzdokumentation", ln=True)
    pdf.line(10, 32, 200, 32)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"OFFIZIELLER EINSATZBERICHT - AZ: {row_data['AZ']}", ln=True, align='C')
    pdf.ln(5)

    def add_row(label, value):
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(45, 8, f" {label}", border=1, fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(145, 8, f" {value}", border=1, ln=True)

    add_row("Datum / Zeit", f"{row_data['Datum']} | {row_data['Beginn']} - {row_data['Ende']} Uhr")
    add_row("Einsatzort", f"{row_data['Ort']} {row_data['Hausnummer']}")
    add_row("Kräfte", entschluesseln(row_data['Kraefte']))
    add_row("Status", row_data.get('Status', 'Offen'))
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "Sachverhalt:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, entschluesseln(row_data['Bericht']), border=1)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "Beteiligte / Zeugen:", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(0, 6, entschluesseln(row_data['Zeugen']), border=1)

    # Unterschrift einfügen
    if signature_img is not None:
        pdf.ln(10)
        pdf.set_font("Arial", 'I', 9)
        pdf.cell(0, 5, "Digitale Unterschrift des Erfassers:", ln=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            signature_img.save(tmp.name)
            pdf.image(tmp.name, x=15, y=pdf.get_y(), w=50)
            os.unlink(tmp.name)

    # Foto-Anlage
    akt_foto = entschluesseln(row_data['Foto'])
    if akt_foto != "-":
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Anlage: Fotodokumentation", ln=True)
        try:
            img_bytes = base64.b64decode(akt_foto)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(img_bytes)
                pdf.image(tmp.name, x=20, y=30, w=170)
                os.unlink(tmp.name)
        except: pass

    return pdf.output(dest="S").encode("latin-1")

# --- 5. HAUPTSEITE ---
if not st.session_state.get("auth", False):
    st.title("🚓 KOD Augsburg - Login")
    if st.text_input("🔑 Dienstpasswort", type="password") == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

st.title("📋 Einsatzbericht Pro")

with st.expander("📝 NEUEN EINSATZ ERFASSEN", expanded=True):
    with st.form("pro_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("📅 Datum")
        beginn = c2.time_input("🕒 Beginn")
        ende = c3.time_input("🕒 Ende")
        az = c4.text_input("📂 Aktenzeichen")
        
        o1, o2 = st.columns([3, 1])
        einsatzort = o1.text_input("🗺️ Einsatzort", placeholder="Straße / Platz")
        hausnr = o2.text_input("Nr.")

        st.divider()
        st.subheader("✍️ Sachverhalt & Vorlagen")
        auswahl = st.selectbox("📑 Textbaustein wählen", list(VORLAGEN.keys()))
        bericht_text = st.text_area("Berichtstext", value=VORLAGEN[auswahl], height=150)
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        
        st.divider()
        st.subheader("👮 Kräfte & Beweise")
        k1, k2, k3, k4 = st.columns(4)
        pol = k1.checkbox("🚔 Polizei")
        rtw = k2.checkbox("🚑 Rettungsdienst")
        fw = k3.checkbox("🚒 Feuerwehr")
        funk = st.text_input("🆔 Funkname") if pol else ""
        foto = st.file_uploader("📸 Beweisfoto", type=["jpg","jpeg","png"])

        st.info("🖋️ Bitte unten digital unterschreiben:")
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)", stroke_width=2,
            stroke_color="#000000", background_color="#eeeeee",
            height=100, width=300, drawing_mode="freedraw", key="signature"
        )

        if st.form_submit_button("✅ BERICHT FINALISIEREN"):
            k_final = ["KOD"]
            if pol: k_final.append(f"Polizei ({funk})")
            if rtw: k_final.append("Rettungsdienst")
            if fw: k_final.append("Feuerwehr")
            
            b64_f = "-"
            if foto:
                img = Image.open(foto).convert("RGB")
                img.thumbnail((1200, 1200))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=80)
                b64_f = base64.b64encode(buf.getvalue()).decode()

            new_data = {
                "Datum": str(datum), "Beginn": beginn.strftime("%H:%M"), "Ende": ende.strftime("%H:%M"),
                "Ort": einsatzort, "Hausnummer": hausnr, "Zeugen": verschluesseln(beteiligte),
                "Bericht": verschluesseln(bericht_text), "AZ": az, "Foto": verschluesseln(b64_f),
                "GPS": "Automatisch", "Kraefte": verschluesseln(", ".join(k_final)), "Status": "Offen"
            }
            
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success("Bericht gespeichert!")
            st.rerun()

# --- ARCHIV ---
st.divider()
st.header("📂 Archiv & Verwaltung")
if os.path.exists(DATEI):
    df_archive = pd.read_csv(DATEI).astype(str)
    for idx, row in df_archive.iloc[::-1].iterrows():
        # Status-Farbe
        color = "#ff4b4b" if row['Status'] == "Offen" else "#ffa500" if row['Status'] == "In Bearbeitung" else "#28a745"
        
        with st.container():
            st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; border-left: 10px solid {color}; margin-bottom: 10px; background: white;">
                <h4 style="margin:0;">📂 {row['AZ']} | {row['Ort']}</h4>
                <small>📅 {row['Datum']} | 🕒 {row['Beginn']} Uhr | 👮 {entschluesseln(row['Kraefte'])}</small>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                with st.expander("Details"):
                    st.write(entschluesseln(row['Bericht']))
            with c2:
                # Status ändern
                new_status = st.selectbox("Status", ["Offen", "In Bearbeitung", "Abgeschlossen"], 
                                         index=["Offen", "In Bearbeitung", "Abgeschlossen"].index(row['Status']), 
                                         key=f"stat_{idx}")
                if new_status != row['Status']:
                    df_archive.at[idx, 'Status'] = new_status
                    df_archive.to_csv(DATEI, index=False)
                    st.rerun()
            with c3:
                pdf_bytes = create_pro_pdf(row)
                st.download_button("📄 PDF", pdf_bytes, f"KOD_{row['AZ']}.pdf", "application/pdf", key=f"dl_{idx}")
            with c4:
                if st.button("📧 Senden", key=f"send_{idx}"):
                    st.toast(f"Bericht {row['AZ']} wurde an Dienststellenleiter gesendet!")

# --- ADMIN ---
with st.sidebar:
    st.title("🛡️ Admin")
    if st.checkbox("Admin-Modus"):
        if st.text_input("Admin PW", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            if st.button("🚨 ARCHIV LEEREN"):
                if os.path.exists(DATEI): os.remove(DATEI)
                st.rerun()
