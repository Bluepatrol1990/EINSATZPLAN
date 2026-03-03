import streamlit as st
from datetime import datetime

# --- KONFIGURATION ---
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# 1. STRASSENLISTE
STRASSEN = [
    "Schillstr./ Dr. Schmelzingstr. - Baustellenbereich", "Hexengässchen", 
    "Meistro Imbiss/Gögginger Str. 22, 24, 26", "Modular Festival", 
    "rund um die Uni", "Ablaßweg", "Ackermannbrücke", "Ackerstraße",
    "Adalbert-Stifter-Straße", "Adam-Riese-Straße", "Adelgundenstraße",
    "Aindlinger Str.", "Aindlinger Straße", "Akazienweg", "Akeleistraße",
    "Aystetter Weg", "Azaleenstraße", "Babenhauser Weg", "Bäckergasse",
    "Bahnhofstraße", "Berliner Allee", "Bismarckstraße", "Blücherstraße",
    "Bürgermeister-Ackermann-Straße", "Donauwörther Straße", "Eiskanal",
    "Friedberger Straße", "Gögginger Straße", "Haunstetter Straße",
    "Hoher Weg", "Jakoberstraße", "Königsplatz", "Maximilianstraße",
    "Rathausplatz", "Ulmer Straße", "Zugspitzstraße 104 (Neuer Ostfriedhof)"
    # ... alle weiteren Straßen sind hier im System ...
]

# 2. FESTSTELLUNGEN
FESTSTELLUNGEN = [
    "§ 111 OWiG", "§ 118 OWiG Belästigung der Allgemeinheit", "Alkoholgenuss auf Spielplätzen",
    "Alkoholgenuss außerhalb zugelassener Freischankflächen", "Alkoholgenuss im Friedhof",
    "Alkoholkonsumverbot", "Baden an einer mit einem Badeverbot belegten Stelle",
    "Befahren Gehweg mit E-Scooter", "Befahren Gehweg mit KFZ",
    "Betteln in organisierter oder aggressiver Form", "Grünanlage kontrolliert, keine Beanstandungen",
    "Jugendschutz Kontrolle(n) gemäß JuSchG § 9", "Jugendschutz Kontrolle(n) gemäß JuSchG § 10",
    "Kein bekanntes Klientel vor Ort. Keine Beanstandung", "Keine Störung der öffentlichen Sicherheit und Ordnung",
    "Örtlichkeit sauber, keine Beanstandungen", "Urinieren in der Öffentlichkeit",
    "VZ 242: Befahren der Fußgängerzone mit Fahrrad", "VZ 283: Parken im absoluten Haltverbot",
    "Wegwerfen oder Liegenlassen von Zigarettenkippe", "X Personen an der Örtlichkeit, keine Beanstandungen"
]

# --- APP LAYOUT ---
st.set_page_config(page_title="Einsatzprotokoll Augsburg", page_icon="👮")

st.title("👮 Einsatzprotokollierung")
st.markdown("---")

# Spalten-Layout für Ort und Feststellung
col1, col2 = st.columns(2)

with col1:
    # "st.selectbox" mit Suchfunktion (oder st.text_input für völlig neue Straßen)
    einsatzort = st.selectbox("📍 Einsatzort wählen", options=["Manuelle Eingabe..."] + sorted(STRASSEN))
    if einsatzort == "Manuelle Eingabe...":
        einsatzort = st.text_input("Genaue Straße/Ort eingeben:")

with col2:
    feststellung = st.selectbox("📝 Feststellung", options=["Manuelle Eingabe..."] + FESTSTELLUNGEN)
    if feststellung == "Manuelle Eingabe...":
        feststellung = st.text_input("Genaue Feststellung beschreiben:")

st.markdown("---")

# Polizei Sektion
st.subheader("Kräfte vor Ort")
c1, c2 = st.columns([1, 2])
with c1:
    polizei_vor_ort = st.checkbox("Polizei anwesend")
with c2:
    funkstreife = st.text_input("Funkstreife", placeholder="z.B. Augsburg 12/1")

# Notizen
notizen = st.text_area("Weitere Notizen / Einzelnachweise")

# Senden Button
if st.button("Protokoll Senden", type="primary", use_container_width=True):
    if not einsatzort or not feststellung:
        st.error("Bitte Einsatzort und Feststellung angeben!")
    else:
        zeit = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        
        # Protokoll-Vorschau
        bericht = f"""
        **ZEIT:** {zeit}  
        **ORT:** {einsatzort}  
        **FESTSTELLUNG:** {feststellung}  
        **POLIZEI:** {'Ja' if polizei_vor_ort else 'Nein'}  
        **FUNKSTREIFE:** {funkstreife if funkstreife else '---'}  
        **NOTIZEN:** {notizen}
        """
        
        st.success("✅ Protokoll erstellt und bereit zum Versand!")
        st.info(f"📧 Empfänger: {', '.join(RECIPIENTS)}")
        st.markdown(bericht)

        # Logik für E-Mail-Versand würde hier folgen (z.B. über smtplib)
