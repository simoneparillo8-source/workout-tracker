import streamlit as st
import pandas as pd
import json
import os

DATA_DIR = "data"

def load_user_data(user):
    path = os.path.join(DATA_DIR, f"{user}.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return []

def save_user_data(user, data):
    path = os.path.join(DATA_DIR, f"{user}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

st.set_page_config(page_title="Workout Tracker", layout="wide")

st.title("🏋️ Workout Tracker")

user = st.selectbox("Seleziona atleta:", ["simone", "antonio"])

motivazioni = [
    "Spingi un po’ di più, è così che cresci.",
    "Nessuna scusa: solo miglioramenti.",
    "Oggi meglio di ieri.",
    "Se non tremi, non stai lavorando abbastanza."
]

st.write(f"### 💬 {motivazioni[len(user) % len(motivazioni)]}")

data = load_user_data(user)
df = pd.DataFrame(data)
edited_df = st.data_editor(df, num_rows="dynamic")

if st.button("💾 Salva modifiche"):
    save_user_data(user, edited_df.to_dict(orient="records"))
    st.success("Dati salvati con successo!")
