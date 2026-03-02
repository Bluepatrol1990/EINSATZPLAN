import streamlit as st
from datetime import datetime
import pandas as pd

# Design der App
st.set_page_config(page_title="Einsatzbericht", page_icon="📋")
st.title("📋 Einsatzbericht")

# Formular für neue Berichte
with st.expander("➕ Neuen Bericht erstellen", expanded=True):
    datum = st.date_input("Datum", datetime.now())
    zeit = st.time_input("Anfangszeit", datetime.now())
    zeugen = st.text_input("Zeugen")
    bericht_text = st.text_area("Bericht")
    
    if st.button("Speichern"):
        if bericht_text:
            st.success("Bericht erfolgreich erfasst!")
            # Hinweis: In der Grundversion wird hier nur bestätigt. 
            # Später zeige ich dir das dauerhafte Speichern in einer Tabelle.
        else:
            st.warning("Bitte Text eingeben.")

# Suche und Liste
st.divider()
st.subheader("Suche & Archiv")
suche = st.text_input("Suchen nach Zeugen oder Inhalt...")
st.info("Hier erscheinen bald deine gespeicherten Berichte.")
