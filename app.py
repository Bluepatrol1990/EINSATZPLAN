import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# --- DESIGN-KONFIGURATION ---
st.set_page_config(page_title="Einsatzliste OA Nacht", page_icon="🚓", layout="wide")

# CSS für modernes Interface
st.markdown("""
    <style>
    .report-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        border-left: 6px solid #004b95;
        margin-bottom: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

PASSWORT = "1234" 
DATEI = "zentral_archiv.csv"

# --- LOGIN-LOGIK ---
if "autentifiziert" not in st.session_state:
    st.session_state["autentifiziert"] = False

if not st.session_state["autentifiziert"]:
    st.title("🔐 Sicherheits-Login")
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
    # Wir definieren, welche Spalten wir MINDESTENS brauchen
    spalten_soll = ["Datum", "Zeit", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"]
    
    if os.path.exists(DATEI):
        try:
            df = pd.read_csv(DATEI)
            
            # Fehlerbehebung für alte Spaltennamen (Rettungsdienst -> RD)
            if "Rettungsdienst" in df.columns and "RD" not in df.columns:
                df = df.rename(columns={"Rettungsdienst": "RD"})
            if "Funkstreife" in df.columns and "FS" not in df.columns:
                df = df.rename(columns={"Funkstreife": "FS"})
                
            # Fehlende Spalten ergänzen, damit es keinen Crash gibt
            for col in spalten_soll:
                if col not in df.columns:
                    df[col] = ""
                    
            return df.fillna("").astype(str)
        except:
            pass
    return pd.DataFrame(columns=spalten_soll)

def erstelle_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="EINSATZPROTOKOLL - ORDNUNGSAMT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    content = [
        f"Datum: {row['Datum']} | Zeit: {row['Zeit']}",
        f"Zeugen: {row['Zeugen']}",
        f"Kräfte: Pol: {row['Polizei']} | RD: {row['RD']} | FS: {row['FS']} ({row['FS_Details']})",
        "-"*30,
        "Sachverhalt:",
        str(row['Bericht'])
    ]
    
    for line in content:
        clean_line = line.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
        pdf.multi_cell(0, 10, txt=clean_line)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- SIDEBAR ---
with st.sidebar:
    st.title("🚓 Optionen")
    if st.button("🔴 Logout / Sperren"):
        st.session_state["autentifiziert"] = False
        st.rerun()
    st.divider()
    st.write("Einsatzliste v3.0")

# --- HAUPTBEREICH ---
st.title("📝 Einsatzliste Ordnungsamt")

# Eingabe
with st.expander("➕ Neuen Einsatzbericht schreiben", expanded=True):
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        d = c1.date_input("Datum", datetime.now())
        z = c2.time_input("Uhrzeit", datetime.now())
        zeuge = st.text_input("Beteiligte Personen / Zeugen")
        
        st.write("**Hinzugezogene Kräfte**")
        k1, k2, k3, k4 = st.columns([1,1,1,2])
        pol = k1.checkbox("Polizei")
        rd = k2.checkbox("RD")
        fs = k3.checkbox("FS")
        fs_info = k4.text_input("Details FS (Wagen/Name)")
        
        bericht_text = st.text_area("Ausführlicher Bericht")
        
        if st.form_submit_button("✅ Bericht speichern & Archivieren", use_container_width=True):
            if bericht_text:
                neue_zeile = pd.DataFrame([[str(d), str(z), str(zeuge), 
                                            "Ja" if pol else "Nein", 
                                            "Ja" if rd else "Nein", 
                                            "Ja" if fs else "Nein", 
                                            str(fs_info), str(bericht_text)]], 
                                         columns=["Datum", "Zeit", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"])
                df = lade_daten()
                pd.concat([df, neue_zeile], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Gespeichert!")
                st.rerun()

# --- ARCHIV ---
st.divider()
st.subheader("📚 Archivierte Berichte")
daten = lade_daten()

if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        # Karten-Vorschau
        st.markdown(f"""
            <div class="report-card">
                <strong>📅 {row['Datum']} | ⏰ {row['Zeit']}</strong><br>
                <small>Beteiligt: {row['Zeugen'][:30]}...</small>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Vollständigen Bericht lesen"):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"**Kräfte:** Pol: {row['Polizei']} | RD: {row['RD']} | FS: {row['FS']} ({row['FS_Details']})")
                st.info(row['Bericht'])
            with col_b:
                st.download_button("📄 PDF Export", erstelle_pdf(row), f"Einsatz_{i}.pdf", "application/pdf", key=f"pdf_{i}")
else:
    st.info("Keine Einträge vorhanden.")
