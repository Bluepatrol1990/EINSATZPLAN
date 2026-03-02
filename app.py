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
            df = pd.read_csv(DATEI)
            # WICHTIG: Leere Felder mit leerem Text füllen, um Abstürze zu vermeiden
            return df.fillna("")
        except:
            pass
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
        str(d), str(z), zeuge if zeuge else "Keine", 
        "Ja" if pol else "Nein", 
        "Ja" if rd else "Nein", 
        "Ja" if fs else "Nein", 
        fs_info, text
    ]], columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "FS_Details", "Bericht"])
    
    df = lade_daten()
    df = pd.concat([df, neue_zeile], ignore_index=True)
    df.to_csv(DATEI, index=False)
    st.success("✅ Bericht gespeichert!")
    
    # E-Mail Link bauen
    betreff = f"Einsatzbericht {d} {z}"
    mail_body = f"Datum: {d}\nZeit: {z}\nZeugen: {zeuge}\nKräfte: Pol:{'Ja' if pol else 'Nein'}, RD:{'Ja' if rd else 'Nein'}, FS:{'Ja' if fs else 'Nein'} ({fs_info})\n\nBericht:\n{text}"
    mailto_link = f"mailto:{EMPFAENGER}?subject={urllib.parse.quote(betreff)}&body={urllib.parse.quote(mail_body)}"
    
    st.link_button("📧 E-Mail an Zentrale senden", mailto_link, use_container_width=True)

# --- ARCHIV ---
st.divider()
st.subheader("📚 Zentrales Archiv")
daten = lade_daten()

if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        # FEHLER-FIX: Falls Zeugen leer ist, wird ein Standardtext genutzt
        zeugen_vorschau = str(row['Zeugen'])[:15] if row['Zeugen'] else "Keine Angabe"
        
        with st.expander(f"📄 {row['Datum']} - {row['Zeit']} - {zeugen_vorschau}..."):
            st.write(f"**Zeugen:** {row['Zeugen']}")
            st.write(f"**Kräfte:** Polizei: {row['Polizei']} | RD: {row['Rettungsdienst']} | FS: {row['Funkstreife']} ({row['FS_Details']})")
            st.info(f"**Bericht:**\n\n{row['Bericht']}")
            
            # Mail Link im Archiv
            m_subj = urllib.parse.quote(f"Kopie Bericht {row['Datum']}")
            m_body = urllib.parse.quote(f"Bericht vom {row['Datum']}:\n\n{row['Bericht']}")
            st.link_button("📧 Erneut senden", f"mailto:{EMPFAENGER}?subject={m_subj}&body={m_body}", key=f"arch_mail_{i}")
else:
    st.info("Noch keine Berichte im Archiv.")
