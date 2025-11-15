import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from datetime import datetime

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Workout Tracker PRO", page_icon="🏋️", layout="wide")
DATA_DIR = "data"
USERS = ["simone", "antonio"]

# ensure data dir
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USER_FILES = {u: os.path.join(DATA_DIR, f"{u}.json") for u in USERS}

def load_user_data(user):
    if not os.path.exists(USER_FILES[user]):
        save_user_data(user, [])
    with open(USER_FILES[user], "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_user_data(user, data):
    with open(USER_FILES[user], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_session(user):
    # append current exercises to history file user_history.json
    history_file = os.path.join(DATA_DIR, f"{user}_history.json")
    now = datetime.now().isoformat()
    exercises = load_user_data(user)
    records = []
    for ex in exercises:
        records.append({
            "date": now,
            "esercizio": ex.get("esercizio"),
            "peso": ex.get("peso"),
            "ripetizioni": ex.get("ripetizioni"),
            "serie": ex.get("serie")
        })
    # save
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            try:
                hist = json.load(f)
            except:
                hist = []
    else:
        hist = []
    hist.extend(records)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

def load_history(user):
    history_file = os.path.join(DATA_DIR, f"{user}_history.json")
    if not os.path.exists(history_file):
        return []
    with open(history_file, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

# -----------------------
# UI - Header / Theme
# -----------------------
st.markdown("""<style>
.stApp { background-color: #0b0b0b; color: #e6eef8; }
.big-title { color: #00ffc6; font-weight:700; }
.muted { color: #9aa6b2; }
.card { background: #0f1720; padding:10px; border-radius:8px; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🏋️ Workout Tracker PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="muted">Traccia allenamenti, registra sessioni e visualizza progressi — versione PRO (no login).</div>', unsafe_allow_html=True)

# -----------------------
# Sidebar - user selection + actions
# -----------------------
st.sidebar.header("Controlli")
selected_user = st.sidebar.selectbox("Seleziona atleta", USERS)
st.sidebar.markdown("---")
if st.sidebar.button("Registra sessione (log)"):
    log_session(selected_user)
    st.sidebar.success("Sessione registrata nello storico")

if st.sidebar.button("Esporta CSV (allenamenti)"):
    df_export = pd.DataFrame(load_user_data(selected_user))
    st.sidebar.download_button("Download CSV", df_export.to_csv(index=False).encode('utf-8'), file_name=f"{selected_user}_workouts.csv")

st.sidebar.markdown("---")
st.sidebar.subheader("Impostazioni")
show_history = st.sidebar.checkbox("Mostra storico", value=True)
show_progress_chart = st.sidebar.checkbox("Mostra grafico progressione", value=True)

# -----------------------
# Main - Load data
# -----------------------
user_data = load_user_data(selected_user)
df = pd.DataFrame(user_data)

# normalize empty df
if df.empty:
    df = pd.DataFrame(columns=["esercizio","peso","ripetizioni","serie","giorno"])

st.subheader(f"Esercizi — {selected_user.capitalize()}")

# editable table
edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# Save button
col_save, col_add, col_del = st.columns([1,1,1])
with col_save:
    if st.button("💾 Salva modifiche"):
        save_user_data(selected_user, edited.to_dict(orient="records"))
        st.success("Dati salvati")

# Quick-add new exercise
with col_add:
    with st.form("add_form", clear_on_submit=True):
        n1, n2, n3, n4, n5 = st.columns([3,1,1,1,1])
        with n1:
            new_name = st.text_input("Esercizio", key="new_name")
        with n2:
            new_peso = st.number_input("Peso (kg)", min_value=0, value=20, key="new_peso")
        with n3:
            new_reps = st.number_input("Ripetizioni", min_value=0, value=8, key="new_reps")
        with n4:
            new_sets = st.number_input("Serie", min_value=0, value=3, key="new_sets")
        with n5:
            new_day = st.selectbox("Giorno", ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"], key="new_day")
        add = st.form_submit_button("Aggiungi")
        if add:
            row = {"esercizio": new_name, "peso": new_peso, "ripetizioni": new_reps, "serie": new_sets, "giorno": new_day}
            user_data.append(row)
            save_user_data(selected_user, user_data)
            st.success("Esercizio aggiunto")
            st.rerun()


# Delete option
with col_del:
    if not df.empty:
        to_remove = st.selectbox("Rimuovi esercizio", df["esercizio"].tolist(), key="del_select")
        if st.button("Elimina"):
            df2 = df[df["esercizio"] != to_remove]
            save_user_data(selected_user, df2.to_dict(orient="records"))
            st.success("Eliminato")
            st.experimental_rerun()

st.markdown("---")

# -----------------------
# Quick sliders for weights
# -----------------------
st.subheader("Regola velocemente i pesi")
if not df.empty:
    cols = st.columns(2)
    for i, row in df.iterrows():
        c = cols[i % 2]
        with c:
            neww = st.slider(f"{row['esercizio']} ({row.get('giorno','')})", 0, 300, int(row.get('peso',0)), key=f"w_{i}")
            df.at[i, "peso"] = neww
    save_user_data(selected_user, df.to_dict(orient='records'))

st.markdown("---")

# -----------------------
# History and charts
# -----------------------
if show_history:
    st.subheader("Storico allenamenti")
    history = load_history(selected_user)
    if history:
        hdf = pd.DataFrame(history)
        st.dataframe(hdf.sort_values('date', ascending=False).head(200), use_container_width=True)
    else:
        st.info("Nessuno storico registrato. Usa 'Registra sessione (log)'.")

if show_progress_chart:
    st.subheader("Grafico progressione peso per esercizio")
    history = load_history(selected_user)
    if history:
        hdf = pd.DataFrame(history)
        # prepare chart for selected exercise
        exercises = sorted(hdf['esercizio'].unique())
        sel = st.selectbox('Scegli esercizio per grafico', exercises)
        plot_df = hdf[hdf['esercizio'] == sel].copy()
        plot_df['date_dt'] = pd.to_datetime(plot_df['date'])
        plot_df = plot_df.sort_values('date_dt')
        fig = px.line(plot_df, x='date_dt', y='peso', markers=True, title=f'Progressione {sel}')
        fig.update_layout(paper_bgcolor='#0b0b0b', plot_bgcolor='#0f1416', font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Nessuno storico per generare il grafico.')

# footer
st.markdown("---")
st.caption("Workout Tracker PRO — pronto per GitHub / Streamlit Cloud")
