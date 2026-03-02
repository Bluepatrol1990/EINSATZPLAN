import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- KONFIGURATION ---
# Dein sauberer Link (wichtig: nur bis /edit)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1qPHocyweIjksO6zhGVAqlxo4IqIeNM_8FmmStAt9eKc/edit"

st.set_page_config(page_title="Einsatzbericht Profi", page_icon="📋")
st.title("📋 Einsatzbericht")

# Verbindung initialisieren
conn = st.connection("gsheets", type=GSheetsConnection)

# --- DATEN LADEN ---
def get_data():
    try:
        # Wir laden nur die ersten 4 Spalten
        return conn.read(spreadsheet=SHEET_URL, usecols=[0,1,2,3], ttl="0s")
    except:
        return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Bericht"])

# --- FORMULAR ---
with st.form("mein_formular", clear_on_submit=True):
    d = st.date_input("Datum", datetime.now())
    z = st.time_input("Zeit", datetime.now())
    zeuge = st.text_input("Zeugen")
    text = st.text_area("Bericht")
    submit = st.form_submit_button("Speichern")

if submit:
    if text:
        # Neue Daten vorbereiten
        neue_zeile = pd.DataFrame([{
            "Datum": str(d),
            "Zeit": str(z),
            "Zeugen": zeuge,
            "Bericht": text
        }])
        
        try:
            # Bestehende Daten holen
            alte_daten = get_data()
            # Zusammenfügen
            alle_daten = pd.concat([alte_daten, neue_zeile], ignore_index=True)
            # Komplett neu hochladen
            conn.update(spreadsheet=SHEET_URL, data=alle_daten)
            
            st.success("✅ Erfolg! Der Bericht wurde gespeichert.")
            st.balloons()
        except Exception as e:
            st.error("Speichern fehlgeschlagen.")
            st.warning("HINWEIS: Prüfe in Google Sheets, ob die Datei 'Einsatzberichte' heißt und die Freigabe auf 'Mitarbeiter' steht.")
    else:
        st.error("Bitte gib einen Text ein.")

# --- ANZEIGE ---
st.divider()
st.subheader("Bisherige Berichte")
st.dataframe(get_data().sort_index(ascending=False), use_container_width=True)
