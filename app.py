import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Einsatzbericht Archiv", page_icon="📋")
st.title("📋 Einsatzbericht")

DATEI = "berichte_archiv.csv"

def lade_daten():
    if os.path.exists(DATEI):
        return pd.read_csv(DATEI)
    else:
        return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Bericht"])

# --- EINGABE ---
with st.form("input_form", clear_on_submit=True):
    d = st.date_input("Datum", datetime.now())
    z = st.time_input("Zeit", datetime.now())
    zeuge = st.text_input("Zeugen")
    text = st.text_area("Bericht / Details")
    submit = st.form_submit_button("Bericht Speichern")

if submit and text:
    neue_zeile = pd.DataFrame([[str(d), str(z), zeuge, text]], 
                             columns=["Datum", "Zeit", "Zeugen", "Bericht"])
    df = lade_daten()
    df = pd.concat([df, neue_zeile], ignore_index=True)
    df.to_csv(DATEI, index=False)
    st.success("✅ Gespeichert!")
    st.rerun()

# --- ARCHIV & DOWNLOAD ---
st.divider()
daten = lade_daten()

if not daten.empty:
    st.subheader("📚 Gespeicherte Berichte")
    # Zeige Tabelle
    st.dataframe(daten.iloc[::-1], use_container_width=True)
    
    # Download Button
    csv = daten.to_csv(index=False).encode('utf-8-sig') # utf-8-sig ist wichtig für Excel!
    st.download_button(
        label="📥 Alle Berichte als Excel/CSV herunterladen",
        data=csv,
        file_name=f"Einsatzberichte_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )
else:
    st.info("Noch keine Einträge vorhanden.")
