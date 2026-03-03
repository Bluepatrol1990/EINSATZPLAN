import streamlit as st
import pandas as pd
import os
import io
import base64
from datetime import datetime
from PIL import Image
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation
from fpdf import FPDF

# --- 1. GLOBALE VARIABLEN & KONFIGURATION ---
DATEI = "zentral_archiv_secure.csv"
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
EMPFAENGER = "Kevin.woelki@augsburg.de, kevinworlki@outlook.de"

st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide")

# CSS für das Design
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
    </style>
    """, unsafe_allow_html=True)

# --- 2. SICHERHEIT & VERSCHLÜSSELUNG ---
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
    except: return "[Fehler bei Dekodierung]"

# --- 3. PDF GENERATOR KLASSE ---
class BerichtPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'KOD Augsburg - Einsatzbericht', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.cell(0, 5, f'Empfänger: {EMPFAENGER}', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, label, 0, 1, 'L', 1)
        self.ln(3)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, body)
        self.ln(5)

def generate_pdf_bytes(row, bericht, kraefte, zeugen):
    pdf = BerichtPDF()
    pdf.add_page()
    
    # Sektion: Stammdaten
    pdf.chapter_title(f"Einsatzdetails - Datum: {row['Datum']} | AZ: {row['AZ']}")
    stammdaten = (f"Einsatzort: {row['Ort']} {row['Hausnummer']}\n"
                  f"Zeitraum: {row['Beginn']} - {row['Ende']} Uhr\n"
                  f"Eingesetzte Kräfte: {kraefte}\n"
                  f"GPS-Koordinaten: {row['GPS']}")
    pdf.chapter_body(stammdaten)
    
    # Sektion: Bericht
    pdf.chapter_title("Sachverhalt / Feststellungen")
    pdf.chapter_body(bericht)
    
    # Sektion: Beteiligte
    if zeugen != "-":
        pdf.chapter_title("Beteiligte Personen / Zeugen")
        pdf.chapter_body(zeugen)
    
    # Fußzeile mit Zeitstempel
    pdf.set_y(-25)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, f'Erstellt am: {datetime.now().strftime("%d.%m.%Y %H:%M")} | Dienststelle Augsburg', 0, 0, 'C')
    
    return pdf.output()

# --- 4. DATENLISTEN ---
STRASSEN_AUGSBURG = sorted(["Schillstr./ Dr. Schmelzingstr.", "Rathausplatz", "Maximilianstraße", "Königsplatz", "Zwölf-Apostel-Platz"])
FESTSTELLUNGEN = sorted(["§ 111 OWiG", "Alkohol Spielplatz", "Betteln aggressiv", "Urinieren", "Lärmbeschwerde"])

# --- 5. LOGIN ---
if not st.session_state["auth"]:
    st.title("🚓 KOD Augsburg")
    pw_input = st.text_input("Dienstpasswort", type="password")
    if pw_input == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

# --- 6. HAUPTSEITE & FORMULAR ---
st.title("📋 Einsatzbericht erstellen")

loc = get_geolocation()
gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Nicht erfasst"

with st.expander("➕ NEUEN EINSATZBERICHT ERSTELLEN", expanded=True):
    st.subheader("👮 Kräfte vor Ort")
    k_col1, k_col2 = st.columns([1, 2])
    
    with k_col1:
        st.checkbox("🚓 KOD", value=True, disabled=True)
        pol_check = st.checkbox("🚔 Polizei")
        rtw_check = st.checkbox("🚑 Rettungsdienst")
        fw_check = st.checkbox("🚒 Feuerwehr")
    
    with k_col2:
        funkstreife = ""
        if pol_check:
            funkstreife = st.text_input("Funkstreife", placeholder="z.B. Augsburg 12/1")

    with st.form("bericht_form", clear_on_submit=True):
        st.subheader("📍 Ort & Zeit")
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("📅 Datum")
        t_start = c2.time_input("🕒 Beginn")
        t_end = c3.time_input("🕒 Ende")
        az = c4.text_input("📂 Aktenzeichen (AZ)")
        
        o1, o2 = st.columns([3, 1])
        ort = o1.selectbox("🗺️ Einsatzort", [None] + STRASSEN_AUGSBURG)
        hnr = o2.text_input("Nr.")

        st.divider()
        st.subheader("📝 Sachverhalt")
        vorlage = st.selectbox("📑 Feststellung (Vorlage)", [None] + FESTSTELLUNGEN)
        inhalt = st.text_area("Sachverhalt", value=vorlage if vorlage else "", height=150)
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        foto = st.file_uploader("📸 Beweisfoto", type=["jpg", "jpeg", "png"])

        if st.form_submit_button("✅ Bericht speichern"):
            k_final = ["KOD"]
            if pol_check:
                k_final.append(f"Polizei ({funkstreife})" if funkstreife else "Polizei")
            if rtw_check: k_final.append("Rettungsdienst")
            if fw_check: k_final.append("Feuerwehr")
            
            f_b64 = "-"
            if foto:
                img = Image.open(foto)
                img.thumbnail((800, 800))
                b = io.BytesIO(); img.save(b, format="JPEG", quality=75)
                f_b64 = base64.b64encode(b.getvalue()).decode()

            new_data = {
                "Datum": str(datum), "Beginn": t_start.strftime("%H:%M"), "Ende": t_end.strftime("%H:%M"),
                "Ort": str(ort), "Hausnummer": hnr, "Zeugen": verschluesseln(beteiligte),
                "Bericht": verschluesseln(inhalt), "AZ": az, "Foto": verschluesseln(f_b64),
                "GPS": gps_val, "Kraefte": verschluesseln(", ".join(k_final))
            }
            
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success("Bericht erfolgreich im Archiv gespeichert!")
            st.rerun()

# --- 7. ARCHIV ---
st.divider()
st.header("📂 Einsatzarchiv")
suche = st.text_input("🔍 Suche (nach Ort oder AZ)")

if os.path.exists(DATEI):
    archiv_data = pd.read_csv(DATEI).astype(str)
    if suche:
        mask = archiv_data['Ort'].str.contains(suche, case=False) | archiv_data['AZ'].str.contains(suche, case=False)
        display_data = archiv_data[mask]
    else:
        display_data = archiv_data

    for i, r in display_data.iloc[::-1].iterrows():
        # Daten entschlüsseln für die Anzeige und PDF
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
        
        with st.expander("🔍 Details & PDF Export"):
            col_a, col_b = st.columns([2, 1])
            with col_a:
                st.write(f"**Sachverhalt:**\n{akt_bericht}")
                if akt_zeugen != "-": st.write(f"**👥 Beteiligte:** {akt_zeugen}")
                st.write(f"📍 **GPS:** `{r['GPS']}`")
            
            with col_b:
                # PDF GENERIERUNG
                pdf_bytes = generate_pdf_bytes(r, akt_bericht, akt_kraefte, akt_zeugen)
                st.download_button(
                    label="📄 PDF Download",
                    data=pdf_bytes,
                    file_name=f"Bericht_{r['Datum']}_{r['AZ']}.pdf",
                    mime="application/pdf",
                    key=f"pdf_{i}"
                )

            if akt_foto != "-": 
                st.image(base64.b64decode(akt_foto), caption="Einsatzfoto", width=400)
            
            if st.session_state["admin_auth"]:
                if st.button(f"🗑️ Datensatz löschen", key=f"del_{i}"):
                    updated_df = archiv_data.drop(i)
                    updated_df.to_csv(DATEI, index=False)
                    st.warning("Bericht gelöscht.")
                    st.rerun()

# Sidebar Admin-Bereich
with st.sidebar:
    st.image("https://www.augsburg.de/typo3conf/ext/mag_theme_augsburg/Resources/Public/Images/logo-augsburg.png", width=100)
    if st.checkbox("🔑 Admin-Bereich"):
        if st.text_input("Admin-Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin-Zugriff gewährt")
        else: st.session_state["admin_auth"] = False
