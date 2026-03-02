import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import urllib.parse

# Titel & Layout
st.set_page_config(page_title="Einsatzliste OA Nacht", page_icon="📝", layout="wide")
st.title("📝 Einsatzliste Ordnungsamt Nacht")

# --- VERBINDUNG ZUR ZENTRALEN DATEI ---
# Wir nutzen hier wieder Google Sheets, aber robuster programmiert.
from streamlit_gsheets import GSheetsConnection
conn = st.connection("gsheets", type=GSheetsConnection)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1qPHocyweIjksO6zhGVAqlxo4IqIeNM_8FmmStAt9eKc/edit"

def lade_zentrale_daten():
    try:
        # Holt die Daten live von Google
        return conn.read(spreadsheet=SHEET_URL, ttl="0s")
    except:
        return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])

# --- EINGABEMASKE ---
with st.expander("➕ Neuer Eintrag erstellen", expanded=True):
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1: d = st.date_input("Datum", datetime.now())
        with col2: z = st.time_input("Zeit", datetime.now())
        
        zeuge = st.text_input("Zeugen / Beteiligte")
        
        st.write("**Hinzugezogene Kräfte:**")
        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        pol = c1.checkbox("Polizei")
        rd = c2.checkbox("Rettungsdienst")
        fs = c3.checkbox("Funkstreife")
        fs_info = c4.text_input("Details Funkstreife", placeholder="Wagen-Nr. / Name")
        
        text = st.text_area("Ausführlicher Bericht")
        submit = st.form_submit_button("Bericht in Cloud speichern")

if submit and text:
    neue_zeile = pd.DataFrame([[
        str(d), str(z), zeuge, 
        "Ja" if pol else "Nein", 
        "Ja" if rd else "Nein", 
        "Ja" if fs else "Nein",
        fs_info,
        text
    ]], columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])
    
    try:
        existierende = lade_zentrale_daten()
        alle_daten = pd.concat([existierende, neue_zeile], ignore_index=True)
        # Speichern in die Cloud
        conn.update(spreadsheet=SHEET_URL, data=alle_daten)
        st.success("✅ Für alle gespeichert!")
        st.balloons()
    except Exception as e:
        st.error(f"Fehler beim Cloud-Speichern: Prüfe ob die Tabelle auf 'Mitarbeiter' steht!")

# --- ARCHIV (FÜR ALLE SICHTBAR) ---
st.divider()
st.subheader("📚 Alle gespeicherten Berichte")
daten = lade_zentrale_daten()

if not daten.empty:
    # Wir zeigen das Archiv in einer Liste an, die man aufklappen kann
    for i, row in daten.iloc[::-1].iterrows(): # Neueste zuerst
        with st.expander(f"📄 Bericht vom {row['Datum']} - {row['Zeit']} (Zeugen: {row['Zeugen']})"):
            st.write(f"**Kräfte:** Polizei: {row['Polizei']} | RD: {row['Rettungsdienst']} | FS: {row['Funkstreife']} ({row['FS_Details']})")
            st.write(f"**Details:**\n{row['Bericht']}")
            
            # PDF & Mail Buttons für DIESEN spezifischen Bericht
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, txt="EINSATZLISTE OA NACHT", ln=True, align='C')
            pdf.set_font("Arial", size=12)
            pdf.ln(10)
            pdf.multi_cell(0, 10, txt=f"Datum: {row['Datum']}\nBericht: {row['Bericht']}".replace('ä','ae').replace('ö','oe').replace('ü','ue'))
            pdf_out = pdf.output(dest='S').encode('latin-1', 'ignore')
            
            btn_col1, btn_col2 = st.columns(2)
            btn_col1.download_button("📄 Als PDF", pdf_out, f"Bericht_{i}.pdf", "application/pdf", key=f"pdf_{i}")
            
            mail_body = urllib.parse.quote(f"Bericht vom {row['Datum']}:\n\n{row['Bericht']}")
            btn_col2.link_button("📧 Mail senden", f"mailto:?subject=Einsatzbericht&body={mail_body}", key=f"mail_{i}")

else:
    st.info("Noch keine gemeinsamen Berichte vorhanden.")
