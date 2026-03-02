import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Einsatzbericht Lokal", page_icon="📋")
st.title("📋 Einsatzbericht (Gesichert)")

# Name der Speicherdatei
DATEI = "berichte_archiv.csv"

# Funktion zum Laden der Daten
def lade_daten():
    if os.path.exists(DATEI):
        return pd.read_csv(DATEI)
    else:
        return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Bericht"])

# Formular
with st.form("input_form", clear_on_submit=True):
    d = st.date_input("Datum", datetime.now())
    z = st.time_input("Zeit", datetime.now())
    zeuge = st.text_input("Zeugen")
    text = st.text_area("Bericht / Details")
    submit = st.form_submit_button("Speichern")

if submit:
    if text:
        # Neue Zeile erstellen
        neue_zeile = pd.DataFrame([[str(d), str(z), zeuge, text]], 
                                 columns=["Datum", "Zeit", "Zeugen", "Bericht"])
        
        # Daten laden und neue Zeile anhängen
        df = lade_daten()
        df = pd.concat([df, neue_zeile], ignore_index=True)
        
        # Speichern als CSV
        df.to_csv(DATEI, index=False)
        
        st.success("✅ Bericht erfolgreich gespeichert!")
        st.balloons()
    else:
        st.error("Bitte gib einen Berichtstext ein.")

# Archiv anzeigen
st.divider()
st.subheader("📚 Archiv")
daten = lade_daten()
if not daten.empty:
    # Zeige die neuesten Einträge oben
    st.dataframe(daten.iloc[::-1], use_container_width=True)
else:
    st.info("Noch keine Berichte vorhanden.")
