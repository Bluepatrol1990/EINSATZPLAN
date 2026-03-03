<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Einsatzprotokoll - Stadt Augsburg</title>
    <style>
        :root {
            --augsburg-blue: #0054a6;
            --light-grey: #f4f4f4;
        }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: var(--light-grey); }
        .container { max-width: 650px; margin: auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h2 { color: var(--augsburg-blue); border-bottom: 3px solid var(--augsburg-blue); padding-bottom: 10px; margin-top: 0; }
        
        .info-box { background: #e7eff6; padding: 10px; border-radius: 8px; margin-bottom: 20px; font-size: 0.9em; border-left: 5px solid var(--augsburg-blue); }
        
        label { display: block; margin-top: 15px; font-weight: bold; color: #333; }
        input, select, textarea { width: 100%; padding: 12px; margin-top: 5px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 16px; }
        
        button { background-color: var(--augsburg-blue); color: white; padding: 15px; border: none; border-radius: 6px; cursor: pointer; width: 100%; margin-top: 25px; font-size: 18px; font-weight: bold; transition: background 0.3s; }
        button:hover { background-color: #003d7a; }
        
        .footer-text { text-align: center; margin-top: 15px; font-size: 0.8em; color: #777; }
    </style>
</head>
<body>

<div class="container">
    <h2>Einsatzprotokoll</h2>
    
    <div class="info-box">
        <strong>Empfänger:</strong> Kevin.woelki@augsburg.de; kevinworlki@outlook.de
    </div>

    <label for="standort">Standort / Örtlichkeit</label>
    <input type="text" id="standort" placeholder="z.B. Königsplatz, Kuhsee...">

    <label for="feststellung">Feststellung</label>
    <select id="feststellung">
        <option value="">-- Bitte wählen --</option>
        <option value="§ 111 OWiG">§ 111 OWiG</option>
        <option value="§ 118 OWiG Belästigung der Allgemeinheit">§ 118 OWiG Belästigung der Allgemeinheit</option>
        <option value="Alkoholgenuss auf Spielplätzen">Alkoholgenuss auf Spielplätzen</option>
        <option value="Alkoholgenuss außerhalb zugelassener Freischankflächen">Alkoholgenuss außerhalb zugelassener Freischankflächen</option>
        <option value="Alkoholgenuss im Friedhof">Alkoholgenuss im Friedhof</option>
        <option value="Alkoholkonsumverbot">Alkoholkonsumverbot</option>
        <option value="als Berechtigter außerhalb der zugelassenen Zeiten ein KFZ abgestellt">als Berechtigter außerhalb der zugelassenen Zeiten ein KFZ abgestellt</option>
        <option value="als Berechtigter außerhalb der zugelassenen Zeiten ein KFZ benutzt">als Berechtigter außerhalb der zugelassenen Zeiten ein KFZ benutzt</option>
        <option value="Anzeige(n) an das Jugendamt wird / werden erstellt">Anzeige(n) an das Jugendamt wird / werden erstellt</option>
        <option value="Aufstellen von Zelten und Wohnwagen">Aufstellen von Zelten und Wohnwagen</option>
        <option value="Baden an einer mit einem Badeverbot belegten Stelle">Baden an einer mit einem Badeverbot belegten Stelle</option>
        <option value="Befahren Gehweg mit E-Scooter">Befahren Gehweg mit E-Scooter</option>
        <option value="Befahren Gehweg mit KFZ">Befahren Gehweg mit KFZ</option>
        <option value="Betreiben von Feuerstellen und das Grillen außerhalb der dafür gekennzeichneten Flächen">Betreiben von Feuerstellen und das Grillen außerhalb der dafür gekennzeichneten Flächen</option>
        <option value="Betreten von Blumenschmuckpflanzungen">Betreten von Blumenschmuckpflanzungen</option>
        <option value="Betretenlassen des Kuhsees, Ilsesees oder Autobahnsees durch Hunde">Betretenlassen des Kuhsees, Ilsesees oder Autobahnsees durch Hunde</option>
        <option value="Betteln in organisierter oder aggressiver Form">Betteln in organisierter oder aggressiver Form</option>
        <option value="Bürgerinformationen">Bürgerinformationen</option>
        <option value="Dienstfahrzeug getankt">Dienstfahrzeug getankt</option>
        <option value="direktes unverwahrtes Feuer auf Kiesbänken">direktes unverwahrtes Feuer auf Kiesbänken</option>
        <option value="div. Innendiensttätigkeiten">div. Innendiensttätigkeiten</option>
        <option value="Ermittlungen für den Innendienst">Ermittlungen für den Innendienst</option>
        <option value="E-Scooter auf unbesch. Gehweg">E-Scooter auf unbesch. Gehweg</option>
        <option value="E-Scooter ohne Licht">E-Scooter ohne Licht</option>
        <option value="Fahren, Parken oder Abstellen in Grünanlage (E-Scooter)">Fahren, Parken oder Abstellen in Grünanlage (E-Scooter)</option>
        <option value="Fahren, Parken oder Abstellen in Grünanlage (KFZ)">Fahren, Parken oder Abstellen in Grünanlage (KFZ)</option>
        <option value="Falsche Umweltplakette">Falsche Umweltplakette</option>
        <option value="Fehlende Umweltplakette">Fehlende Umweltplakette</option>
        <option value="Grünanlage kontrolliert, keine Auffälligkeiten.">Grünanlage kontrolliert, keine Auffälligkeiten.</option>
        <option value="Grünanlage kontrolliert, keine Beanstandungen">Grünanlage kontrolliert, keine Beanstandungen</option>
        <option value="Hexengässchen">Hexengässchen</option>
        <option value="Hunde in Blumenschmuckpflanzung">Hunde in Blumenschmuckpflanzung</option>
        <option value="Jugendschutz Kontrolle(n) gemäß JuSchG § 10">Jugendschutz Kontrolle(n) gemäß JuSchG § 10</option>
        <option value="Jugendschutz Kontrolle(n) gemäß JuSchG § 9">Jugendschutz Kontrolle(n) gemäß JuSchG § 9</option>
        <option value="Kein bekanntes Klientel vor Ort. Keine Beanstandung">Kein bekanntes Klientel vor Ort. Keine Beanstandung</option>
        <option value="Kein ordnungswidriges Verhalten feststellbar.">Kein ordnungswidriges Verhalten feststellbar.</option>
        <option value="Kein Vandalismus feststellbar.">Kein Vandalismus feststellbar.</option>
        <option value="Keine Beanstandungen">Keine Beanstandungen</option>
        <option value="Keine beschwerderelevanten Vorkommnisse feststellbar.">Keine beschwerderelevanten Vorkommnisse feststellbar.</option>
        <option value="Keine Bettler vor Ort">Keine Bettler vor Ort</option>
        <option value="Keine Obdachlose an der Örtlichkeit, keine Beanstandungen">Keine Obdachlose an der Örtlichkeit, keine Beanstandungen</option>
        <option value="Keine Ordnungswidrigkeiten festgestellt.">Keine Ordnungswidrigkeiten festgestellt.</option>
        <option value="Keine Personen vor Ort">Keine Personen vor Ort</option>
        <option value="Keine Personen vor Ort. Keine Beanstandungen.">Keine Personen vor Ort. Keine Beanstandungen.</option>
        <option value="Keine Störung der öffentlichen Sicherheit und Ordnung">Keine Störung der öffentlichen Sicherheit und Ordnung</option>
        <option value="Keine Verunreinigung durch Sperrmüll feststellbar.">Keine Verunreinigung durch Sperrmüll feststellbar.</option>
        <option value="Lagern und Nächtigen">Lagern und Nächtigen</option>
        <option value="Mitführen u./o. Laufenlassen von Hunden auf Liegeflächen">Mitführen u./o. Laufenlassen von Hunden auf Liegeflächen</option>
        <option value="Mitführen u./o. Laufenlassen von Hunden auf Spielplätzen">Mitführen u./o. Laufenlassen von Hunden auf Spielplätzen</option>
        <option value="Mitführen u./o. Laufenlassen von Hunden im Friedhof">Mitführen u./o. Laufenlassen von Hunden im Friedhof</option>
        <option value="ohne zum Kreis der Berechtigten zu gehören und außerhalb der zugelassenen Zeiten ein KFZ abgestellt">ohne zum Kreis der Berechtigten zu gehören und außerhalb der zugelassenen Zeiten ein KFZ abgestellt</option>
        <option value="ohne zum Kreis der Berechtigten zu gehören und außerhalb der zugelassenen Zeiten ein KFZ benutzt">ohne zum Kreis der Berechtigten zu gehören und außerhalb der zugelassenen Zeiten ein KFZ benutzt</option>
        <option value="Örtlichkeit gut besucht, keine Beanstandungen">Örtlichkeit gut besucht, keine Beanstandungen</option>
        <option value="Örtlichkeit sauber, keine Beanstandungen">Örtlichkeit sauber, keine Beanstandungen</option>
        <option value="Örtlichkeit verschmutzt, kein Verursacher feststellbar">Örtlichkeit verschmutzt, kein Verursacher feststellbar</option>
        <option value="Örtlichkeit wenig besucht, keine Beanstandungen.">Örtlichkeit wenig besucht, keine Beanstandungen.</option>
        <option value="Parken auf Gehweg">Parken auf Gehweg</option>
        <option value="Parken im Straßenbegleitgrün">Parken im Straßenbegleitgrün</option>
        <option value="Parken in amtlich gekennzeichneter Feuerwehrzufahrt">Parken in amtlich gekennzeichneter Feuerwehrzufahrt</option>
        <option value="Parken in der Bordsteinabsenkung">Parken in der Bordsteinabsenkung</option>
        <option value="Parken in einer Grünanlage mit E-Scooter">Parken in einer Grünanlage mit E-Scooter</option>
        <option value="Parken in einer Grünanlage mit KFZ">Parken in einer Grünanlage mit KFZ</option>
        <option value="Parken nicht am rechten Fahrbahnrand">Parken nicht am rechten Fahrbahnrand</option>
        <option value="Parken vor Bordsteinabsenkung">Parken vor Bordsteinabsenkung</option>
        <option value="Radfahren auf einem Friedhof">Radfahren auf einem Friedhof</option>
        <option value="Radfahren auf Radweg in falscher Richtung">Radfahren auf Radweg in falscher Richtung</option>
        <option value="Radfahren auf unbeschildertem Gehweg">Radfahren auf unbeschildertem Gehweg</option>
        <option value="Radfahren in einer Grünanlage">Radfahren in einer Grünanlage</option>
        <option value="Radfahren in entgegengesetzte Richtung">Radfahren in entgegengesetzte Richtung</option>
        <option value="Radfahren mit Gehörbeeinträchtigung">Radfahren mit Gehörbeeinträchtigung</option>
        <option value="Radfahren ohne Licht">Radfahren ohne Licht</option>
        <option value="Radfahren und Handybenutzung">Radfahren und Handybenutzung</option>
        <option value="Rauchen auf Spielplätzen">Rauchen auf Spielplätzen</option>
        <option value="Siehe Einzelnachweise">Siehe Einzelnachweise</option>
        <option value="Spielplatz kontrolliert, keine Beanstandungen">Spielplatz kontrolliert, keine Beanstandungen</option>
        <option value="Übermäßiges Füttern von Tauben">Übermäßiges Füttern von Tauben</option>
        <option value="Urinieren in der Öffentlichkeit">Urinieren in der Öffentlichkeit</option>
        <option value="Verbot für Glasbehälter oder ähnliche Gegenstände aus Glas">Verbot für Glasbehälter oder ähnliche Gegenstände aus Glas</option>
        <option value="Verrichten der Notdurft">Verrichten der Notdurft</option>
        <option value="Verstoß gegen das Merkblatt für Straßenmusikanten">Verstoß gegen das Merkblatt für Straßenmusikanten</option>
        <option value="Verstoß gegen die Lärmschutzverordnung">Verstoß gegen die Lärmschutzverordnung</option>
        <option value="Verstoß gegen die Straßensondernutzung">Verstoß gegen die Straßensondernutzung</option>
        <option value="Verunreinigung durch Hundekot">Verunreinigung durch Hundekot</option>
        <option value="VZ 229: Parken im Taxistand">VZ 229: Parken im Taxistand</option>
        <option value="VZ 237: nicht Benutzung des vorhandenen Radweges (Fahrtrichtung)">VZ 237: nicht Benutzung des vorhandenen Radweges (Fahrtrichtung)</option>
        <option value="VZ 239: Befahren eines beschilderten Gehweges mit E-Scooter">VZ 239: Befahren eines beschilderten Gehweges mit E-Scooter</option>
        <option value="VZ 239: Befahren eines beschilderten Gehweges mit KFZ">VZ 239: Befahren eines beschilderten Gehweges mit KFZ</option>
        <option value="VZ 239: Radfahren auf einem beschilderten Gehweg">VZ 239: Radfahren auf einem beschilderten Gehweg</option>
        <option value="VZ 240: nicht Benutzung des vorhandenen Radweges">VZ 240: nicht Benutzung des vorhandenen Radweges</option>
        <option value="VZ 241: nicht Benutzung des vorhandenen Radweges">VZ 241: nicht Benutzung des vorhandenen Radweges</option>
        <option value="VZ 242: Befahren der Fußgängerzone mit E-Scooter">VZ 242: Befahren der Fußgängerzone mit E-Scooter</option>
        <option value="VZ 242: Befahren der Fußgängerzone mit Fahrrad">VZ 242: Befahren der Fußgängerzone mit Fahrrad</option>
        <option value="VZ 242: Befahren der Fußgängerzone mit KFZ">VZ 242: Befahren der Fußgängerzone mit KFZ</option>
        <option value="VZ 242: Befahren Fußgängerzone ohne Ausnahmegenehmigung">VZ 242: Befahren Fußgängerzone ohne Ausnahmegenehmigung</option>
        <option value="VZ 242: Befahren Fußgängerzone schneller als Schrittgeschwindigkeit">VZ 242: Befahren Fußgängerzone schneller als Schrittgeschwindigkeit</option>
        <option value="VZ 242: Parken in der Fußgängerzone mit KFZ">VZ 242: Parken in der Fußgängerzone mit KFZ</option>
        <option value="VZ 250: Verbot für Fahrzeuge aller Art">VZ 250: Verbot für Fahrzeuge aller Art</option>
        <option value="VZ 260: Verbot für Kraftfahrzeuge">VZ 260: Verbot für Kraftfahrzeuge</option>
        <option value="VZ 283: Parken im absoluten Haltverbot">VZ 283: Parken im absoluten Haltverbot</option>
        <option value="VZ 286: Parken im eingeschränkten Haltverbot">VZ 286: Parken im eingeschränkten Haltverbot</option>
        <option value="VZ 314: + ZZZ 1044 10: Parken Sonderparkplatz Schwerbehinderte">VZ 314: + ZZZ 1044 10: Parken Sonderparkplatz Schwerbehinderte</option>
        <option value="VZ 314: Parken mit KFZ Nur Elektrofahrzeuge">VZ 314: Parken mit KFZ Nur Elektrofahrzeuge</option>
        <option value="VZ 325: Parken außerhalb gekennzeichneten Flächen">VZ 325: Parken außerhalb gekennzeichneten Flächen</option>
        <option value="VZ 325: schneller als Schrittgeschwindigkeit">VZ 325: schneller als Schrittgeschwindigkeit</option>
        <option value="Wegwerfen oder Liegenlassen gefährlicher Gegenstände">Wegwerfen oder Liegenlassen gefährlicher Gegenstände</option>
        <option value="Wegwerfen oder Liegenlassen von Abfällen">Wegwerfen oder Liegenlassen von Abfällen</option>
        <option value="Wegwerfen oder Liegenlassen von Zigarettenkippe">Wegwerfen oder Liegenlassen von Zigarettenkippe</option>
        <option value="X Personen an der Örtlichkeit, keine Beanstandungen">X Personen an der Örtlichkeit, keine Beanstandungen</option>
        <option value="Zugspitzstraße 104 (Neuer Ostfriedhof)">Zugspitzstraße 104 (Neuer Ostfriedhof)</option>
    </select>

    <label for="details">Zusätzliche Details / Bemerkungen</label>
    <textarea id="details" rows="4" placeholder="Hier weitere Infos eintragen..."></textarea>

    <button onclick="sendMail()">Bericht erstellen & senden</button>
    
    <div class="footer-text">Stadt Augsburg - Ordnungsdienst</div>
</div>

<script>
    function sendMail() {
        const email1 = "Kevin.woelki@augsburg.de";
        const email2 = "kevinworlki@outlook.de";
        
        const standort = document.getElementById('standort').value || "Nicht angegeben";
        const feststellung = document.getElementById('feststellung').value || "Keine Feststellung ausgewählt";
        const details = document.getElementById('details').value || "Keine weiteren Details";

        // Betreffzeile
        const subject = "Einsatzbericht: " + standort;

        // Nachrichtentext
        const body = "Guten Tag,\n\nanbei der aktuelle Einsatzbericht:\n\n" +
                     "STANDORT: " + standort + "\n" +
                     "FESTSTELLUNG: " + feststellung + "\n" +
                     "DETAILS: " + details + "\n\n" +
                     "Erstellt am: " + new Date().toLocaleString('de-DE');

        // Mailto Link generieren
        // Hinweis: Outlook und manche Mail-Apps nutzen Komma, manche Semikolon. Semikolon ist Standard für Windows-Outlook.
        const mailLink = "mailto:" + email1 + ";" + email2 + 
                         "?subject=" + encodeURIComponent(subject) + 
                         "&body=" + encodeURIComponent(body);
        
        window.location.href = mailLink;
    }
</script>

</body>
</html>
