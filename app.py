import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF

# --- KONFIGURATION & MODERNES STYLING ---
st.set_page_config(page_title="OA Einsatzbericht", page_icon="🚓", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    h1, h2, h3, p, span, label, div, .stMarkdown { color: #ffffff !important; font-family: 'Segoe UI', Roboto, sans-serif; }
    .main-title { color: #ffffff; font-size: 2.5rem; font-weight: 800; border-bottom: 3px solid #004b95; padding-bottom: 15px; margin-bottom: 30px; }
    .einsatz-card { background: linear-gradient(145deg, #111111, #1a1a1a); border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid #333; border-left: 8px solid #004b95; }
    .card-header { font-size: 1.3rem; font-weight: bold; color: #6ea8fe !important; margin-bottom: 5px; }
    .card-meta { font-size: 0.85rem; color: #aaaaaa !important; margin-bottom: 10px; }
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; margin-right: 8px; text-transform: uppercase; display: inline-block; }
    .b-pol { background-color: #004b95; color: white; }
    .b-rd { background-color: #8b0000; color: white; }
    .b-fs { background-color: #ffcc00; color: black; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div { background-color: #1a1a1a !important; color: white !important; border-radius: 8px !important; border: 1px solid #444 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- PASSWÖRTER & DATEIEN ---
DIENST_PW = "1234"      # Für alle (Berichte schreiben & lesen)
ADMIN_PW = "admin789"   # Nur für dich (Löschen & Bearbeiten)
DATEI = "zentral_archiv.csv"
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# --- STRASSENLISTE AUGSBURG ---
STRASSEN_AUGSBURG = sorted([
    "Maximilianstraße", "Königsplatz", "Rathausplatz", "Annastraße", "Bahnhofstraße", "Hermanstraße", "Karlstraße", 
    "Grottenau", "Moritzplatz", "Ulrichsplatz", "Fuggerstraße", "Konrad-Adenauer-Allee", "Donauwörther Straße", 
    "Ulmer Straße", "Hirblinger Straße", "Lechhauser Straße", "Neuburger Straße", "Haunstetter Straße", 
    "Gögginger Straße", "Friedberger Straße", "Berliner Allee", "Bgm.-Ackermann-Straße",
    "📍 Manuelle Eingabe / Sonstiger Ort"
])

# --- FUNKTIONEN ---
def lade_daten():
    spalten = ["Datum", "Anfang", "Ende", "Ort", "Zusatz", "Zeugen", "Polizei", "RD", "FS", "FS_Details", "Bericht"]
    if os.path.exists(DATEI):
        try:
            df = pd.read_csv(DATEI)
            for s in spalten:
                if s not in df.columns: df[s] = "-"
            return df[spalten].fillna("-").astype(str)
        except: return pd.DataFrame(columns=spalten)
    return pd.DataFrame(columns=spalten)

# --- LOGIN LOGIK ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "is_admin" not in st.session_state: st.session_state["is_admin"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("<h1 style='text-align:center;'>🚓 Dienst-Login</h1>", unsafe_allow_html=True)
        pw_input = st.text_input("Dienst-Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw_input == DIENST_PW:
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Falsches Passwort")
    st.stop()

# --- SIDEBAR (ADMIN-MODUS) ---
with st.sidebar:
    st.title("⚙️ Verwaltung")
    if not st.session_state["is_admin"]:
        admin_in = st.text_input("Admin-Passwort (Bearbeiten)", type="password")
        if st.button("Admin-Modus aktivieren"):
            if admin_in == ADMIN_PW:
                st.session_state["is_admin"] = True
                st.success("Modus aktiv!")
                st.rerun()
    else:
        st.warning("🔓 Admin-Modus AKTIV")
        if st.button("Admin-Modus beenden"):
            st.session_state["is_admin"] = False
            st.rerun()
    st.divider()
    if st.button("🔴 Logout"):
        st.session_state["auth"] = False
        st.rerun()

# --- HAUPTBEREICH ---
st.markdown("<div class='main-title'>📋 Einsatzbericht</div>", unsafe_allow_html=True)
daten = lade_daten()

# NEUEN BERICHT ERFASSEN (Für jeden nach Login erlaubt)
with st.expander("➕ NEUEN EINSATZBERICHT SCHREIBEN", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        d = c1.date_input("Datum", datetime.now())
        ts = c2.time_input("Beginn", datetime.now().time())
        te = c3.time_input("Ende", datetime.now().time())
        
        o1, o2 = st.columns([2, 1])
        auswahl_str = o1.selectbox("Straße / Platz", options=STRASSEN_AUGSBURG)
        zusatz = o2.text_input("Nr. / Zusatz (z.B. 12a, 3. OG)")
        
        finaler_ort = auswahl_str
        if auswahl_str == "📍 Manuelle Eingabe / Sonstiger Ort":
            finaler_ort = st.text_input("Genaue Adresse manuell")
        
        zeuge = st.text_input("Beteiligte / Zeugen")
        k1, k2, k3, k4 = st.columns([1,1,1,2])
        pol, rd, fs = k1.checkbox("POL"), k2.checkbox("RD"), k3.checkbox("FS")
        fsi = k4.text_input("Details Funkstreife")
        txt = st.text_area("Bericht / Sachverhalt", height=150)
        
        if st.form_submit_button("🚀 BERICHT SPEICHERN", use_container_width=True):
            if txt and finaler_ort:
                new = pd.DataFrame([[str(d), ts.strftime("%H:%M"), te.strftime("%H:%M"), str(finaler_ort), str(zusatz), str(zeuge), 
                                     "Ja" if pol else "Nein", "Ja" if rd else "Nein", "Ja" if fs else "Nein", 
                                     str(fsi), str(txt)]], columns=daten.columns)
                pd.concat([daten, new], ignore_index=True).to_csv(DATEI, index=False)
                st.success("Bericht erfolgreich gespeichert!")
                st.rerun()

# --- ARCHIV ---
st.subheader("📂 Archivierte Berichte")
if not daten.empty:
    for i, row in daten.iloc[::-1].iterrows():
        p_b = f'<span class="badge b-pol">POL</span>' if row['Polizei'] == "Ja" else ""
        r_b = f'<span class="badge b-rd">RD</span>' if row['RD'] == "Ja" else ""
        f_b = f'<span class="badge b-fs">FS</span>' if row['FS'] == "Ja" else ""
        
        st.markdown(f"""
            <div class="einsatz-card">
                <div class="card-header">📍 {row['Ort']} {row.get('Zusatz', '-')}</div>
                <div class="card-meta">📅 {row['Datum']} | ⏰ {row['Anfang']} - {row['Ende']}</div>
                <div>{p_b}{r_b}{f_b}</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Details anzeigen"):
            st.info(f"**Beteiligte:** {row['Zeugen']}\n\n**Sachverhalt:**\n{row['Bericht']}")
            
            # BEARBEITEN / LÖSCHEN NUR FÜR ADMIN
            if st.session_state["is_admin"]:
                st.divider()
                st.subheader("🛠️ Admin-Bereich")
                if st.button(f"🗑️ Bericht unwiderruflich löschen", key=f"del_{i}"):
                    daten = daten.drop(i)
                    daten.to_csv(DATEI, index=False)
                    st.success("Gelöscht!")
                    st.rerun()
            else:
                st.caption("🔒 Löschen und Bearbeiten ist nur für Admins möglich.")
else:
    st.info("Keine Berichte im Archiv vorhanden.")
