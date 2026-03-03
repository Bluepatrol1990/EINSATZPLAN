import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64
from PIL import Image
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation
from fpdf import FPDF

# --- 1. GLOBALE VARIABLEN & EMPFÄNGER ---
DATEI = "zentral_archiv_secure.csv"
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# --- 2. SEITEN-KONFIGURATION & DARK DESIGN ---
st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    .report-card { 
        background-color: #1e1e1e; 
        border-radius: 10px; 
        padding: 15px; 
        border-left: 5px solid #004b95; 
        margin-bottom: 10px; 
        border: 1px solid #333333;
        color: white;
    }
    .report-card strong, .report-card small {
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SICHERHEIT & VERSCHLÜSSELUNG ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False

DIENST_PW = st.secrets.get("dienst_password", "1234")
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")
ADMIN_PW = "admin789"

def get_cipher():
    key_64 = base64.urlsafe_b64encode(MASTER_KEY[:32].encode().ljust(32))
    return Fernet(key_64)

def verschluesseln(text):
    if not text or text == "-": return "-"
    return get_cipher().encrypt(str(text).encode()).decode()

def entschluesseln(safe_text):
    if not safe_text or safe_text == "-": return "-"
    try: return get_cipher().decrypt(safe_text.encode()).decode()
    except: return "[Fehler]"

# --- 4. PDF GENERATOR KLASSE ---
class AmtlicherBericht(FPDF):
    def header(self):
        # Platzhalter für Logo (Wenn 'logo.png' existiert)
        # self.image('logo.png', 10, 8, 33) 
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Stadt Augsburg', 0, 1, 'R')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Ordnungsreferat', 0, 1, 'R')
        self.cell(0, 5, 'Kommunaler Ordnungsdienst (KOD)', 0, 1, 'R')
        self.ln(10)
        self.set_draw_color(0, 75, 149)
        self.line(10, 35, 200, 35)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()} | Amtliches Dokument - Vertraulich', 0, 0, 'C')

def erstelle_pdf(row_data):
    pdf = AmtlicherBericht()
    pdf.add_page()
    
    # Titel
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f"Einsatzbericht - AZ: {row_data['AZ']}", 0, 1, 'L')
    pdf.ln(5)
    
    # Infobox
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(40, 8, "Datum:", 1, 0, 'L', True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(50, 8, str(row_data['Datum']), 1, 0, 'L')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Zeitraum:", 1, 0, 'L', True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(60, 8, f"{row_data['Beginn']} - {row_data['Ende']} Uhr", 1, 1, 'L')
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Ort:", 1, 0, 'L', True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(150, 8, f"{row_data['Ort']} {row_data['Hausnummer']}", 1, 1, 'L')
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 8, "Eingesetzte Kräfte:", 1, 0, 'L', True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(150, 8, entschluesseln(row_data['Kraefte']), 1, 1, 'L')
    
    pdf.ln(10)
    
    # Sachverhalt
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Sachverhalt / Feststellungen:", 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, entschluesseln(row_data['Bericht']))
    
    pdf.ln(5)
    if row_data['Zeugen'] != "-":
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, "Beteiligte Personen / Zeugen:", 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, entschluesseln(row_data['Zeugen']))

    pdf.ln(10)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 10, f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')} | GPS: {row_data['GPS']}", 0, 1, 'L')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 5. DATENLISTEN & LOGIN --- (Gekürzt für die Anzeige, bleibt wie in deinem File)
STRASSEN_AUGSBURG = sorted(list(set([
    "Schillstr./ Dr. Schmelzingstr. - Baustellenbereich", "Annastraße", "Königsplatz", "Maximilianstraße", "Rathausplatz"
    # ... Deine vollständige Liste hier einfügen
])))

FESTSTELLUNGEN = ["§ 111 OWiG", "Alkoholkonsumverbot", "Wilder Müll", "Lärmbeschwerde"]

if not st.session_state["auth"]:
    st.title("🚓 KOD Augsburg")
    pw_input = st.text_input("Dienstpasswort", type="password")
    if pw_input == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

# --- 6. HAUPTSEITE ---
st.title("📋 Einsatzbericht")

loc = get_geolocation()
gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Nicht erfasst"

# Formular-Bereich (Bleibt identisch zu deinem Code)
with st.expander("➕ NEUEN EINSATZBERICHT ERSTELLEN", expanded=True):
    with st.form("bericht_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("📅 Datum")
        t_start = c2.time_input("🕒 Beginn")
        t_end = c3.time_input("🕒 Ende")
        az = c4.text_input("📂 Aktenzeichen (AZ)")
        ort = st.selectbox("🗺️ Einsatzort", [None] + STRASSEN_AUGSBURG)
        hnr = st.text_input("Hausnummer")
        
        pol_check = st.checkbox("🚔 Polizei")
        funkstreife = st.text_input("Funkstreife")
        inhalt = st.text_area("Sachverhalt")
        beteiligte = st.text_input("👥 Beteiligte")
        foto = st.file_uploader("📸 Foto", type=["jpg", "png"])

        if st.form_submit_button("✅ Bericht speichern"):
            # Speichermethode wie gehabt...
            k_final = "KOD" + (f", Polizei ({funkstreife})" if pol_check else "")
            new_data = {
                "Datum": str(datum), "Beginn": t_start.strftime("%H:%M"), "Ende": t_end.strftime("%H:%M"),
                "Ort": str(ort), "Hausnummer": hnr, "Zeugen": verschluesseln(beteiligte),
                "Bericht": verschluesseln(inhalt), "AZ": az, "Foto": "-", "GPS": gps_val, 
                "Kraefte": verschluesseln(k_final)
            }
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            pd.concat([df, pd.DataFrame([new_data])], ignore_index=True).to_csv(DATEI, index=False)
            st.success("Gespeichert!")

# --- 7. ARCHIV & PDF EXPORT ---
st.divider()
st.header("📂 Einsatzarchiv")
suche = st.text_input("🔍 Suche (Ort oder AZ)")

if os.path.exists(DATEI):
    archiv_data = pd.read_csv(DATEI).astype(str)
    display_data = archiv_data[archiv_data['Ort'].str.contains(suche, case=False)] if suche else archiv_data

    for i, r in display_data.iloc[::-1].iterrows():
        st.markdown(f"""
        <div class="report-card">
            <strong>📅 {r['Datum']} | 📍 {r['Ort']} {r['Hausnummer']}</strong> (AZ: {r['AZ']})
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("📝 Details & PDF-Export"):
            st.write(f"**Sachverhalt:** {entschluesseln(r['Bericht'])}")
            
            # ADMIN FUNKTIONEN
            if st.session_state["admin_auth"]:
                col_a, col_b = st.columns(2)
                
                # PDF BUTTON
                pdf_data = erstelle_pdf(r)
                col_a.download_button(
                    label="📄 Als amtliches PDF exportieren",
                    data=pdf_data,
                    file_name=f"Einsatzbericht_{r['AZ']}_{r['Datum']}.pdf",
                    mime="application/pdf"
                )
                
                if col_b.button(f"🗑️ Bericht löschen", key=f"del_{i}"):
                    pd.read_csv(DATEI).drop(i).to_csv(DATEI, index=False)
                    st.rerun()

# Sidebar Admin
with st.sidebar:
    st.image("https://www.augsburg.de/typo3conf/ext/mag_theme_augsburg/Resources/Public/Images/logo-augsburg.png", width=150)
    st.write("---")
    if st.checkbox("🔑 Admin-Bereich"):
        if st.text_input("Admin-Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin aktiv")
