import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64
from PIL import Image
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation
from fpdf import FPDF  # Neu: Für PDF-Erstellung

# --- 1. GLOBALE VARIABLEN ---
DATEI = "zentral_archiv_secure.csv"
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]

# --- PDF GENERATOR FUNKTION ---
def create_pdf(daten_reihe, bericht_text, zeugen_text, kraefte_text, foto_b64):
    pdf = FPDF()
    pdf.add_page()
    
    # Header: Stadt Augsburg
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "Stadt Augsburg", ln=True, align="C")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(0, 10, "Ordnungsamt - Kommunaler Ordnungsdienst (KOD)", ln=True, align="C")
    pdf.ln(10)
    
    # Titel
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, f"Einsatzbericht - AZ: {daten_reihe['AZ']}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Stammdaten Tabelle
    pdf.set_font("helvetica", "", 11)
    pdf.cell(40, 8, "Datum:", border=0)
    pdf.cell(0, 8, str(daten_reihe['Datum']), border=0, ln=True)
    pdf.cell(40, 8, "Zeitraum:", border=0)
    pdf.cell(0, 8, f"{daten_reihe['Beginn']} - {daten_reihe['Ende']} Uhr", border=0, ln=True)
    pdf.cell(40, 8, "Ort:", border=0)
    pdf.cell(0, 8, f"{daten_reihe['Ort']} {daten_reihe['Hausnummer']}", border=0, ln=True)
    pdf.cell(40, 8, "Einsatzkräfte:", border=0)
    pdf.cell(0, 8, kraefte_text, border=0, ln=True)
    pdf.ln(5)
    
    # Sachverhalt
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Sachverhalt / Feststellungen:", ln=True)
    pdf.set_font("helvetica", "", 11)
    pdf.multi_cell(0, 7, bericht_text)
    pdf.ln(5)
    
    # Beteiligte
    if zeugen_text != "-":
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "Beteiligte / Zeugen:", ln=True)
        pdf.set_font("helvetica", "", 11)
        pdf.multi_cell(0, 7, zeugen_text)
        pdf.ln(5)

    # Foto (falls vorhanden)
    if foto_b64 != "-":
        try:
            img_data = base64.b64decode(foto_b64)
            img_io = io.BytesIO(img_data)
            # Temporäres Bild für PDF
            pdf.ln(5)
            pdf.image(img_io, x=10, w=100)
        except:
            pdf.cell(0, 10, "[Foto konnte nicht geladen werden]", ln=True)

    # Fußzeile
    pdf.set_y(-30)
    pdf.set_font("helvetica", "I", 8)
    pdf.cell(0, 10, f"Erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M')} | GPS: {daten_reihe['GPS']}", align="C")
    
    return pdf.output()

# ... (Rest deines Codes bis zum Archiv bleibt gleich) ...

# --- 7. ARCHIV ---
st.divider()
st.header("📂 Einsatzarchiv")
suche = st.text_input("🔍 Suche (Ort oder AZ)")

if os.path.exists(DATEI):
    archiv_data = pd.read_csv(DATEI).astype(str)
    # Suche-Filter... (wie gehabt)
    display_data = archiv_data[(archiv_data['Ort'].str.contains(suche, case=False)) | (archiv_data['AZ'].str.contains(suche, case=False))] if suche else archiv_data

    for i, r in display_data.iloc[::-1].iterrows():
        akt_bericht = entschluesseln(r['Bericht'])
        akt_kraefte = entschluesseln(r['Kraefte'])
        akt_zeugen = entschluesseln(r['Zeugen'])
        akt_foto = entschluesseln(r['Foto'])

        st.markdown(f"""
        <div class="report-card">
            <strong>📅 {r['Datum']} | 📍 {r['Ort']} {r['Hausnummer']}</strong> (AZ: {r['AZ']})<br>
            <small>🕒 {r['Beginn']} - {r['Ende']} | 👮 {akt_kraefte}</small>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📝 Details & Sachverhalt"):
            st.write(f"**Sachverhalt:**\n{akt_bericht}")
            if akt_zeugen != "-": st.write(f"**👥 Beteiligte:** {akt_zeugen}")
            if akt_foto != "-": st.image(base64.b64decode(akt_foto), width=400)
            
            # ADMIN FUNKTIONEN
            if st.session_state["admin_auth"]:
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    # PDF GENERIEREN
                    pdf_bytes = create_pdf(r, akt_bericht, akt_zeugen, akt_kraefte, akt_foto)
                    st.download_button(
                        label="📄 Als PDF downloaden",
                        data=pdf_bytes,
                        file_name=f"Einsatzbericht_{r['AZ']}_{r['Datum']}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{i}"
                    )
                
                with col_btn2:
                    if st.button(f"🗑️ Bericht löschen", key=f"del_{i}"):
                        updated_df = archiv_data.drop(i)
                        updated_df.to_csv(DATEI, index=False)
                        st.rerun()
