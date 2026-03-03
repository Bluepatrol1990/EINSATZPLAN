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

# --- 1. KONFIGURATION & EMPFÄNGER ---
DATEI = "zentral_archiv_secure.csv"
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

st.set_page_config(page_title="KOD Augsburg", page_icon="🚓", layout="wide")

# --- 2. SICHERHEIT ---
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

# --- 3. PDF FUNKTION (STABILISIERT FÜR ANDROID) ---
def create_pdf(row, bericht, kraefte, zeugen, foto_b64):
    pdf = FPDF()
    pdf.add_page()
    
    # Text-Säuberung für PDF-Standard (Umlaute & Sonderzeichen)
    def pdf_safe(t):
        if not t: return "-"
        return str(t).encode('cp1252', 'replace').decode('cp1252')

    # Header
    pdf.set_font("Courier", "B", 16)
    pdf.cell(0, 10, pdf_safe("KOD AUGSBURG - EINSATZBERICHT"), ln=True, align='C')
    pdf.set_font("Courier", "I", 8)
    pdf.cell(0, 5, pdf_safe(f"Kopie an: {', '.join(RECIPIENTS)}"), ln=True, align='C')
    pdf.ln(10)

    # Stammdaten Tabelle
    pdf.set_font("Courier", "B", 10)
    labels = [
        ("Datum:", row.get('Datum', '-')),
        ("Zeit:", f"{row.get('Beginn', '-')} - {row.get('Ende', '-')}"),
        ("Ort:", f"{row.get('Ort', '-')} {row.get('Hausnummer', '-')}"),
        ("AZ:", row.get('AZ', '-')),
        ("Kraefte:", kraefte),
        ("GPS:", row.get('GPS', '-'))
    ]

    for label, val in labels:
        pdf.set_font("Courier", "B", 10)
        pdf.cell(40, 7, pdf_safe(label), 0)
        pdf.set_font("Courier", "", 10)
        pdf.cell(0, 7, pdf_safe(val), 0, ln=True)

    pdf.ln(5)
    pdf.set_font("Courier", "B", 12)
    pdf.cell(0, 10, "SACHVERHALT:", ln=True)
    pdf.set_font("Courier", "", 10)
    pdf.multi_cell(0, 6, pdf_safe(bericht))

    if zeugen and zeugen != "-":
        pdf.ln(5)
        pdf.set_font("Courier", "B", 10)
        pdf.cell(0, 8, "BETEILIGTE / ZEUGEN:", ln=True)
        pdf.set_font("Courier", "", 10)
        pdf.multi_cell(0, 6, pdf_safe(zeugen))

    # Foto-Einbettung
    if foto_b64 and foto_b64 != "-":
        try:
            img_data = base64.b64decode(foto_b64)
            img_io = io.BytesIO(img_data)
            pdf.ln(10)
            pdf.image(img_io, x=10, w=100)
        except:
            pdf.cell(0, 10, "[Foto konnte nicht geladen werden]", ln=True)

    return pdf.output()

# --- 4. LOGIN ---
if not st.session_state["auth"]:
    st.title("🚓 KOD Augsburg")
    if st.text_input("Dienstpasswort", type="password") == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

# --- 5. HAUPTSEITE & FORMULAR ---
st.title("📋 Einsatzbericht")
loc = get_geolocation()
gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Nicht erfasst"

with st.expander("➕ NEUEN EINSATZBERICHT ERSTELLEN", expanded=True):
    # Kräfte Auswahl
    st.subheader("👮 Kräfte vor Ort")
    k1, k2 = st.columns([1, 2])
    with k1:
        pol = st.checkbox("🚔 Polizei")
        rtw = st.checkbox("🚑 Rettungsdienst")
    with k2:
        funk = st.text_input("Funkstreife") if pol else ""

    with st.form("bericht_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("📅 Datum")
        t1 = c2.time_input("🕒 Beginn")
        t2 = c3.time_input("🕒 Ende")
        az = c4.text_input("📂 AZ")
        
        o1, o2 = st.columns([3, 1])
        ort = o1.selectbox("🗺️ Ort", [None, "Maximilianstraße", "Königsplatz", "Rathausplatz", "Schillstraße", "Zwölf-Apostel-Platz"])
        hnr = o2.text_input("Nr.")

        st.divider()
        vorlage = st.selectbox("📑 Vorlage", [None, "§ 111 OWiG", "Alkohol Spielplatz", "Lärmbeschwerde", "Urinieren"])
        inhalt = st.text_area("Sachverhalt", value=vorlage if vorlage else "", height=150)
        zeugen = st.text_input("👥 Beteiligte")
        foto = st.file_uploader("📸 Foto", type=["jpg", "png"])

        if st.form_submit_button("✅ Speichern"):
            k_list = ["KOD"]
            if pol: k_list.append(f"Polizei ({funk})" if funk else "Polizei")
            if rtw: k_list.append("Rettungsdienst")
            
            img_str = "-"
            if foto:
                img = Image.open(foto)
                img.thumbnail((800, 800))
                b = io.BytesIO(); img.save(b, format="JPEG", quality=70)
                img_str = base64.b64encode(b.getvalue()).decode()

            new_entry = {
                "Datum": str(datum), "Beginn": t1.strftime("%H:%M"), "Ende": t2.strftime("%H:%M"),
                "Ort": str(ort), "Hausnummer": hnr, "Zeugen": verschluesseln(zeugen),
                "Bericht": verschluesseln(inhalt), "AZ": az, "Foto": verschluesseln(img_str),
                "GPS": gps_val, "Kraefte": verschluesseln(", ".join(k_list))
            }
            
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATEI, index=False)
            st.success("Gespeichert!")
            st.rerun()

# --- 6. ARCHIV ---
st.divider()
st.header("📂 Archiv")
suche = st.text_input("🔍 Suche (Ort oder AZ)")

if os.path.exists(DATEI):
    df_archiv = pd.read_csv(DATEI).astype(str)
    if suche:
        df_archiv = df_archiv[df_archiv['Ort'].str.contains(suche, case=False) | df_archiv['AZ'].str.contains(suche, case=False)]

    for i, r in df_archiv.iloc[::-1].iterrows():
        b_dec = entschluesseln(r['Bericht'])
        k_dec = entschluesseln(r['Kraefte'])
        z_dec = entschluesseln(r['Zeugen'])
        f_dec = entschluesseln(r['Foto'])

        st.info(f"📅 {r['Datum']} | 📍 {r['Ort']} | AZ: {r['AZ']}")
        with st.expander("📝 Details & PDF"):
            st.write(f"**Bericht:** {b_dec}")
            if f_dec != "-": st.image(base64.b64decode(f_dec), width=250)
            
            # PDF Download Button
            pdf_bytes = create_pdf(r, b_dec, k_dec, z_dec, f_dec)
            st.download_button("📄 PDF Download", pdf_bytes, f"Bericht_{r['AZ']}.pdf", "application/pdf", key=f"p_{i}")

            if st.session_state["admin_auth"]:
                if st.button(f"🗑️ Löschen", key=f"d_{i}"):
                    df_archiv.drop(i).to_csv(DATEI, index=False)
                    st.rerun()

with st.sidebar:
    if st.checkbox("🔑 Admin"):
        if st.text_input("PW", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
