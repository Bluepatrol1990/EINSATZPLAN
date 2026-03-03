# --- LOGIN BEREICH ---
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    # Geänderter Name beim Login
    st.title("🚓 Dienst Login") 
    pw = st.text_input("Dienst-Passwort eingeben", type="password")
    if st.button("Anmelden"):
        if pw == DIENST_PW: 
            st.session_state["auth"] = True
            st.rerun()
        else: 
            st.error("Falsches Passwort")
    st.stop()

# --- FORMULAR MIT STRASSEN-VORAUSWAHL ---
with st.expander("➕ NEUEN BERICHT SCHREIBEN", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        c1, c2, c3 = st.columns([1,1,2])
        d = c1.date_input("Datum")
        t = c2.time_input("Zeit")
        gps_field = c3.text_input("GPS-Koordinaten", value=gps_ready, disabled=True)
        
        o1, o2, o3 = st.columns([3,1,2])
        
        # Hier ist die Vorwahl der Augsburger Straßen
        ort = o1.selectbox(
            "Straße / Ort wählen", 
            options=STRASSEN_AUGSBURG, 
            index=None, 
            placeholder="Straße suchen..."
        )
        
        hsnr = o2.text_input("Nr.")
        az = o3.text_input("AZ")
        
        # ... Rest wie gehabt (Textbausteine, Bericht, Foto)
