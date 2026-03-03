import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# --- KONFIGURATION & MODERNES STYLING ---
st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div, .stMarkdown { color: #ffffff !important; font-family: 'Segoe UI', Roboto, sans-serif; }
    
    .main-title { 
        color: #ffffff; 
        font-size: 2.5rem; 
        font-weight: 800; 
        letter-spacing: -1px;
        border-bottom: 3px solid #004b95; 
        padding-bottom: 15px; 
        margin-bottom: 30px; 
    }

    /* MODERN ARCHIVE CARDS */
    .einsatz-card {
        background: linear-gradient(145deg, #111111, #1a1a1a);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #333;
        border-left: 8px solid #004b95;
        transition: transform 0.2s;
    }
    .einsatz-card:hover {
        transform: scale(1.01);
        border-color: #004b95;
    }
    .card-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #6ea8fe !important;
        margin-bottom: 5px;
    }
    .card-meta {
        font-size: 0.85rem;
        color: #aaaaaa !important;
        margin-bottom: 10px;
    }
    
    /* INPUT FIELDS */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #1a1a1a !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #444 !important;
    }

    /* BADGES */
    .badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 800;
        margin-right: 8px;
        text-transform: uppercase;
    }
    .b-pol { background-color: #004b95; color: white; }
    .b-rd { background-color: #8b0000; color: white; }
    .b-fs { background-color: #ffcc00; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- STRASSENLISTE AUGSBURG (Gekürzt für Code-Übersicht, erweiterbar) ---
STRASSEN_AUGSBURG = sorted([
    "Maximilianstraße", "Königsplatz", "Rathausplatz", "Annastraße", "Bahnhofstraße", "Hermanstraße", "Karlstraße", 
    "Grottenau", "Moritzplatz", "Ulrichsplatz", "Fuggerstraße", "Konrad-Adenauer-Allee", "Kennedy-Platz", "Schaezlerstraße",
    "Donauwörther Straße", "Ulmer Straße", "Hirblinger Straße", "Lechhauser Straße", "Neuburger Straße", "Blücherstraße",
    "Haunstetter Straße", "Gögginger Straße", "Friedberger Straße", "Berliner Allee", "Bgm.-Ackermann-Straße",
    "📍 Manuelle Eingabe / Sonstiger Ort"
])

PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"
LOGO_DATEI = "logo.jpg" 
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# --- FUNKTIONEN ---
def lade_daten():
    if os.path.exists(DATEI):
        return pd.read_csv(DATEI).fillna("-").astype(str)
    return pd.DataFrame(columns=["Datum", "Anfang", "Ende", "Ort", "Zusatz", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"])

# --- LOGIN ---
if "autentifiziert" not in st.session_state:
    st.session_state["autentifiziert"] = False

if not st.session_state["autentifiziert"]:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("<h1 style='text-align:center;'>🚓 Login</h1>", unsafe_allow_html=True)
        pw = st.text_input("Dienst-Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw == PASSWORT:
                st.session_state["autentifiziert"] = True
                st.rerun()
    st.stop()

# --- INTERFACE ---
st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()

with st.expander("➕ NEUEN BERICHT ERFASSEN", expanded=False):
    with st.form("modern_entry_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        d = c1.date_input("Datum", datetime.now())
        ts = c2.time_input("Beginn", datetime.now().time())
        te = c3.time_input("Ende", datetime.now().time())
        
        # NEUE ORTSANGABE MIT HAUSNUMMER/ZUSATZ
        o1, o2 = st.columns([2, 1])
        auswahl_str = o1.selectbox("Straße / Platz", options=STRASSEN_AUGSBURG)
        zusatz = o2.text_input("Nr. / Zusatz (z.B. 12a, 3. OG)")
        
        ort_tippen = ""
        if auswahl_str == "📍 Manuelle Eingabe / Sonstiger Ort":
            ort_tippen = st.text_input("Genaue Adresse manuell eingeben")
        
        finaler_ort = ort_tippen if auswahl_str == "📍 Manuelle Eingabe / Sonstiger Ort" else auswahl_str
        zeuge = st.text_input("Beteiligte Personen / Zeugen")
        
        k1, k2, k3, k4 = st.columns([1,1,1,2])
        pol = k1.checkbox("Polizei")
        rd = k2.checkbox("RD")
        fs = k3.checkbox("FS")
        fsi = k4.text_input("Details Funkstreife")
        
        txt = st.text_area("Ausführlicher Sachverhalt", height=150)
        
        if st.form_submit_button("🚀 BERICHT ABSPEICHERN", use_container_width=True):
            if txt and finaler_ort:
                new = pd.DataFrame([[str(d), ts.strftime("%H:%M"), te.strftime("%H:%M"), str(finaler_ort), str(zusatz), str(zeuge), 
                                     "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", 
                                     str(fsi), str(txt)]], columns=daten.columns)
                pd.concat([daten, new], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Bericht erfolgreich archiviert!")
                st.rerun()

# --- MODERNES ARCHIV ---
st.subheader("📂 Archivierte Berichte")
if not daten.empty:
    # Sortierung: Neueste zuerst
    for i, row in daten.iloc[::-1].iterrows():
        # Badges generieren
        pol_b = '<span class="badge b-pol">POL</span>' if row['Polizei'] == "Ja" else ""
        rd_b = '<span class="badge b-rd">RD</span>' if row['RD'] == "Ja" else ""
        fs_b = '<span class="badge b-fs">FS</span>' if row['FS'] == "Ja" else ""
        
        st.markdown(f"""
            <div class="einsatz-card">
                <div class="card-header">📍 {row['Ort']} {row['Zusatz']}</div>
                <div class="card-meta">📅 {row['Datum']} | ⏰ {row['Anfang']} - {row['Ende']} Uhr</div>
                <div>{pol_b}{rd_b}{fs_b}</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Bericht öffnen / Bearbeiten"):
            st.info(f"**Beteiligte:** {row['Zeugen']}\n\n**Sachverhalt:**\n{row['Bericht']}")
            if st.button("🗑️ Löschen", key=f"del_{i}"):
                daten = daten.drop(i)
                daten.to_csv(DATEI, index=False)
                st.rerun()
else:
    st.info("Noch keine Berichte vorhanden.")
