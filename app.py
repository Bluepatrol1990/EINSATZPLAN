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

# --- 1. GLOBALE VARIABLEN & KONFIGURATION ---
DATEI = "zentral_archiv_secure.csv"
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]

# Empfänger gemäß Anforderung
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide") 

# --- 2. SICHERHEIT & VERSCHLÜSSELUNG ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False 

DIENST_PW = st.secrets.get("dienst_password", "1234")
MASTER_KEY = st.secrets.get("master_key", "AugsburgSicherheit32ZeichenCheck!")
ADMIN_PW = "admin789" 

def get_cipher():
    # Erzeugt einen validen Fernet-Key aus dem Master-Key
    key_64 = base64.urlsafe_b64encode(MASTER_KEY[:32].encode().ljust(32))
    return Fernet(key_64) 

def verschluesseln(text):
    if not text or text == "-": return "-"
    return get_cipher().encrypt(str(text).encode()).decode() 

def entschluesseln(safe_text):
    if not safe_text or safe_text == "-": return "-"
    try: return get_cipher().decrypt(safe_text.encode()).decode()
    except: return "[Fehler]" 

# --- 3. PDF GENERIERUNG ---
def create_pdf(row, bericht, kraefte, zeugen, foto_b64):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    
    # Kopfzeile
    pdf.cell(0, 10, "KOD Augsburg - Einsatzbericht", ln=True, align='C')
    pdf.set_font("helvetica", "I", 8)
    pdf.cell(0, 5, f"Kopie an: {', '.join(RECIPIENTS)}", ln=True, align='C')
    pdf.ln(10)
    
    # Daten-Tabelle
    pdf.set_font("helvetica", "B", 12)
    data = [
        ["Datum", str(row['Datum'])],
        ["Zeit", f"{row['Beginn']} - {row['Ende']}"],
        ["Ort", f"{row['Ort']} {row['Hausnummer']}"],
        ["Aktenzeichen", str(row['AZ'])],
        ["Kräfte", str(kraefte)]
    ]
    
    for item in data:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(40, 7, item[0] + ":", border=0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 7, item[1], border=0, ln=True)
    
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Sachverhalt:", ln=True)
    pdf.set_font("helvetica", "", 10)
    pdf.multi_cell(0, 6, bericht)
    
    if zeugen != "-":
        pdf.ln(5)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(0, 8, "Beteiligte / Zeugen:", ln=True)
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(0, 6, zeugen)

    if foto_b64 != "-":
        try:
            img_data = base64.b64decode(foto_b64)
            img_path = "temp_img.jpg"
            with open(img_path, "wb") as f:
                f.write(img_data)
            pdf.ln(10)
            pdf.image(img_path, x=10, w=100)
            os.remove(img_path)
        except:
            pdf.cell(0, 10, "[Bildfehler]", ln=True)
            
    return pdf.output(dest='S')

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

# --- 6. HAUPTSEITE ---
st.title("📋 Einsatzbericht") 

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
        funkstreife = st.text_input("Funkstreife", placeholder="z.B. Augsburg 12/1") if pol_check else ""

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
            if pol_check: k_final.append(f"Polizei ({funkstreife})" if funkstreife else "Polizei")
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
            st.success("Bericht erfolgreich gespeichert!")
            st.rerun() 

# --- 7. ARCHIV ---
st.divider()
st.header("📂 Einsatzarchiv")
suche = st.text_input("🔍 Suche (Ort oder AZ)") 

if os.path.exists(DATEI):
    archiv_data = pd.read_csv(DATEI).astype(str)
    display_data = archiv_data[archiv_data['Ort'].str.contains(suche, case=False) | archiv_data['AZ'].str.contains(suche, case=False)] if Suche else archiv_data

    for i, r in display_data.iloc[::-1].iterrows():
        akt_bericht = entschluesseln(r['Bericht'])
        akt_kraefte = entschluesseln(r['Kraefte'])
        akt_zeugen = entschluesseln(r['Zeugen'])
        akt_foto = entschluesseln(r['Foto']) 

        st.markdown(f"""<div style="background-color: #1e1e1e; border-radius: 10px; padding: 15px; border-left: 5px solid #004b95; margin-bottom: 10px; border: 1px solid #333; color: white;">
            <strong>📅 {r['Datum']} | 📍 {r['Ort']} {r['Hausnummer']}</strong> (AZ: {r['AZ']})<br>
            <small>🕒 {r['Beginn']} - {r['Ende']} | 👮 {akt_kraefte}</small></div>""", unsafe_allow_html=True)
        
        with st.expander("📝 Details & PDF Export"):
            st.write(f"**Sachverhalt:**\n{akt_bericht}")
            if akt_zeugen != "-": st.write(f"**👥 Beteiligte:** {akt_zeugen}")
            if akt_foto != "-": st.image(base64.b64decode(akt_foto), width=400)
            
            # PDF BUTTON
            pdf_data = create_pdf(r, akt_bericht, akt_kraefte, akt_zeugen, akt_foto)
            st.download_button(
                label="📄 Bericht als PDF herunterladen",
                data=pdf_data,
                file_name=f"KOD_Bericht_{r['Datum']}_{r['AZ']}.pdf",
                mime="application/pdf",
                key=f"pdf_{i}"
            )

            if st.session_state["admin_auth"]:
                if st.button(f"🗑️ Löschen", key=f"del_{i}"):
                    archiv_data.drop(i).to_csv(DATEI, index=False)
                    st.rerun() 

# Sidebar Admin
with st.sidebar:
    if st.checkbox("🔑 Admin"):
        if st.text_input("Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin-Mode AN")
