import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import io
import base64
from PIL import Image, ImageOps
import tempfile
from cryptography.fernet import Fernet
from streamlit_js_eval import get_geolocation

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="OA Augsburg Pro", page_icon="🚓", layout="wide")

# --- 2. SESSION STATE ---
if "auth" not in st.session_state: st.session_state["auth"] = False
if "admin_auth" not in st.session_state: st.session_state["admin_auth"] = False

# --- 3. SICHERHEIT & SECRETS ---
try:
    DIENST_PW = st.secrets["dienst_password"]
    MASTER_KEY = st.secrets["master_key"]
except:
    DIENST_PW = "1234"
    MASTER_KEY = "AugsburgSicherheit32ZeichenCheck!"

ADMIN_PW = "admin789"

def get_cipher():
    key_64 = base64.urlsafe_b64encode(MASTER_KEY[:32].encode().ljust(32))
    return Fernet(key_64)

def verschluesseln(text):
    if not text or text == "-": return "-"
    return get_cipher().encrypt(text.encode()).decode()

def entschluesseln(safe_text):
    if not safe_text or safe_text == "-": return "-"
    try:
        return get_cipher().decrypt(safe_text.encode()).decode()
    except:
        return "[Entschlüsselungsfehler]"

# --- 4. VOLLSTÄNDIGE STRASSENLISTE AUGSBURG ---
STRASSEN_AUGSBURG = sorted([
    "Schillstr./ Dr. Schmelzingstr. - Baustellenbereich", "Hallo Werner", "Hexengässchen", 
    "Meistro Imbiss/Gögginger Str. 22, 24, 26", "Modular Festival", "rund um die Uni", 
    "Ablaßweg", "Ackermannbrücke", "Ackermannpark Spielplatz", "Ackerstraße", 
    "Adalbert-Stifter-Straße", "Adam-Riese-Straße", "Adelgundenstraße", "Adelheidstraße", 
    "Adelmannstraße", "Adolph-Kolping-Straße", "Adrian-de-Vries-Straße", "Affinger Straße", 
    "Afrabrücke", "Afrabrücke Lechufer", "Afragäßchen", "Afrastraße", "Afrawald", 
    "Aggensteinstraße", "Agnes-Bernauer-Straße", "Ahornerstraße", "Ahrenstraße", 
    "Aichacher Weg", "Aichingerstraße", "Aindlinger Str.", "Aindlinger Straße", 
    "Akazienweg", "Akeleistraße", "Alatseestraße", "Albert-Einstein-Straße", 
    "Albert-Greiner-Straße", "Albert-Kirchmayer-Weg", "Albert-Leidl-Straße", 
    "Albert-Schenavsky-Straße", "Albert-Schweitzer-Straße", "Albrecht-Dürer-Straße", 
    "Alemannenstraße", "Alfonsstraße", "Alfred-Nobel-Straße", "Alfred-Wainald-Weg", 
    "Allensteinstraße", "Allgäuer Straße", "Allgäuer Straße Spielplatz", "Almenrauschstraße", 
    "Alois-Senefelder-Allee", "Alpenrosenstraße", "Alpenstraße", "Alpenstraße (Äußere Ladehöfe Spielplatz)", 
    "Alpenstraße Spielplatz", "Alpseestraße", "Alpspitzstraße", "Alraunenweg", "Alte Auerstraße", 
    "Alte Gasse", "Alte Gasse 7", "Alte Straße", "Alte Straße (Neusäß)", "Alter Haunstetter Friedhof", 
    "Alter Haunstetter Friedhof, Bgm.-Widmeier-Straße 55", "Alter Heuweg", "Alter Ostfriedhof", 
    "Alter Ostfriedhof (Gehwege zum Friedhof und Eingänge)", "Alter Postweg", "Alter und Neuer Friedhof", 
    "Altes Kautzengäßchen", "Altes Stadtbad", "Altes Zeughausgäßchen", "Altstadt", 
    "Altstadtgasthaus Bauerntanz", "Am Adlerhorst", "Am Alten Einlaß", "Am Alten Einlaß Grünanlage", 
    "Am Alten Gaswerk", "Am Alten Hessenbach", "Am Alten Schlachthof", "Am Backofenwall", 
    "Am Bahnhoffeld", "Am Bergacker", "Am Bogen", "Am Bogen Spielplatz", "Am Brachfeld", 
    "Am Breitle", "Am Brunnenlech", "Am Bühl", "Am Dürren Ast / Lochbach", "Am Einlass Grünanlage", 
    "Am Eiskanal", "Am Eser", "Am Eulenhorst", "Am Exerzierplatz", "Am Exerzierplatz / KiTa Kleine Freunde", 
    "Am Färberturm", "Am Fischertor", "Am Floßgraben", "Am Forellenbach", "Am Gerstenacker", 
    "Am Grießle", "Am Grünland", "Am Haferfeld", "Am Hanreibach", "Am Hinteren Perlachberg", 
    "Am Hinteren Perlachberg 1 - 4", "Am Jeschken", "Am Katzenstadel", "Am Katzenstadel 1", 
    "Am Katzenstadel Spielplatz", "Am Köpfle", "Am Kornfeld", "Am Kriegerdenkmal", "Am Langen Berg", 
    "Am Lueginsland", "Am Lueginsland Spielplatz", "Am Martinipark", "Am Mauerberg", "Am Medizincampus", 
    "Am Messezentrum", "Am Mittleren Moos", "Am Mühlholz", "Am Neubruch", "Am Oberen Zwinger", 
    "Am Perlachberg", "Am Pfannenstiel", "Am Pferseer Feld", "Am Pferseer Feld Spielplatz", 
    "Am Provinopark", "Am Rauhen Forst", "Am Rehsprung", "Am Ringofen", "Am Roggenfeld", 
    "Am Römerstein", "Am Rößlebad", "Am Roten Tor", "Am Schäfflerbach", "Am Schwabenfeld", 
    "Am Schwalbeneck", "Am Schwall", "Am Silbermannpark", "Am Sonnenhang", "Am Sparrenlech", 
    "Am Stelzenacker", "Am Taubenacker", "Am Technologiezentrum", "Am Vehicle-Park", "Am Vogeltor", 
    "Am Wachtelschlag", "Am Waldrand", "Am Webereck", "Am Weizenfeld", "Am Wertachdamm", 
    "Am Zehntstadel", "Am Zwergacker", "Am Zwirnacker", "Amagasaki-Allee", "Amberger Wiese Spielplatz", 
    "Ambergerstraße", "Ammannstraße", "Ammerseestraße", "Amperstraße", "Amselweg", "Amselweg Spielplatz", 
    "Amtsgericht Aichach", "Amtsgericht Göggingen", "Amundsenstraße", "An der Blauen Kappe", 
    "An der Brühlbrücke", "An der Dolle", "An der Halde", "An der Hochschule", "An der Sandhülle", 
    "An der Sinkel", "Andechser Straße", "Angerstraße", "Anna-German-Weg", "Annahof", "Anna-Krölin-Platz", 
    "Anna-Seghers-Straße", "Annastraße", "Annastraße 16", "Annastraße, Martin-Luther-Platz, Moritzplatz.....", 
    "Anne-Frank-Straße", "Annegert-Fuchshuber-Weg", "Anstoßgäßchen", "Anton-Bezler-Straße", 
    "Anton-Bezler-Straße Spielplatz", "Anton-Bruckner-Straße", "Anton-Günther-Straße", 
    "Anton-Hockelmann-Straße", "Anton-Sorg-Straße", "Anton-Stöckle-Weg", "Anwaltinger Straße", 
    "Apfelweg", "Apostelstraße", "Apothekergäßchen", "Apprichstraße", "Aprikosenweg", "Arberstrale", 
    "Archimedesstraße", "Archimedesstraße Spielplatz", "Argonstraße", "Arhornerstr", "Armenhausgasse", 
    "Arminstraße", "Arnikaweg", "Arnulfstraße", "Arthur-Piechler-Straße", "Aspernstraße", "Asternweg", 
    "Auenweg", "Auerbergweg", "Auerhahnweg", "Auerstraße", "Auf dem Kreuz", "Auf dem Nol", 
    "Auf dem Plätzchen", "Auf dem Rain", "Auf dem Rain 5: ,,The Drunken Monkey\"", "Augsburger Dom", 
    "Augsburger Hauptbahnhof", "Augsburger Str. 14 vor Rot-Kreuz-Laden", "Augsburger Straße", 
    "Augsburger Straße / Am Webereck", "Augsburger Straße 1 bis 41", "Augsburger Straße 3", 
    "Augustastraße", "Augustusstraße", "August-Vetter-Straße", "August-Wessels-Straße", 
    "Aulzhausener Straße", "Aurikelstraße", "Äußere Uferstraße", "Äußere Uferstraße Spielplatz", 
    "Äußerer Gang", "Äußeres Pfaffengäßchen", "Aussiger Weg", "Austraße", "Autobahnsee", 
    "Auwaldstraße", "Aystetter Weg", "Azaleenstraße", "Babenhauser Weg", "Bachstelzenweg", 
    "Bäckergasse", "Backside Alm, Predigerberg 4", "Badanger", "Badstraße", "Badstraße/Holzbachstraße", 
    "Baggersee", "Bahnhofstr. 5 - Obdachlose", "Bahnhofstraße", "Bahnstraße", "Balanstraße", 
    "Banater Straße", "Bannacker", "Bannackerstraße", "Bannwaldseestraße", "Banya Luka", 
    "Barbara-Gignoux-Weg", "Bärenhorststraße", "Bärenstraße", "Barfüßerstraße", "Barthshof", 
    "Barthshof 3", "Basketballplatz Schlösslepark", "Bauernfeindstraße", "Bauernfeld", "Bauerntanzgäßchen", 
    "Baumgärtleingäßchen", "Baumgartnerstraße", "Bautzener Straße", "Bavousstraße", "Bayerstraße", 
    "Bebo-Wager-Straße", "Beethovenstraße", "Behringerstraße", "Bei den Sieben Kindeln", 
    "Bei der Jakobskirche", "Bei der Wettersaule", "Bei Sankt Barbara", "Bei Sankt Max", 
    "Bei Sankt Ursula", "Beim Dürren Ast", "Beim Glaspalast", "Beim Grenzgraben", "Beim Hafnerberg", 
    "Beim Märzenbad", "Beim Pfaffenkeller", "Beim Rabenbad", "Beim Schnarrbrunnen", "Beim Winkelacker", 
    "Beimlerstraße", "Belzmühlgäßchen", "Benatzkystraße", "Benediktbeurer Straße", "Benedikt-Kern-Weg", 
    "Berberitzenweg", "Berchtesgadener Straße", "Bereich vor dem Liliom", "Bergheimer Baggersee", 
    "Bergheimer Straße", "Bergiusstraße", "Bergmühlstraße", "Bergstraße", "Bergwandstrale", 
    "Berliner Allee", "Berliner Allee 28c DoIT", "Berliner Allee Osramsteg", "Bert-Brecht-Straße", 
    "Bertha-von-Suttner-Straße", "Besselstraße", "Biberbachstraße", "Biberkopfstraße", 
    "Bieberkopfstr. Spielplatz", "Bienenweg", "Biermannstraße", "Billerstraße", "Birkenau", 
    "Birkenfeldstraße", "Birkenstraße", "Birkhahnweg", "Birnbaumweg", "Bischoffstraße", 
    "Bischofsackerweg", "Bischof-von-Zollern-Platz", "Bismarckbrücke", "Bismarckbrücke und Umfeld", 
    "Bismarckstraße", "Bismarckstraße Spielplatz", "Bissingerstraße", "Bitschlinstraße", 
    "Blaichacher Straße", "Blankenfelder Weg", "Blaue Kappe", "Bleicherbreite", "Bleicherhornweg", 
    "Bleichstraße", "Bleigäßchen", "Bleriotstraße", "Bleriotstraße Schule", "Blücherstraße", 
    "Blumenstraße", "Blütenstraße", "Bobinger Straße", "Böheimstraße", "Böhmerwaldstraße", 
    "Bolzplatz Zugspitzstr. / Peißenbergstr.", "Bopp-Passage", "Böttgerstraße", "Bourges-Platz", 
    "Bozener Straße", "Brachvogelstraße", "Brahmsstraße", "Branderstraße", "Brandstraße", 
    "Brandweg", "Bräuergäßchen", "Braunstraße", "Brehmplatz", "Breitachweg", "Breitenbergstraße", 
    "Breitwiesenstraße", "Brennhölzerweg", "Brentanostraße", "Breslauer Straße", "Brixener Straße", 
    "Brückenstr. Nr. 2 und Nr. 5", "Brückenstraße", "Brückenstraße Spielplatz", "Brunecker Straße", 
    "Brunhildenstraße", "Brunnenbachstraße", "Brunnenbar", "Brunnenlechgäßchen", "Brunnenstraße", 
    "Brunostraße", "Buchenländer Straße", "Buchenstraße", "Buchinger Straße", "Buchmayergäßchen", 
    "Büchnerstraße", "Bülowstraße", "Burgauer Straße", "Burgergäßchen", "Bürgermeister-Ackermann-Straße", 
    "Bürgermeister-Ackermann-Straße (Brücke)", "Bürgermeister-Aurnhammer-Straße", "Bürgermeister-Bohl-Straße", 
    "Bürgermeister-Bunk-Straße", "Bürgermeister-Fischer-Straße", "Bürgermeister-Lutzenberger-Weg", 
    "Bürgermeister-Miehle-Straße", "Bürgermeister-Rieger-Straße", "Bürgermeister-Schlosser-Straße", 
    "Bürgermeister-Ulrich-Straße", "Bürgermeister-Ulrich-Straße Ecke Keltenstraße", "Bürgermeister-Wegele-Straße", 
    "Bürgermeister-Widmeier-Straße", "Bürgermeister-Widmeier-Straße Spielplatz", "Burgfriedenstraße", 
    "Burgkmairstraße", "Burgunderstraße", "Burgwalder Straße", "Burkhard-Zink-Straße", "Bussardweg", 
    "Butzenbergle", "Butzstraße", "Calmbergstraße", "Canisiusstraße", "Caritasweg", "Carl-Hüber-Straße", 
    "Carl-Loewe-Straße", "Carl-Maria-von-Weber-Straße", "Carl-Natterer-Straße", "Carl-Schurz-Straße", 
    "Carl-Zeiss-Straße", "Carron-du-Val-Straße", "Chemnitzer Straße", "Christian-Dierig-Park", 
    "Christian-Dierig-Straße", "Christkindlesmarkt", "Christleseeweg", "Christoph-von-Schmid-Straße", 
    "City Galerie Brücke", "City-Galerie", "Clara-Hätzler-Straße", "Clara-Tott-Straße", "Clematisweg", 
    "Clementine-Heymann-Straße", "Columbusstraße", "Columbusstraße Schule", "Columbusstraße Spielplatz", 
    "Cranachstraße", "Curt-Frenzel-Stadion", "Curt-Frenzel-Straße", "Curtiusstraße", "Dachsweg", 
    "Dahlienweg", "Damaschkebad", "Damaschkeplatz", "Damaschkestraße", "Damastweg", "Dambörstraße", 
    "Damenhof", "Dammstraße", "Danziger Straße", "Dasinger Straße", "Daucherstraße", "Davton-Ring", 
    "Dekan-Mayer-Straße", "Delbrückstraße", "Demharterhof", "Dennewitzstraße", "Dennewitzstraße Spielplatz", 
    "Depotstraße", "Derchinger Straße", "Derchinger Straße 141", "Dessauer Straße", 
    "Deutschenbauerstraße Spielplatz", "Deutschenbaurstraße", "Diebelbachstraße", "Diebelbachstraße Spielplatz", 
    "Dieboldgäßchen", "Diedorfer Straße", "Dienstgebäude Ernst-Reuter-Platz 4", "Dienstgebäude Grottenau 1", 
    "Dieselbrücke", "Dieselstraße", "Dietrichstraße", "Dillinger Weg", "Dinglerstraße", 
    "Dinkelsbühler Weg", "Dinkelscherbener Straße", "Dohlenweg", "Doktorgäßchen", "Döllgast-Straße", 
    "Dominikanergasse", "Dompfaffweg", "Donaustraße", "Donauwörther Straße", "Donauwörther Straße 1-58", 
    "Donauwörther Straße Wertach Kiosk", "Don-Bosco-Platz", "Dornierstraße", "Dornröschenweg", 
    "Dr.-Dürrwanger-Straße", "Dr.-Grandel-Straße", "Dr.-Hörmann-Straße", "Dr.-Lagai-Straße", 
    "Dr.-Mack-Straße", "Dr.-Nebel-Straße", "Dr.-Nick-Straße", "Dr.-Otto-Meyer-Straße", 
    "Dr.-Port-Straße", "Dr.-Schmelzing-Straße", "Dr.-Troeltsch-Straße", "Dr.-Zamenhof-Straße", 
    "Dr.-Ziegenspeck-Weg", "Drei-Auen-Platz", "Drentwettstraße", "Drescherstraße", "Dresdener Straße", 
    "Drittes Quergäßchen", "Drosselweg", "Droste-Hülshoff-Straße", "Drususstraße", "Dudenstraße", 
    "Dumlerstraße", "Dußmannstraße", "Ebereschenstraße", "Eberlestraße", "Ebnerstraße", 
    "Edelsbergstraße", "Edelweißstraße", "Edenberger Straße", "Edisonstraße", "Egelseestraße", 
    "Egerländer Straße", "Eggenstraße", "Ehingerstraße", "Eibenweg", "Eibseestraße", 
    "Eibseestraße Spielplatz", "Eichelhäherweg", "Eichendorffstraße", "Eichendorffstraße Spielplatz", 
    "Eichenhofstraße", "Eichenstraße", "Eichhornstraße", "Eichleitnerstraße", "Eichlerstraße", 
    "Eisackstraße", "Eisenbahnbrücke", "Eisenbahnbrücke Hochzoll", "Eisenberg", "Eisenhutstraße", 
    "Eiskanal Gehweg", "Eisstadion Spielplatz", "Eisvogelweg", "Elias-Holl-Platz", "Elisabeth-Selbert-Straße", 
    "Elisabethstraße", "Elisenstraße", "Ellensindstraße", "Ellgauer Weg", "Elmauer Weg", 
    "Elmauer Weg Spielplatz", "Elsa-Brändström-Straße", "Elsässer Straße", "Elsenbornstraße", 
    "Elsterweg", "Emaushof", "Emil-Esche-Weg", "Emilienstraße", "Emil-Nolde-Straße", "Emily-Balch-Straße", 
    "Endorferstraße", "Engelbergerstraße", "Enzianstraße", "Enzianstraße Spielplatz", 
    "Eppaner Straße", "Erfurter Straße", "Erhard-Wunderlich-Allee", "Erhart-Kästner-Straße", 
    "Erhart-Kästner-Straße Spielplatz", "Erhart-Kästner-Straße, Alter Heuweg", "Erhartstraße", 
    "Erledigungsfahrt Innendienst", "Erlenweg", "Erlkönigweg", "Ermittlungen für den Innendienst", 
    "Erna-Wachter-Straße", "Ernst- Reuter- Platz 4", "Ernst-Barlach-Straße", "Ernst-Cramer-Weg", 
    "Ernst-Heinkel-Straße", "Ernst-Lehner-Straße", "Ernst-Lossa-Straße", "Ernst-Moritz-Arndt-Straße", 
    "Ernst-Reuter-Platz", "Erstes Fabrikgäßchen", "Erstes Quergäßchen", "Erstes Quersächsengäßchen", 
    "Erzgebirgsstraße", "Eschenhofstraße", "Eselsberg", "Eserwallstraße", "Espenweg", "ESSO Tankstelle", 
    "Ettaler Straße", "Euler-Chelpin-Straße", "Eupenstraße", "Euringerstraße", "Europaplatz", 
    "Fabrikstraße", "Fahrrad Laden Pfanz", "Fahrradweg unter Wertachbrücke", "Fahrten für den Innendienst", 
    "Falkensteinstraße", "Falkenweg", "Fallerslebenstraße", "Falterweg", "Familie-Einstein-Straße", 
    "Familie-Einstein-Straße (im Umfeld des dortigen Wohnheims)", "Färbergäßchen", "Färberstraße", 
    "Färberstraße / Bouleplatz", "Farchanter Weg", "Farchanter Weg Spielplatz", "Farnweg", 
    "Fasanenweg", "Felberstraße", "Feldstraße", "Fellhornstraße", "Felsensteinstraße", 
    "Ferdinand-Halbeck-Straße", "Ferdinand-Lassalle-Straße", "Feuerdornweg", "Feuerhausstraße", 
    "Fichtelbachstraße", "Fichtenweg", "Fichtestraße", "Findelgäßchen", "Finkenweg", "Firnhaberstraße", 
    "Fischmarkt", "Fischmarkt (Baustelle)", "Flachsstraße", "Flandernstraße", "Flandernstraße Spielplatz", 
    "Flemingstraße", "Fliederweg", "Flößerpark", "Flößerstraße", "Floßlände (Treppenanlage)", 
    "Flugfeldstraße", "Flughafenstraße", "Flurstraße", "Flurstraße 45, Lokal \"Hettenbach 45\"", 
    "Föhrenweg", "Föllstraße", "Fontanestraße", "Forggenseestraße", "Forsterpark Spielplatz", 
    "Forsterstraße", "Forsthausweg", "FOS/BOS Augsburg", "Frankenweg", "Frankfurter Straße", 
    "Franzensbadstraße", "Franziskanergasse", "Franziska-Wittmann-Straße", "Franz-Josef-Strauß-Straße", 
    "Franz-Kobinger-Straße", "Franz-Marc-Straße", "Frauenschuhstraße", "Frauentorstraße", 
    "Fräulein Smilla Cafe & Bar", "Fraunhoferstraße", "Freibergseestraße", "Freiburger Straße", 
    "Freilichtbühne", "Freudenthalstraße", "Frickingerstraße", "Friedberger Straße", 
    "Friedberger Straße 103-160", "Friedberger Straße/Herrenbach Spielplatz", "Friedbergerstraße 121 (Kiosk)", 
    "Friedensplatz", "Friedenstraße", "Friedhof", "Friedhofweg", "Friedl-Urban-Straße", 
    "Friedrich-Chur-Straße", "Friedrich-Deffner-Straße", "Friedrich-Ebert-Straße", "Friedrich-List-Straße", 
    "Friedrich-Maurer-Weg", "Friedrich-Merz-Straße", "Friedrichshafener Straße", "Friedrich-Sohnle-Straße", 
    "Friesenstraße", "Frischstraße", "Fritz-Hintermayr-Straße", "Fritz-Klopper-Straße", 
    "Fritz-Koelle-Straße", "Fritz-Strassmann-Straße", "Fritz-Wendel-Straße", "Fröbelstraße", 
    "Fröbelstraße 29 ( Bermuda3Eck)", "Frohsinnstraße", "Frölichstraße", "Fronhof", "Fronhof Spielplatz", 
    "Fronsbergstraße", "Frühlingstraße", "Fuchsweg", "Fuchswinkel", "Fuggerei", "Fuggerplatz", 
    "Fuggerstraße", "Fünftes Quergäßchen", "Füssener Straße", "Fußgängerzone", "Gabelsbergerstraße", 
    "Gablinger Weg", "Gablonzer Weg", "Gailenbachweg", "Galgentalweg", "Galileistraße", 
    "Gallusbergle", "Gallusplatz", "Galvanistraße", "Ganghoferstraße", "Gänsbühl", "Gänsbühl Spielplatz", 
    "Garbenstraße", "Garmischer Straße", "Gartenstraße", "Gärtnerstraße", "Gärtnerwinkel", 
    "Gaußstraße", "Gebrüder-Münch-Straße", "Gehweg hinter der City-Galerie", "Geibelstraße", 
    "Geierweg", "Geiselsteinweg", "Geishornstraße", "Geißgäßchen", "Geißgäßchen Spielplatz", 
    "Gellertstraße", "Gellertstraße 6", "General-Cramer-Weg", "Gentnerstraße", "Georg-Brach-Straße", 
    "George-Gershwin-Straße", "Georgenstr. 2, Schank- und Speisewirtschaft \"Oki's\"", "Georgenstraße", 
    "Georg-Haindl-Straße", "Georg-Käß-Platz", "Georg-Mayr-Weg", "Georg-von-Krauß-Straße", 
    "Gerhart-Hauptmann-Straße", "Germersheimer Straße", "Germersheimer Straße 20 Grünanlage", 
    "Gerstenstraße", "Gersthofer Straße", "Gesamtes Stadtgebiet", "Geschindigkeitsüberwachung", 
    "Geschwister-Scholl-Straße", "Gesundbrunnenstraße", "Gesundbrunnenstraße Spielplatz", 
    "Gieseckestraße", "Giggenbachstraße", "Ginsterweg", "Girlitzstraße", "Gladiolenstraße", 
    "Glückstraße", "Gneisenaustraße", "Goethestraße", "Gögginger Brücke", "Gögginger Friedhof", 
    "Gögginger Frühlingsfest", "Gögginger Luftbad", "Gögginger Mauer", "Gögginger Park", 
    "Gögginger Straße", "Gögginger Straße \"Meistro Imbiss Kiosk\"", "Göhlsdorfer Weg", 
    "Goldammerstraße", "Goldregenweg", "Goldschlägerweg", "Goldwiesenstraße", "Gollwitzerstraße", 
    "Gossenbrotstraße", "Gotenweg", "Gottfried-Keller-Straße", "Grabenstraße", "Graf-Bothmer-Straße", 
    "Graf-Dietbald-Straße", "Grafstraße", "Graf-von-Seyssel-Straße", "Graham-Bell-Straße", 
    "Grainauer Weg", "Grainauer Weg Spielplatz", "Grasiger Weg", "Graslitzer Straße", 
    "Grasmückenweg", "Gratzmüllerstraße", "Graupener Straße", "Greiffstraße", "Grenzstraße", 
    "Griesle Nord Spielplatz", "Griesle Park", "Grieslepark (Bauwagen)", "Griesstraße", 
    "Grillparzerstraße", "Grimmstraße", "Großbeerenstraße", "Grottenau", "Grottenau 2/Ludwigstraße", 
    "Grünanlage entlang Herrenbachkanal", "Grünanlage neben City Galerie", "Grundschule Bärenkeller", 
    "Grundschule Hammerschmiede", "Grünerstraße", "Grüntenstraße", "Gubener Straße", 
    "Gumpelzhaimerstraße", "Gumpelzhaimerstraße Spielplatz", "Gumppenbergstraße", "Gundelfinger Weg", 
    "Gundelfinger Weg Spielplatz", "Gunterstraße", "Günzburger Straße", "Gunzesrieder Weg", 
    "Günzstraße", "Gustav-Heinemann-Straße", "Gustav-Stresemann-Straße", "Gutenbergstraße", 
    "Gutermannstraße", "Guttenbrunnstraße", "Habichtsweg", "Habsburgstraße", "Hafenmühlweg", 
    "Haferstraße", "Hafnerberg", "Hagebuttenweg", "Hagenmähderstraße Grünanlage", "Hagenmähderstraße Spielplatz", 
    "Hainbergstraße", "Hainbuchenweg", "Hainhoferstraße", "Halderstraße", "Hallstraße", 
    "Hallstraße Freizeitbereich", "Haltestelle Bärenwirt", "Haltestelle Frohsinnstr.", 
    "Haltestelle Haunstetten West", "Haltestelle Haunstetten-Nord nebst Spielplatz", 
    "Haltestelle Mozarthaus - Frauentorstraße", "Haltestelle Neuer-Ost-Friedhof", "Hambacher Weg", 
    "Hammerschmiedweg", "Hanauer Straße", "Händelweg", "Händelweg Spielplatz", "Hänflingweg", 
    "Hangstraße", "Hannah-Arendt-Straße", "Hanns-Rupp-Weg", "Hanreiweg", "Hans-Adlhoch-Straße", 
    "Hans-Böckler-Straße", "Hans-Heiling-Straße", "Hans-König-Straße", "Hans-Nagel-Gasse", 
    "Hans-Rollwagen-Straße", "Hans-Sachs-Straße", "Hans-Watzlik-Straße", "Hardenbergstraße", 
    "Hardergäßle", "Harlekin Wilhelm-Hauff-Straße", "Hartmannstraße", "Haselnußweg", "Hasengasse", 
    "Häspelegäßchen", "Haspingerstraße", "Haßlerstraße", "Haunstetten Hallenbad", "Haunstetten Neuer Friedhof", 
    "Haunstetten Nord", "Haunstetter Straße", "Haunstetter Straße auf Höhe Christuskirche / REWE", 
    "Hauptstraße", "Hauschildstraße", "Haußerstraße", "Hechtstraße", "Heckenrosenweg", 
    "Heckenrosenweg Spielplatz", "Heckenstraße", "Hegelstraße", "Heiligenangerstraße", 
    "Heilig-Grab-Gasse", "Heilig-Kreuz-Strafe", "Heilig-Kreuz-Straße", "Heimbaustraße", 
    "Heimgartenweg", "Heimstättenweg", "Heinestraße", "Heini-Dittmar-Straße", "Heini-Dittmar-Straße 17 Night Fly", 
    "Heinrich-Böll-Straße", "Heinrich-Böll-Straße Spielplatz", "Heinrich-Hertz-Straße", 
    "Heinrich-Kaspar-Schmid-Str./Fallerslebensstr./Herrenbachkanal/Grünanlage", "Heinrich-Kaspar-Schmid-Straße", 
    "Heinrich-von-Buz-Str. 23", "Heinrich-von-Buz-Straße", "Heisenbergstraße Spielplatz", 
    "Helmschmiedstraße", "Helmut-Haller-Platz", "Henisiusstraße", "Henlestraße", "Hennchstraße", 
    "Henri-Dunant-Straße", "Herbststraße", "Herkulesbrunnen", "Hermann-Frieb-Park", "Hermann-Frieb-Straße", 
    "Hermann-Hesse-Straße", "Hermann-Kluftinger-Straße", "Hermann-Köhl-Straße", "Hermann-Löns-Straße", 
    "Hermanstraße", "Hermelinweg", "Herrenbach Kanal", "Herrenbachstraße", "Herrenhäuser", 
    "Hertelstraße", "Herwartstraße", "Herz-Jesu Kirche", "Herzogstandstraße", "Hessenbachstraße", 
    "Hessingstraße", "Hettenbachpark", "Hettenbachufer", "Heumahdstraße", "Heyzel Coffee", 
    "Hillenbrandstraße", "Himmerstraße", "Hindelanger Straße", "Hinter dem Schwalbeneck", 
    "Hinter den Gärten", "Hinter der Metzg", "Hinterer Lech", "Hinteres Kretzengäßchen", 
    "Hippelstraße", "Hirblinger Straße", "Hirblinger Straße 4 (Bistro Absolut)", 
    "Hirblinger Straße höhe \"Hirblinger Hof\"", "Hirblinger Straße Spielplatz", "Hirschstraße", 
    "Hirsestraße", "Hirtenmahdweg", "Hochablaß", "Hochablaß Kiesbänke", "Hochfeldstr. 67 - \"Lé Fresh\"", 
    "Hochfeldstraße", "Hochgratstraße", "Höchstetterstraße", "Hochstiftstraße", "Hochvogelstraße", 
    "Hochzoller Straße", "Hofackerstraße", "Hofackerstraße 26 - \"Millsfrisch\"", "Höfatsstraße", 
    "Hofer Straße", "Hofgarten", "Hofgartenstraße", "Hofmannsthalstraße", "Hofrat-Röhrer-Straße", 
    "Höggstrale", "Hohenstaufenstraße", "Hoher Weg", "Holbeinplatz", "Holbeinstraße", 
    "Holbeinstraße 9", "Hölderlinstraße", "Holunderweg", "Holzbachstraße", "Holzbachstraße Spielplatz", 
    "Holzhauser Weg", "Holzweg", "Hooverstraße", "Hooverstraße Spielplatz", "Hopfenseeweg", 
    "Hopfenstraße", "Hörbrotstraße", "Horgauer Weg", "Hornissenweg", "Hornsteinstraße", 
    "Hornungstraße", "Hötzelstraße", "Hubertusplatz", "Hübnerstraße", "Hugenottenweg", 
    "Hugo-Eckener-Straße", "Hugo-Junkers-Straße", "Hugo-Wolf-Straße", "Humboldtstraße", 
    "Hummelspassage", "Hummelstraße", "Hunoldsberg", "Hunoldsgraben", "Hunoldsgraben Spielplatz", 
    "Hurlacher Weg", "Ifenstraße", "Illerstraße", "Ilsesee", "Ilsungstraße", "Iltisweg", 
    "Im Anger", "Im Annahof", "Im Eigenen Heim", "Im Feierabend", "Im Gries", "Im Hoferstraße", 
    "Im Neufeld", "Im Neuland", "Im Ölhöfle", "Im Sack", "Im Sack Spielplatz", "Im Tal", 
    "Im Thäle", "Im Windhof", "Imhofstraße", "Immelmannstraße", "Immenstädter Straße", 
    "In der Fuchssiedlung", "Innen", "Innenstadt", "Innenstadtbereich (Maxstr, KÖ)", 
    "Innere Uferstraße", "Innere Uferstraße 20 - \"Himilo\"", "Innere Uferstraße Spielplatz", 
    "Inneres Pfaffengäßchen", "Inningen Bahnhof", "Inningen Haltestellen", "Inninger Dorfplatz", 
    "Inninger Straße", "Innsbrucker Straße", "Innstraße", "Insterburgstraße", "Inverness-Allee", 
    "Isarstraße", "Isegrimstraße", "Iselerstraße", "Iselinstraße", "Jagdweg", "Jägerbachstraße", 
    "Jägergäßchen", "Jahnstraße", "Jahnstraße Spielplatz", "Jakoberstr. 60 Sportsbar", 
    "Jakoberstraße", "Jakoberstraße 42 - \"Bar Cobra\"", "Jakoberstraße 77 - \"L & A Kiosk\"", 
    "Jakobertorplatz", "Jakoberwall Parkanlage und Spielplatz", "Jakoberwallstraße", 
    "Jakobine-Lauber-Straße", "Jakob-Krause-Straße", "Jakobsplatz", "James-Cook-Straße", 
    "Jane-Addams-Straße", "Jasminweg", "Jean-Paul-Straße", "Jedelhauserstraße", "Jenaer Straße", 
    "Jesse-Owens-Straße", "Jesuitengasse", "Jesuitengasse Grünanlage", "Jochbergstraße", 
    "Johannes-Haag-Straße", "Johannes-Holzer-Straße", "Johannes-Rösle-Straße", 
    "Johannes-Rösle-Straße (Übergangsheim)", "Johann-Georg-Halske-Straße", "Johannisgasse", 
    "Johann-Marxreiter-Weg", "Johann-Sebastian-Bach-Straße", "Johann-Strauß-Straße", 
    "Johann-Strauß-Straße (Spiel/Bolzplatz)", "John-May-Weg", "Jörg-Breu-Straße", "Jörg-Seld-Straße", 
    "Josef-Felder-Straße", "Josef-Fischer-Platz", "Josef-Kerker-Weg", "Josef-Kronthaler-Straße", 
    "Josef-Priller-Straße", "Josef-Schorer-Straße", "Joseph-Dantonello-Weg", "Joseph-Haas-Straße", 
    "Joseph-Mayer-Straße", "Judenberg", "Jüdischer Friedhof Wolfram- und Herrenbachviertel – Haunstetter Straße 64", 
    "Jugendtreff Von-Parseval-Str.", "Julius-Spokojny-Weg", 
    "Julius-Spokojny-Weg bei HsNR 10 rechts den kleinen weg bis zur Parkbank", 
    "Julius-Spokojny-Weg Spielplatz", "Julius-Spokojny-Weg Spielplatz und Gehweg dahinter", 
    "Julius-Spokojny-Weg Spielplatz und Gehweg dahinter / HsNr. 10 Parkbank", "Jupiterstraße", 
    "Kaffeegäßchen", "Kagerstrale", "Kalkbrennerweg", "Kaltenhoferstraße", "Kalterer Straße", 
    "Kanalstraße", "Kandinskystraße", "Kantstraße", "Kanzelwandweg", "Kapellenstraße", 
    "Kapellenstraße 1", "Kappelberg", "Kappeneck", "Kapuzinergasse", "Kargstraße", 
    "Karl-Drais-Str. bis Hans-Jonas-Str.", "Karl-Drais-Straße", "Karl-Drais-Straße bis Hans-Jonas-Straße", 
    "Karl-Haberstock-Straße", "Karl-Nagel-Straße", "Karl-Nolan-Straße", "Karl-Radinger-Weg", 
    "Karl-Rommel-Weg", "Karlsbader Straße", "Karl-Settele-Straße", "Karlsruher Straße", 
    "Karlstraße", "Karl-Strehle-Straße", "Karmelitengasse", "Karmelitenmauer", "Karmelitenplatz", 
    "Karolinenstraße", "Karrengäßchen", "Karwendelstraße", "Kasernstraße", "Kaspar-Reiter-Weg", 
    "Kastanienweg", "Katharinengasse", "Käthe-Schäfer-Straße", "Kathreinerstraße", "Katzbachstraße", 
    "Katzenhof", "Kaufbeurer Straße", "Käuzchenweg", "Kazböckstraße", "K-Club (Gögginger Straße 10)", 
    "Kellerstraße", "Keltenstraße", "Kemptener Straße", "Kennedy-Platz", "Keplerstraße", 
    "Kernbeißerweg", "Kernriedstraße", "Kerschensteiner Grund- & Mittelschule", "Kesselmarkt", 
    "Kesterstraße", "Kettengäßchen", "Kiebitzweg", "Kiefernweg", "Kiesbühlstraße", "Kiesowstraße", 
    "Kilianstraße", "Kino Lilliom und Umfeld", "Kirchbergstraße", "Kirchenpräsident-Veit-Straße", 
    "Kirchenweg", "Kirchgasse", "Kirschenweg", "Kitzenmarkt", "Klärwerkstraße", "Klauckestraße", 
    "Klausenberg", "Klausenberg 14 (Mietbar)", "Klausstraße", "Kleestraße", "Kleiberweg", 
    "Kleine Grottenau", "Kleiner Weiher östlich vom Ilsesee", "Kleines Karmelitengäßchen", 
    "Kleines Katharinengäßchen", "Kleingartenweg", "Kleiststraße", "Klettenstraße", "Klimacamp", 
    "Klinkerberg", "Klinkerberg Grünanlage", "Klinkertorplatz", "Klinkertorstraße", "Klopstockstraße", 
    "Kobelcenter Süd Spielplatz", "Kobelweg", "Koblenzer Straße", "Koboldstraße", "Koboldstraße Spielplatz", 
    "Kochelseestraße", "Kohlengasse", "Kohlergasse", "Kohlstattstraße", "Kolbergstraße", 
    "Kollmannstraße", "Koloniestraße", "Kongress am Park", "Königsberger Straße", "Königsbrunner Straße", 
    "Königsplatz", "Königsplatz Gleisdreieck", "Königsplatz Grünanlage", "Königsseestraße", 
    "Konrad-Adenauer-Allee", "Konrad-Zuse-Straße", "Kopernikusstraße", "Körberstraße", 
    "Korianderweg", "Kornblumenweg", "Körnerstraße", "Kornhausgasse", "Kornstraße", "Krähenweg", 
    "Kranichweg", "Kranichweg Spielplatz", "Krankenhausstraße", "Krankenhausstraße Grünanlage", 
    "Krankenhausstraße Spielplatz", "Krautgartenweg", "Kreitmayrstraße", "Kreutzerstraße", 
    "Kreutzerstraße Spielplatz", "Kreuzdornweg", "Kreuzeckstraße", "Kreuzschnabelweg", 
    "Kriegerdenkmal - Blaue Kappe", "Kriegshaberstraße", "Kriemhildenstraße", "Krottenkopfweg", 
    "Krumbacher Straße", "Krumperstraße", "Kuckuckweg", "Kühbacher Weg", "Kuhgäßchen", 
    "Kuhsee", "Kuhsee Pavillon", "Kulturstraße", "Kümmelweg", "Kunstmühlweg", "Kurhausstraße", 
    "Kurt-Bösch-Straße", "Kurt-Schumacher-Straße", "Kurt-Viermetz-Straße", "Kurze Gewanne", 
    "Kurze Straße", "Kurze Wertachstraße", "Kurzes Geländ", "Kustosgäßchen", "Kutak Parkplatz", 
    "Kuttlergäßchen", "Lachnerstraße", "Ladehofstraße", "Landgerichtstraße", "Landsberger Straße", 
    "Landvogtstraße", "Landwehrstraße", "Lange Gasse", "Lange Gewanne", "Langenmantelstraße", 
    "Langes Sächsengäßchen", "Langweider Weg", "Lärchenstraße", "Lärchenweg Kirchplatz", 
    "Laubenweg", "Laugingerstraße", "Lauinger Weg", "Lautenbacherstraße", "Lauterlech", 
    "Lavendelstraße", "Le Coq - Weiße Gasse 8", "Lech Ost/Calisthenics nähe TSG Hochzoll Spielplatz", 
    "Lech Ost/Königsseestraße", "Lech Ost/Königsseestraße Spielplatz", "Lech Ost/Königsstraße Spielplatz", 
    "Lech Ost/TT-Platten bei DJK Hochzoll Spielplatz", "Lech West / Bolzplatz Höhe St. Andreas Freizeitbereich", 
    "Lech West / Spielplatz ggü. Höhe St. Andreas", "Lech West am Grillhügel", "Lechbrucker Straße", 
    "Lechhauser Straße", "Lechpark Grillbereich", "Lechpark Grillbereich Beliner Allee", 
    "Lechrainstraße", "Lechrainstraße Spielplatz", "Lechrainstraße/Lechufer, Ecke Untersbergstraße", 
    "Lechrainstraße/Untersbergstraße", "Lechtalstraße", "Lechufer", 
    "Lechufer im Bereich des Wasserkraftwerkes bzw auf Höhe Untersbergstraße incl Wiese hin zum Osramsteg", 
    "Lechufer, Höhe John Farmer", "Lehárstraße", "Lehningerstraße", "Leibnizstraße", "Leipheimer Weg", 
    "Leipziger Straße", "Leisenmahd", "Leitenbergstraße", "Leitershofer Str. 163", "Leitershofer Straße", 
    "Lenaustraße", "Lenbachstraße", "Leni-Hirsch-Weg", "Lenzstraße", "Leonhard-Hausmann-Straße", 
    "Leonhard-Rucker-Straße", "Leonhardsberg", "Leonhardstraße", "Leopoldstraße", "Lerchenweg", 
    "Lerchenweg Kirchplatz", "Lessingstraße", "Leustraße", "Leustraße Spielplatz", "Leyboldstraße", 
    "Libellenweg", "Liebigstraße", "Liegnitzer Straße", "Ligusterweg", "Lilienstraße", "Lilienthalstraße", 
    "Lincolnstraße", "Lindauer Straße", "Lindenberger Straße", "Lindenstraße", "Linke Brandstraße", 
    "Linnéstraße", "Lippschützstraße", "Lise-Meitner-Straße", "Localbahnstraße", "Lochbachstraße", 
    "Lochbihlerstraße", "Lochgäßchen", "Loco-Bar", "Löfflerstraße", "Loisachstraße", "Lorbeerweg", 
    "Lorenz-Stötter-Weg", "Lortzingstraße", "Loscherstraße", "Lotzbeckstraße", "Louis-Braille-Straße", 
    "Louis-Perridon-Straße", "Löwenstraße", "Luchsweg", "Ludwig-Bauer-Straße", "Ludwig-Gaßner-Weg", 
    "Ludwig-Ottler-Straße", "Ludwig-Ottler-Straße Spielplatz", "Ludwig-Richter-Weg", 
    "Ludwigshafener Straße", "Ludwigstraße", "Ludwig-Thoma-Straße", "Ludwig-Thoma-Straße Spielplatz", 
    "Lueginsland", "Lueginsland Spielplatz", "Lueginslandgäßchen", "Luipoldstraße", "Luisenweg", 
    "Luitpoldstraße", "Luitpoldstraße Spielplatz", "Lüneburger Straße", "Lupinenstraße", 
    "Luther-King-Straße", "Lützowstraße", "Lutzstraße", "Mädelegabelweg", "Madisonstraße", 
    "Madisonstraße Spielplatz", "Magdeburger Straße", "Magellanstraße", "Maienstraße", "Maisenweg", 
    "Maisstraße", "Majolikastraße", "Malerwinkel", "Malmedystraße", "Malmedystraße Spielplatz", 
    "Malvenweg", "Malzstraße", "Manlichstraße", "Manlichstraße Spielplatz", "Marconistraße", 
    "Marco-Polo-Straße", "Marderweg", "Margaretenstraße", "Margeritenweg", "Maria-Ward-Platz", 
    "Marie-Curie-Straße", "Marie-Juchacz-Straße", "Marie-Juchacz-Straße Spielplatz", "Marienbader Straße", 
    "Marienburger Straße", "Marienplatz", "Mariusstraße", "Markgrafenstraße", "Marktoberdorfer Straße", 
    "Mark-Twain-Straße", "Marsweg", "Marthesiastraße", "Martin-Gomm-Weg", "Martini Park", 
    "Martini Wiese", "Martinistraße", "Martinistraße Spielplatz", "Martinistraße Spielplatz und Wiese", 
    "Martin-Luther-Platz", "Märzenhöfle", "Maschenbauerstraße", "Maschenbauerstraße Grünanlage", 
    "Masurenstraße", "Mathildenstraße", "Matthäus-Lang-Straße", "Matthäus-Reichart-Platz", 
    "Matthias-Claudius-Straße", "Matthias-Erzberger-Straße", "Mauerberg", "Mauerberg 12", 
    "Mauerberg 31", "Max-Beckmann-Straße", "Max-Born-Weg", "Max-Gutmann-Straße", "Max-Hempel-Straße", 
    "Maximilianstr Corso/Savage", "Maximilianstr Momo", "Maximilianstr Voyage", "Maximilianstraße", 
    "Maximilianstraße \"Sommercal\"", "Maximilianstraße 35 / Caffe-Centro", "Maximilianstraße 37 / SAUSALITOS", 
    "Max-Josef-Metzger-Straße", "Max-Pechstein-Straße", "Max-Planck-Straße", "Max-Planck-Straße Spielplatz", 
    "Max-Reger-Straße", "Max-von-Laue-Straße", "Maystraße", "Meierweg", "Meisenweg", "Meister-Veits-Gäßchen", 
    "Meitinger Weg", "Melissenweg", "Melissenweg Spielplatz", "Memelweg", "Memminger Straße", 
    "Mendelssohnstraße", "Mendelweg", "Mennwarthstraße", "Meraner Straße", "Merianstraße", 
    "Merianstraße Spielplatz", "Meringer Straße", "Merkurstraße", "Merowingerstraße", "Messe", 
    "Mettlochgäßchen", "Metzgplatz", "Metzstraße", "Milchberg", "Miltenbergstraße", "Mindelheimer Straße", 
    "Mindelstraße", "Mirabellenweg", "Mittelberger Straße", "Mittelfeldstraße", "Mittelstraße", 
    "Mittenfelderstraße Spielplatz", "Mittenwalder Straße", "Mittenwalder Straße Spielplatz", 
    "Mittlere Osterfeldstraße", "Mittlerer Graben", "Mittlerer Graben 12", "Mittlerer Lech", 
    "Mittlerer Lech 50: ,,Die Sizilianerin\"", "Mittlerer Lechfeldweg", "Mittlerer Schleisweg", 
    "Mittlerer Weg", "Mittleres Pfaffengäßchen", "Modular Festival", "Mohnblumenweg", "Mohnstraße", 
    "Moltkestraße", "Mondstraße", "Moosgrabenweg", "Morellstraße", "Mörikestraße", "Moritzplatz", 
    "Moritzplatz (Klimacamp)", "Moritzplatz (Moritzkirche)", "Mößmannstraße", "Mozarthaus", 
    "Mozarthaus (Ratten)", "Mozartstraße", "Muesmannstraße", "Mühlangerweg", "Mühlhauser Straße", 
    "Mühlmahdweg", "Mühlstraße", "Mülichstraße", "Müllerstraße", "Mulzerstraße", "Münchner Straße", 
    "Mundingstraße", "Murnauer Weg", "Muskatellerstraße", "Nagahama-Allee", "Nanette-Streicher-Straße", 
    "Nansenstraße", "Narzissenstraße", "Nebelhornstraße", "Neidhartstraße", "Neißestraße", 
    "Nelkenstraße", "Neptunstraße", "Nesselwanger Straße", "Nestackerweg", "Neuburger Straße", 
    "Neuburger Straße (Platz ggü. Schlößle)", "Neuburger Straße 23 / Kiosk", "Neudeker Straße", 
    "Neue Straße", "Neuer Gang", "Neuer Ostfriedhof", "Neues Kautzengäßchen", "Neufnachweg", 
    "Neuhäuserstr. Ecke Ulmerstr. Bahzanimarkt", "Neuhäuserstraße", "Neuhoferstraße", "Neunkirchenstraße", 
    "Neusässer Straße", "Neuschwansteinstraße", "Neuschwansteinstraße Schule", "Nibelungenstraße", 
    "Nietzschestraße", "Nine O Five", "Nordendorfer Weg", "Nordfriedhof", "Nordfriedhofstraße", 
    "Nördlingerstraße", "Nordstraße", "Novalisstraße", "Nürnberger Straße", "Nußbaumweg", 
    "Nuva Altstadt", "Oberbürgermeister-Dreifuß-Straße", "Oberbürgermeister-Hohner-Straße", 
    "Oberbürgermeister-Müller-Ring", "Obere Jakobermauer", "Obere Osterfeldstraße", "Oberer Auweg", 
    "Oberer Feldweg", "Oberer Feldweg Spielplatz", "Oberer Graben", "Oberer Krautgartenweg", 
    "Oberer Schleisweg", "Oberer Schleisweg Spielplatz", "Oberhausen Nord P+R", "Oberhauser Bahnhof", 
    "Oberländer Straße", "Oberschönenfelder Straße", "Oberstaufener Straße", "Oberstdorfer Straße", 
    "Oblatterwallstraße", "Obstgartenweg", "Obstmarkt", "Occostraße", "Ochsenbachweg (Siebenbrunn)", 
    "Oesterreicherstraße", "Oettinger Straße", "Offenbachweg", "Offinger Straße", "Oglinstrale", 
    "OG's Café & Bar, Dinglerstraße 2", "Ohmstraße", "Ohnsorgstraße", "Oktavianstraße", "Ölbachstraße", 
    "Oleanderweg", "Olof-Palme-Straße", "Olof-Palme-Straße Spielplatz", "Olympiastraße", "ÖPNV", 
    "Orchideenweg", "Orleansstraße", "Ortlerstraße", "Oskar-Kokoschka-Straße", "Oskar-Schindler-Straße", 
    "Oskar-von-Miller-Straße", "Osramsteg", "Osramsteg - Brücke", "Osserweg", "Osterfeldpark", 
    "Ostlandstraße", "Ostrachstraße", "Ottmarsgäßchen", "Ottobeurer Straße", "Otto-Hahn-Straße", 
    "Otto-Holzer-Weg", "Otto-Jochum-Straße", "Otto-Lindenmeyer-Straße", "Otto-Nicolai-Straße", 
    "Otto-Sauler-Straße", "Otto-Schalk-Straße", "Ottostraße", "Oytalstraße", "Palmstraße", 
    "Pankratiusstraße", "Panoramastraße", "Pantheon Lounge, Heilig-Grab-Gasse 1", "Pappelweg", 
    "Pappenheimstraße", "Paracelsusstraße", "Paracelsusstraße Spielplatz", "Paradiesgässchen", 
    "Paradiesgässchen Spielplatz", "Park Am Alten Einlass", "Parkanlage Jakoberwallstraße (auf Höhe Haus-Nr. 21)", 
    "Parkplatz Botanischer Garten", "Parkplatz Sportanlage Süd", "Partnachweg", "Pasteurstraße", 
    "Pater-Roth-Straße", "Paul- Ben- Haim- Weg Spielplatz / Schöppler- Anlage nördlich Seitzsteg", 
    "Paul-Ben-Haim-Weg", "Paul-Ben-Haim-Weg Spielplatz", "Paul-Eipper-Straße", "Paul-Gerhardt-Straße", 
    "Paul-Heyse-Straße", "Paul-Klee-Straße", "Paul-Lincke-Straße", "Paul-Reusch-Straße", 
    "Pavillion am Kuhsee", "Pearl-S.-Buck-Straße", "Peißenbergstraße", "Penzbergweg", 
    "Penzbergweg Spielplatz", "Perzheimstraße", "Pestalozzistraße", "Petelstraße", "Peter-Cornelius-Straße", 
    "Peter-Dörfler-Straße", "Peter-Henlein-Straße", "Peterhofstraße", "Peter-Kötzer-Gasse", 
    "Pettenkoferstraße", "Peutingerstraße", "Pfaffenhofener Straße", "Pfarrer-Anton-Schwab-Weg", 
    "Pfarrer-Bogner-Straße", "Pfarrer-Hacker-Platz", "Pfarrer-Herz-Straße", "Pfarrer-Mayr-Weg", 
    "Pfarrer-Neumeir-Straße", "Pfarrer-Riehl-Weg", "Pfarrhausstraße", "Pfärrle", "Pfaustraße", 
    "Pfersee Schlössle", "Pferseer Straße", "Pferseer Unterführung", "Pfirsichweg", "Pfladergasse", 
    "Pflugstraße", "Pfrontener Straße", "Philipp-Häring-Straße", "Philippine-Welser-Straße", 
    "Philipp-Scheidemann-Straße", "Philipp-Ulhart-Straße", "PI 5 Oberhausen", "PI 6", "PI Lechhausen", 
    "PI Mitte", "PI Süd", "Piccardstraße", "Pilgerhausstraße", "Pilgerhausstraße 19 - \"Huma Er\"", 
    "Pilsener Straße", "Pirolstraße", "Plärrer", "Plärrer Parkplatz", "Platanenweg", "PlayFountain", 
    "Polkstraße", "Ponteilstraße", "Pop Up Store Polizei", "Postbank", "Postillionstraße", "Poststraße", 
    "Pöttmeser Straße", "Prälat-Bigelmair-Straße", "Pranthochstraße", "Präses-Hauser-Platz", 
    "Präses-Hauser-Platz Spielplatz", "Predigerberg", "Predigerberg 14 - „The Green House“", 
    "Preißenbergstraße Bolzplatz", "Preßburger Straße", "Prinz-Karl-Palais", "Prinz-Karl-Park", 
    "Prinz-Karl-Weg", "Prinzregentenplatz", "Prinzregentenstraße", "Prinzstraße", "Prof.-Messerschmitt-Straße 19B", 
    "Professor-Kurz-Straße", "Professor-Messerschmitt-Straße", "Professor-Steinbacher-Straße", 
    "Pröllstraße", "Promenadestraße", "Proviantbach Grünanlage", "Proviantbachstraße", 
    "Provinostraße", "PSV Gögginger Str.", "Puccinistraße", "Pulvergäßchen", "Pürnerstraße", 
    "Quellenstraße", "Quergäßchen", "Quittenweg", "Radauangerstraße", "Radaustraße", "Raddoltstraße", 
    "Radegundis", "Radegundisstraße", "Radegundisweg", "Radetzkystraße", "Rahmgartengäßchen", 
    "Raiffeisenstraße", "Ramsbergstraße", "Randstraße", "Rappenseeweg", "Rapsstraße", "Rastenburgstraße", 
    "Ratdoltstraße", "Räterstraße", "Rathausplatz", "Rathausstraße", "Rathausstraße Spielplatz", 
    "Ratskeller Rathausplatz", "Raunerstraße", "Rauwolffstraße", "Ravenspurgerstraße", "Rebhuhnstraße", 
    "Rechenstraße", "Rechte Brandstraße", "Reeseallee", "Reesepark", "Reesepark Rodelhügel", 
    "Rehlingenstraße", "Rehlingenstraße Spielplatz", "Rehmstraße", "Reichenbachstraße", 
    "Reichenberger Straße", "Reichensteinstraße", "Reiherweg", "Reinekeweg", "Reinöhlstraße", 
    "Reintalstraße", "Reischlestraße", "Reisingerstraße", "Reitmayrgäßchen", "Remboldstraße", 
    "Rembrandtstraße", "Remigiusgasse", "Remshartgäßchen", "Renkenstraße", "Rentmeisterstraße", 
    "Restaurant Ganesha", "Restaurant La Boheme", "Rettenbergweg", "Reutlinger Straße", 
    "Rhododendronweg", "Ricarda-Huch-Straße", "Richard-Hohenner-Platz", "Richard-Wagner-Straße", 
    "Riedingerstraße", "Riedlerstraße", "Riedweg", "Rieslingstraße", "Rießerseestraße", 
    "Rilkestraße", "Ringstraße", "Ritter-von-Steiner-Straße", "Robert-Bosch-Straße", 
    "Robert-Gerber-Straße", "Robert-Koch-Straße", "Robert-Stolz-Straße", "Rockensteinstraße", 
    "Roggenburger Straße", "Roggenstraße", "Römerstädter Straße", "Römerweg", "Röntgenstraße", 
    "Roseggerstraße", "Rosenaustraße", "Rosengasse", "Rose-Oehmichen-Weg", "Rosmarinweg", 
    "Roßhauptener Straße", "Rossinistraße", "Rösslestraße", "Rostocker Straße", "Rotbuchenweg", 
    "Rotes Tor Spielplatz/Grünanlage", "Rote-Torwall-Anlage", "Rote-Torwall-Straße", "Rotkäppchenweg", 
    "Rotkehlchenweg", "Rotkleestraße", "Rot-Kreuz-Straße", "Rot-Kreuz-Straße Spielplatz", 
    "Rot-Kreuz-Straße Spielplatz und Parkanlage", "Rottenbucher Straße", "Rottenhammerstraße", 
    "Roy-Black-Weg", "Rubensstraße", "Rubensstraße Spielplatz", "Rübezahlstraße", "Rubihornstraße", 
    "Rudolf-Diesel-Gymnasium", "Rugendasstraße", "Ruländerstraße", "Rumburgstraße", 
    "Rumplerstr. Ecke Bleriotstr. Spielplatz", "Rumplerstraße", "Rungestraße", "Rupprechtstraße", 
    "Rüsterweg", "Saarburgstraße", "Sägmühlstraße", "Salbeiweg", "Sallingerstraße", "Salomon-Idler-Straße", 
    "Salzachstraße", "Salzmannstraße", "Sämannstraße", "Sanddornweg", "Sanddornweg Spielplatz", 
    "Sanderstraße", "Sandstraße", "Sankt-Antoni-Steig", "Sankt-Anton-Straße", "Sankt-Lukas-Straße", 
    "Sankt-Mang-Weg", "Saturnstraße", "Sauerbruchstraße", "Säulingstraße", "Saurengreinswinkel", 
    "Schackstraße", "Schackstraße Spielplatz", "Schackstraße Unterführung", "Schaezlerstraße", 
    "Schäfflerbach", "Schäfflerbachstraße", "Schäfflergäßchen", "Schafgarbenstraße", "Schafweidstraße", 
    "Schallerstraße", "Scharnhorststraße", "Scharnitzer Weg", "Scharnitzer Weg Spielplatz", 
    "Schärtlstraße", "Scheffelstraße", "Scheidegger Straße", "Schelklingerstraße", "Schellingstraße", 
    "Schenkendorfstraße", "Schernecker Straße", "Schertlinstraße", "Schießgrabenstraße", 
    "Schießstättenstraße", "Schießstättenstraße Spielplatz", "Schiffmacherweg", "Schillerpark", 
    "Schillerpark (Parkplatz bei Kutak)", "Schillerstraße", "Schillstraße", "Schillstraße / Rodelberg / Rewe", 
    "Schillstraße 111", "Schillstraße, Kiesbank", "Schillstraße/Griesle (Skaterpark)", "Schißlerstraße", 
    "Schlachthausgäßchen", "SchlachthofQuartier", "Schlegelstraße", "Schlehenweg", "Schleiermacherstraße", 
    "Schleifergäßchen", "Schlettererstraße", "Schloßanger", "Schlosser`sche Buchhandlung", "Schlossermauer", 
    "Schloßgartenstraße", "Schlössle Park", "Schlößlestraße", "Schlößlestraße 21 (Hexengässchen)", 
    "Schmale Straße", "Schmelzerbreitenweg", "Schmetterlingsweg", "Schmidtkunzstraße", "Schmiedberg", 
    "Schmiedgasse", "Schmutterstraße", "Schneefernerstraße", "Schneehuhnweg", "Schneelingstraße", 
    "Schneewittchenweg", "Schnitterstrale", "Schönbachstraße", "Schönbachstraße 11 Spielewiese", 
    "Schönbachstraße 21 Spielplatz", "Schönbachstraße 27 Spielplatz", "Schöneckstraße", 
    "Schönefelder Gasse", "Schongauer Straße", "Schönspergerstraße", "Schopenhauerstraße", 
    "Schöpplerstraße", "Schrannenstraße", "Schrobenhauser Straße", "Schrobenhauser Straße Spielplatz", 
    "Schroeckstraße", "Schrofenstraße", "Schubertstraße", "Schülestraße", "Schulstraße", 
    "Schumannstraße", "Schützenstraße", "Schwabecker Straße", "Schwabenhof", "Schwabenweg", 
    "Schwalbenstraße", "Schwammerlweg", "Schwangaustraße", "Schwanseestraße", "Schwarzenbergstraße", 
    "Schwedenstiege", "Schwedenweg", "Schweidnitzer Straße", "Schweizerstraße", "Schweriner Straße", 
    "Schwester-Agathe-Straße", "Schwibbogengasse", "Schwibbogenmauer", "Schwibbogenplatz", 
    "Schwimmschulstr. Wertachufer", "Schwimmschulstraße", "Schwimmschulstraße, Langemantelstraße (Plärrerdienst)", 
    "Sebastian-Buchegger-Platz", "Sebastian-Kneipp-Gasse", "Sebastianstraße", "Seefelder Straße", 
    "Seidelbaststraße", "Seidererstraße", "Seidererstraße Spielplatz", "Seilerstraße", "Seitzstraße", 
    "Semmelweisstraße", "Senefelderstraße", "Senkelbachstraße", "Sensenstraße", "Sepp-Mastaller-Straße", 
    "Seydlitzstraße", "Sheridan Park Casino Schaukelspielplatz", "Sheridan Park/Skateanlage", 
    "Sheridanpark", "Sheridanpark/Multifunktionsfläche südlich John-May-Weg Spielplatz", 
    "Sheridanweg", "Sichelstraße", "Siebenbrunn", "Siebenbrunner Straße (Siebenbrunn)", 
    "Siebenbürgenstraße", "Siebentischpark", "Siebentischstraße", "Siedlerweg", "Siedlung des Volkes", 
    "Siegfried-Aufhäuser-Straße", "Siegfriedstraße", "Sieglindenstraße", "Sigmund-Schuckert-Straße", 
    "Sigmundstraße", "Silbermannstraße", "Silcherstraße", "Simpertstraße", "Singerstraße", 
    "Singoldstraße", "Soldnerstraße", "Söllereckstraße", "Sommernächte", "Sommerstraße", 
    "Sommestraße", "Sonnenbachweg", "Sonnenstraße", "Sonnwendstraße", "Sonthofer Straße", 
    "Spechtstraße", "Speckbacherstraße", "Spenglergäßchen", "Sperberweg", "Sperlingstraße", 
    "Speyerer Straße", "Spicherer Straße", "Spickelstraße", "Spickelwiese/Ablaßweg Spielplatz", 
    "Spielfeldstraße", "Spiesleweg", "Spitalgasse", "Spitzmahdstraße", "Spitzmahdstraße Spielplatz", 
    "Sportanlage Süd", "Sportplatzstraße", "Springergäßchen", "St. Moritz Kirche", "Stadionstraße", 
    "Stadlerweg", "Stadtbachstraße", "Stadtberger Str. 17 + 19 - Jugend- und Bürgerhaus", 
    "Stadtberger Straße", "Stadtbücherei 86150", "Stadtjägerstraße", "Stadtmarkt", "Stadtwald", 
    "Staffelseestraße", "Stainingerstraße", "Starstraße", "Stätzlinger Straße", "Staudenweg", 
    "Stauffenbergstraße", "Stauffenstraße", "Stefan-Höpfinger-Weg", "Stefan-Zweig-Straße", 
    "Stegstraße", "Steinbrechstraße", "Steinerne Furt", "Steingadener Straße", "Steingasse", 
    "Steinmetzstraße", "Stenglinstraße", "Stephansgasse", "Stephansplatz", "Stephingerberg", 
    "Stephingergraben", "Sterngässchen", "Sterngasse", "Sterntalerweg", "Sterzinger Straße", 
    "Stettenstraße", "Stettiner Straße", "Stieglitzweg", "Stieranger", "Stiermannstraße", 
    "Stillachweg", "Storchenstraße", "Stoygäßchen", "Stralsunder Straße", "Straßenname", 
    "Stuibenstraße", "Stuttgarter Straße", "Sudermannstraße", "Sudetenstraße", 
    "Sudetenstraße / Endhaltestelle Linie 2", "Sudetenstraße Spielplatz", "Südmährer Weg", 
    "Südstraße", "Südtiroler Straße", "Südwestecke des CFS", "Sullastrafe", "Sulzerstraße", 
    "Sylvanerweg", "Synagoge Innenstadt – Halderstraße 6 – 8", "Synagoge Kriegshaber – Ulmer Straße 228", 
    "Täfertinger Weg", "Täfertinger Weg Spielplatz", "Talweg", "Tannenstraße", "Tannheimer Straße", 
    "Tatrastraße", "Tattenbachstraße", "Taubenstraße", "Tauentzienstraße", "Tauroggener Straße", 
    "Tauscherstraße", "Taxisstraße", "TBA - Oberhausen", "Tegelbergstraße", "Tegernseestraße", 
    "Teplitzer Straße", "Terlaner Straße", "Textilstraße", "Thaddäus-Schmid-Straße", "Thalesstraße", 
    "Thalkirchdorfer Weg", "Thanellerstraße", "The", "Theaterstraße", "Thelottstraße", 
    "Theodor-Heuss-Platz", "Theodor-Sachs-Straße", "Theodor-Wiedemann-Straße", "Theresienstraße", 
    "Thierhaupter Weg", "Thomas-Breit-Straße", "Thomas-Breit-Straße Spielplatz", "Thomas-Mann-Straße", 
    "Thomastraße", "Thommstraße", "Thurgauerstraße", "Tiberiusstraße", "Tieckstraße", "Tiefbauamt", 
    "Tiefgarage Stadtmetz", "Tiergartenweg", "Tillystraße", "Tilsiter Straße", "Tiroler Straße", 
    "Tobias-Maurer-Straße", "Toblacher Straße", "Toni-Park", "Traminerweg", "Trauchgaustraße", 
    "Trendelstraße", "Trendelstraße Spielplatz", "Trettachstraße", "Treustraße", "Troppauer Weg", 
    "Tuchbleichstraße", "Tuchbleichstraße Spielplatz", "Tulpenstraße", "Tunnelstraße", 
    "Tunnelstraße Spielplatz", "Türkenbundstraße", "Turmgäßchen", "Turnerstrale", "Tylerstraße", 
    "Uhlandstraße", "Uhlandwiese", "Ulmenhofstraße", "Ulmenweg", "Ulmer Straße", "Ulmer Straße 23", 
    "Ulmer Straße Haltestelle Wertach bis Unterführung Oberhauser Bahnhof", "Ulmer Straße/Dumler Straße", 
    "Ulrich-Hofmaier-Straße", "Ulrich-Schiegg-Straße", "Ulrich-Schiegg-Straße Spielplatz", 
    "Ulrich-Schwarz-Straße", "Ulrichsgasse", "Ulrichsmahd", "Ulrichsplatz", "Ulrichsplatz \"Cafe Europa\"", 
    "Ulrichsplatz 3 \"U3 Club\"", "Ulrichsschule Spielplatz Außenstelle Schubertschule", "Ulstettstraße", 
    "Umfeld der ESSO-Tankstelle an der Blauen Kappe", "Umfeld der Werner-von-Siemens Grundschule", 
    "UNI- Klinik", "Universitätsklinik", "Universitätsstraße", "Univiertel", "Unter dem Bogen", 
    "Unterberger Str. Kiesbänke", "Untere Jakobermauer", "Untere Jakobermauer 13", "Untere Osterfeldstraße", 
    "Unterer Auweg", "Unterer Graben", "Unterer Griesweg", "Unterer Krautgartenweg", "Unterer Stockplatz", 
    "Unterer Talweg", "Unterfeldstraße", "Unterfeldweg", "Untersbergstraße", "Urlspergerstraße", 
    "Utzschneiderstraße", "Valentin-Heider-Straße", "Veilchenweg", "Verdistraße", "Vesaliusstraße", 
    "VG1 Eingangsbereich", "Via-Claudia-Straße", "Viertes Quergäßchen", "Viktoriastraße", 
    "Vinzenz-von-Paul-Platz", "Virchowstraße", "Vogelmauer", "Vogelmauer (Brücke)", "Vogesenstraße", 
    "Vogteistraße", "Vohenburgerstraße", "Volkhartstraße", "Völkstraße", "Von-Arnim-Straße", 
    "Von-Bieber-Straße", "Von-Cobres-Straße", "Von-Cobres-Straße 5", "Von-der-Tann-Straße", 
    "Von-Görres-Straße", "Von-Hoesslin-Straße", "Von-Osten-Straße", "Von-Paris-Straße", 
    "Von-Parseval-Straße", "Von-Parseval-Straße Spielplatz", "Von-Rad-Straße", "Von-Richthofen-Straße", 
    "Von-Willibald-Straße", "Von-Ysenburg-Straße", "Vorderer Lech", "Vorderes Kretzengäßchen", 
    "Vorplatz Wendehammer Hbf", "Waaggäßchen", "Wacholderweg", "Wachstuchstraße", "Wachtelstraße", 
    "Wagenhalsstraße", "Waibelstraße", "Waidmannstraße", "Waisengäßchen", "Walchenseestraße", 
    "Walchstraße", "Waldfriedenstraße", "Waldhaus", "Waldheimstraße", "Waldkauzstraße", 
    "Waldkindergarten (Waldwichtel)", "Waldmeisterweg", "Waldstraße", "Wallensteinstraße", 
    "Wallgauer Weg", "Wallgauer Weg Spielplatz", "Wallnerstraße", "Wallstraße", "Wallstraße Späti", 
    "Walsertalweg", "Walter-Oehmichen-Weg", "Walterstraße", "Walther-Heim-Straße", "Walther-Rathenau-Straße", 
    "Wämstlergäßchen", "Wankstraße", "Warndtstraße", "Wartenburger Straße", "Wasenmeisterweg", 
    "Wasserhausweg", "Wasserturmstraße", "Waterloostraße", "Watzmannstraße", "Watzmannstraße Bolzplatz", 
    "Waxensteinstraße", "Waxensteinstraße Spielplatz", "Waxensteinstraße/Kleingartenanlage", 
    "Weberstraße", "Weddigenstraße", "Weg der Barmherzigen Schwestern", "Wegwartstraße", 
    "Weichenbergerstraße", "Weichselweg", "Weidachstraße", "Weidenstraße", "Weihenstraße", 
    "Weiherstraße", "Weingartenweg", "Weißdornstraße", "Weiße Gasse", "Weißenburger Straße", 
    "Weißenseestraße", "Weißstraße", "Weite Gasse", "Weizenstraße", "Weldener Weg", "Weldishoferstraße", 
    "Welfenstraße", "Wellenburg", "Wellenburger Straße", "Welser Passage", "Welserplatz", 
    "Wemdinger Weg", "Wendelsteinstraße", "Werbhausgasse", "Werdenfelser Straße", "Werderstraße", 
    "Werner-Egk-Weg", "Werner-Haas-Straße", "Werner-Heisenberg-Straße", "Werner-von-Siemens-Straße", 
    "Werner-von-Siemens-Volksschule", "Wernhüterstraße", "Wertach Ostufer auf Höhe Straße in der Fuchssiedlung", 
    "Wertachbrücke Oberhausen", "Wertachbrucker-Tor-Straße", "Wertachpavillion", "Wertachstraße", 
    "Wertachstraße Kiosk", "Wertachufer", "Wertachufer Inningen", "Wertinger Straße", "Wessobrunner Weg", 
    "Westendorfer Weg", "Westfriedhof", "Westparkschule am Sheridanpark", "Weststraße", 
    "Wettersteinstraße", "Widdersteinweg", "Widderstraße", "Wieselweg", "Wiesenbachstraße", 
    "Wiesenstraße", "Wildtaubenweg", "Wilhelm-Busch-Weg", "Wilhelm-Hauff-Straße", 
    "Wilhelmine-Reichard-Straße", "Wilhelm-Raabe-Straße", "Wilhelm-Reitzmayr-Straße", 
    "Wilhelmstraße", "Wilhelm-Wörle-Straße", "Willibald-Popp-Straße", "Willi-Stör-Straße", 
    "Willi-Weise-Straße", "Willi-Willadt-Weg", "Willy-Brandt-Platz", "Willy-Brandt-Platz Gehweg hinter City Galerie", 
    "Windprechtstraße", "Wintergasse", "Wirsungstraße", "Wirthshölzelweg", "Wittelsbacher Park", 
    "Wittelsbacher Park - Großer Spielplatz mit Röhrenrutsche", "Wittelsbacherstraße", 
    "Wolfgang-/Ecke Wertachstraße", "Wolfgangstraße", "Wolfgang-von-Gronau-Straße", "Wolfleitenweg", 
    "Wolfram-/Sanderstraße", "Wolframstraße", "Wolframstraße Spielplatz", "Wolfsgäßchen", "Wolfzahnau", 
    "Wolfzahnau \" The Spitz \"", "Wolfzahnau ggü. Schillerpark", "Wolfzahnstraße", "Wollmarkt", 
    "Wörishofer Straße", "World of Carwash", "Wörnitzstraße", "Wörthstraße", "Wulfertshauser Weg", 
    "Yorckstraße", "Zainerstraße", "Zaunkönigweg", "Zedernweg", "Zedlitzstraße", "Zeisigweg", 
    "Zenettistraße", "Zeppelinstraße", "Zeuggasse", "Zeugplatz", "Ziegeleistraße", "Zieglerstraße", 
    "Zietenstraße", "Zimmererstraße", "Zimmermannstraße", "Zirbelstraße", "Zobelstraße", 
    "Zollernstraße", "Zoo, Trinkwasserschutzgebiet", "Zugspitzstraße", "Zugspitzstraße 104 (Neuer Ostfriedhof)", 
    "Zugspitzstraße/Peißenbergstraße Spielplatz", "Zum Fuggerschloß", "Zum Griesle", "Zum Hinterfeld", 
    "Zum Lechwehr", "Zum Maierberg", "Zum Neuen Friedhof", "Zusamstraße", "Zwerchgasse", 
    "Zwischen Bürgertreff und Heilig-Geist-Kirche", "Zwölf-Apostel-Platz", "Zwölf-Apostel-Platz Spielplatz"
])

# --- 5. AMTKLICHER PDF GENERATOR ---
class BehoerdenPDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 30)
        else:
            self.set_font("Arial", "B", 10); self.set_text_color(150, 150, 150)
            self.cell(30, 10, "STADTWAPPEN", ln=False)
        self.set_font("Arial", "B", 16); self.set_text_color(0, 75, 149); self.set_x(50)
        self.cell(0, 10, "STADT AUGSBURG", ln=True)
        self.set_font("Arial", "", 12); self.set_x(50)
        self.cell(0, 7, "Ordnungsamt | Kommunaler Ordnungsdienst", ln=True)
        self.ln(10); self.line(10, 42, 200, 42)

    def footer(self):
        self.set_y(-15); self.set_font("Arial", "I", 8); self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Einsatzprotokoll KOD Augsburg | Seite {self.page_no()}/{{nb}}", align="C")

def erstelle_pdf(row):
    pdf = BehoerdenPDF(); pdf.alias_nb_pages(); pdf.add_page()
    pdf.ln(5); pdf.set_font("Arial", "B", 14); pdf.cell(0, 10, f"Einsatzprotokoll | AZ: {row['AZ']}", ln=True); pdf.ln(5)
    pdf.set_font("Arial", "B", 10); pdf.set_fill_color(245, 245, 245)
    fields = [("Datum / Zeit:", f"{row['Datum']} | {row['Beginn']} - {row['Ende']}"), ("Einsatzort:", f"{row['Ort']} {row['Hausnummer']}"), ("Kräfte:", row['Kraefte']), ("Beteiligte:", row['Zeugen']), ("GPS:", row['GPS'])]
    for label, val in fields:
        pdf.set_font("Arial", "B", 10); pdf.cell(45, 7, f" {label}", fill=True)
        pdf.set_font("Arial", "", 10); pdf.cell(0, 7, f" {val}", ln=True, fill=True)
    pdf.ln(10); pdf.set_font("Arial", "B", 12); pdf.cell(0, 10, "Sachverhalt:", ln=True)
    pdf.set_font("Arial", "", 11); pdf.multi_cell(0, 6, row['Bericht'])
    if row['Foto'] != "-":
        pdf.add_page()
        try:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(base64.b64decode(row['Foto']))))
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                img.save(tmp.name, format="JPEG", quality=85); w, h = img.size; aspect = h / w
                pdf_w = 170; pdf_h = min(220, pdf_w * aspect); x_pos = (210 - (pdf_h / aspect if pdf_h == 220 else pdf_w)) / 2
                pdf.image(tmp.name, x_pos, 40, (pdf_h / aspect if pdf_h == 220 else pdf_w), pdf_h); os.unlink(tmp.name)
        except: pdf.cell(0, 10, "[Bildfehler]", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 6. UI ---
if not st.session_state["auth"]:
    st.markdown("<h1 style='text-align: center;'>🚓 Dienst Login</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        pw = st.text_input("Passwort", type="password")
        if st.button("Anmelden", use_container_width=True):
            if pw == DIENST_PW: st.session_state["auth"] = True; st.rerun()
    st.stop()

with st.sidebar:
    st.header("⚙️ Admin")
    if not st.session_state["admin_auth"]:
        if st.text_input("Admin-Passwort", type="password") == ADMIN_PW: st.session_state["admin_auth"] = True; st.rerun()
    else:
        st.success("Admin-Modus aktiv")
        if st.button("Logout"): st.session_state["admin_auth"] = False; st.rerun()

st.title("📋 Einsatzbericht")
loc = get_geolocation()
gps_ready = f"{loc['coords']['latitude']}, {loc['coords']['longitude']}" if loc else "-"
DATEI = "zentral_archiv_secure.csv"

def lade_daten():
    spalten = ["Datum", "Beginn", "Ende", "Ort", "Hausnummer", "Zeugen", "Bericht", "AZ", "Foto", "Dienstkraft", "GPS", "Kraefte"]
    if os.path.exists(DATEI):
        df = pd.read_csv(DATEI).astype(str)
        for col in spalten:
            if col not in df.columns: df[col] = "-"
        for col in ["Bericht", "Zeugen", "Foto", "Kraefte"]: df[col] = df[col].apply(entschluesseln)
        return df[spalten]
    return pd.DataFrame(columns=spalten)

daten = lade_daten()

with st.expander("➕ NEUER BERICHT", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        d, t1, t2 = c1.date_input("Datum"), c2.time_input("Beginn"), c3.time_input("Ende")
        o1, o2, o3 = st.columns([3,1,2])
        ort = o1.selectbox("Ort", STRASSEN_AUGSBURG, index=None, placeholder="Straße suchen...")
        nr = o2.text_input("Nr.")
        az = o3.text_input("AZ")
        st.write("Kräfte vor Ort:")
        ck1, ck2, ck3 = st.columns(3)
        p_on = ck1.checkbox("Polizei")
        funk = ck1.text_input("Funkstreife") if p_on else ""
        r_on, f_on = ck2.checkbox("RTW"), ck3.checkbox("Feuerwehr")
        k_list = []
        if p_on: k_list.append(f"Polizei ({funk})")
        if r_on: k_list.append("RTW")
        if f_on: k_list.append("Feuerwehr")
        bericht, z, f = st.text_area("Sachverhalt"), st.text_input("Zeugen/Beteiligte"), st.file_uploader("Foto")
        if st.form_submit_button("Speichern"):
            f_b = "-"
            if f:
                img = ImageOps.exif_transpose(Image.open(f))
                img.thumbnail((1000, 1000)); buf = io.BytesIO(); img.save(buf, format="JPEG", quality=75)
                f_b = base64.b64encode(buf.getvalue()).decode()
            new_row = [str(d), t1.strftime("%H:%M"), t2.strftime("%H:%M"), str(ort), nr, verschluesseln(z), verschluesseln(bericht), az, verschluesseln(f_b), "KOD", gps_ready, verschluesseln(", ".join(k_list))]
            pd.concat([pd.read_csv(DATEI) if os.path.exists(DATEI) else pd.DataFrame(columns=daten.columns), pd.DataFrame([new_row], columns=daten.columns)]).to_csv(DATEI, index=False)
            st.rerun()

st.divider()
for i, row in daten.iloc[::-1].iterrows():
    with st.expander(f"📍 {row['Ort']} | {row['Datum']} (AZ: {row['AZ']})"):
        st.write(f"Zeit: {row['Beginn']}-{row['Ende']} | Kräfte: {row['Kraefte']}")
        st.info(row['Bericht'])
        if row['Foto'] != "-": st.image(base64.b64decode(row['Foto']), width=300)
        if st.session_state["admin_auth"]:
            st.download_button("📄 Amtliches PDF", data=erstelle_pdf(row), file_name=f"Bericht_{row['AZ']}.pdf", key=f"p{i}")
