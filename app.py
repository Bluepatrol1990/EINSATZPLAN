import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- DIE VERBINDUNG ---
# Hier fügst du deinen Link zwischen die Anführungszeichen ein:
# Beispiel: SHEET_URL = "https://docs.google.com/spreadsheets/d/12345..."
SHEET_URL = "https://docs.google.com/spreadsheets/d/1qPHocyweIjksO6zhGVAqlxo4IqIeNM_8FmmStAt9eKc/edit?usp=drivesdk"

st.set_page_config(page_title="Einsatzbericht Cloud", page_icon="📋")
st.title("📋 Einsatzbericht")

# Verbindung zur Google Tabelle herstellen
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Wir laden die vorhandenen Daten
    existierende_daten = conn.read(spreadsheet=SHEET_URL, usecols=[0,1,2,3])
except:
    existierende_daten = pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Bericht"])

# --- EINGABE-FORMULAR ---
with st.form("bericht_form"):
    st.subheader("Neuer Eintrag")
    d = st.date_input("Datum", datetime.now())
    z = st.time_input("Anfangszeit", datetime.now())
    zeuge = st.text_input("Zeugen")
    text = st.text_area("Bericht / Details")
    
    submit = st.form_submit_button("Speichern")

if submit:
    if text:
        # Neuen Datensatz erstellen
        neue_zeile = pd.DataFrame([{
            "Datum": str(d),
            "Zeit": str(z),
            "Zeugen": zeuge,
            "Bericht": text
        }])
        
        # Daten zusammenfügen
        aktualisierte_daten = pd.concat([existierende_daten, neue_zeile], ignore_index=True)
        
        # In Google Sheets zurückschreiben
        conn.update(spreadsheet=SHEET_URL, data=aktualisierte_daten)
        st.success("Erfolgreich in Google Tabelle gespeichert!")
        st.ballons()
    else:
        st.error("Bitte gib einen Berichtstext ein.")

# --- ARCHIV & FILTER ---
st.divider()
st.subheader("Gespeicherte Berichte")
suche = st.text_input("Suche im Archiv (Zeugen/Bericht)")

if not existierende_daten.empty:
    filter_df = existierende_daten.copy()
    if suche:
        filter_df = filter_df[filter_df.astype(str).apply(lambda x: suche.lower() in x.str.lower().values, axis=1)]
    st.dataframe(filter_df, use_container_width=True)
