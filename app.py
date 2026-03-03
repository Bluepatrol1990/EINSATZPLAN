import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# --- SEITEN-STYLING ---
st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div, .stMarkdown { color: #ffffff !important; }
    .main-title { color: #ffffff; font-size: 2.2rem; font-weight: 800; border-bottom: 2px solid #004b95; padding-bottom: 10px; margin-bottom: 20px; }
    .einsatz-card { background-color: #111111; border-radius: 10px; padding: 15px; margin-bottom: 10px; border: 1px solid #333; border-left: 5px solid #004b95; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div { background-color: #1a1a1a !important; color: white !important; border: 1px solid #444 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MASSIVE STRASSENLISTE AUGSBURG ---
STRASSEN_AUGSBURG = sorted([
    # Zentrum / Innenstadt
    "Maximilianstraße", "Königsplatz", "Rathausplatz", "Annastraße", "Bahnhofstraße", "Hermanstraße", "Karlstraße", 
    "Grottenau", "Moritzplatz", "Ulrichsplatz", "Fuggerstraße", "Konrad-Adenauer-Allee", "Kennedy-Platz", "Schaezlerstraße",
    "Hallstraße", "Heilig-Kreuz-Straße", "Frauentorstraße", "Hoher Weg", "Karolinenstraße", "Leonhardsberg", "Pilgerhausstraße",
    # Lechhausen
    "Lechhauser Straße", "Neuburger Straße", "Blücherstraße", "Hans-Böckler-Straße", "Zugspitzstraße", "Meraner Straße",
    "Klausstraße", "Schleiermacherstraße", "Insterburger Straße", "Derchinger Straße", "Pappelweg",
    # Oberhausen / Bärenkeller
    "Donauwörther Straße", "Ulmer Straße", "Hirblinger Straße", "Wertachstraße", "Äußere Uferstraße", "Dieselstraße",
    "Gablinger Straße", "Holzweg", "Bärenstraße", "Am Katzenstadel", "Zollernstraße",
    # Haunstetten / Siebentisch
    "Haunstetter Straße", "Landsberger Straße", "Inninger Straße", "Königsbrunner Straße", "Poststraße", "Hofackerstraße",
    "Tattenbachstraße", "Siebentischstraße", "Ilsungstraße", "Brahmsstraße",
    # Göggingen
    "Gögginger Straße", "Bürgermeister-Aurnhammer-Straße", "Butzstraße", "Friedrich-Ebert-Straße", "Klausenberg",
    "Waldstraße", "Gabelsbergerstraße", "Apprichstraße",
    # Pfersee / Kriegshaber
    "Pferseer Straße", "Augsburger Straße", "Stadtberger Straße", "Bürgermeister-Ackermann-Straße", "Kobelweg",
    "Kriegshaberstraße", "Ulmer Straße", "Hessenbachstraße", "Spicherer Straße",
    # Hochzoll / Herrenbach
    "Friedberger Straße", "Hochzoller Straße", "Zugspitzstraße", "Herrenbachstraße", "Reichenberger Straße",
    "Afrawald", "Salzmannstraße", "Mittenwalder Straße",
    # Große Alleen & Ringe
    "Berliner Allee", "Schleifenstraße", "Nagahama-Allee", "Viktoriastraße", "Prinzregentenstraße", "Am Alten Einlaß",
    "Klinkerberg", "Langemarckstraße", "Holzbachstraße", "Stettenstraße", "Eichleitnerstraße",
    # Besondere Orte
    "Plärrergelände", "Hauptbahnhof", "City-Galerie", "WWK Arena", "Botanischer Garten", "Zoo Augsburg",
    "📍 Manuelle Eingabe / Nicht in Liste"
])

# --- KONSTANTEN ---
PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"
LOGO_DATEI = "logo.jpg" 
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# --- FUNKTIONEN ---
def lade_daten():
    spalten = ["Datum", "Anfang", "Ende", "Ort", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"]
    if os.path.exists(DATEI):
        return pd.read_csv(DATEI).fillna("-").astype(str)
    return pd.DataFrame(columns=spalten)

# --- LOGIN ---
if "autentifiziert" not in st.session_state:
    st.session_state["autentifiziert"] = False

if not st.session_state["autentifiziert"]:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.title("🚓 Dienst-Login")
        pw = st.text_input("Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw == PASSWORT:
                st.session_state["autentifiziert"] = True
                st.rerun()
    st.stop()

# --- INTERFACE ---
st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()

with st.expander("➕ NEUEN BERICHT ERFASSEN"):
    with st.form("entry_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        d = c1.date_input("Datum", datetime.now())
        ts = c2.time_input("Beginn", datetime.now().time())
        te = c3.time_input("Ende", datetime.now().time())
        
        # DROPDOWN MIT FILTER-FUNKTION
        auswahl_ort = st.selectbox("Genaue Ortsangabe (Suchen oder wählen)", options=STRASSEN_AUGSBURG)
        
        ort_tippen = ""
        if auswahl_ort == "📍 Manuelle Eingabe / Nicht in Liste":
            ort_tippen = st.text_input("Genaue Adresse manuell eingeben (z.B. Musterstraße 12)")
        
        finaler_ort = ort_tippen if auswahl_ort == "📍 Manuelle Eingabe / Nicht in Liste" else auswahl_ort
        zeuge = st.text_input("Beteiligte Personen / Zeugen")
        
        k1, k2, k3, k4 = st.columns([1,1,1,2])
        pol = k1.checkbox("Polizei")
        rd = k2.checkbox("RD")
        fs = k3.checkbox("FS")
        fsi = k4.text_input("Details Funkstreife")
        
        txt = st.text_area("Sachverhalt", height=150)
        
        if st.form_submit_button("🚀 BERICHT SPEICHERN", use_container_width=True):
            if txt and finaler_ort:
                new = pd.DataFrame([[str(d), ts.strftime("%H:%M"), te.strftime("%H:%M"), str(finaler_ort), str(zeuge), 
                                     "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", 
                                     str(fsi), str(txt)]], columns=daten.columns)
                pd.concat([daten, new], ignore_index=True).to_csv(DATEI, index=False)
                st.success(f"Bericht gespeichert! (Info an Kevin hinterlegt)")
                st.rerun()

# --- ARCHIV ---
st.subheader("📂 Archiv")
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        st.markdown(f"""<div class="einsatz-card"><b>📍 {row['Ort']}</b><br><small>{row['Datum']} | {row['Anfang']}-{row['Ende']} Uhr</small></div>""", unsafe_allow_html=True)
