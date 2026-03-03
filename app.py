import streamlit as st
from datetime import datetime

# --- EMPFÄNGER AUS DEINEN VORGABEN ---
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# --- DATENLISTEN ---
# (Hier sind beispielhaft die ersten Straßen und Feststellungen, 
# du kannst die Liste im Code einfach mit deiner kompletten Liste füllen)
STRASSEN = [
    "Schillstr./ Dr. Schmelzingstr. - Baustellenbereich", "Hexengässchen", 
    "Meistro Imbiss/Gögginger Str. 22, 24, 26", "Modular Festival", 
    "rund um die Uni", "Ablaßweg", "Ackermannbrücke", "Ackerstraße",
    "Adalbert-Stifter-Straße", "Zugspitzstraße 104 (Neuer Ostfriedhof)"
]

FESTSTELLUNGEN = [
    "§ 111 OWiG", "§ 118 OWiG Belästigung der Allgemeinheit", "Alkoholgenuss auf Spielplätzen",
    "Baden an einer mit einem Badeverbot belegten Stelle", "Befahren Gehweg mit E-Scooter",
    "Grünanlage kontrolliert, keine Beanstandungen", "Keine Störung der öffentlichen Sicherheit und Ordnung",
    "VZ 242: Befahren der Fußgängerzone mit Fahrrad", "VZ 283: Parken im absoluten Haltverbot"
]

# --- APP LAYOUT ---
st.set_page_config(page_title="OD Augsburg Protokoll", page_icon="👮", layout="wide")

st.title("👮 Einsatzprotokollierung Ordnungsdienst")
st.info(f"Berichte werden gesendet an: {', '.join(RECIPIENTS)}")

# Sektion 1: Ort & Feststellung
st.subheader("Einsatzdetails")
col1, col2 = st.columns(2)

with col1:
    # "Index=None" erlaubt leeres Feld am Anfang
    ort_auswahl = st.selectbox("📍 Einsatzort wählen", options=sorted(STRASSEN), index=None, placeholder="Straße suchen...")
    manueller_ort = st.text_input("Oder anderen Ort/Straße eingeben:", placeholder="Falls oben nicht gelistet...")
    finaler_ort = manueller_ort if manueller_ort else ort_auswahl

with col2:
    fest_auswahl = st.selectbox("📝 Feststellung wählen", options=FESTSTELLUNGEN, index=None, placeholder="Verstoß suchen...")
    manuelle_fest = st.text_input("Oder andere Feststellung eingeben:", placeholder="Eigener Text...")
    finale_fest = manuelle_fest if manuelle_fest else fest_auswahl

st.markdown("---")

# Sektion 2: Polizei & Funkstreife
st.subheader("Kräfte vor Ort")
c1, c2 = st.columns([1, 2])
with c1:
    polizei_vor_ort = st.checkbox("Polizei anwesend")
with c2:
    # Dieses Feld ist immer sichtbar, damit die Funkstreife eingetragen werden kann
    funkstreife = st.text_input("Funkstreife", placeholder="Rufname eingeben (z.B. Augsburg 12/1)")

# Sektion 3: Notizen
st.subheader("Zusätzliche Informationen")
notizen = st.text_area("Notizen / Einzelnachweise", placeholder="Hier Details eintragen...")

# --- SENDEN BUTTON ---
if st.button("Protokoll Senden", type="primary", use_container_width=True):
    if not finaler_ort or not finale_fest:
        st.error("❌ Fehler: Einsatzort und Feststellung müssen angegeben werden!")
    else:
        zeitpunkt = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        
        # Protokoll-Zusammenfassung
        st.success("✅ Protokoll erfolgreich generiert!")
        
        ausgabe = f"""
        **PROTOKOLL-DETAILS:**
        - **Zeit:** {zeitpunkt}
        - **Ort:** {finaler_ort}
        - **Feststellung:** {finale_fest}
        - **Polizei:** {"Ja" if polizei_vor_ort else "Nein"}
        - **Funkstreife:** {funkstreife if funkstreife else "Keine Angabe"}
        - **Zusatz:** {notizen if notizen else "Keine weiteren Anmerkungen"}
        """
        st.markdown(ausgabe)
        
        # Hier kann später die E-Mail-Funktion (SMTP) aktiviert werden
        st.toast("Daten wurden für den Versand vorbereitet!")

