import streamlit as st
import pandas as pd
import os
import io
import base64
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from PIL import Image
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation
from fpdf import FPDF

# --- 1. KONFIGURATION & EMPFÄNGER ---
DATEI = "zentral_archiv_secure.csv"
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# --- 2. SICHERHEIT (PASSWÖRTER & VERSCHLÜSSELUNG) ---
DIENST_PW = st.secrets.get("dienst_password", "1234")
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")
ADMIN_PW = "admin789"

# E-Mail Account Daten (Sollten in .streamlit/secrets.toml stehen)
SMTP_SERVER = st.secrets.get("smtp_server", "smtp.dein-server.de")
SMTP_PORT = 587
SENDER_EMAIL = st.secrets.get("sender_email", "berichte@deinedomain.de")
SENDER_PASSWORD = st.secrets.get("sender_password", "dein_passwort")

def get_cipher():
    key_64 = base64.urlsafe_b64encode(MASTER_KEY[:32].encode().ljust(32))
    return Fernet(key_64)

def verschluesseln(text):
    if not text or text == "-": return "-"
    return get_cipher().encrypt(str(text).encode()).decode()

def entschluesseln(safe_text):
    if not safe_text or safe_text == "-": return "-"
    try: return get_cipher().decrypt(safe_text.encode()).decode()
    except: return "[Fehler]"

# --- 3. FUNKTIONEN: PDF & E-MAIL ---
class AmtlicherBericht(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Stadt Augsburg', 0, 1, 'R')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Ordnungsreferat / KOD', 0, 1, 'R')
        self.ln(15)
        self.set_draw_color(0, 75, 149)
        self.line(10, 32, 200, 32)

def erstelle_pdf_buffer(row_data):
    pdf = AmtlicherBericht()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Einsatzbericht - AZ: {row_data['AZ']}", 0, 1)
    pdf.ln(5)
    
    # Tabelle für Basisinfos
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Datum/Zeit:", 1); pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f"{row_data['Datum']} ({row_data['Beginn']} - {row_data['Ende']} Uhr)", 1, 1)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Einsatzort:", 1); pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f"{row_data['Ort']} {row_data['Hausnummer']}", 1, 1)
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Sachverhalt:", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Bericht']))
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

def send_report_email(subject, body, attachment_data=None, filename=None):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECIPIENTS)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if attachment_data:
        part = MIMEApplication(attachment_data, Name=filename)
        part['Content-Disposition'] = f'attachment; filename="{filename}"'
        msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENTS, msg.as_string())
        return True
    except:
        return False

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="KOD Augsburg", page_icon="🚓", layout="wide")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False

# Login
if not st.session_state["auth"]:
    st.title("🚓 KOD Augsburg - Login")
    if st.text_input("Dienstpasswort", type="password") == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

# --- HAUPTSEITE & FORMULAR ---
st.title("📋 Neuer Einsatzbericht")

# (Straßenliste & GPS Logik hier einfügen wie im vorherigen Step...)
# [Platzhalter für STRASSEN_AUGSBURG Liste]

with st.form("einsatz_form"):
    col1, col2 = st.columns(2)
    datum = col1.date_input("Datum")
    az = col2.text_input("Aktenzeichen")
    ort = st.selectbox("Ort", ["Königsplatz", "Maximilianstraße", "Rathausplatz"]) # Beispielhaft
    bericht_text = st.text_area("Sachverhalt")
    
    submit = st.form_submit_button("Bericht speichern & Senden")
    
    if submit:
        # 1. Daten verschlüsseln & Speichern
        new_row = {
            "Datum": str(datum), "Beginn": "00:00", "Ende": "00:00", "Ort": ort, 
            "Hausnummer": "-", "Zeugen": "-", "Bericht": verschluesseln(bericht_text), 
            "AZ": az, "Foto": "-", "GPS": "-", "Kraefte": verschluesseln("KOD")
        }
        df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
        pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).to_csv(DATEI, index=False)
        
        # 2. PDF für E-Mail generieren
        pdf_raw = erstelle_pdf_buffer(new_row)
        
        # 3. E-Mail Versand
        mail_success = send_report_email(
            f"KOD Bericht - AZ: {az} - {ort}",
            f"Anbei der neue Einsatzbericht vom {datum}.",
            pdf_raw, f"Bericht_{az}.pdf"
        )
        
        st.success("Bericht lokal gespeichert!")
        if mail_success: st.info(f"E-Mail an {RECIPIENTS} versendet.")
        else: st.warning("E-Mail Versand fehlgeschlagen (SMTP nicht konfiguriert).")

# --- ARCHIV (ADMIN) ---
st.divider()
st.header("📂 Archiv")
if st.sidebar.checkbox("🔑 Admin"):
    if st.sidebar.text_input("Admin PW", type="password") == ADMIN_PW:
        st.session_state["admin_auth"] = True
        
        if os.path.exists(DATEI):
            data = pd.read_csv(DATEI)
            for i, r in data.iterrows():
                with st.expander(f"Bericht {r['AZ']} - {r['Ort']}"):
                    st.write(entschluesseln(r['Bericht']))
                    # PDF Download Button im Archiv
                    pdf_btn = erstelle_pdf_buffer(r)
                    st.download_button("📄 PDF herunterladen", pdf_btn, f"{r['AZ']}.pdf", "application/pdf")
