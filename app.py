# --- PDF GENERATOR FUNKTION (v9.3) ---
def erstelle_behoerden_pdf(row):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 75, 149) # Augsburg Blau
    pdf.cell(0, 10, "Ordnungsamt Stadt Augsburg", ln=True, align='L')
    
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Amtlicher Einsatzbericht | AZ: {row['AZ']}", ln=True, align='L')
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    
    # Daten-Tabelle
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Einsatzort:", 0); pdf.set_font("Arial", "", 11); pdf.cell(0, 8, f"{row['Ort']} {row['Hausnummer']}", 1)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Zeitraum:", 0); pdf.set_font("Arial", "", 11); pdf.cell(0, 8, f"{row['Datum']} ({row['Beginn']} - {row['Ende']} Uhr)", 1)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Dienstkraft:", 0); pdf.set_font("Arial", "", 11); pdf.cell(0, 8, f"{row['Dienstkraft']}", 1)
    pdf.ln(12)
    
    # Sachverhalt
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Sachverhalt / Feststellungen:", ln=True)
    pdf.set_font("Arial", "", 11)
    # Umlaute-Fix für PDF
    safe_text = str(row['Bericht']).replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
    pdf.multi_cell(0, 7, safe_text)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- IM ARCHIV-BEREICH (Auszug) ---
with st.expander("Details & Foto anzeigen"):
    st.info(f"**Sachverhalt:**\n\n{row['Bericht']}")
    # NUR FÜR ADMINS SICHTBAR:
    if st.session_state.get("is_admin", False):
        pdf_data = erstelle_behoerden_pdf(row)
        st.download_button(
            label="📄 Als PDF speichern (Behörden-Layout)",
            data=pdf_data,
            file_name=f"Einsatz_{row['Datum']}_{row['Ort']}.pdf",
            mime="application/pdf",
            key=f"pdf_btn_{i}"
        )
