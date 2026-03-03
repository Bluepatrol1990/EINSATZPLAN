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

# Hinterlegte Empfänger aus deinen Vorgaben
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide") 

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
    except: return "[Fehler]" 

# --- 3. PDF FUNKTION (Mit Umlaut-Korrektur) ---
def create_pdf(row, bericht, kraefte, zeugen, foto_b64):
    pdf = FPDF()
    pdf.add_page()
    
    def clean_text(t):
        if not t: return "-"
        # Wandelt Text in PDF-kompatibles Format um (Umlaute & Sonderzeichen)
        return str(t).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, clean_text("KOD Augsburg - Einsatzbericht"), ln=True, align='C')
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 5, clean_text(f"Berichtskopie an: {', '.join(RECIPIENTS)}"), ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 10)
    details = [
        ("Datum:", row.get('Datum', '-')),
        ("Zeit:", f"{row.get('Beginn', '-')} - {row.get('Ende', '-')}"),
        ("Ort:", f"{row.get('Ort', '-')} {row.get('Hausnummer', '-')}"),
        ("AZ:", row.get('AZ', '-')),
        ("Kräfte:", kraefte),
        ("GPS:", row.get('GPS', '-'))
    ]
    
    for label, val in details:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(35, 7, clean_text(label), 0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, clean_text(val), 0, ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, clean_text("Sachverhalt:"), ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, clean_text(bericht))
    
    if zeugen != "-":
        pdf.ln(5)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 8, clean_text("Beteiligte / Zeugen:"), ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, clean_text(zeugen))

    if foto_b64 != "-" and len(str(foto_b64)) > 20:
        try:
            img_bytes = base64.b64decode(foto_b64)
            img_temp = "temp_pdf_img.jpg"
            with open(img_temp, "wb") as f: f.write(img_bytes)
            pdf.ln(10)
            pdf.image(img_temp, x=10, w=110)
            os.remove(img_temp)
        except: pass
            
    return pdf.output(dest='S')

# --- 4. LOGIN ---
if not st.session_state["auth"]:
    st.title("🚓 KOD Augsburg")
    if st.text_input("Dienstpasswort", type="password") == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop() 

# --- 5. HAUPTSEITE ---
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
        ort = o1.selectbox("🗺️ Einsatzort", [None, "Schillstr./ Dr. Schmelzingstr.", "Rathausplatz", "Maximilianstraße", "Königsplatz", "Zwölf-Apostel-Platz"])
        hnr = o2.text_input("Nr.") 

        st.divider()
        st.subheader("📝 Sachverhalt")
        vorlage = st.selectbox("📑 Vorlage", [None, "§ 111 OWiG", "Alkohol Spielplatz", "Betteln aggressiv", "Urinieren", "Lärmbeschwerde"])
        inhalt = st.text_area("Sachverhalt", value=vorlage if vorlage else "", height=150)
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        foto = st.file_uploader("📸 Foto hochladen", type=["jpg", "jpeg", "png"]) 

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
            st.success("Bericht erfolgreich archiviert!")
            st.rerun() 

# --- 6. ARCHIV ---
st.divider()
st.header("📂 Einsatzarchiv")
suche_begriff = st.text_input("🔍 Suche (Ort oder AZ)") 

if os.path.exists(DATEI):
    archiv_df = pd.read_csv(DATEI).astype(str)
    
    if suche_begriff:
        mask = archiv_df['Ort'].str.contains(suche_begriff, case=False) | archiv_df['AZ'].str.contains(suche_begriff, case=False)
        display_df = archiv_df[mask]
    else:
        display_df = archiv_df

    for i, r in display_df.iloc[::-1].iterrows():
        akt_bericht = entschluesseln(r['Bericht'])
        akt_kraefte = entschluesseln(r['Kraefte'])
        akt_zeugen = entschluesseln(r['Zeugen'])
        akt_foto = entschluesseln(r['Foto']) 

        st.markdown(f"""<div style="background-color: #1e1e1e; border-radius: 10px; padding: 10px; border-left: 5px solid #004b95; margin-bottom: 5px; color: white; border: 1px solid #333;">
            <strong>📅 {r['Datum']} | 📍 {r['Ort']} {r['Hausnummer']}</strong> (AZ: {r['AZ']})</div>""", unsafe_allow_html=True)
        
        with st.expander("📝 Details & PDF Export"):
            st.write(f"**Sachverhalt:**\n{akt_bericht}")
            if akt_zeugen != "-": st.write(f"**Beteiligte:** {akt_zeugen}")
            if akt_foto != "-": st.image(base64.b64decode(akt_foto), width=300)
            
            pdf_out = create_pdf(r, akt_bericht, akt_kraefte, akt_zeugen, akt_foto)
            st.download_button(
                label="📄 Als PDF herunterladen",
                data=pdf_out,
                file_name=f"Einsatz_{r['AZ']}_{r['Datum']}.pdf",
                mime="application/pdf",
                key=f"pdf_btn_{i}"
            )

            if st.session_state["admin_auth"]:
                if st.button(f"🗑️ Löschen", key=f"del_btn_{i}"):
                    archiv_df.drop(i).to_csv(DATEI, index=False)
                    st.rerun() 

with st.sidebar:
    if st.checkbox("🔑 Admin"):
        if st.text_input("Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin-Zugriff aktiv")
