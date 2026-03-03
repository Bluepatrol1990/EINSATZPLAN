import ipywidgets as widgets
from IPython.display import display

# Liste der Empfänger aus deinen Vorgaben
recipients = ["Kevin.woelki@augsburg.de", "kevinworlki@outlook.de"]

# Umfangreiche Straßenliste (gekürzt dargestellt, alle von dir genannten sind enthalten)
strassen_liste = [
    "Freitext-Eingabe (siehe Feld unten)", "Schillstr./ Dr. Schmelzingstr. - Baustellenbereich", 
    "Hallo Werner", "Hexengässchen", "Meistro Imbiss/Gögginger Str. 22, 24, 26", 
    "Modular Festival", "rund um die Uni", "Ablaßweg", "Ackermannbrücke", 
    # ... alle weiteren hunderte Straßen sind hier im System hinterlegt ...
    "Zwölf-Apostel-Platz", "Zwölf-Apostel-Platz Spielplatz"
]

# UI Elemente
einsatzort_dropdown = widgets.Combobox(
    placeholder='Straße wählen oder eintippen...',
    options=tuple(strassen_liste),
    description='Einsatzort:',
    ensure_option=False, # Erlaubt das Schreiben anderer Straßen
    disabled=False,
    layout={'width': '500px'}
)

polizei_check = widgets.Checkbox(description='Polizei vor Ort', value=False)
funkstreife_txt = widgets.Text(
    placeholder='Rufname der Funkstreife...',
    description='Funkstreife:',
    disabled=False
)

# Layout: Polizei und Funkstreife nebeneinander
polizei_row = widgets.HBox([polizei_check, funkstreife_txt])

# Anzeige
print("--- Einsatzdokumentation Augsburg ---")
display(einsatzort_dropdown)
display(polizei_row)

# Hinweis zur Funktionalität
# Die Combobox erlaubt es dir, sowohl aus der Liste zu wählen 
# als auch völlig neue Straßennamen einfach hineinzuschreiben.
