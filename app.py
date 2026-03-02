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
            return pd.read_csv(DATEI)
        except:
            return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])
    return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])

# --- SIDEBAR (ABMELDEN) ---
with st.sidebar:
    if st.button("🔴 Abmelden / Sperren"):
        st.session_state["autentifiziert"] = False
        st.rerun()

# --- HAUPTSEITE ---
st.title("📝 Einsatzliste Ordnungsamt Nacht")

with st.expander("➕ Neuen Bericht erstellen", expanded=True):
    with st.form("input_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        d = col1.date_input("Datum", datetime.now())
        z = col2.time_input("Zeit", datetime.now())
        zeuge = st.text_input("Zeugen / Beteiligte")
        
        st.write("**Hinzugezogene Kräfte:**")
        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        pol = c1.checkbox("Polizei")
        rd = c2.checkbox("Rettungsdienst")
        fs = c3.checkbox("Funkstreife")
        fs_info = c4.text_input("Details Funkstreife", placeholder="Wagen / Name")
        
        text = st.text_area("Bericht / Sachverhalt")
        submit = st.form_submit_button("Bericht Speichern")

if submit and text:
    neue_zeile = pd.DataFrame([[
        str(d), str(z), zeuge, 
        "Ja" if pol else "Nein", 
        "Ja" if rd else "Nein", 
        "Ja" if fs else "Nein", 
        fs_info, text
    ]], columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])
    
    df = lade_daten()
    df = pd.concat([df, neue_zeile], ignore_index=True)
    df.to_csv(DATEI, index=False)
    st.success("✅ Bericht gespeichert!")
    
    # E-Mail Link sicher bauen
    empfaenger = "Kevin.woelki@augsburg.de,kevinworlki@outlook.de"
    betreff = f"Einsatzbericht {d} {z}"
    mail_body = f"Datum: {d}\nZeit: {z}\nZeugen: {zeuge}\nKräfte: Pol:{'Ja' if pol else 'Nein'}, RD:{'Ja' if rd else 'Nein'}, FS:{'Ja' if fs else 'Nein'} ({fs_info})\n\nBericht:\n{text}"
    
    # WICHTIG: Komplettes Encoding des gesamten Links
    mailto_link = f"mailto:{empfaenger}?subject={urllib.parse.quote(betreff)}&body={urllib.parse.quote(mail_body)}"
    
    st.link_button("📧 E-Mail an Zentrale senden", mailto_link, use_container_width=True)

# --- ARCHIV ---
st.divider()
st.subheader("📚 Zentrales Archiv")
daten = lade_daten()
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        with st.expander(f"📄 {row['Datum']} - {row['Zeit']} - {row['Zeugen'][:15]}..."):
            st.write(f"**Bericht:** {row['Bericht']}")
            
            # Link im Archiv ebenfalls absichern
            m_empf = "Kevin.woelki@augsburg.de,kevinworlki@outlook.de"
            m_subj = urllib.parse.quote(f"Kopie Bericht {row['Datum']}")
            m_body = urllib.parse.quote(f"Bericht vom {row['Datum']}:\n\n{row['Bericht']}")
            
            # Hier bauen wir den Link so zusammen, dass keine Leerzeichen stören
            final_link = f"mailto:{m_empf}?subject={m_subj}&body={m_body}"
            
            st.link_button("📧 Erneut senden", final_link, key=f"arch_mail_{i}")
