import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- KONFIGURATION ---
SHEET_URL "SHEET_URL = "https://docs.google.com/spreadsheets/d/1qPHocyweIjksO6zhGVAqlxo4IqIeNM_8FmmStAt9eKc/edit"

st.set_page_config(page_title="Einsatzbericht Cloud", layout="centered")
st.title("📋 Einsatzbericht")

# Verbindung herstellen
conn = st.connection("gsheets", type=GSheetsConnection)

# Daten laden (mit Cache-Löschung, damit es immer frisch ist)
def load_data():
    return conn.read(spreadsheet=SHEET_URL, ttl="0s")

try:
    existierende_daten = load_data()
except:
    existierende_daten = pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Bericht"])

# --- FORMULAR ---
with st.form("bericht_form", clear_on_submit=True):
    st.subheader("Neuer Eintrag")
    d = st.date_input("Datum", datetime.now())
    z = st.time_input("Anfangszeit", datetime.now())
    zeuge = st.text_input("Zeugen")
    text = st.text_area("Bericht")
    
    submit = st.form_submit_button("Speichern")

if submit:
    if text:
        neue_zeile = pd.DataFrame([{
            "Datum": str(d),
            "Zeit": str(z),
            "Zeugen": zeuge,
            "Bericht": text
        }])
        
        # Sicherstellen, dass die Spalten passen
        aktualisierte_daten = pd.concat([existierende_daten, neue_zeile], ignore_index=True)
        
        try:
            # Speichern erzwingen
            conn.update(spreadsheet=SHEET_URL, data=aktualisierte_daten)
            st.success("✅ Erledigt! Bericht wurde in Google Sheets gespeichert.")
            st.balloons()
            # Seite kurz warten und dann neu laden
            st.info("Aktualisiere Archiv...")
        except Exception as e:
            st.error(f"Fehler: Bitte prüfe, ob die Google Tabelle auf 'Mitarbeiter' steht.")
    else:
        st.error("Bitte einen Text eingeben!")

# --- ARCHIV ---
st.divider()
st.subheader("Archiv")
if not existierende_daten.empty:
    st.dataframe(existierende_daten.sort_index(ascending=False), use_container_width=True)
