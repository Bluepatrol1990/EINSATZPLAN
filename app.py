import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io
import base64
from PIL import Image, ImageOps
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="KOD Augsburg - Einsatzbericht", page_icon="🚓", layout="wide")

# Custom CSS für schöneres Archiv-Design
st.markdown("""
    <style>
    .report-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #004b95;
        margin-bottom: 10px;
        color: #1a1a1a;
    }
    .stExpander { border: none !important; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE & SICHERHEIT ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False

# Secrets (Fallback für lokale Tests)
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

# --- 3. DATENLISTEN ---
STRASSEN_AUGSBURG = sorted(["Rathausplatz", "Königsplatz", "Maximilianstraße", "Bahnhofstraße", "Moritzplatz", "Jakoberstraße", "Ulmer Straße", "Gögginger Straße", "Haunstetter Straße", "Hochzoll Mitte", "Lechhauser Str."]) # Gekürzt für Code-Beispiel
FESTSTELLUNGEN = sorted(["§ 111 OWiG", "§ 118 OWiG Belästigung", "Alkoholgenuss Spielplatz", "Alkoholkonsumverbot", "Betteln aggressiv", "Grünanlage o.B.", "Keine Beanstandungen", "Lärmschutzverordnung", "Urinieren Öffentlichkeit", "Wilder Müll"])

# --- 4. DATEN-HANDLING ---
DATEI = "zentral_archiv_secure.csv"
COLUMNS = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "GPS", "Kraefte"]

def lade_daten():
    if os.path.exists(DATEI):
        df = pd.read_csv(DATEI).astype(str)
        for col in ["Bericht", "Zeugen", "Foto", "Kraefte"]: 
            df[col] = df[col].apply(entschluesseln)
        return df
    return pd.DataFrame(columns=COLUMNS)

# --- 5. LOGIN ---
if not st.session_state["auth"]:
    st.title("🚓 KOD Login")
    if st.text_input("Dienstpasswort", type="password") == DIENST_PW:
        st.session_state["auth"] = True
        st.rerun()
    st.stop()

# --- 6. HAUPTSEITE ---
st.title("📋 Einsatzbericht")

# GPS Tracking im Hintergrund
loc = get_geolocation()
gps_ready = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Nicht verfügbar"

with st.expander("➕ NEUEN BERICHT ERSTELLEN", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        st.subheader("📍 Ort & Zeit")
        c1, c2, c3, c4 = st.columns(4)
        d = c1.date_input("📅 Datum")
        t1 = c2.time_input("🕒 Beginn")
        t2 = c3.time_input("🕒 Ende")
        az = c4.text_input("📂 Aktenzeichen")
        
        o1, o2 = st.columns([3,1])
        ort = o1.selectbox("🗺️ Einsatzort", STRASSEN_AUGSBURG, index=None, placeholder="Straße wählen...")
        nr = o2.text_input("Nr.")

        st.divider()
        st.subheader("🔍 Feststellung & Sachverhalt")
        fest_wahl = st.selectbox("📑 Vorlage auswählen", [None] + FESTSTELLUNGEN)
        bericht_text = st.text_area("📝 Sachverhalt / Details", value=fest_wahl if fest_wahl else "", height=150)
        zeugen = st.text_input("👥 Beteiligte Personen / Zeugen")
        
        st.divider()
        st.subheader("👮 Kräfte vor Ort")
        ck1, ck2, ck3, ck4 = st.columns(4)
        kod_on = ck1.checkbox("KOD", value=True, disabled=True)
        pol_on = ck2.checkbox("Polizei")
        rtw_on = ck3.checkbox("RTW/Notarzt")
        fw_on = ck4.checkbox("Feuerwehr")
        
        funkstreife = ""
        if pol_on:
            funkstreife = st.text_input("🚔 Name der Funkstreife / Dienststelle", placeholder="z.B. Augsburg 12/1")

        foto = st.file_uploader("📸 Foto-Beweis", type=["jpg", "png", "jpeg"])

        if st.form_submit_button("✅ BERICHT ABSCHLIESSEN & SPEICHERN"):
            # Kräfte-Liste bauen
            k_final = ["KOD"]
            if pol_on: k_final.append(f"Polizei ({funkstreife if funkstreife else 'o.A.'})")
            if rtw_on: k_final.append("Rettungsdienst")
            if fw_on: k_final.append("Feuerwehr")

            f_b = "-"
            if foto:
                img = Image.open(foto)
                img.thumbnail((800, 800))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=70)
                f_b = base64.b64encode(buf.getvalue()).decode()
            
            new_row = {
                "Datum": str(d), "Beginn": t1.strftime("%H:%M"), "Ende": t2.strftime("%H:%M"),
                "Ort": str(ort), "Hausnummer": nr, "Zeugen": verschluesseln(zeugen),
                "Bericht": verschluesseln(bericht_text), "AZ": az, "Foto": verschluesseln(f_b),
                "GPS": gps_ready, "Kraefte": verschluesseln(", ".join(k_final))
            }
            
            df_current = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            pd.concat([df_current, pd.DataFrame([new_row])]).to_csv(DATEI, index=False)
            st.success("Bericht erfolgreich im Archiv gespeichert!"); st.rerun()

# --- 7. ARCHIV ---
st.divider()
st.header("📂 Einsatzarchiv")

suche = st.text_input("🔍 Schnellsuche (Ort oder AZ)", placeholder="z.B. Rathausplatz...")
daten = lade_daten()

if not daten.empty:
    # Filterung
    if suche:
        display_df = daten[daten['Ort'].str.contains(suche, case=False) | daten['AZ'].str.contains(suche, case=False)]
    else:
        display_df = daten

    for i, row in display_df.iloc[::-1].iterrows():
        with st.expander(f"📄 {row['Datum']} | {row['Ort']} {row['Hausnummer']} (AZ: {row['AZ']})"):
            # Header-Infos als Spalten
            a1, a2, a3 = st.columns(3)
            a1.markdown(f"**🕒 Zeit:** {row['Beginn']} - {row['Ende']}")
            a2.markdown(f"**👮 Kräfte:** {row['Kraefte']}")
            a3.markdown(f"**📍 GPS:** `{row['GPS']}`")
            
            st.markdown("---")
            st.markdown(f"**📝 Sachverhalt:**")
            st.info(row['Bericht'])
            
            if row['Zeugen'] != "-":
                st.markdown(f"**👥 Beteiligte:** {row['Zeugen']}")
            
            if row['Foto'] != "-":
                st.image(base64.b64decode(row['Foto']), caption="Einsatzfoto", width=400)
            
            # Admin-Funktionen (Export)
            if st.session_state["admin_auth"]:
                st.button(f"🗑️ Bericht löschen (ID: {i})", key=f"del_{i}") # Logik müsste noch ergänzt werden
else:
    st.write("Keine Berichte vorhanden.")

# Sidebar Admin
with st.sidebar:
    if st.checkbox("🔑 Admin-Bereich"):
        if st.text_input("Admin-Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin-Modus aktiv")
