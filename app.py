import streamlit as st
import urllib.parse

# Seite konfigurieren
st.set_page_config(page_title="Einsatzprotokoll Stadt Augsburg", layout="centered")

st.title("📋 Einsatzprotokoll")
st.subheader("Stadt Augsburg - Ordnungsdienst")

# Empfänger aus deinen Vorgaben
RECIPIENTS = "Kevin.woelki@augsburg.de; kevinworlki@outlook.de"

# Formular-Felder
standort = st.text_input("Standort / Örtlichkeit", placeholder="z.B. Königsplatz, Kuhsee...")

# Die Liste der Feststellungen
feststellungen_liste = [
    "-- Bitte wählen --", "§ 111 OWiG", "§ 118 OWiG Belästigung der Allgemeinheit", 
    "Alkoholgenuss auf Spielplätzen", "Alkoholgenuss außerhalb zugelassener Freischankflächen", 
    "Alkoholgenuss im Friedhof", "Alkoholkonsumverbot", 
    "als Berechtigter außerhalb der zugelassenen Zeiten ein KFZ abgestellt", 
    "als Berechtigter außerhalb der zugelassenen Zeiten ein KFZ benutzt", 
    "Anzeige(n) an das Jugendamt wird / werden erstellt", "Aufstellen von Zelten und Wohnwagen", 
    "Baden an einer mit einem Badeverbot belegten Stelle", "Befahren Gehweg mit E-Scooter", 
    "Befahren Gehweg mit KFZ", "Betreiben von Feuerstellen und das Grillen außerhalb der dafür gekennzeichneten Flächen", 
    "Betreten von Blumenschmuckpflanzungen", "Betretenlassen des Kuhsees, Ilsesees oder Autobahnsees durch Hunde", 
    "Betteln in organisierter oder aggressiver Form", "Bürgerinformationen", "Dienstfahrzeug getankt", 
    "direktes unverwahrtes Feuer auf Kiesbänken", "div. Innendiensttätigkeiten", 
    "Ermittlungen für den Innendienst", "E-Scooter auf unbesch. Gehweg", "E-Scooter ohne Licht", 
    "Fahren, Parken oder Abstellen in Grünanlage (E-Scooter)", "Fahren, Parken oder Abstellen in Grünanlage (KFZ)", 
    "Falsche Umweltplakette", "Fehlende Umweltplakette", "Grünanlage kontrolliert, keine Auffälligkeiten.", 
    "Grünanlage kontrolliert, keine Beanstandungen", "Hexengässchen", "Hunde in Blumenschmuckpflanzung", 
    "Jugendschutz Kontrolle(n) gemäß JuSchG § 10", "Jugendschutz Kontrolle(n) gemäß JuSchG § 9", 
    "Kein bekanntes Klientel vor Ort. Keine Beanstandung", "Kein ordnungswidriges Verhalten feststellbar.", 
    "Kein Vandalismus feststellbar.", "Keine Beanstandungen", "Keine beschwerderelevanten Vorkommnisse feststellbar.", 
    "Keine Bettler vor Ort", "Keine Obdachlose an der Örtlichkeit, keine Beanstandungen", 
    "Keine Ordnungswidrigkeiten festgestellt.", "Keine Personen vor Ort", 
    "Keine Personen vor Ort. Keine Beanstandungen.", "Keine Störung der öffentlichen Sicherheit und Ordnung", 
    "Keine Verunreinigung durch Sperrmüll feststellbar.", "Lagern und Nächtigen", 
    "Mitführen u./o. Laufenlassen von Hunden auf Liegeflächen", "Mitführen u./o. Laufenlassen von Hunden auf Spielplätzen", 
    "Mitführen u./o. Laufenlassen von Hunden im Friedhof", 
    "ohne zum Kreis der Berechtigten zu gehören und außerhalb der zugelassenen Zeiten ein KFZ abgestellt", 
    "ohne zum Kreis der Berechtigten zu gehören und außerhalb der zugelassenen Zeiten ein KFZ benutzt", 
    "Örtlichkeit gut besucht, keine Beanstandungen", "Örtlichkeit sauber, keine Beanstandungen", 
    "Örtlichkeit verschmutzt, kein Verursacher feststellbar", "Örtlichkeit wenig besucht, keine Beanstandungen.", 
    "Parken auf Gehweg", "Parken im Straßenbegleitgrün", "Parken in amtlich gekennzeichneter Feuerwehrzufahrt", 
    "Parken in der Bordsteinabsenkung", "Parken in einer Grünanlage mit E-Scooter", 
    "Parken in einer Grünanlage mit KFZ", "Parken nicht am rechten Fahrbahnrand", 
    "Parken vor Bordsteinabsenkung", "Radfahren auf einem Friedhof", "Radfahren auf Radweg in falscher Richtung", 
    "Radfahren auf unbeschildertem Gehweg", "Radfahren in einer Grünanlage", "Radfahren in entgegengesetzte Richtung", 
    "Radfahren mit Gehörbeeinträchtigung", "Radfahren ohne Licht", "Radfahren und Handybenutzung", 
    "Rauchen auf Spielplätzen", "Siehe Einzelnachweise", "Spielplatz kontrolliert, keine Beanstandungen", 
    "Übermäßiges Füttern von Tauben", "Urinieren in der Öffentlichkeit", 
    "Verbot für Glasbehälter oder ähnliche Gegenstände aus Glas", "Verrichten der Notdurft", 
    "Verstoß gegen das Merkblatt für Straßenmusikanten", "Verstoß gegen die Lärmschutzverordnung", 
    "Verstoß gegen die Straßensondernutzung", "Verunreinigung durch Hundekot", "VZ 229: Parken im Taxistand", 
    "VZ 237: nicht Benutzung des vorhandenen Radweges", "VZ 239: Befahren eines beschilderten Gehweges mit E-Scooter", 
    "VZ 239: Befahren eines beschilderten Gehweges mit KFZ", "VZ 239: Radfahren auf einem beschilderten Gehweg", 
    "VZ 240: nicht Benutzung des vorhandenen Radweges", "VZ 241: nicht Benutzung des vorhandenen Radweges", 
    "VZ 242: Befahren der Fußgängerzone mit E-Scooter", "VZ 242: Befahren der Fußgängerzone mit Fahrrad", 
    "VZ 242: Befahren der Fußgängerzone mit KFZ", "VZ 242: Befahren Fußgängerzone ohne Ausnahmegenehmigung", 
    "VZ 242: Befahren Fußgängerzone schneller als Schrittgeschwindigkeit", "VZ 242: Parken in der Fußgängerzone mit KFZ", 
    "VZ 250: Verbot für Fahrzeuge aller Art", "VZ 260: Verbot für Kraftfahrzeuge", 
    "VZ 283: Parken im absoluten Haltverbot", "VZ 286: Parken im eingeschränkten Haltverbot", 
    "VZ 314: + Zusatzzeichen 1044 10: Parken Sonderparkplatz Schwerbehinderte", 
    "VZ 314: Parken mit KFZ Nur Elektrofahrzeuge", "VZ 325: Parken außerhalb gekennzeichneten Flächen", 
    "VZ 325: schneller als Schrittgeschwindigkeit", "Wegwerfen oder Liegenlassen gefährlicher Gegenstände", 
    "Wegwerfen oder Liegenlassen von Abfällen", "Wegwerfen oder Liegenlassen von Zigarettenkippe", 
    "X Personen an der Örtlichkeit, keine Beanstandungen", "Zugspitzstraße 104 (Neuer Ostfriedhof)"
]

feststellung = st.selectbox("Feststellung", feststellungen_liste)
details = st.text_area("Zusätzliche Details / Bemerkungen")

# E-Mail Link Logik
if st.button("📧 Bericht in E-Mail App öffnen"):
    if not standort:
        st.warning("Bitte gib einen Standort an.")
    else:
        subject = f"Einsatzbericht: {standort}"
        body = f"Guten Tag,\n\nanbei der Einsatzbericht:\n\nSTANDORT: {standort}\nFESTSTELLUNG: {feststellung}\nDETAILS: {details}"
        
        # URL Encoding für Mailto
        mailto_link = f"mailto:{RECIPIENTS}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        
        # HTML Link zum Klicken (da Streamlit keine direkten redirects erlaubt)
        st.markdown(f'<a href="{mailto_link}" target="_blank" style="text-decoration: none; color: white; background-color: #0054a6; padding: 10px 20px; border-radius: 5px;">Klicke hier zum Senden</a>', unsafe_allow_html=True)

st.info(f"Standard-Empfänger: {RECIPIENTS}")
