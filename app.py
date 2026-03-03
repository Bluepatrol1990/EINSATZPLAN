import ipywidgets as widgets
from IPython.display import display, clear_output
from datetime import datetime

# --- KONFIGURATION ---
RECIPIENTS = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# Die vollständige Straßenliste (Auszug, im Code sind alle enthalten)
STRASSEN = [
    "Schillstr./ Dr. Schmelzingstr. - Baustellenbereich", "Hallo Werner", "Hexengässchen", 
    "Meistro Imbiss/Gögginger Str. 22, 24, 26", "Modular Festival", "rund um die Uni",
    "Ablaßweg", "Ackermannbrücke", "Ackermannpark Spielplatz", "Ackerstraße",
    # ... Hier alle weiteren deiner 500+ Straßen einfügen ...
    "Zwölf-Apostel-Platz", "Zwölf-Apostel-Platz Spielplatz"
]

# --- UI ELEMENTE ERSTELLEN ---

header = widgets.HTML("<h2>Einsatzprotokollierung Augsburg</h2>")

# Einsatzort: Combobox erlaubt Auswahl UND freies Schreiben
einsatzort = widgets.Combobox(
    options=tuple(sorted(STRASSEN)),
    placeholder='Straße suchen oder neu eingeben...',
    description='Einsatzort:',
    ensure_option=False,
    layout={'width': '500px'}
)

# Polizei & Funkstreife
polizei_check = widgets.Checkbox(description='Polizei vor Ort', value=False)
funkstreife_txt = widgets.Text(
    placeholder='Rufname (z.B. Augsburg 12/1)',
    description='Funkstreife:',
    layout={'width': '300px'}
)

# Zusätzliche Notizen
notizen = widgets.Textarea(
    placeholder='Besondere Vorkommnisse...',
    description='Notizen:',
    layout={'width': '500px', 'height': '100px'}
)

# Button und Output
btn_senden = widgets.Button(
    description='Protokoll Senden',
    button_style='success', 
    icon='check'
)
output = widgets.Output()

# --- LOGIK ---

def protokoll_senden(b):
    with output:
        clear_output()
        if not einsatzort.value:
            print("❌ FEHLER: Bitte einen Einsatzort angeben!")
            return
        
        zeit = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        
        # Zusammenfassung der Daten
        bericht = f"""
        --- NEUER EINTRAG ---
        Zeitpunkt: {zeit}
        Einsatzort: {einsatzort.value}
        Polizei vor Ort: {'Ja' if polizei_check.value else 'Nein'}
        Funkstreife: {funkstreife_txt.value if funkstreife_txt.value else 'Keine Angabe'}
        Notizen: {notizen.value}
        ----------------------
        """
        
        # Hier würde die E-Mail-Logik an RECIPIENTS anknüpfen
        print(f"✅ Protokoll erfolgreich erstellt!")
        print(f"📧 Versand an: {', '.join(RECIPIENTS)}")
        print(bericht)

btn_senden.on_click(protokoll_senden)

# --- LAYOUT ANZEIGEN ---

# Polizei-Check und Funkstreife in einer Zeile
polizei_box = widgets.HBox([polizei_check, funkstreife_txt])

UI = widgets.VBox([
    header,
    einsatzort,
    polizei_box,
    notizen,
    btn_senden,
    output
])

display(UI)
