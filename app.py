import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io
import base64
from PIL import Image

# --- STYLING ---
st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div, .stMarkdown { color: #ffffff !important; }
    .main-title { font-size: 2.5rem; font-weight: 800; border-bottom: 3px solid #004b95; padding-bottom: 10px; margin-bottom: 30px; }
    
    /* Status-Farben für die Karten-Ränder */
    .card-offen { border-left: 10px solid #ff4b4b !important; }
    .card-arbeit { border-left: 10px solid #ffcc00 !important; }
    .card-done { border-left: 10px solid #28a745 !important; }
    
    .einsatz-card { background: #151515; border-radius: 12px; padding: 20px; margin-bottom: 15px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- KONSTANTEN ---
DIENST_PW = "1234"
ADMIN_PW = "admin789"
DATEI = "zentral_archiv.csv"
LOGO_DATEI = "logo.png"

# --- HILFSFUNKTIONEN ---
def bild_zu_base64(bild_datei):
    if bild_datei:
        img = Image.open(bild_datei)
        img.thumbnail((800, 800))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=75)
        return base64.b64encode(buffered.getvalue()).decode()
    return "-"

def lade_daten():
    # Spalte 'Status' hinzugefügt
    spalten = ["Datum", "Anfang", "Ende", "Ort", "Zusatz", "Zeugen", "Polizei", "RD", "FS", "Bericht", "AZ", "Foto", "Status"]
    if os.path.exists(DATEI):
        df = pd.read_csv(DATEI)
        for s in spalten:
            if s not in df.columns: df[s] = "Offen" if s == "Status" else "-"
        return df[spalten].fillna("-").astype(str)
    return pd.DataFrame(columns=spalten)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🚓 Dienst-Login Ordnungsamt")
    if st.text_input("Dienst-Passwort", type="password") == DIENST_PW:
        if st.button("Anmelden"): st.session_state["auth"] = True; st.rerun()
    st.stop()

# --- HAUPTBEREICH ---
st.markdown("<div class='main-title'>📋 Einsatzbericht & Status-Zentrale</div>", unsafe_allow_html=True)
daten = lade_daten()

# --- FORMULAR ---
with st.expander("➕ NEUEN BERICHT SCHREIBEN", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2,1,1])
        ort = c1.text_input("Einsatzort")
        d = c2.date_input("Datum", datetime.now())
        status_neu = c3.selectbox("Priorität/Status", ["Offen", "In Bearbeitung", "Abgeschlossen"])
        
        zeuge = st.text_input("Beteiligte / Zeugen")
        az = st.text_input("Aktenzeichen (POL)")
        txt = st.text_area("Sachverhalt", height=120)
        
        # FOTO-LOGIK: Kamera startet erst nach Klick auf den Button im Formular
        st.write("---")
        st.write("📷 **Beweissicherung**")
        foto_aktiv = st.checkbox("Foto jetzt aufnehmen/hochladen")
        foto_datei = None
        if foto_aktiv:
            foto_datei = st.file_uploader("Kamera/Galerie öffnen", type=['jpg', 'png'])
        
        if st.form_submit_button("🚀 BERICHT SPEICHERN", use_container_width=True):
            if txt and ort:
                foto_b64 = bild_zu_base64(foto_datei) if foto_datei else "-"
                new_row = pd.DataFrame([[str(d), "-", "-", str(ort), "-", str(zeuge), "-", "-", "-", str(txt), str(az), foto_b64, status_neu]], columns=daten.columns)
                pd.concat([daten, new_row], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Gespeichert!")
                st.rerun()

# --- ARCHIV ---
st.subheader("📂 Aktuelle Vorgänge")
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        # CSS Klasse je nach Status bestimmen
        s_class = "card-offen" if row['Status'] == "Offen" else "card-arbeit" if row['Status'] == "In Bearbeitung" else "card-done"
        icon = "🔴" if row['Status'] == "Offen" else "🟡" if row['Status'] == "In Bearbeitung" else "🟢"
        
        st.markdown(f"""
            <div class="einsatz-card {s_class}">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-size:1.2rem; font-weight:bold; color:#6ea8fe;">📍 {row['Ort']}</span>
                    <span>{icon} <b>{row['Status']}</b></span>
                </div>
                <div style="color:#888; font-size:0.9rem;">📅 {row['Datum']} | 🆔 AZ: {row['AZ']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Details & Bearbeitung"):
            st.write(f"**Bericht:** {row['Bericht']}")
            if row['Foto'] != "-":
                st.image(base64.b64decode(row['Foto']), caption="Beweisfoto", width=400)
            
            # Status direkt im Archiv ändern (für Kevin)
            if st.checkbox("Status ändern", key=f"edit_{i}"):
                neuer_status = st.radio("Neuer Status:", ["Offen", "In Bearbeitung", "Abgeschlossen"], key=f"rad_{i}")
                if st.button("Übernehmen", key=f"btn_{i}"):
                    daten.at[i, 'Status'] = neuer_status
                    daten.to_csv(DATEI, index=False)
                    st.rerun()
else:
    st.info("Keine Berichte vorhanden.")
