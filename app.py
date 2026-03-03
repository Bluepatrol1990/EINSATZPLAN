import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64
import tempfile
from PIL import Image
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation 
from fpdf import FPDF

# --- 1. GLOBALE VARIABLEN ---
DATEI = "zentral_archiv_secure.csv"
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]

# --- 2. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="KOD Augsburg - Management", page_icon="🚓", layout="wide") 

st.markdown("""
    <style>
    .report-card { 
        background-color: #1e1e1e; 
        border-radius: 8px; 
        padding: 15px; 
        border-left: 5px solid #004b95; 
        margin-bottom: 10px; 
        border: 1px solid #333333;
        color: white;
    }
    .admin-only {
        color: #ff4b4b;
        font-weight: bold;
        border: 1px solid #ff4b4b;
        padding: 5px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True) 

# --- 3. SICHERHEIT & CRYPTO ---
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
    except: return "[Fehlerhafte Verschlüsselung]" 

# --- 4. BEHÖRDEN-PDF FUNKTION ---
def create_official_pdf(row_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header: Stadt Augsburg
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Stadt Augsburg", ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Ordnungsamt", ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "Kommunaler Ordnungsdienst (KOD)", ln=True)
    
    pdf.line(10, 35, 200, 35) # Trennlinie
    pdf.ln(15)
    
    # Titel
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Einsatzbericht - AZ: {row_data['AZ']}", ln=True, align='C')
    pdf.ln(5)
    
    # Stammdaten Tabelle
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    
    pdf.cell(40, 8, "Datum:", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(55, 8, row_data['Datum'], border=1)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 8, "Einsatzzeit:", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(55, 8, f"{row_data['Beginn']} - {row_data['Ende']}", border=1, ln=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 8, "Ort:", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(150, 8, f"{row_data['Ort']} {row_data['Hausnummer']}", border=1, ln=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 8, "Eingesetzte Kraefte:", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(150, 8, entschluesseln(row_data['Kraefte']), border=1, ln=True)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(40, 8, "GPS-Daten:", border=1, fill=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(150, 8, row_data['GPS'], border=1, ln=True)
    
    # Sachverhalt
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Sachverhalt / Feststellungen:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 6, entschluesseln(row_data['Bericht']), border='T')
    
    # Zeugen
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Beteiligte Personen / Zeugen:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 6, entschluesseln(row_data['Zeugen']), border='T')
    
    # Bilder hinzufügen
    akt_foto = entschluesseln(row_data['Foto'])
    if akt_foto != "-":
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Beweismittel / Fotodokumentation:", ln=True)
        
        # Temporäre Datei für das Bild erstellen
        try:
            img_data = base64.b64decode(akt_foto)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(img_data)
                tmp_path = tmp.name
            
            # Bild einfügen (zentriert, Breite max 170mm)
            pdf.image(tmp_path, x=20, y=30, w=170)
            os.unlink(tmp_path) # Temp Datei löschen
        except Exception as e:
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 10, f"Bild konnte nicht geladen werden: {e}", ln=True)

    return pdf.output(dest="S").encode("latin-1")

# --- 5. DATENLISTEN ---
STRASSEN_AUGSBURG = sorted(["Schillstr./ Dr. Schmelzingstr.", "Rathausplatz", "Maximilianstraße", "Königsplatz", "Zwölf-Apostel-Platz", "Oberhauser Bahnhof"])
FESTSTELLUNGEN = sorted(["§ 111 OWiG", "Alkohol Spielplatz", "Betteln aggressiv", "Urinieren", "Lärmbeschwerde", "Sondernutzung"]) 

# --- 6. LOGIN ---
if not st.session_state["auth"]:
    st.title("🚓 KOD Augsburg - Login")
    pw_input = st.text_input("Dienstpasswort", type="password")
    if pw_input == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop() 

# --- 7. FORMULAR ---
st.title("📋 Einsatzbericht Erfassung") 

loc = get_geolocation()
gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Nicht erfasst" 

with st.expander("➕ NEUEN BERICHT ERSTELLEN", expanded=True):
    # Kräfte Auswahl
    st.subheader("👮 Kräfte")
    k_col1, k_col2 = st.columns([1, 2])
    with k_col1:
        st.checkbox("🚓 KOD", value=True, disabled=True)
        pol_check = st.checkbox("🚔 Polizei")
        rtw_check = st.checkbox("🚑 Rettungsdienst")
    with k_col2:
        funkstreife = st.text_input("Funkstreife / Name", placeholder="z.B. Augsburg 12/1") if pol_check else ""

    with st.form("bericht_form", clear_on_submit=True):
        st.subheader("📍 Details")
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("Datum")
        t_start = c2.time_input("Beginn")
        t_end = c3.time_input("Ende")
        az = c4.text_input("Aktenzeichen (AZ)")
        
        o1, o2 = st.columns([3, 1])
        ort = o1.selectbox("Einsatzort", [None] + STRASSEN_AUGSBURG)
        hnr = o2.text_input("Hausnr.") 

        st.divider()
        st.subheader("📝 Bericht")
        vorlage = st.selectbox("Vorlage wählen", [None] + FESTSTELLUNGEN)
        inhalt = st.text_area("Sachverhalt", value=vorlage if vorlage else "", height=150)
        beteiligte = st.text_input("Beteiligte / Zeugen")
        foto = st.file_uploader("Beweisfoto (Optional)", type=["jpg", "png"]) 

        if st.form_submit_button("✅ Bericht speichern"):
            k_final = ["KOD"]
            if pol_check: k_final.append(f"Polizei ({funkstreife})")
            if rtw_check: k_final.append("Rettungsdienst")
            
            f_b64 = "-"
            if foto:
                img = Image.open(foto)
                img.thumbnail((1000, 1000))
                b = io.BytesIO(); img.save(b, format="JPEG", quality=80)
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
            st.success("Gespeichert!")
            st.rerun() 

# --- 8. ARCHIV ---
st.divider()
st.header("📂 Einsatzarchiv")

if os.path.exists(DATEI):
    archiv_df = pd.read_csv(DATEI).astype(str)
    suche = st.text_input("🔍 Suche (AZ oder Ort)")
    
    if suche:
        archiv_df = archiv_df[archiv_df['AZ'].str.contains(suche) | archiv_df['Ort'].str.contains(suche)]

    for i, r in archiv_df.iloc[::-1].iterrows():
        st.markdown(f"""
        <div class="report-card">
            <strong>📅 {r['Datum']} | 📍 {r['Ort']} {r['Hausnummer']}</strong> (AZ: {r['AZ']})<br>
            <small>🕒 {r['Beginn']} - {r['Ende']} | 👮 {entschluesseln(r['Kraefte'])}</small>
        </div>
        """, unsafe_allow_html=True)
        
        col_view, col_pdf = st.columns([5, 1])
        
        with col_view:
            with st.expander("Details ansehen"):
                st.write(f"**Sachverhalt:**\n{entschluesseln(r['Bericht'])}")
                st.write(f"**Beteiligte:** {entschluesseln(r['Zeugen'])}")
                f_dec = entschluesseln(r['Foto'])
                if f_dec != "-": st.image(base64.b64decode(f_dec), width=400)

        with col_pdf:
            # NUR FÜR ADMINS
            if st.session_state["admin_auth"]:
                pdf_data = create_official_pdf(r)
                st.download_button(
                    label="📥 PDF Export",
                    data=pdf_data,
                    file_name=f"KOD_Bericht_{r['AZ']}.pdf",
                    mime="application/pdf",
                    key=f"pdf_btn_{i}"
                )
            else:
                st.markdown("<div class='admin-only'>PDF (Nur Admin)</div>", unsafe_allow_html=True)

# --- 9. SIDEBAR ADMIN ---
with st.sidebar:
    st.title("🛡️ Admin-Panel")
    if st.checkbox("🔑 Login Admin"):
        if st.text_input("Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin-Bereich freigeschaltet")
            
            st.divider()
            if st.button("🚨 ARCHIV LÖSCHEN"):
                if os.path.exists(DATEI):
                    os.remove(DATEI)
                    st.rerun()
        else:
            st.session_state["admin_auth"] = False
