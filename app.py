import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("📋 Einsatzbericht")

# Verbindung herstellen
conn = st.connection("gsheets", type=GSheetsConnection)

# Formular
with st.form("input_form"):
    datum = st.date_input("Datum")
    bericht = st.text_area("Bericht")
    submit = st.form_submit_button("Speichern")

if submit:
    if bericht:
        # Bestehende Daten lesen
        df = conn.read()
        # Neue Zeile
        new_row = pd.DataFrame([{"Datum": str(datum), "Bericht": bericht}])
        # Verbinden
        updated_df = pd.concat([df, new_row], ignore_index=True)
        # Hochladen
        conn.update(data=updated_df)
        st.success("Gespeichert!")
    else:
        st.error("Bitte Text eingeben")

# Archiv anzeigen
st.dataframe(conn.read())
