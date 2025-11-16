# app.py — Workout Tracker PRO (Animated Neon, local-ready)
import streamlit as st
import json
import os
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any
from io import BytesIO

import pandas as pd
import plotly.express as px
from PIL import Image

# ------------- Page config -------------
st.set_page_config(page_title="Workout Tracker PRO", page_icon="🏋️", layout="wide")

# ------------- Paths & ensures -------------
DATA_DIR = "data"
AVATAR_DIR = os.path.join(DATA_DIR, "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)

ATHLETES_FILE = os.path.join(DATA_DIR, "athletes.json")
EXERCISES_FILE = os.path.join(DATA_DIR, "exercises.json")  # per esercizi preloaded o custom
# workouts and history files per-atleta are created on demand

def ensure_file(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)

ensure_file(ATHLETES_FILE, ["Simone", "Antonio"])
ensure_file(EXERCISES_FILE, {
    "Panca piana": "Petto",
    "Chest press": "Petto",
    "Squat": "Gambe",
    "Pulldown": "Dorso",
    "Rematore": "Dorso",
    "Military press": "Spalle"
})

# ------------- Helpers -------------
def load_json(path, fallback=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return fallback

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def workout_file(a: str) -> str:
    return os.path.join(DATA_DIR, f"{a.lower()}_workouts.json")

def history_file(a: str) -> str:
    return os.path.join(DATA_DIR, f"{a.lower()}_history.json")

def plan_file(a: str) -> str:
    return os.path.join(DATA_DIR, f"{a.lower()}_plan.txt")

def ensure_athlete_files(a: str):
    ensure_file(workout_file(a), [])
    ensure_file(history_file(a), [])
    ensure_file(plan_file(a), "")

def avatar_path(name: str) -> str:
    safe = name.strip().lower().replace(" ", "_")
    return os.path.join(AVATAR_DIR, f"{safe}.png")

def avatar_exists(name: str) -> bool:
    return os.path.exists(avatar_path(name))

def save_avatar(name: str, uploaded) -> str:
    # convert to PNG and save with Pillow for consistency
    try:
        img = Image.open(uploaded)
        img = img.convert("RGBA")
        p = avatar_path(name)
        img.thumbnail((512, 512))  # limit size
        img.save(p, format="PNG")
        return p
    except Exception as e:
        st.warning(f"Errore salvataggio avatar: {e}")
        return ""

# ------------- Load persisted data -------------
ATHLETES = load_json(ATHLETES_FILE, ["Simone", "Antonio"])
EXERCISES = load_json(EXERCISES_FILE, {})
# ensure session_state keys
if "athlete" not in st.session_state:
    st.session_state.athlete = ATHLETES[0] if ATHLETES else None
if "show_plan_editor" not in st.session_state:
    st.session_state.show_plan_editor = False

# ------------- CSS / Neon style -------------
st.markdown(
    """
    <style>
    :root {
      --bg1: #04020a;
      --card: rgba(255,255,255,0.02);
      --accent: linear-gradient(90deg,#9b4dff,#6fc3ff);
      --muted: #9aa6b2;
    }
    .stApp { background: linear-gradient(135deg,#10001a,#04102a); color:#eaf0ff; font-family: Inter, sans-serif; }
    .header { padding:12px; border-radius:10px; margin-bottom:12px; background: linear-gradient(90deg, rgba(27,6,47,0.6), rgba(6,16,42,0.6)); box-shadow:0 10px 30px rgba(0,0,0,0.6); }
    .avatar { width:86px; height:86px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center; font-weight:800; color:white; cursor:pointer; border:3px solid rgba(255,255,255,0.06); box-shadow:0 6px 18px rgba(0,0,0,0.5); }
    .avatar:hover { transform:scale(1.05); }
    .card { background: var(--card); padding:10px; border-radius:10px; border:1px solid rgba(155,77,255,0.06); }
    .motiv { padding:10px 14px; border-radius:999px; background: rgba(155,77,255,0.08); font-weight:700; color:#fff; display:inline-block; }
    .small { font-size:12px; color:var(--muted); }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="header"><h2 style="margin:0">🏋️ Workout Tracker PRO — Neon</h2><div class="small">Tema: motivazionale · per-set editing · analytics</div></div>', unsafe_allow_html=True)

# ------------- Motivational ticker (safe) -------------
MOTIVS = [
    "Non mollare ora.",
    "Ogni rep ti avvicina al tuo obiettivo.",
    "Il dolore è temporaneo, il risultato è per sempre.",
    "Diventa la versione più forte di te stesso.",
    "Disciplina > Motivazione.",
    "Un giorno o il giorno 1 — scegli oggi."
]
# JS component: rotate every 30s, safe JSON encoding
from streamlit.components.v1 import html as components_html
motivs_json = json.dumps(MOTIVS)
ticker_html = f"""
<div id="motiv" class="motiv">Caricamento...</div>
<script>
const motivs = {motivs_json};
let idx = 0;
function showMotiv() {{
  const el = document.getElementById('motiv');
  if (!el) return;
  el.innerText = motivs[idx % motivs.length];
  idx++;
}}
showMotiv();
setInterval(showMotiv, 30000);
</script>
"""
components_html(ticker_html, height=50)

st.markdown("---")

# ------------- Athletes section with avatar upload -------------
st.subheader("👤 Atleti")

with st.expander("➕ Aggiungi / Modifica atleta", expanded=False):
    left, right = st.columns([3,2])
    with left:
        new_name = st.text_input("Nome atleta (nuovo o esistente)")
    with right:
        uploaded = st.file_uploader("Carica avatar (png/jpg/webp)", type=["png", "jpg", "jpeg", "webp"])
    if st.button("Salva atleta"):
        if not new_name or new_name.strip() == "":
            st.error("Inserisci un nome valido.")
        else:
            name = new_name.strip()
            if name not in ATHLETES:
                ATHLETES.append(name)
                save_json(ATHLETES_FILE, ATHLETES)
            if uploaded is not None:
                p = save_avatar(name, uploaded)
                if p:
                    st.success("Avatar salvato.")
            else:
                st.success(f"Atleta '{name}' salvato.")
            st.experimental_rerun()

# show avatars horizontally (one column per atleta)
cols = st.columns(len(ATHLETES) if len(ATHLETES) > 0 else 1)
for i, a in enumerate(ATHLETES):
    with cols[i]:
        is_selected = (st.session_state.get("athlete") == a)
        # show avatar image if exists, otherwise initial circle
        if avatar_exists(a):
            st.image(avatar_path(a), width=86, caption=a)
        else:
            bg = "#7c52ff" if a == "Simone" else "#4db8ff"
            st.markdown(f"<div class='avatar' style='background:{bg}; text-align:center; line-height:86px; font-size:34px'>{a[0]}</div>", unsafe_allow_html=True)

        if st.button(f"Seleziona {a}", key=f"sel_{a}"):
            st.session_state.athlete = a
            ensure_athlete_files(a)
            st.experimental_rerun()

# set session athlete if unset
if not st.session_state.get("athlete") and ATHLETES:
    st.session_state.athlete = ATHLETES[0]
ath = st.session_state.get("athlete")
st.markdown("---")

# ------------- Top controls -------------
col1, col2, col3 = st.columns([3,2,2])
with col1:
    st.markdown(f"<div class='card'><b>{ath}</b> — <span class='small'>dati localmente in /data</span></div>", unsafe_allow_html=True)
with col2:
    if st.button("📥 Esporta storico (CSV)"):
        hist = load_json(history_file(ath), [])
        if hist:
            df = pd.DataFrame(hist)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, file_name=f"{ath.lower()}_history.csv")
        else:
            st.info("Nessuno storico disponibile.")
with col3:
    if st.button("🧹 Reset locale"):
        save_json(workout_file(ath), [])
        save_json(history_file(ath), [])
        save_json(plan_file(ath), "")
        st.success("Dati resettati")
        st.experimental_rerun()

st.markdown("---")

# ------------- Add exercise UI -------------
st.subheader("➕ Aggiungi esercizio alla routine")
with st.expander("Aggiungi nuovo esercizio", expanded=True):
    # preload groups from EXERCISES values or PRELOADED fallback
    PRELOADED = {
      "Petto":["Panca piana","Panca inclinata","Chest press","Croci con manubri"],
      "Dorso":["Lat machine","Rematore con bilanciere","Pulldown","Trazioni"],
      "Spalle":["Military press","Alzate laterali","Arnold press"],
      "Bicipiti":["Curl bilanciere","Curl manubri","Hammer curl"],
      "Tricipiti":["French press","Pushdown","Dip"],
      "Gambe":["Squat","Leg press","Affondi","Leg extension"],
      "Core":["Crunch","Plank","Russian twist"]
    }
    # combine EXERCISES if present
    exercises_map = EXERCISES.copy()
    groups = sorted(set(list(exercises_map.values()) + list(PRELOADED.keys())))
    col_g, col_e, col_d = st.columns([2,4,1])
    with col_g:
        group = st.selectbox("Gruppo muscolare", groups)
    with col_e:
        # build exercise list for the chosen group
        options = []
        # from PRELOADED
        if group in PRELOADED:
            options.extend(PRELOADED[group])
        # from user EXERCISES
        for ex, g in exercises_map.items():
            if g == group and ex not in options:
                options.append(ex)
        options.append("➕ Personalizzato")
        exercise_choice = st.selectbox("Scegli esercizio", options)
        if exercise_choice == "➕ Personalizzato":
            exercise = st.text_input("Nome esercizio (personalizzato)").strip()
        else:
            exercise = exercise_choice
    with col_d:
        day = st.selectbox("Giorno", ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"])
    if exercise:
        sets_n = st.number_input("Numero serie", min_value=1, max_value=12, value=3)
        st.markdown("**Pesi & reps per serie (opzionale)**")
        cols_weights = st.columns(min(4, sets_n))
        new_sets = []
        for i in range(sets_n):
            c = cols_weights[i % len(cols_weights)]
            w = c.number_input(f"S{i+1} kg", min_value=0, max_value=600, value=0, key=f"new_w_{i}")
            r = c.number_input(f"S{i+1} rep", min_value=0, max_value=200, value=0, key=f"new_r_{i}")
            new_sets.append({"peso": int(w), "reps": int(r)})
        if st.button("Aggiungi alla routine"):
            ensure_athlete_files(ath)
            # load, append, save
            wlist = load_json(workout_file(ath), [])
            new_entry = {
                "id": str(uuid.uuid4()),
                "group": group,
                "exercise": exercise,
                "day": day,
                "sets": new_sets if any(s["peso"]>0 or s["reps"]>0 for s in new_sets) else [{"peso":0,"reps":0} for _ in range(sets_n)],
                "timestamp": datetime.now().isoformat()
            }
            wlist.append(new_entry)
            save_json(workout_file(ath), wlist)
            st.success("Esercizio aggiunto!")
            st.experimental_rerun()

st.markdown("---")

# ------------- Routine display & per-set editing -------------
st.subheader("📋 Routine — modifica per-set")
workouts = load_json(workout_file(ath), [])
# normalize sets structure if needed
def normalize_item(e: Dict[str,Any]) -> Dict[str,Any]:
    out = dict(e)
    sets = out.get("sets")
    if not isinstance(sets, list):
        out["sets"] = [{"peso":0,"reps":0} for _ in range(3)]
    return out

workouts = [normalize_item(w) for w in workouts]

f1, f2 = st.columns([2,3])
with f1:
    filter_day = st.selectbox("Filtra giorno", ["Tutti","Lun","Mar","Mer","Gio","Ven","Sab","Dom"])
with f2:
    all_ex = sorted({w["exercise"] for w in workouts})
    filter_ex = st.selectbox("Filtra esercizio", ["Tutti"] + all_ex)

display_list = []
for w in workouts:
    if filter_day != "Tutti" and w["day"] != filter_day: continue
    if filter_ex != "Tutti" and w["exercise"] != filter_ex: continue
    display_list.append(w)

if not display_list:
    st.info("Nessun esercizio con i filtri selezionati.")
else:
    for entry in display_list:
        st.markdown(f"<div class='card'><b>{entry['exercise']}</b> <span class='small'> — {entry.get('group','Generale')} ({entry.get('day','')})</span></div>", unsafe_allow_html=True)
        for i, s in enumerate(entry["sets"]):
            cols = st.columns([2,1,1,1])
            cols[0].markdown(f"**Serie {i+1}**")
            p = cols[1].number_input(f"peso_{entry['id']}_{i}", min_value=0, max_value=2000, value=int(s.get("peso",0)), key=f"peso_{entry['id']}_{i}")
            r = cols[2].number_input(f"rep_{entry['id']}_{i}", min_value=0, max_value=500, value=int(s.get("reps",0)), key=f"rep_{entry['id']}_{i}")
            # update local list
            idx = next((ix for ix,w in enumerate(workouts) if w["id"]==entry["id"]), None)
            if idx is not None:
                workouts[idx]["sets"][i]["peso"] = int(p)
                workouts[idx]["sets"][i]["reps"] = int(r)
        b1, b2 = st.columns([1,1])
        if b1.button("💾 Salva entry", key=f"save_{entry['id']}"):
            save_json(workout_file(ath), workouts)
            st.success("Salvato")
        if b2.button("🗑️ Elimina entry", key=f"del_{entry['id']}"):
            workouts = [w for w in workouts if w["id"] != entry["id"]]
            save_json(workout_file(ath), workouts)
            st.experimental_rerun()
        st.markdown("---")

st.markdown("---")

# ------------- Scheda palestra (hidden editor) -------------
st.subheader("📒 Scheda palestra (opzionale)")
if st.button("🔽 Mostra / Nascondi scheda"):
    st.session_state.show_plan_editor = not st.session_state.show_plan_editor

if st.session_state.show_plan_editor:
    plan_text = load_json(plan_file(ath), "")
    txt = st.text_area("Modifica la tua scheda (Markdown / testo). Salva quando hai finito.", value=plan_text, height=240)
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("💾 Salva scheda"):
            save_json(plan_file(ath), txt)  # store raw text into json to keep single-file logic
            st.success("Scheda salvata")
    with c2:
        st.download_button("📄 Esporta scheda (TXT)", txt.encode("utf-8"), file_name=f"{ath.lower()}_plan.txt")

st.markdown("---")

# ------------- Register session (history) -------------
st.subheader("📥 Registra sessione")
st.write("La nota verrà salvata insieme a ciascuna serie registrata.")
note = st.text_input("Nota sessione (opzionale)", value="")
if st.button("Registra sessione nello storico"):
    hist = load_json(history_file(ath), [])
    now = datetime.now().isoformat()
    for w in workouts:
        for s in w["sets"]:
            hist.append({
                "date": now,
                "exercise": w["exercise"],
                "group": w.get("group","Generale"),
                "day": w.get("day",""),
                "peso": s.get("peso", 0),
                "reps": s.get("reps", 0),
                "note": note
            })
    save_json(history_file(ath), hist)
    st.success("Sessione registrata")
    st.experimental_rerun()

st.markdown("---")

# ------------- Analytics -------------
st.subheader("📈 Analytics")
hist = load_json(history_file(ath), [])
if not hist:
    st.info("Nessuno storico: registra sessioni per popolare i grafici.")
else:
    df = pd.DataFrame(hist)
    df["date_dt"] = pd.to_datetime(df["date"])
    mode = st.radio("Visualizza per", ["Esercizio","Gruppo muscolare"], horizontal=True)
    if mode == "Esercizio":
        ex_list = sorted(df["exercise"].unique())
        sel = st.selectbox("Scegli esercizio", ex_list)
        df_sel = df[df["exercise"] == sel].sort_values("date_dt")
        df_plot = df_sel.groupby("date_dt", as_index=False).agg({"peso":"mean","reps":"sum"})
        fig = px.line(df_plot, x="date_dt", y="peso", markers=True, title=f"Progressione peso — {sel}")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        groups = sorted(df["group"].unique())
        selg = st.selectbox("Scegli gruppo muscolare", groups)
        df_g = df[df["group"] == selg].copy()
        df_g["week"] = df_g["date_dt"].dt.strftime("%Y-%U")
        df_g["volume"] = df_g["peso"] * df_g["reps"]
        vol = df_g.groupby("week", as_index=False).agg({"volume":"sum"}).sort_values("week")
        if vol.empty:
            st.info("Dati insufficienti per questo gruppo.")
        else:
            fig2 = px.bar(vol.tail(12), x="week", y="volume", title=f"Volume settimanale — {selg} (ultime 12 settimane)")
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("Workout Tracker PRO — Animated Neon — dati locali in /data")
