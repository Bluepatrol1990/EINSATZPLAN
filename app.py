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
    spalten = ["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"]
    if os.path.exists(DATEI):
        try:
            df = pd.read_csv(DATEI)
            # Sicherstellen, dass alle Spalten da sind
            for col in spalten:
                if col not in df.columns:
                    df[col] = ""
            return df.fillna("").astype(str)
        except Exception as e:
            st.warning(f"Fehler beim Laden der CSV: {e}")
    return pd.DataFrame(columns=spalten)

# --- SIDEBAR ---
with st.sidebar:
    st.write("### Menü")
    if st.button("🔴 Abmelden"):
        st.session_state["autentifiziert"] = False
        st.rerun()

# --- HAUPTSEITE ---
st.title("📝 Einsatzliste Ordnungsamt Nacht")

with st.expander("➕ Neuer Bericht", expanded=True):
    with st.form("input_form", clear_on_submit=True):
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
        submit = st.form_submit_button("💾 Speichern")

if submit and text:
    try:
        neue_zeile = pd.DataFrame([[str(d), str(z), str(zeuge), "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", str(fs_info), str(text)]], 
                                 columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])
        df = lade_daten()
        df_neu = pd.concat([df, neue_zeile], ignore_index=True)
        df_neu.to_csv(DATEI, index=False)
        st.success("✅ Bericht gespeichert!")
        
        # Sicherer Mail Link (Text kürzen für Link-Stabilität)
        safe_text = (text[:500] + '...') if len(text) > 500 else text
        m_body = f"Datum: {d}\nZeit: {z}\n\nBericht:\n{safe_text}"
        link = f"mailto:{EMPFAENGER}?subject={urllib.parse.quote(f'Einsatz {d}')}&body={urllib.parse.quote(m_body)}"
        st.link_button("📧 E-Mail an Zentrale senden", link)
    except Exception as e:
        st.error(f"Konnte nicht speichern: {e}")

# --- ARCHIV ---
st.divider()
st.subheader("📚 Zentrales Archiv")
daten = lade_daten()

if not daten.empty:
    # Neueste Einträge zuerst
    for i, row in daten.iloc[::-1].iterrows():
        # Absolut sichere Vorschau
        datum_v = row.get('Datum', 'Unbekannt')
        zeuge_v = str(row.get('Zeugen', ''))[:15]
        
        with st.expander(f"📄 {datum_v} - {zeuge_v}..."):
            st.write(f"**Zeit:** {row.get('Zeit', '')}")
            st.write(f"**Kräfte:** Pol: {row.get('Polizei', '')}, RD: {row.get('Rettungsdienst', '')}, FS: {row.get('Funkstreife', '')}")
            st.info(f"**Bericht:**\n\n{row.get('Bericht', '')}")
            
            # Mail Link im Archiv (ebenfalls Text kürzen gegen Absturz)
            arch_text = row.get('Bericht', '')
            safe_arch_text = (arch_text[:500] + '...') if len(arch_text) > 500 else arch_text
            m_link = f"mailto:{EMPFAENGER}?subject={urllib.parse.quote('Bericht Kopie')}&body={urllib.parse.quote(safe_arch_text)}"
            st.link_button("📧 Erneut senden", m_link, key=f"btn_{i}")
else:
    st.info("Noch keine Berichte vorhanden.")
