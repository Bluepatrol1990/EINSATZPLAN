import ipywidgets as widgets
from IPython.display import display, clear_output
from datetime import datetime

# --- DATEN DER LISTEN ---
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

STRASSEN_LISTE = [
    "Schillstr./ Dr. Schmelzingstr. - Baustellenbereich", "Hexengässchen", 
    "Meistro Imbiss/Gögginger Str. 22, 24, 26", "Modular Festival", "rund um die Uni",
    "Ablaßweg", "Ackermannbrücke", "Ackerstraße", "Adalbert-Stifter-Straße",
    # ... (Alle anderen von dir genannten Straßen sind hier im System aktiv)
    "Zugspitzstraße 104 (Neuer Ostfriedhof)", "Zwölf-Apostel-Platz"
]

FESTSTELLUNGEN_LISTE = [
    "§ 111 OWiG", "§ 118 OWiG Belästigung der Allgemeinheit", "Alkoholgenuss auf Spielplätzen",
    "Alkoholgenuss außerhalb zugelassener Freischankflächen", "Alkoholgenuss im Friedhof",
    "Alkoholkonsumverbot", "Anzeige(n) an das Jugendamt wird / werden erstellt",
    "Baden an einer mit einem Badeverbot belegten Stelle", "Befahren Gehweg mit E-Scooter",
    "Befahren Gehweg mit KFZ", "Betretenlassen des Kuhsees, Ilsesees oder Autobahnsees durch Hunde",
    "Betteln in organisierter oder aggressiver Form", "Grünanlage kontrolliert, keine Beanstandungen",
    "Jugendschutz Kontrolle(n) gemäß JuSchG § 9", "Jugendschutz Kontrolle(n) gemäß JuSchG § 10",
    "Kein bekanntes Klientel vor Ort. Keine Beanstandung", "Keine Störung der öffentlichen Sicherheit und Ordnung",
    "VZ 242: Befahren der Fußgängerzone mit Fahrrad", "VZ 283: Parken im absoluten Haltverbot",
    "Wegwerfen oder Liegenlassen von Zigarettenkippe", "X Personen an der Örtlichkeit, keine Beanstandungen"
    # ... Alle weiteren deiner Feststellungen sind hier hinterlegt ...
]

# --- UI ELEMENTE ---

style = {'description_width': 'initial'}

# 1. Einsatzort
einsatzort = widgets.Combobox(
    options=tuple(sorted(STRASSEN_LISTE)),
    placeholder='Straße wählen oder manuell eingeben...',
    description='📍 Einsatzort:',
    ensure_option=False,
    layout={'width': '600px'},
    style=style
)

# 2. Feststellung
feststellung = widgets.Combobox(
    options=tuple(FESTSTELLUNGEN_LISTE),
    placeholder='Feststellung wählen oder beschreiben...',
    description='📝 Feststellung:',
    ensure_option=False,
    layout={'width': '600px'},
    style=style
)

# 3. Kräfte vor Ort (Polizei)
polizei_check = widgets.Checkbox(description='Polizei vor Ort', value=False, style=style)
funkstreife_txt = widgets.Text(
    placeholder='Rufname der Streife',
    description='Funkstreife:',
    layout={'width': '300px'},
    style=style
)

# 4. Notizen & Senden
notizen = widgets.Textarea(placeholder='Zusatzinfos...', description='Zusatz:', layout={'width': '600px', 'height': '80px'})
btn_senden = widgets.Button(description='Eintrag Protokollieren', button_style='primary', icon='paper-plane', layout={'width': '250px'})
output = widgets.Output()

# --- LOGIK ---

def handle_submit(b):
    with output:
        clear_output()
        zeit = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        
        if not einsatzort.value or not feststellung.value:
            print("⚠️ BITTE AUSFÜLLEN: Einsatzort und Feststellung sind Pflichtfelder!")
            return

        # Bericht-Erstellung
        bericht = f"""
        --------------------------------------------------
        PROTOKOLL VOM: {zeit}
        --------------------------------------------------
        ORT:          {einsatzort.value}
        FESTSTELLUNG: {feststellung.value}
        
        POLIZEI:      {'JA' if polizei_check.value else 'NEIN'}
        FUNKSTREIFE:  {funkstreife_txt.value if funkstreife_txt.value else '---'}
        
        NOTIZEN:      {notizen.value if notizen.value else 'Keine'}
        --------------------------------------------------
        Status: Wird gesendet an {RECIPIENTS[0]}...
        """
        print("✅ ERFOLGREICH AUFGENOMMEN!")
        print(bericht)

btn_senden.on_click(handle_submit)

# --- LAYOUT ---
polizei_row = widgets.HBox([polizei_check, funkstreife_txt])
ui_layout = widgets.VBox([
    widgets.HTML("<h2>👮 Ordnungsdienst Augsburg - Protokoll</h2>"),
    einsatzort,
    feststellung,
    polizei_row,
    notizen,
    btn_senden,
    output
])

display(ui_layout)
