import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import urllib.parse

# --- KONFIGURATION ---
st.set_page_config(page_title="Einsatzliste OA Nacht", page_icon="📝", layout="wide")
PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"
EMPFAENGER = "Kevin.woelki@augsburg.de,kevinworlki@outlook.de"

# --- LOGIN-LOGIK ---
if "autentifiziert" not in st.session_state:
    st.session_state["autentifiziert"] = False

if not st.session_state["autentifiziert"]:
    st.title("🔐 Login - Ordnungsamt Nacht")
    eingabe = st.text_input("Dienst-Passwort eingeben", type="password")
    if st.button("Anmelden"):
        if eingabe == PASSWORT:
            st.session_state["autentifiziert"] = True
            st.rerun()
        else:
            st.error("Falsches Passwort!")
    st.stop()

# --- DATEN-FUNKTIONEN ---
def lade_daten():
    if os.path.exists(DATEI):
        try:
            df = pd.read_csv(DATEI).fillna("")
            # Sicherstellen, dass alles Text ist
            return df.astype(str)
        except:
            pass
    return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])

# --- SIDEBAR ---
with st.sidebar:
    if st.button("🔴 Abmelden"):
        st.session_state["autentifiziert"] = False
        st.rerun()

# --- HAUPTSEITE ---
st.title("📝 Einsatzliste Ordnungsamt Nacht")

with st.expander("➕ Neuer Bericht", expanded=True):
    with st.form("input_form"):
        c1, c2 = st.columns(2)
        d = c1.date_input("Datum", datetime.now())
        z = c2.time_input("Zeit", datetime.now())
        zeuge = st.text_input("Zeugen")
        
        st.write("**Kräfte:**")
        k1, k2, k3, k4 = st.columns([1,1,1,2])
        pol = k1.checkbox("Polizei")
        rd = k2.checkbox("RD")
        fs = k3.checkbox("FS")
        fs_info = k4.text_input("Details FS")
        
        text = st.text_area("Bericht")
        submit = st.form_submit_button("Speichern")

if submit and text:
    neue_zeile = pd.DataFrame([[str(d), str(z), str(zeuge), "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", str(fs_info), str(text)]], 
                             columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])
    df = lade_daten()
    pd.concat([df, neue_zeile], ignore_index=True).to_csv(DATEI, index=False)
    st.success("Gespeichert!")
    
    # Mail Link
    m_body = f"Datum: {d}\nZeit: {z}\nBericht: {text}"
    link = f"mailto:{EMPFAENGER}?subject={urllib.parse.quote(f'Einsatz {d}')}&body={urllib.parse.quote(m_body)}"
    st.link_button("📧 E-Mail senden", link)

# --- ARCHIV ---
st.divider()
daten = lade_daten()
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        # Absolut sichere Vorschau
        v_datum = row.get('Datum', 'Unbekannt')
        v_zeuge = str(row.get('Zeugen', ''))[:10]
        
        with st.expander(f"📄 {v_datum} - {v_zeuge}..."):
            st.write(f"**Bericht:** {row['Bericht']}")
            
            # Mail Link im Archiv
            m_link = f"mailto:{EMPFAENGER}?subject={urllib.parse.quote('Bericht Kopie')}&body={urllib.parse.quote(str(row['Bericht']))}"
            st.link_button("📧 Erneut senden", m_link, key=f"btn_{i}")
