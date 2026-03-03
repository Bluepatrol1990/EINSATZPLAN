import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- SETTINGS ---
st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

# Passwörter (Hier kannst du dein persönliches Admin-Passwort ändern)
DIENST_PW = "1234" 
ADMIN_PW = "admin789" # Nur dieses Passwort erlaubt das Bearbeiten/Löschen

DATEI = "zentral_archiv.csv"

# --- STYLING (DARK MODE) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div, .stMarkdown { color: #ffffff !important; }
    .main-title { color: #ffffff; font-size: 2.5rem; font-weight: 800; border-bottom: 3px solid #004b95; padding-bottom: 15px; margin-bottom: 30px; }
    .einsatz-card { background: linear-gradient(145deg, #111111, #1a1a1a); border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid #333; border-left: 8px solid #004b95; }
    .card-header { font-size: 1.3rem; font-weight: bold; color: #6ea8fe !important; }
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; margin-right: 8px; text-transform: uppercase; display: inline-block; }
    .b-pol { background-color: #004b95; color: white; }
    .b-rd { background-color: #8b0000; color: white; }
    .b-fs { background-color: #ffcc00; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- DATEN LADEN ---
def lade_daten():
    spalten = ["Datum", "Anfang", "Ende", "Ort", "Zusatz", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"]
    if os.path.exists(DATEI):
        df = pd.read_csv(DATEI)
        for s in spalten:
            if s not in df.columns: df[s] = "-"
        return df[spalten].fillna("-").astype(str)
    return pd.DataFrame(columns=spalten)

# --- LOGIN LOGIK ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "is_admin" not in st.session_state: st.session_state["is_admin"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("<h1 style='text-align:center;'>🚓 Dienst-Login</h1>", unsafe_allow_html=True)
        if st.text_input("Passwort", type="password") == DIENST_PW:
            if st.button("Anmelden", use_container_width=True):
                st.session_state["auth"] = True
                st.rerun()
    st.stop()

# --- SIDEBAR (ADMIN-RECHTE) ---
with st.sidebar:
    st.title("⚙️ Verwaltung")
    if not st.session_state["is_admin"]:
        admin_check = st.text_input("Admin-Passwort für Bearbeitung", type="password")
        if st.button("Admin-Modus aktivieren"):
            if admin_check == ADMIN_PW:
                st.session_state["is_admin"] = True
                st.success("Bearbeitungsmodus aktiv!")
                st.rerun()
            else:
                st.error("Falsches Passwort")
    else:
        st.warning("🔓 Admin-Modus AKTIV")
        if st.button("Admin-Modus beenden"):
            st.session_state["is_admin"] = False
            st.rerun()
    
    st.divider()
    if st.button("🔴 Logout"):
        st.session_state["auth"] = False
        st.rerun()

# --- HAUPTBEREICH ---
st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()

# Neuen Bericht erfassen (Immer für alle erlaubt)
with st.expander("➕ NEUEN BERICHT ERFASSEN"):
    with st.form("new_report"):
        # ... (Felder wie vorher: Datum, Ort, Bericht etc.)
        st.info("Alle Kollegen können hier Berichte einspeisen.")
        if st.form_submit_button("Speichern"):
            # Speichercode hier einfügen
            pass

# --- ARCHIV ---
st.subheader("📂 Archiv")
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        st.markdown(f"""
            <div class="einsatz-card">
                <div class="card-header">📍 {row['Ort']} {row.get('Zusatz', '-')}</div>
                <div class="card-meta">📅 {row['Datum']} | {row['Anfang']} Uhr</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Details anzeigen"):
            st.info(row['Bericht'])
            
            # DIESER TEIL IST NUR FÜR DICH SICHTBAR (ADMIN)
            if st.session_state["is_admin"]:
                st.divider()
                st.subheader("🛠️ Admin-Optionen")
                if st.button(f"🗑️ Bericht {i} endgültig löschen", key=f"del_{i}"):
                    daten = daten.drop(i)
                    daten.to_csv(DATEI, index=False)
                    st.success("Gelöscht!")
                    st.rerun()
            else:
                st.caption("🔒 Bearbeitung durch Admin-Passwort geschützt.")
