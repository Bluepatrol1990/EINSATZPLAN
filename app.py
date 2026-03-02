import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import urllib.parse

# Konfiguration
st.set_page_config(page_title="Einsatzliste OA Nacht", page_icon="📝", layout="wide")
PASSWORT = "1234"

# --- LOGIN ---
if "autentifiziert" not in st.session_state:
    st.session_state["autentifiziert"] = False

if not st.session_state["autentifiziert"]:
    st.title("🔐 Login")
    eingabe = st.text_input("Dienst-Passwort", type="password")
    if st.button("Anmelden"):
        if eingabe == PASSWORT:
            st.session_state["autentifiziert"] = True
            st.rerun()
        else:
            st.error("Falsches Passwort!")
    st.stop()

# --- DATEN-MANAGEMENT (Zentraler Cloud Speicher) ---
# Wir nutzen st.status oder einfach eine Datei, die im persistenten Speicher bleibt
DATEI = "zentral_archiv.csv"

def lade_daten():
    if os.path.exists(DATEI):
        return pd.read_csv(DATEI)
    return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])

import os

# --- HAUPTSEITE ---
st.title("📝 Einsatzliste Ordnungsamt Nacht")

with st.expander("➕ Neuer Bericht"):
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        d = col1.date_input("Datum", datetime.now())
        z = col2.time_input("Zeit", datetime.now())
        zeuge = st.text_input("Zeugen")
        
        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        pol = c1.checkbox("Polizei")
        rd = c2.checkbox("Rettungsdienst")
        fs = c3.checkbox("Funkstreife")
        fs_info = c4.text_input("Details Funkstreife")
        
        text = st.text_area("Bericht")
        submit = st.form_submit_button("Speichern")

if submit and text:
    neue_zeile = pd.DataFrame([[str(d), str(z), zeuge, "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", fs_info, text]], 
                             columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])
    df = lade_daten()
    df = pd.concat([df, neue_zeile], ignore_index=True)
    df.to_csv(DATEI, index=False)
    st.success("Gespeichert!")
    st.rerun()

# --- ARCHIV (FÜR ALLE) ---
st.divider()
st.subheader("📚 Zentrales Archiv")
daten = lade_daten()

if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        with st.expander(f"📄 {row['Datum']} - {row['Zeugen'][:20]}..."):
            st.write(f"**Zeit:** {row['Zeit']} | **Kräfte:** Pol:{row['Polizei']}, RD:{row['Rettungsdienst']}, FS:{row['Funkstreife']} ({row['FS_Details']})")
            st.write(row['Bericht'])
            
            # Einfacher PDF Export ohne Umlaute-Probleme
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Einsatzbericht {row['Datum']}", ln=True)
            pdf.multi_cell(0, 10, txt=f"Bericht: {row['Bericht']}".encode('latin-1', 'ignore').decode('latin-1'))
            pdf_out = pdf.output(dest='S').encode('latin-1')
            
            st.download_button("📄 PDF", pdf_out, f"Bericht_{i}.pdf", key=f"p_{i}")
else:
    st.info("Noch keine Berichte vorhanden.")
