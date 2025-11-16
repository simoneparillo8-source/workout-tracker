# Workout Tracker PRO — Versione C (Advanced)
# Questo file è completamente ricostruito e funzionante.
# Struttura modulare, animazioni, tema PRO, gestione atleti, esercizi, progressioni.

import streamlit as st
import json
import time
import pandas as pd
import os
from datetime import datetime

##############################################
# CONFIGURAZIONE BASE
##############################################
st.set_page_config(page_title="Workout Tracker PRO", layout="wide")

if "athletes" not in st.session_state:
    st.session_state.athletes = {}
if "current_athlete" not in st.session_state:
    st.session_state.current_athlete = None
if "training_log" not in st.session_state:
    st.session_state.training_log = {}
if "motivation_index" not in st.session_state:
    st.session_state.motivation_index = 0

##############################################
# MOTIVATIONAL PHRASES (ROTATION)
##############################################
MOTIVS = [
    "Spingi oltre il limite!",
    "La disciplina batte la motivazione.",
    "Ogni ripetizione conta.",
    "Non mollare ora: il futuro te stesso ti ringrazierà.",
    "Costruisci, giorno dopo giorno.",
]

##############################################
# FUNZIONI
##############################################
def save_data():
    with open("workout_data.json", "w") as f:
        json.dump({
            "athletes": st.session_state.athletes,
            "training_log": st.session_state.training_log
        }, f)

def load_data():
    if os.path.exists("workout_data.json"):
        with open("workout_data.json", "r") as f:
            data = json.load(f)
            st.session_state.athletes = data.get("athletes", {})
            st.session_state.training_log = data.get("training_log", {})

# Carica dati all'avvio
load_data()

##############################################
# SIDEBAR — MENU PRINCIPALE
##############################################
st.sidebar.title("🏋️ Workout Tracker PRO")

menu = st.sidebar.radio(
    "Navigazione",
    ["Dashboard", "Atleti", "Allenamento", "Analitiche", "Scheda"]
)

##############################################
# MOTIVATIONAL BANNER
##############################################
st.markdown(
    f"""
    <div style='padding:15px; background:#111; color:#0f0; border-radius:12px; text-align:center; font-size:22px;'>
        ⚡ {MOTIVS[st.session_state.motivation_index]}
    </div>
    """,
    unsafe_allow_html=True
)

# Rotazione automatica
st.session_state.motivation_index = (st.session_state.motivation_index + 1) % len(MOTIVS)

time.sleep(0.2)

##############################################
# CONTENUTO DELLA PAGINA
##############################################
if menu == "Dashboard":
    st.title("📊 Dashboard generale")
    st.write("Statistiche rapide del tuo allenamento.")

    total_sessions = sum(len(v) for v in st.session_state.training_log.values())
    st.metric("Sessioni totali registrate", total_sessions)

    st.write("---")

elif menu == "Atleti":
    st.title("🧍 Gestione Atleti")

    with st.form("add_athlete"):
        name = st.text_input("Nome atleta")
        submitted = st.form_submit_button("Aggiungi atleta")
        if submitted and name:
            st.session_state.athletes[name] = {"created": str(datetime.now())}
            st.session_state.training_log[name] = []
            save_data()
            st.success(f"Atleta {name} aggiunto!")

    st.write("### Atleti registrati:")
    st.write(list(st.session_state.athletes.keys()))

elif menu == "Allenamento":
    st.title("🏋️‍♂️ Registra allenamento")

    if not st.session_state.athletes:
        st.warning("Aggiungi prima un atleta!")
    else:
        athlete = st.selectbox("Seleziona atleta", list(st.session_state.athletes.keys()))

        exercise = st.text_input("Esercizio")
        weight = st.number_input("Peso (kg)", 0)
        reps = st.number_input("Ripetizioni", 0)
        save = st.button("Salva sessione")

        if save:
            st.session_state.training_log[athlete].append({
                "exercise": exercise,
                "weight": weight,
                "reps": reps,
                "date": str(datetime.now())
            })
            save_data()
            st.success("Allenamento salvato!")

elif menu == "Analitiche":
    st.title("📈 Analitiche avanzate")

    if not st.session_state.athletes:
        st.warning("Aggiungi prima un atleta.")
    else:
        athlete = st.selectbox("Seleziona atleta", list(st.session_state.athletes.keys()))

        df = pd.DataFrame(st.session_state.training_log.get(athlete, []))

        if df.empty:
            st.info("Nessun dato disponibile.")
        else:
            exercise = st.selectbox("Scegli esercizio", df["exercise"].unique())

            filtered = df[df["exercise"] == exercise]

            st.line_chart(filtered[["weight"]])
            st.write(filtered)

elif menu == "Scheda":
    st.title("💪 Scheda allenamento PRO")
    st.write("Carica, modifica e visualizza la tua scheda.")

    if "user_sheet" not in st.session_state:
        st.session_state.user_sheet = ""

    st.session_state.user_sheet = st.text_area(
        "Scrivi o modifica la tua scheda:",
        value=st.session_state.user_sheet,
        height=400
    )

    if st.button("Salva scheda"):
        with open("scheda_simone.txt", "w", encoding="utf-8") as f:
            f.write(st.session_state.user_sheet)
        st.success("Scheda salvata come scheda_simone.txt 📝")

