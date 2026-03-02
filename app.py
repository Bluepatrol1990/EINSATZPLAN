import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title="Einsatz-Profi", page_icon="📝")
st.title("📝 Einsatzbericht & Versand")

DATEI = "berichte_archiv.csv"

def lade_daten():
    if os.path.exists(DATEI):
        return pd.read_csv(DATEI)
    return pd.DataFrame(columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "Bericht"])

# --- EINGABE ---
with st.form("input_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1: d = st.date_input("Datum", datetime.now())
    with col2: z = st.time_input("Zeit", datetime.now())
    
    zeuge = st.text_input("Zeugen / Beteiligte")
    
    st.write("**Hinzugezogene Kräfte:**")
    c1, c2, c3 = st.columns(3)
    pol = c1.checkbox("Polizei")
    rd = c2.checkbox("Rettungsdienst")
    fs = c3.checkbox("Funkstreife")
    
    text = st.text_area("Ausführlicher Bericht")
    submit = st.form_submit_button("Bericht Speichern")

if submit and text:
    neue_zeile = pd.DataFrame([[
        str(d), str(z), zeuge, 
        "Ja" if pol else "Nein", 
        "Ja" if rd else "Nein", 
        "Ja" if fs else "Nein", 
        text
    ]], columns=["Datum", "Zeit", "Zeugen", "Polizei", "Rettungsdienst", "Funkstreife", "Bericht"])
    
    df = lade_daten()
    df = pd.concat([df, neue_zeile], ignore_index=True)
    df.to_csv(DATEI, index=False)
    st.success("✅ Gespeichert!")
    st.rerun()

# --- ARCHIV & EXPORT ---
st.divider()
daten = lade_daten()

if not daten.empty:
    st.subheader("📚 Letzter Bericht")
    letzter = daten.iloc[-1]
    
    # Details anzeigen
    st.info(f"Datum: {letzter['Datum']} | Polizei: {letzter['Polizei']} | RD: {letzter['Rettungsdienst']} | FS: {letzter['Funkstreife']}")
    
    # --- PDF ERSTELLEN ---
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 33)
        pdf.ln(25)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="EINSATZBERICHT", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    
    # Text für PDF vorbereiten (Umlaute-Fix)
    einsatz_info = f"Datum: {letzter['Datum']}  Zeit: {letzter['Zeit']}\n"
    einsatz_info += f"Zeugen: {letzter['Zeugen']}\n"
    einsatz_info += f"Polizei: {letzter['Polizei']} | Rettungsdienst: {letzter['Rettungsdienst']} | Funkstreife: {letzter['Funkstreife']}\n\n"
    einsatz_info += f"Bericht:\n{letzter['Bericht']}"
    
    clean_text = einsatz_info.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('Ä','Ae').replace('Ö','Oe').replace('Ü','Ue').replace('ß','ss')
    
    pdf.multi_cell(0, 10, txt=clean_text)
    pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
    
    # --- BUTTONS ---
    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button("📄 PDF laden", pdf_output, f"Einsatz_{letzter['Datum']}.pdf", "application/pdf")
    
    with col_b:
        # E-Mail Versand vorbereiten
        mail_body = f"EINSATZBERICHT\n\nDatum: {letzter['Datum']}\nZeit: {letzter['Zeit']}\nZeugen: {letzter['Zeugen']}\n\nKräfte vor Ort:\n- Polizei: {letzter['Polizei']}\n- Rettungsdienst: {letzter['Rettungsdienst']}\n- Funkstreife: {letzter['Funkstreife']}\n\nBericht:\n{letzter['Bericht']}"
        betreff = urllib.parse.quote(f"Einsatzbericht {letzter['Datum']}")
        body = urllib.parse.quote(mail_body)
        st.link_button("📧 Per E-Mail senden", f"mailto:?subject={betreff}&body={body}")

    st.write("**Historie:**")
    st.dataframe(daten.iloc[::-1], use_container_width=True)
else:
    st.info("Noch keine Berichte vorhanden.")
