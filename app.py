# --- 2. OPTIMIERTES KONTRAST-DESIGN (KLARES SCHWARZ/WEISS) ---
st.markdown("""
    <style>
    /* Grundhintergrund der App auf tiefschwarz */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Globale Textfarbe: Erzwingt Reinweiß für alle Standard-Texte */
    .stMarkdown, p, span, label, li, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    /* Spezielle Korrektur für Formular-Labels (Eingabefelder Beschriftung) */
    .stWidget label p {
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    /* EINGABEFELDER: Dunkler Hintergrund mit hellem Rahmen für Sichtbarkeit */
    input, textarea, [data-baseweb="input"], [data-baseweb="select"] > div {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important; /* Weißer Rahmen für Fokus */
    }

    /* Fix für Text in Eingabefeldern (verhindert graue Schrift auf dunklem Grund) */
    input {
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Buttons: Blau mit weißer Schrift für primäre Aktionen */
    .stButton>button {
        background-color: #004b95 !important;
        color: white !important;
        border: 1px solid #ffffff !important;
        width: 100%;
    }

    /* Expander / Klappmenü Design */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        border: 1px solid #555 !important;
    }
    .streamlit-expanderHeader p {
        color: #ffffff !important;
    }

    /* Archiv-Karten Design */
    .report-card { 
        background-color: #111111; 
        border-radius: 10px; 
        padding: 20px; 
        border: 1px solid #ffffff; /* Weißer Rand zur Abgrenzung */
        margin-bottom: 15px; 
    }

    /* Infoboxen im Archiv */
    .metric-box {
        background-color: #222222;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #444444;
        color: #ffffff !important;
        margin-bottom: 5px;
    }

    /* Checkbox-Texte explizit weiß */
    .stCheckbox label span {
        color: #ffffff !important;
    }

    /* Header & Footer ausblenden */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
