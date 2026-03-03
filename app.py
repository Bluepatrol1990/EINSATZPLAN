import streamlit as st
import pandas as pd
import os
from datetime import datetime
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
    .einsatz-card { background: #151515; border-radius: 12px; padding: 20px; margin-bottom: 15px; border: 1px solid #333; border-left: 10px solid #004b95; }
    .card-meta { color: #888; font-size: 0.95rem; margin-top: 5px; }
    .card-zeugen { background: #222; padding: 8px; border-radius: 5px; margin-top: 10px; font-size: 0.9rem; color: #ccc !important; }
    </style>
    """, unsafe_allow_html=True)

# --- KONSTANTEN & XL-STRASSENLISTE AUGSBURG ---
DIENST_PW = "1234"
DATEI = "zentral_archiv.csv"

# Massiv erweiterte Liste (Auszug der wichtigsten Orte)
STRASSEN_AUGSBURG = sorted([
    # Zentrum / Plätze
    "Maximilianstraße", "Königsplatz", "Rathausplatz", "Moritzplatz", "Ulrichsplatz", "Klinkerberg",
    "Annastraße", "Bahnhofstraße", "Hermanstraße", "Karlstraße", "Grottenau", "Fuggerstraße", 
    "Konrad-Adenauer-Allee", "Elias-Holl-Platz", "Holbeinplatz", "Zeugplatz", "Judenberg",
    # Hauptverkehrsstraßen
    "Haunstetter Straße", "Gögginger Straße", "Friedberger Straße", "Berliner Allee", "Bgm.-Ackermann-Straße",
    "Donauwörther Straße", "Ulmer Straße", "Hirblinger Straße", "Lechhauser Straße", "Neuburger Straße",
    "Schertlinstraße", "Prinzregentenstraße", "Viktoriastraße", "Schaezlerstraße", "Halderstraße",
    "Imhofstraße", "Inninger Straße", "Landsberger Straße", "Stuttgarter Straße", "Pferseer Straße",
    # Stadtteile / Gebiete
    "Lechhausen (Zentrum)", "Oberhausen (Zentrum)", "Pfersee (Zentrum)", "Hochzoll (Zentrum)", 
    "Bärenkeller", "Kriegshaber", "Firnhaberau", "Hammerschmiede", "Herrenbach", "Spickel",
    "Universitätsviertel", "Textilviertel", "Siebentischwald / Park", "Kuhsee-Areal", "Autobahnsee",
    # Wichtige Seitenstraßen & Brennpunkte
    "Jakoberstraße", "Pilgerhausstraße", "Barfüßerstraße", "Mittlerer Graben", "Oberer Graben",
    "Vorderer Lech", "Hinterer Lech", "Schmiedberg", "Metzgplatz", "Leonhardsberg",
    "Kesselmarkt", "Heilig-Kreuz-Straße", "Frauentorstraße", "Hoher Weg", "Karolinenstraße",
    "📍 Sonstiger Ort / Manuelle Eingabe"
])

# --- FUNKTIONEN ---
def lade_daten():
    spalten = ["Datum", "Uhrzeit", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto"]
    if os.path.exists(DATEI):
        df = pd.read_csv(DATEI)
        for s in spalten:
            if s not in df.columns: df[s] = "-"
        return df[spalten].fillna("-").astype(str)
    return pd.DataFrame(columns=spalten)

def bild_zu_base64(bild_datei):
    if bild_datei:
        img = Image.open(bild_datei)
        img.thumbnail((800, 800))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=75)
        return base64.b64encode(buffered.getvalue()).decode()
    return "-"

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if not st.session_state["auth"]:
    st.title("🚓 Dienst-Login Ordnungsamt")
    pw_input = st.text_input("Dienst-Passwort", type="password")
    if st.button("Anmelden") and pw_input == DIENST_PW:
        st.session_state["auth"] = True; st.rerun()
    st.stop()

# --- HAUPTBEREICH ---
st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()

# --- FORMULAR ---
with st.expander("➕ NEUEN EINSATZBERICHT SCHREIBEN", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([2,1,1])
        d = c1.date_input("Datum", datetime.now())
        uhr = c2.time_input("Uhrzeit", datetime.now().time())
        az = c3.text_input("Aktenzeichen (POL)")
        
        o1, o2 = st.columns([3,1])
        auswahl_str = o1.selectbox("Straße / Platz auswählen (Tippen zum Suchen)", options=STRASSEN_AUGSBURG)
        hsnr = o2.text_input("Hausnr.")
        
        final_ort = auswahl_str
        if auswahl_str == "📍 Sonstiger Ort / Manuelle Eingabe":
            final_ort = st.text_input("Genaue Adresse manuell eingeben")
            
        zeuge = st.text_input("Beteiligte Personen / Zeugen / Geschädigte")
        
        # XL-Sachverhalt Feld
        txt = st.text_area("Sachverhalt / Feststellungen", height=250, placeholder="Genaue Beschreibung des Vorfalls...")
        
        st.write("---")
        foto_aktiv = st.checkbox("📸 Foto zur Beweissicherung hinzufügen")
        foto_datei = None
        if foto_aktiv:
            foto_datei = st.file_uploader("Kamera oder Galerie öffnen", type=['jpg', 'jpeg', 'png'])
        
        if st.form_submit_button("🚀 BERICHT SPEICHERN", use_container_width=True):
            if txt and final_ort:
                foto_b64 = bild_zu_base64(foto_datei) if foto_datei else "-"
                new_row = pd.DataFrame([[str(d), uhr.strftime("%H:%M"), str(final_ort), str(hsnr), str(zeuge), str(txt), str(az), foto_b64]], columns=daten.columns)
                pd.concat([daten, new_row], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Bericht erfolgreich gespeichert!")
                st.rerun()

# --- ARCHIV ---
st.subheader("📂 Archiv")
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        st.markdown(f"""
            <div class="einsatz-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:1.3rem; font-weight:bold; color:#6ea8fe;">📍 {row['Ort']} {row['Hausnummer']}</span>
                    <span style="font-weight:bold; color:#aaa;">🆔 AZ: {row['AZ']}</span>
                </div>
                <div class="card-meta">📅 {row['Datum']} | 🕒 {row['Uhrzeit']} Uhr</div>
                <div class="card-zeugen"><b>👥 Beteiligte:</b> {row['Zeugen']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Details anzeigen"):
            st.info(f"**Sachverhalt:**\n\n{row['Bericht']}")
            if row['Foto'] != "-":
                st.image(base64.b64decode(row['Foto']), caption="Beweisfoto", width=500)
else:
    st.info("Keine Berichte vorhanden.")
