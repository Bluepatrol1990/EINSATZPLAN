import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import urllib.parse

# --- KONFIGURATION ---
st.set_page_config(page_title="Einsatzliste OA Nacht", page_icon="📝", layout="wide")
PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"
# Deine festen Empfänger
REZEPTIENTEN = "Kevin.woelki@augsburg.de, kevinworlki@outlook.de"

# --- LOGIN-LOGIK ---
if "autentifiziert" not in st.session_state:
    st.session_state["autentifiziert"] = False

if not st.session_state["autentifiziert"]:
    st.title("🔐 Login - Ordnungsamt Nacht")
    eingabe = st.text_input("Dienst-Passwort eingeben", type="password")
    if st.button("Anmelden"):
        if eingabe == PASSWORT:
            st.session_state["autentifiziert"] = True
            st.rerun()
        else:
            st.error("Falsches Passwort!")
    st.stop()

# --- DATEN-FUNKTIONEN ---
def lade_daten():
    if os.path.exists(DATEI):
        return pd.read_csv(DATEI)
    return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])

# --- SIDEBAR (ABMELDEN) ---
with st.sidebar:
    if st.button("🔴 Abmelden / Sperren"):
        st.session_state["autentifiziert"] = False
        st.rerun()

# --- HAUPTSEITE ---
st.title("📝 Einsatzliste Ordnungsamt Nacht")

# Formular
with st.expander("➕ Neuen Bericht erstellen", expanded=True):
    with st.form("input_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        d = col1.date_input("Datum", datetime.now())
        z = col2.time_input("Zeit", datetime.now())
        zeuge = st.text_input("Zeugen / Beteiligte")
        
        st.write("**Hinzugezogene Kräfte:**")
        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        pol = c1.checkbox("Polizei")
        rd = c2.checkbox("Rettungsdienst")
        fs = c3.checkbox("Funkstreife")
        fs_info = c4.text_input("Details Funkstreife", placeholder="Wagen / Name")
        
        text = st.text_area("Bericht / Sachverhalt")
        submit = st.form_submit_button("Bericht Speichern")

if submit and text:
    neue_zeile = pd.DataFrame([[
        str(d), str(z), zeuge, 
        "Ja" if pol else "Nein", 
        "Ja" if rd else "Nein", 
        "Ja" if fs else "Nein", 
        fs_info, text
    ]], columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])
    
    df = lade_daten()
    df = pd.concat([df, neue_zeile], ignore_index=True)
    df.to_csv(DATEI, index=False)
    
    st.success("✅ Bericht gespeichert!")
    
    # --- SOFORT-VERSAND ---
    st.write("### 📤 Jetzt direkt versenden:")
    v_col1, v_col2 = st.columns(2)
    
    mail_inhalt = (
        f"EINSATZBERICHT - ORDNUNGSAMT NACHT\n"
        f"----------------------------------\n"
        f"Datum: {d}\nZeit: {z}\nZeugen: {zeuge}\n\n"
        f"Kräfte vor Ort:\n"
        f"- Polizei: {'Ja' if pol else 'Nein'}\n"
        f"- Rettungsdienst: {'Ja' if rd else 'Nein'}\n"
        f"- Funkstreife: {'Ja' if fs else 'Nein'} ({fs_info})\n\n"
        f"Sachverhalt:\n{text}"
    )
    
    betreff = urllib.parse.quote(f"Einsatzbericht {d} {z}")
    body = urllib.parse.quote(mail_inhalt)
    
    # Mailto-Link mit Empfängern
    mail_link = f"mailto:{REZEPTIENTEN}?subject={betreff}&body={body}"
    v_col1.link_button("📧 E-Mail an Zentrale senden", mail_link, use_container_width=True)
    
    # PDF Erstellung
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="EINSATZLISTE OA NACHT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    clean_pdf = mail_inhalt.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
    pdf.multi_cell(0, 10, txt=clean_pdf)
    pdf_out = pdf.output(dest='S').encode('latin-1', 'ignore')
    
    v_col2.download_button("📄 PDF herunterladen", pdf_out, f"Einsatz_{d}.pdf", "application/pdf", use_container_width=True)

# --- ARCHIV ---
st.divider()
st.subheader("📚 Zentrales Archiv")
daten = lade_daten()
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        with st.expander(f"📄 {row['Datum']} - {row['Zeit']} - {row['Zeugen'][:15]}..."):
            st.write(f"**Bericht:** {row['Bericht']}")
            m_body = urllib.parse.quote(f"Bericht vom {row['Datum']}:\n\n{row['Bericht']}")
            st.link_button("📧 Erneut senden", f"mailto:{REZEPTIENTEN}?subject=Kopie Einsatzbericht&body={m_body}", key=f"old_mail_{i}")
