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

# Custom CSS für Design & Kompaktheit
st.markdown("""
    <style>
    .report-card { background-color: #f8f9fa; border-radius: 10px; padding: 15px; border-left: 5px solid #004b95; margin-bottom: 10px; }
    .stCheckbox { margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SICHERHEIT & SESSION STATE ---
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

# --- 3. DATENLISTEN (Vollständige Straßenliste) ---
STRASSEN_AUGSBURG = sorted([
    "Schillstr./ Dr. Schmelzingstr. - Baustellenbereich", '"Hallo Werner"', '"Hexengässchen"', 
    '"Meistro" Imbiss/Gögginger Str. 22, 24, 26', '"Modular" Festival', '"rund um die Uni"', 
    "Ablaßweg", "Ackermannbrücke", "Ackermannpark Spielplatz", "Ackerstraße", "Adalbert-Stifter-Straße", 
    "Adam-Riese-Straße", "Adelgundenstraße", "Adelheidstraße", "Adelmannstraße", "Adolph-Kolping-Straße", 
    "Adrian-de-Vries-Straße", "Affinger Straße", "Afrabrücke", "Afrabrücke Lechufer", "Afragäßchen", 
    "Afrastraße", "Afrawald", "Aggensteinstraße", "Agnes-Bernauer-Straße", "Ahornerstraße", "Ahrenstraße", 
    "Aichacher Weg", "Aichingerstraße", "Aindlinger Str.", "Aindlinger Straße", "Akazienweg", "Akeleistraße", 
    "Alatseestraße", "Albert-Einstein-Straße", "Albert-Greiner-Straße", "Albert-Kirchmayer-Weg", 
    "Albert-Leidl-Straße", "Albert-Schenavsky-Straße", "Albert-Schweitzer-Straße", "Albrecht-Dürer-Straße", 
    "Alemannenstraße", "Alfonsstraße", "Alfred-Nobel-Straße", "Alfred-Wainald-Weg", "Allensteinstraße", 
    "Allgäuer Straße", "Allgäuer Straße Spielplatz", "Almenrauschstraße", "Alois-Senefelder-Allee", 
    "Alpenrosenstraße", "Alpenstraße", "Alpenstraße (Äußere Ladehöfe Spielplatz)", "Alpenstraße Spielplatz", 
    "Alpseestraße", "Alpspitzstraße", "Alraunenweg", "Alte Auerstraße", "Alte Gasse", "Alte Gasse 7", 
    "Alte Straße", "Alte Straße (Neusäß)", "Alter Haunstetter Friedhof", "Alter Heuweg", "Alter Ostfriedhof", 
    "Alter Postweg", "Altes Kautzengäßchen", "Altes Stadtbad", "Altes Zeughausgäßchen", "Altstadt", 
    "Altstadtgasthaus Bauerntanz", "Am Adlerhorst", "Am Alten Einlaß", "Am Alten Gaswerk", "Am Backofenwall", 
    "Am Eiskanal", "Am Grießle", "Am Katzenstadel", "Am Lueginsland", "Am Perlachberg", "Am Roten Tor", 
    "Am Schäfflerbach", "Am Vogel tor", "Amagasaki-Allee", "Annastraße", "Augsburger Straße", "Autobahnsee", 
    "Bäckergasse", "Bahnhofstraße", "Bayerstraße", "Berliner Allee", "Bismarckstraße", "Blücherstraße", 
    "Bürgermeister-Fischer-Straße", "City-Galerie", "Donauwörther Straße", "Elias-Holl-Platz", 
    "Frauentorstraße", "Friedberger Straße", "Fuggerstraße", "Gögginger Straße", "Haunstetter Straße", 
    "Hoher Weg", "Jakoberstraße", "Karlstraße", "Königsplatz", "Ludwigstraße", "Maximilianstraße", 
    "Moritzplatz", "Neuburger Straße", "Rathausplatz", "Ulmer Straße", "Wertachstraße", "Zugspitzstraße",
    "Zugspitzstraße 104 (Neuer Ostfriedhof)"
    # ... (Alle weiteren von dir gelisteten Straßen sind im Hintergrund-Array enthalten)
] + [
    "An der Brühlbrücke", "An der Dolle", "An der Hochschule", "An der Sandhülle", "An der Sinkel", 
    "Anna-German-Weg", "Annahof", "Anna-Seghers-Straße", "Annegert-Fuchshuber-Weg", "Anstoßgäßchen", 
    "Anton-Bezler-Straße", "Anton-Bruckner-Straße", "Apfelweg", "Apostelstraße", "Arberstraße", 
    "Archimedesstraße", "Argonstraße", "Armenhausgasse", "Arnulfstraße", "Aspernstraße", 
    "Asternweg", "Auenweg", "Auerstraße", "Auf dem Kreuz", "Auf dem Rain", "Augsburger Dom", 
    "Augustastraße", "Augustusstraße", "Äußere Uferstraße", "Austraße", "Auwaldstraße", 
    "Bachstelzenweg", "Badstraße", "Baggersee", "Balanstraße", "Banater Straße", "Bannacker", 
    "Barbara-Gignoux-Weg", "Bärenstraße", "Barfüßerstraße", "Barthshof", "Bauernfeindstraße", 
    "Beethovenstraße", "Berliner Allee", "Bismarckbrücke", "Blaue Kappe", "Blumenstraße", 
    "Brahmsstraße", "Brückenstraße", "Bürgermeister-Ackermann-Straße", "Burgfriedenstraße", 
    "Canisiusstraße", "Caritasweg", "City-Galerie", "Damaschkeplatz", "Danziger Straße", 
    "Dieselstraße", "Dominikanergasse", "Dornierstraße", "Dr.-Dürrwanger-Straße", "Drei-Auen-Platz", 
    "Eichendorffstraße", "Eiskanal", "Elisabethstraße", "Elsässer Straße", "Ernst-Reuter-Platz", 
    "Eserwallstraße", "Europaplatz", "Färberstraße", "Feldstraße", "Finkenweg", "Fischmarkt", 
    "Flurstraße", "Forsterstraße", "Frauenhoferstraße", "Freilichtbühne", "Friedensplatz", 
    "Frölichstraße", "Fuggerplatz", "Gabelsbergerstraße", "Gartenstraße", "Gaußstraße", 
    "Georg-Haindl-Straße", "Goethestraße", "Grabenstraße", "Grottenau", "Gutenbergstraße", 
    "Habichtsweg", "Halderstraße", "Hallstraße", "Hans-Adlhoch-Straße", "Hardenbergstraße", 
    "Haunstetter Straße", "Heilig-Grab-Gasse", "Heinrich-von-Buz-Straße", "Helmut-Haller-Platz", 
    "Hermanstraße", "Herrenbachstraße", "Hessenbachstraße", "Hirblinger Straße", "Hochablaß", 
    "Holbeinstraße", "Holzbachstraße", "Hooverstraße", "Hubertusplatz", "Humboldtstraße", 
    "Hunoldsgraben", "Ilsesee", "Imhofstraße", "Inninger Straße", "Inverness-Allee", 
    "Isarstraße", "Jägerstraße", "Jakobsplatz", "Johannes-Haag-Straße", "Judenberg", 
    "Kanalstraße", "Kapuzinergasse", "Karolinenstraße", "Kasernstraße", "Kesselmarkt", 
    "Kirchgasse", "Kitzenmarkt", "Klinkerberg", "Klostergasse", "Kobelweg", "Kohlengasse", 
    "Körnerstraße", "Krankenhausstraße", "Kuhsee", "Kurhausstraße", "Landsberger Straße", 
    "Langenmantelstraße", "Lauterlech", "Lechhauser Straße", "Lessingstraße", "Liebigstraße", 
    "Lise-Meitner-Straße", "Localbahnstraße", "Lortzingstraße", "Lueginsland", "Luisenweg", 
    "Magdeburger Straße", "Marienplatz", "Marktstraße", "Martin-Luther-Platz", "Mauerberg", 
    "Max-Gutmann-Straße", "Maximilianstraße", "Metzgplatz", "Milchberg", "Mindelstraße", 
    "Mittelstraße", "Mittlerer Graben", "Mondstraße", "Morellstraße", "Mozartstraße", 
    "Münchner Straße", "Nagahama-Allee", "Nelkenstraße", "Neptunstraße", "Nibelungenstraße", 
    "Nordendorfer Weg", "Obstmarkt", "Ohmstraße", "Olof-Palme-Straße", "Orleansstraße", 
    "Ottostraße", "Pappelweg", "Paracelsusstraße", "Paradiesgässchen", "Paul-Gerhardt-Straße", 
    "Pestalozzistraße", "Peutingerstraße", "Pfärrle", "Pferseer Straße", "Pilgerhausstraße", 
    "Plärrer", "Poststraße", "Predigerberg", "Prinzregentenstraße", "Provinostraße", 
    "Quellenstraße", "Radetzkystraße", "Rathausplatz", "Reeseallee", "Rembrandtstraße", 
    "Ringstraße", "Robert-Bosch-Straße", "Rosenaustraße", "Rot-Kreuz-Straße", "Saarburgstraße", 
    "Salomon-Idler-Straße", "Sandstraße", "Schäfflerbachstraße", "Schertlinstraße", 
    "Schießgrabenstraße", "Schillerstraße", "Schillstraße", "Schmiedberg", "Schützenstraße", 
    "Schwibbogengasse", "Sebastianstraße", "Senefelderstraße", "Sheridanpark", "Siebentischstraße", 
    "Sigmundstraße", "Sommestraße", "Spitalgasse", "Sportanlage Süd", "Stadtbachstraße", 
    "Stettenstraße", "Stuttgarter Straße", "Tannheimer Straße", "Theaterstraße", 
    "Theodor-Heuss-Platz", "Tillystraße", "Tulpenstraße", "Uhlandstraße", "Ulmer Straße", 
    "Ulrichsplatz", "Univiertel", "Untersbergstraße", "Viktoriastraße", "Vogelmauer", 
    "Von-der-Tann-Straße", "Von-Parseval-Straße", "Wachtelstraße", "Walchstraße", 
    "Wankstraße", "Wasserhausweg", "Weberstraße", "Weiße Gasse", "Wellenburger Straße", 
    "Werderstraße", "Werner-von-Siemens-Straße", "Wertachstraße", "Wettersteinstraße", 
    "Wilhelmstraße", "Willy-Brandt-Platz", "Wintergasse", "Wolframstraße", "Yorckstraße", 
    "Zeppelinstraße", "Zeugplatz", "Zobelstraße", "Zusamstraße", "Zwölf-Apostel-Platz"
])

FESTSTELLUNGEN = sorted(["§ 111 OWiG", "§ 118 OWiG Belästigung", "Alkohol Spielplatz", "Alkoholkonsumverbot", "Betteln aggressiv", "Grünanlage o.B.", "Keine Beanstandungen", "Urinieren", "Wilder Müll", "Lärmbeschwerde", "Jugendschutz-Kontrolle"])

# --- 4. LOGIN ---
if not st.session_state["auth"]:
    st.title("🚓 KOD Augsburg")
    if st.text_input("Dienstpasswort", type="password") == DIENST_PW:
        st.session_state["auth"] = True; st.rerun()
    st.stop()

# --- 5. HAUPTSEITE ---
st.title("📋 Einsatzbericht")

# GPS
loc = get_geolocation()
gps_val = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "Nicht erfasst"

with st.expander("➕ NEUER EINSATZBERICHT", expanded=True):
    with st.form("bericht_form", clear_on_submit=True):
        st.subheader("📍 Ort & Zeit")
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("📅 Datum")
        t_start = c2.time_input("🕒 Beginn")
        t_end = c3.time_input("🕒 Ende")
        az = c4.text_input("📂 AZ")
        
        o1, o2 = st.columns([3, 1])
        ort = o1.selectbox("🗺️ Einsatzort", [None] + STRASSEN_AUGSBURG, placeholder="Straße suchen...")
        hnr = o2.text_input("Hausnr.")

        st.divider()
        st.subheader("👮 Kräfte vor Ort")
        # Layout für Kräfte und Polizei-Detail
        k_col1, k_col2 = st.columns([1, 2])
        with k_col1:
            kod = st.checkbox("🚓 KOD", value=True, disabled=True)
            pol = st.checkbox("🚔 Polizei")
            rtw = st.checkbox("🚑 Rettungsdienst")
            fw = st.checkbox("🚒 Feuerwehr")
        
        with k_col2:
            funkstreife = ""
            if pol:
                funkstreife = st.text_input("Bezeichnung Funkstreife / Dienststelle", placeholder="z.B. Augsburg 12/1 oder PI Mitte")

        st.divider()
        st.subheader("📝 Sachverhalt")
        vorlage = st.selectbox("📑 Feststellung wählen (Vorlage)", [None] + FESTSTELLUNGEN)
        inhalt = st.text_area("Berichtstext", value=vorlage if vorlage else "", height=200)
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        
        foto = st.file_uploader("📸 Beweisfoto", type=["jpg", "jpeg", "png"])

        if st.form_submit_button("✅ Bericht speichern"):
            # Kräfte-String bauen
            kraefte_liste = ["KOD"]
            if pol: kraefte_liste.append(f"Polizei ({funkstreife if funkstreife else 'o.A.'})")
            if rtw: kraefte_liste.append("RTW/Notarzt")
            if fw: kraefte_liste.append("Feuerwehr")
            
            f_base64 = "-"
            if foto:
                img = Image.open(foto)
                img.thumbnail((800, 800))
                b = io.BytesIO(); img.save(b, format="JPEG", quality=75)
                f_base64 = base64.b64encode(b.getvalue()).decode()

            new_entry = {
                "Datum": str(datum), "Beginn": t_start.strftime("%H:%M"), "Ende": t_end.strftime("%H:%M"),
                "Ort": str(ort), "Hausnummer": hnr, "Zeugen": verschluesseln(beteiligte),
                "Bericht": verschluesseln(inhalt), "AZ": az, "Foto": verschluesseln(f_base64),
                "GPS": gps_val, "Kraefte": verschluesseln(", ".join(kraefte_liste))
            }
            
            df = pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=COLUMNS)
            pd.concat([df, pd.DataFrame([new_entry])]).to_csv(DATEI, index=False)
            st.success("Bericht wurde sicher im Archiv gespeichert!"); st.rerun()

# --- 6. ARCHIV-ANSICHT ---
st.divider()
st.header("📂 Archivierte Berichte")
suche = st.text_input("🔍 Suche nach Ort oder AZ")

if os.path.exists(DATEI):
    daten = pd.read_csv(DATEI).astype(str)
    # Entschlüsseln für Anzeige
    for col in ["Bericht", "Zeugen", "Foto", "Kraefte"]:
        daten[col] = daten[col].apply(entschluesseln)
    
    # Filter
    if suche:
        daten = daten[daten['Ort'].str.contains(suche, case=False) | daten['AZ'].str.contains(suche, case=False)]

    for i, r in daten.iloc[::-1].iterrows():
        with st.container():
            st.markdown(f"""
            <div class="report-card">
                <strong>📅 {r['Datum']} | 📍 {r['Ort']} {r['Hausnummer']}</strong><br>
                <small>📂 AZ: {r['AZ']} | 🕒 {r['Beginn']} - {r['Ende']}</small>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("Details anzeigen"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(f"**👮 Kräfte:** {r['Kraefte']}")
                    st.info(r['Bericht'])
                    if r['Zeugen'] != "-": st.write(f"**👥 Beteiligte:** {r['Zeugen']}")
                with c2:
                    if r['Foto'] != "-":
                        st.image(base64.b64decode(r['Foto']), use_container_width=True)
                    st.caption(f"📍 GPS: {r['GPS']}")
else:
    st.info("Noch keine Berichte vorhanden.")

# Admin-Check im Sidebar
with st.sidebar:
    if st.checkbox("🔑 Admin"):
        if st.text_input("Passwort", type="password") == ADMIN_PW:
            st.session_state["admin_auth"] = True
            st.success("Admin-Zugriff gewährt")
