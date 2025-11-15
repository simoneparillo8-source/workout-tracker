import streamlit as st
import json
import os
from datetime import datetime
import random

# ------------------------------------------------------------
# CONFIGURAZIONE UI
# ------------------------------------------------------------
st.set_page_config(
    page_title="Workout Tracker PRO",
    page_icon="💪",
    layout="wide"
)

# ------------------------------------------------------------
# TEMA PERSONALIZZATO
# ------------------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #0d0d0d;
    color: #e6e6e6;
}

/* Bottoni tondi atleta */
.avatar-btn {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    border: 3px solid #00eaff;
    cursor: pointer;
    margin-right: 20px;
}

.avatar-selected {
    border-color: #9d00ff !important;
    transform: scale(1.05);
}

/* Tabelle più moderne */
thead tr th {
    background-color: #1f1f1f !important;
    color: white !important;
}

tbody tr td {
    background-color: #141414 !important;
}

/* Titoli */
h1, h2, h3 {
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# FILES E SALVATAGGI
# ------------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

USERS = ["Simone", "Antonio"]


def load_user_data(user):
    path = f"{DATA_DIR}/{user.lower()}.json"
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f)
    with open(path, "r") as f:
        return json.load(f)


def save_user_data(user, data):
    with open(f"{DATA_DIR}/{user.lower()}.json", "w") as f:
        json.dump(data, f, indent=4)


# ------------------------------------------------------------
# ESERCIZI PRECARICATI
# ------------------------------------------------------------
PRELOADED_EXERCISES = {
    "Petto": ["Panca Piana", "Panca Inclinata", "Croci ai Cavi"],
    "Schiena": ["Lat Machine", "Rematore", "Trazioni"],
    "Spalle": ["Shoulder Press", "Alzate Laterali"],
    "Bicipiti": ["Curl Bilanciere", "Curl Manubri"],
    "Tricipiti": ["French Press", "Pushdown"],
    "Gambe": ["Squat", "Leg Press", "Affondi", "Leg Extension"],
    "Addome": ["Crunch", "Plank", "Russian Twist"]
}

DAYS = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

MOTIVATION = [
    "Spingi oggi, vinci domani.",
    "Ogni rep ti avvicina al tuo obiettivo.",
    "Disciplina batte motivazione.",
    "Non fermarti quando sei stanco, fermati quando hai finito.",
    "La versione migliore di te stesso ti aspetta."
]

# ------------------------------------------------------------
# SCELTA ATLETA — AVATAR TONDI CLICCABILI
# ------------------------------------------------------------
colA, colB = st.columns([1, 8])
with colA:
    st.write("### Seleziona Atleta:")

with colB:
    c1, c2 = st.columns([1, 1])

    # Avatar Simone
    with c1:
        simone_clicked = st.button("",
            key="simone_btn",
            help="Seleziona Simone"
        )
        st.markdown(
            f"""
            <div>
                <img src="https://via.placeholder.com/90x90.png?text=S" 
                class="avatar-btn {'avatar-selected' if st.session_state.get('user', 'Simone')=='Simone' else ''}">
            </div>
            """,
            unsafe_allow_html=True
        )

    # Avatar Antonio
    with c2:
        antonio_clicked = st.button("",
            key="antonio_btn",
            help="Seleziona Antonio"
        )
        st.markdown(
            f"""
            <div>
                <img src="https://via.placeholder.com/90x90.png?text=A" 
                class="avatar-btn {'avatar-selected' if st.session_state.get('user', 'Simone')=='Antonio' else ''}">
            </div>
            """,
            unsafe_allow_html=True
        )

if simone_clicked:
    st.session_state["user"] = "Simone"
    st.rerun()

if antonio_clicked:
    st.session_state["user"] = "Antonio"
    st.rerun()

user = st.session_state.get("user", "Simone")

# ------------------------------------------------------------
# FRASE MOTIVAZIONALE
# ------------------------------------------------------------
st.markdown(f"### 💬 Motivazione del giorno: *{random.choice(MOTIVATION)}*")

# ------------------------------------------------------------
# CARICA DATI UTENTE
# ------------------------------------------------------------
data = load_user_data(user)

st.write(f"## 💪 Workout Tracker — {user}")

# ------------------------------------------------------------
# FORM AGGIUNTA ESERCIZIO
# ------------------------------------------------------------
with st.expander("➕ Aggiungi esercizio"):
    group = st.selectbox("Gruppo muscolare", list(PRELOADED_EXERCISES.keys()))
    exercise = st.selectbox("Esercizio", PRELOADED_EXERCISES[group])
    day = st.selectbox("Giorno", DAYS)
    peso = st.slider("Peso (kg)", 0, 200, 30)
    reps = st.number_input("Ripetizioni", 1, 50, 10)
    series = st.number_input("Serie", 1, 10, 3)

    if st.button("Aggiungi"):
        data.append({
            "group": group,
            "exercise": exercise,
            "day": day,
            "peso": peso,
            "reps": reps,
            "series": series,
            "timestamp": datetime.now().isoformat()
        })
        save_user_data(user, data)
        st.success("Esercizio aggiunto!")
        st.rerun()

# ------------------------------------------------------------
# MOSTRA TABELLA
# ------------------------------------------------------------
st.write("## 📋 I tuoi esercizi")

if len(data) == 0:
    st.warning("Nessun esercizio registrato.")
else:
    for i, row in enumerate(data):
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2,2,1,1,1,1])

            col1.write(f"**{row['group']}**")
            col2.write(row["exercise"])
            new_peso = col3.slider("Kg", 0, 200, row["peso"], key=f"peso{i}")
            new_reps = col4.number_input("Reps", 1, 50, row["reps"], key=f"reps{i}")
            new_series = col5.number_input("Serie", 1, 10, row["series"], key=f"series{i}")

            if col6.button("❌", key=f"del{i}"):
                data.pop(i)
                save_user_data(user, data)
                st.rerun()

            # Salva modifiche
            row["peso"] = new_peso
            row["reps"] = new_reps
            row["series"] = new_series

    save_user_data(user, data)
