# --- 6. HAUPTSEITE ---
st.title("📋 Einsatzbericht")

# GPS und andere Daten...

with st.expander("➕ NEUEN EINSATZBERICHT ERSTELLEN", expanded=True):
    # 1. Zuerst die Kräfte-Auswahl (AUSSERHALB der Form, damit sie sofort reagiert)
    st.subheader("👮 Kräfte vor Ort")
    k_col1, k_col2 = st.columns([1, 2])
    
    with k_col1:
        st.checkbox("🚓 KOD", value=True, disabled=True)
        pol_check = st.checkbox("🚔 Polizei")
        rtw_check = st.checkbox("🚑 Rettungsdienst")
        fw_check = st.checkbox("🚒 Feuerwehr")
    
    with k_col2:
        funkstreife = ""
        if pol_check:
            # Jetzt erscheint dieses Feld sofort, wenn 'Polizei' angeklickt wird!
            funkstreife = st.text_input("Funkstreife", placeholder="z.B. Augsburg 12/1")

    # 2. Jetzt das eigentliche Formular für den Rest
    with st.form("bericht_form", clear_on_submit=True):
        st.subheader("📍 Ort & Zeit")
        c1, c2, c3, c4 = st.columns(4)
        datum = c1.date_input("📅 Datum")
        t_start = c2.time_input("🕒 Beginn")
        t_end = c3.time_input("🕒 Ende")
        az = c4.text_input("📂 Aktenzeichen (AZ)")
        
        o1, o2 = st.columns([3, 1])
        ort = o1.selectbox("🗺️ Einsatzort", [None] + STRASSEN_AUGSBURG)
        hnr = o2.text_input("Nr.")

        st.divider()
        st.subheader("📝 Sachverhalt")
        vorlage = st.selectbox("📑 Feststellung (Vorlage)", [None] + FESTSTELLUNGEN)
        inhalt = st.text_area("Sachverhalt", value=vorlage if vorlage else "", height=150)
        beteiligte = st.text_input("👥 Beteiligte / Zeugen")
        foto = st.file_uploader("📸 Beweisfoto", type=["jpg", "jpeg", "png"])

        if st.form_submit_button("✅ Bericht speichern"):
            # Hier greifen wir auf die Variablen von oben zu (pol_check, funkstreife, etc.)
            k_final = ["KOD"]
            if pol_check:
                pol_eintrag = f"Polizei ({funkstreife})" if funkstreife else "Polizei"
                k_final.append(pol_eintrag)
            if rtw_check: k_final.append("Rettungsdienst")
            if fw_check: k_final.append("Feuerwehr")
            
            # ... Rest der Speicherlogik (wie im vorherigen Code) ...
