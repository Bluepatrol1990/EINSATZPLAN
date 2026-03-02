import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import urllib.parse

# Titel der App anpassen
st.set_page_config(page_title="Einsatzliste OA Nacht", page_icon="📝")
st.title("📝 Einsatzliste Ordnungsamt Nacht")

DATEI = "berichte_archiv.csv"

def lade_daten():
    if os.path.exists(DATEI):
        return pd.read_csv(DATEI)
    return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])

# --- EINGABE ---
with st.form("input_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1: d = st.date_input("Datum", datetime.now())
    with col2: z = st.time_input("Zeit", datetime.now())
    
    zeuge = st.text_input("Zeugen / Beteiligte")
    
    st.write("**Hinzugezogene Kräfte:**")
    c1, c2, c3, c4 = st.columns([1, 1, 1, 2]) # Spaltenaufteilung für Checkboxen + Textfeld
    pol = c1.checkbox("Polizei")
    rd = c2.checkbox("Rettungsdienst")
    fs = c3.checkbox("Funkstreife")
    fs_info = c4.text_input("Details Funkstreife", placeholder="z.B. Wagen-Nr.")
    
    text = st.text_area("Ausführlicher Bericht")
    submit = st.form_submit_button("Bericht Speichern")

if submit and text:
    neue_zeile = pd.DataFrame([[
        str(d), str(z), zeuge, 
        "Ja" if pol else "Nein", 
        "Ja" if rd else "Nein", 
        "Ja" if fs else "Nein",
        fs_info,
        text
    ]], columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])
    
    df = lade_daten()
    df = pd.concat([df, neue_zeile], ignore_index=True)
    df.to_csv(DATEI, index=False)
    st.success("✅ Gespeichert!")
    st.rerun()

# --- ARCHIV & EXPORT ---
st.divider()
daten = lade_daten()

if not daten.empty:
    st.subheader("📚 Letzter Bericht")
    letzter = daten.iloc[-1]
    
    # Details anzeigen
    st.info(f"Datum: {letzter['Datum']} | Funkstreife: {letzter['Funkstreife']} ({letzter['FS_Details']})")
    
    # --- PDF
