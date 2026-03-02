import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import PIL.Image

# --- DESIGN-KONFIGURATION ---
st.set_page_config(page_title="Einsatzliste OA Nacht", page_icon="🚓", layout="wide")

# Eigenes CSS für modernes Interface und offizielle Farben
st.markdown("""
    <style>
    .report-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 15px;
        border-left: 6px solid #004b95;
        margin-bottom: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    }
    .card-header {
        font-size: 1.1rem;
        font-weight: bold;
        color: #004b95;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    /* Hintergrundbild für die gesamte App (optional, falls gewünscht) */
    /*
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1599420186946-7b6fb4e297f0?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
    }
    */
    </style>
    """, unsafe_allow_html=True)

PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"
LOGO_DATEI = "logo.png" # Name deiner Bilddatei auf GitHub

# Augsburger Orte (erweiterbar)
AUGSBURG_STRASSEN = [
    "Maximilianstraße", "Königsplatz", "Rathausplatz", "Annastraße", "Bahnhofstraße",
    "Hermanstraße", "Karlstraße", "Grottenau", "Moritzplatz", "Ulrichsplatz",
    "Jakoberstraße", "Viktoriastraße", "Prinzregentenstraße", "Ludwigstraße",
    "Oberer Graben", "Unterer Graben", "Vorderer Lech", "Donauwörther Straße",
    "Haunstetter Straße", "Gögginger Straße", "Berliner Allee", "Friedberger Straße"
]
AUGSBURG_STRASSEN.sort()

# --- LOGIN-LOGIK ---
if "autentifiziert" not in st.session_state:
    st.session_state["autentifiziert"] = False

if not st.session_state["autentifiziert"]:
    st.title("🔐 Sicherheits-Login")
    # Logo auch auf dem Login-Bildschirm anzeigen, falls vorhanden
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, width=200)
        
    eingabe = st.text_input("Dienst-Passwort", type="password")
    if st.button("Anmelden", use_container_width=True):
        if eingabe == PASSWORT:
            st.session_state["autentifiziert"] = True
            st.rerun()
        else:
            st.error("Passwort falsch.")
    st.stop()

# --- DATEN-FUNKTIONEN ---
def lade_daten():
    spalten_soll = ["Datum", "Anfang", "Ende", "Ort", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"]
    if os.path.exists(DATEI):
        try:
            df = pd.read_csv(DATEI)
            for col in spalten_soll:
                if col not in df.columns: df[col] = "-"
            return df.fillna("-").astype(str)
        except: pass
    return pd.DataFrame(columns=spalten_soll)

def erstelle_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo im PDF einfügen, falls vorhanden
    if os.path.exists(LOGO_DATEI):
        pdf.image(LOGO_DATEI, 10, 8, 33)
        pdf.ln(20) # Platz nach dem Logo lassen
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="EINSATZPROTOKOLL", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    text = (f"Datum: {row['Datum']}\n"
            f"Zeitraum: {row['Anfang']} bis {row['Ende']}\n"
            f"Ort: {row['Ort']}\n"
            f"Zeugen: {row['Zeugen']}\n"
            f"Kräfte: Pol: {row['Polizei']} | RD: {row['RD']} | FS: {row['FS']}\n\n"
            f"Bericht:\n{row['Bericht']}")
    clean = text.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
    pdf.multi_cell(0, 10, txt=clean)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- SIDEBAR (mit Logo) ---
with st.sidebar:
    # Das Bild in der Sidebar anzeigen, falls vorhanden
    if os.path.exists(LOGO_DATEI):
        st.image(LOGO_DATEI, use_container_width=True)
        st.divider()
    
    st.title("🚓 Steuerung")
    if st.button("🔴 Logout", use_container_width=True):
        st.session_state["autentifiziert"] = False
        st.rerun()
    st.divider()
    st.subheader("🔍 Archiv-Filter")
    filter_datum = st.date_input("Nach Datum suchen", value=None)
    filter_ort = st.text_input("Nach Ort suchen")

# --- HAUPTBEREICH ---
st.title("📝 Einsatzliste Ordnungsamt")

with st.expander("➕ Neuen Bericht erfassen", expanded=True):
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        d = c1.date_input("Datum", datetime.now())
        t_start = c2.time_input("Anfang", datetime.now().time())
        t_end = c3.time_input("Ende", datetime.now().time())
        
        ort = st.selectbox("Ort / Straße", options=["Manuelle Eingabe"] + AUGSBURG_STRASSEN)
        if ort == "Manuelle Eingabe":
            ort_final = st.text_input("Genaue Adresse")
        else:
            ort_final = ort
        
        zeuge = st.text_input("Zeugen / Beteiligte")
        
        st.write("**Kräfte**")
        k1, k2, k3, k4 = st.columns([1,1,1,2])
        pol = k1.checkbox("Polizei")
        rd = k2.checkbox("RD")
        fs = k3.checkbox("FS")
        fs_info = k4.text_input("Details FS")
        
        bericht_text = st.text_area("Bericht")
        
        if st.form_submit_button("✅ Speichern", use_container_width=True):
            if bericht_text and ort_final:
                neue_zeile = pd.DataFrame([[
                    str(d), t_start.strftime("%H:%M"), t_end.strftime("%H:%M"), 
                    str(ort_final), str(zeuge), 
                    "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", 
                    str(fs_info), str(bericht_text)
                ]], columns=["Datum", "Anfang", "Ende", "Ort", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"])
                
                df = lade_daten()
                pd.concat([df, neue_zeile], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Gespeichert!")
                st.rerun()
            else:
                st.error("Bericht und Ort ausfüllen!")

# --- ARCHIV ---
st.divider()
st.subheader("📚 Archiv")
daten = lade_daten()

if not daten.empty:
    if filter_datum:
        daten = daten[daten['Datum'] == str(filter_datum)]
    if filter_ort:
        daten = daten[daten['Ort'].str.contains(filter_ort, case=False)]

    for i, row in daten.iloc[::-1].iterrows():
        st.markdown(f"""
            <div class="report-card">
                <div class="card-header">📅 {row['Datum']} | 📍 {row['Ort']}</div>
                <div style="font-size: 0.9rem; color: #666;">⏰ {row['Anfang']} - {row['Ende']} &nbsp; | &nbsp; {row['Zeugen'][:30]}...</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Bericht anzeigen"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Ort:** {row['Ort']} | Kräfte: Pol:{row['Polizei']}, RD:{row['RD']}, FS:{row['FS']}")
                st.info(row['Bericht'])
            with col2:
                st.download_button("📄 PDF", erstelle_pdf(row), f"Einsatz_{i}.pdf", "application/pdf", key=f"p_{i}", use_container_width=True)
else:
    st.info("Das Archiv ist leer.")
