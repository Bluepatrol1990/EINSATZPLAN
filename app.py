import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# --- DESIGN-KONFIGURATION ---
st.set_page_config(page_title="Einsatzliste OA Nacht", page_icon="🚓", layout="wide")

# Eigenes CSS für einen moderneren Look
st.markdown("""
    <style>
    .report-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #004b95;
        margin-bottom: 10px;
    }
    .stButton>button {
        border-radius: 20px;
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
    with st.container():
        eingabe = st.text_input("Dienst-Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if eingabe == PASSWORT:
                st.session_state["autentifiziert"] = True
                st.rerun()
            else:
                st.error("Passwort ungültig.")
    st.stop()

# --- DATEN-FUNKTIONEN ---
def lade_daten():
    if os.path.exists(DATEI):
        try:
            df = pd.read_csv(DATEI).fillna("").astype(str)
            return df
        except:
            pass
    return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"])

def erstelle_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="EINSATZPROTOKOLL - ORDNUNGSAMT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    text = f"Datum: {row['Datum']} | Zeit: {row['Zeit']}\n"
    text += f"Zeugen: {row['Zeugen']}\n"
    text += f"Kräfte: Pol: {row['Polizei']} | RD: {row['RD']} | FS: {row['FS']} ({row['FS_Details']})\n"
    text += "-"*40 + "\n"
    text += f"Sachverhalt:\n{row['Bericht']}"
    
    clean_text = text.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/police-badge.png")
    st.title("Navigation")
    if st.button("🔴 Logout", use_container_width=True):
        st.session_state["autentifiziert"] = False
        st.rerun()

# --- HAUPTBEREICH ---
st.title("🚓 Einsatzliste Ordnungsamt Nacht")

# Eingabe-Bereich in einer schönen Spaltenansicht
with st.container():
    st.subheader("📝 Neuen Einsatz erfassen")
    with st.form("input_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 2])
        d = c1.date_input("Einsatzdatum", datetime.now())
        z = c2.time_input("Uhrzeit", datetime.now())
        zeuge = c3.text_input("Beteiligte / Zeugen")
        
        st.write("**Hinzugezogene Kräfte**")
        k1, k2, k3, k4 = st.columns([1, 1, 1, 2])
        pol = k1.checkbox("Polizei")
        rd = k2.checkbox("RD")
        fs = k3.checkbox("FS")
        fs_info = k4.text_input("Funkstreife Details (Name/Wagen)")
        
        text = st.text_area("Sachverhalt / Bericht", height=150)
        
        if st.form_submit_button("💾 Einsatzbericht speichern", use_container_width=True):
            if text:
                neue_zeile = pd.DataFrame([[str(d), str(z), str(zeuge), 
                                            "Ja" if pol else "Nein", 
                                            "Ja" if rd else "Nein", 
                                            "Ja" if fs else "Nein", 
                                            str(fs_info), str(text)]], 
                                         columns=["Datum", "Zeit", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"])
                df = lade_daten()
                pd.concat([df, neue_zeile], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Erfolgreich im Archiv gespeichert!")
                st.rerun()
            else:
                st.warning("Bitte gib einen Berichtstext ein.")

# --- ARCHIV ---
st.divider()
st.subheader("📚 Protokoll-Archiv")
daten = lade_daten()

if not daten.empty:
    # Neueste Berichte oben
    for i, row in daten.iloc[::-1].iterrows():
        with st.container():
            # Karten-Design
            st.markdown(f"""
                <div class="report-card">
                    <strong>📅 {row['Datum']} | ⏰ {row['Zeit']}</strong><br>
                    <small>Zeugen: {row['Zeugen'] if row['Zeugen'] else 'Keine'}</small>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Details anzeigen & PDF Export"):
                col_left, col_right = st.columns([3, 1])
                with col_left:
                    st.write(f"**Kräfte:** Polizei: {row['Polizei']} | Rettungsdienst: {row['RD']} | Funkstreife: {row['FS']} ({row['FS_Details']})")
                    st.info(row['Bericht'])
                with col_right:
                    pdf_data = erstelle_pdf(row)
                    st.download_button(
                        label="📄 PDF Download",
                        data=pdf_data,
                        file_name=f"Bericht_{row['Datum']}_{i}.pdf",
                        mime="application/pdf",
                        key=f"dl_{i}",
                        use_container_width=True
                    )
else:
    st.info("Das Archiv ist noch leer.")
