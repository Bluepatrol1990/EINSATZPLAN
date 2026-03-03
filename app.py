import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import base64
from PIL import Image
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation

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

# --- 3. SICHERHEIT ---
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

# --- 4. DATENLISTEN ---
STRASSEN_AUGSBURG = sorted([
    "Schillstr./ Dr. Schmelzingstr. - Baustellenbereich", "Hallo Werner", "Hexengässchen", 
    "Meistro Imbiss/Gögginger Str. 22, 24, 26", "Modular Festival", "rund um die Uni", 
    "Ablaßweg", "Ackermannbrücke", "Ackermannpark Spielplatz", "Ackerstraße", "Adalbert-Stifter-Straße", 
    "Adam-Riese-Straße", "Adelgundenstraße", "Adelheidstraße", "Aystetter Weg", "Azaleenstraße",
    "Zugspitzstraße 104 (Neuer Ostfriedhof)", "Zwölf-Apostel-Platz"
    # Hier können weitere der 500+ Straßen ergänzt werden
])

FESTSTELLUNGEN = sorted([
    "§ 111 OWiG", "§ 118 OWiG Belästigung der Allgemeinheit", "Alkoholgenuss auf Spielplätzen",
    "Alkoholgenuss außerhalb zugelassener Freischankflächen", "Alkoholgenuss im Friedhof",
    "Alkoholkonsumverbot", "Baden an einer mit einem Badeverbot belegten Stelle",
    "Befahren Gehweg mit E-Scooter", "Befahren Gehweg mit KFZ", "Grünanlage kontrolliert, keine Beanstandungen",
    "Kein bekanntes Klientel vor Ort. Keine Beanstandung", "Urinieren in der Öffentlichkeit",
    "VZ 283: Parken im absoluten Haltverbot", "Wegwerfen oder Liegenlassen von Zigarettenkippe"
])

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
    with st.form("bericht_form", clear_on_submit=True):
        st.subheader("📍 Ort & Zeit")
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("📅 Datum")
        t_start = c2.time_input("🕒 Beginn")
        t_end = c3.time_input("🕒 Ende")
        az = c4.text_input("📂 Aktenzeichen (AZ)")
        
        o1, o2 = st.columns([3, 1])
        ort = o1.selectbox("🗺️ Einsatzort", [None] + STRASSEN_AUGSBURG, placeholder="Straße suchen...")
        hnr = o2.text_input("Nr.")

        st.divider()
        st.subheader("👮 Kräfte vor Ort")
        k_col1, k_col2 = st.columns([1, 2])
        
        with k_col1:
            st.checkbox("🚓 KOD", value=True, disabled=True)
            pol_check = st.checkbox("🚔 Polizei")
            rtw_check = st.checkbox("🚑 Rettungsdienst")
            fw_check = st.checkbox("🚒 Feuerwehr")
        
        with k_col2:
            # Das Textfeld erscheint nur, wenn Polizei ausgewählt ist
            funkstreife = st.text_input("Funkstreife", placeholder="Rufname (z.B. Augsburg 12/1)", help="Nur ausfüllen, wenn Polizei vor Ort")

        st.divider()
        st.subheader("📝 Sachverhalt")
        vorlage = st.selectbox("📑 Feststellung (Vorlage)", [None] + FESTSTELLUNGEN)
        inhalt = st.text_area("Sachverhalt", value=vorlage if vorlage else "", height=150)
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        
        foto = st.file_uploader("📸 Beweisfoto", type=["jpg", "jpeg", "png"])

        if st.form_submit_button("✅ Bericht speichern"):
            k_final = ["KOD"]
            if pol_check:
                pol_txt = f"Polizei ({funkstreife})" if funkstreife else "Polizei"
                k_final.append(pol_txt)
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
            pd.concat([df, pd.DataFrame([new_data])], ignore_index=True).to_csv(DATEI, index=False)
            
            st.success(f"Bericht gespeichert und für Versand an {', '.join(RECIPIENTS)} bereit!")
            st.rerun()

# --- 7. ARCHIV ---
st.divider()
st.header("📂 Einsatzarchiv")
suche = st.text_input("🔍 Suche (Ort oder AZ)")

if os.path.exists(DATEI):
    archiv_data = pd.read_csv(DATEI).astype(str)
    if suche:
        mask = archiv_data['Ort'].str.contains(suche, case=False) | archiv_data['AZ'].str.contains(suche, case=False)
        display_data = archiv_data[mask]
    else:
        display_data = archiv_data

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
            
            if st.session_state["admin_auth"]:
                if st.button(f"🗑️ Löschen", key=f"del_{i}"):
                    pd.read_csv(DATEI).drop(i).to_csv(DATEI, index=False)
                    st.rerun()

# Sidebar Admin
with st.sidebar:
    st.write("---")
    if st.checkbox("🔑 Admin-Bereich"):
        if st.text_input("Admin-Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin-Zugriff gewährt")
        else:
            st.session_state["admin_auth"] = False
