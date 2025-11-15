# app.py — Workout Tracker PRO (Dark Purple Gradient) — final
import streamlit as st
import json
import os
import uuid
from datetime import datetime
from collections import defaultdict
import pandas as pd
import plotly.express as px
from typing import List, Dict, Any
import time
import html

# -------------------------
# Page + CSS (Dark Purple Gradient + animations + avatars)
# -------------------------
st.set_page_config(page_title="Workout Tracker PRO", page_icon="🏋️", layout="wide")

st.markdown(
    """
    <style>
    :root{
      --bg-start: #1a002b;
      --bg-end: #061233;
      --card: rgba(255,255,255,0.03);
      --accent: #9b4dff;
      --accent-2: #6fc3ff;
      --muted: #9aa6b2;
    }
    .stApp {
      background: linear-gradient(135deg, var(--bg-start), var(--bg-end));
      color: #eaf0ff;
      font-family: Inter, sans-serif;
    }
    .header {
      padding: 18px;
      border-radius: 12px;
      margin-bottom: 12px;
      background: linear-gradient(90deg, rgba(27,6,47,0.6), rgba(6,16,42,0.6));
      box-shadow: 0 8px 30px rgba(0,0,0,0.45);
    }
    .title { font-size:20px; font-weight:700; color: #fff; }
    .subtitle { color: var(--muted); font-size:13px; margin-top:6px; }

    /* avatar */
    .avatar {
      width:86px; height:86px; border-radius:50%;
      display:inline-flex; align-items:center; justify-content:center;
      font-weight:700; color:white; cursor:pointer;
      transition: transform .18s ease, box-shadow .18s ease;
      border: 3px solid rgba(255,255,255,0.06);
      box-shadow: 0 6px 18px rgba(0,0,0,0.5);
      margin-bottom:6px;
    }
    .avatar:hover { transform:scale(1.05); }
    .avatar-selected { box-shadow: 0 10px 28px rgba(155,77,255,0.28); border-color: rgba(155,77,255,0.9); transform:scale(1.06); }

    /* cards */
    .card {
      background: var(--card);
      padding:12px;
      border-radius:12px;
      border:1px solid rgba(155,77,255,0.08);
      transition: transform .12s ease, box-shadow .12s ease;
    }
    .card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(0,0,0,0.6); }

    .exercise-card {
      background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border-radius:12px;
      padding:10px;
      margin-bottom:10px;
      border:1px solid rgba(255,255,255,0.03);
    }

    .small { font-size:12px; color:var(--muted); }
    .accent-pill { background: linear-gradient(90deg,#9b4dff,#6fc3ff); padding:6px 10px; border-radius:999px; color:white; font-weight:600; }
    .muscle-icon { width:28px; height:28px; vertical-align: middle; margin-right:6px; }

    /* animated motivational area */
    .motiv-container { padding:8px 12px; border-radius:999px; display:inline-block; }
    .motiv-text { font-weight:700; color:#fff; font-size:16px; }

    /* responsive minor fixes */
    @media (max-width: 600px) {
        .avatar { width:64px; height:64px; font-size:18px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="header"><div class="title">🏋️ Workout Tracker PRO</div>'
    '<div class="subtitle">Dark Purple Gradient — per-set editing, progress & weekly volume</div></div>',
    unsafe_allow_html=True
)

# -------------------------
# Data paths and helpers
# -------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

ATHLETES = ["Simone", "Antonio"]

def athlete_workouts_file(a: str) -> str:
    return os.path.join(DATA_DIR, f"{a.lower()}_workouts.json")

def athlete_history_file(a: str) -> str:
    return os.path.join(DATA_DIR, f"{a.lower()}_history.json")

def athlete_plan_file(a: str) -> str:
    return os.path.join(DATA_DIR, f"{a.lower()}_plan.txt")

def ensure_files(a: str):
    for p in (athlete_workouts_file(a), athlete_history_file(a)):
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    if not os.path.exists(athlete_plan_file(a)):
        with open(athlete_plan_file(a), "w", encoding="utf-8") as f:
            f.write("")

def load_workouts(a: str) -> List[Dict[str, Any]]:
    ensure_files(a)
    with open(athlete_workouts_file(a), "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_workouts(a: str, data: List[Dict[str,Any]]):
    with open(athlete_workouts_file(a), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_history(a: str) -> List[Dict[str,Any]]:
    ensure_files(a)
    with open(athlete_history_file(a), "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_history(a: str, data: List[Dict[str,Any]]):
    with open(athlete_history_file(a), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_plan(a: str) -> str:
    p = athlete_plan_file(a)
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            f.write("")
        return ""
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def save_plan(a: str, text: str):
    with open(athlete_plan_file(a), "w", encoding="utf-8") as f:
        f.write(text)

# -------------------------
# Preloaded exercises (with 'bodybuilding' icons as inline SVG)
# -------------------------
PRELOADED = {
    "Petto": ["Panca piana", "Panca inclinata", "Chest press", "Croci con manubri"],
    "Dorso": ["Lat machine", "Rematore con bilanciere", "Pulldown", "Trazioni"],
    "Spalle": ["Military press", "Alzate laterali", "Arnold press"],
    "Bicipiti": ["Curl bilanciere", "Curl manubri", "Hammer curl"],
    "Tricipiti": ["French press", "Pushdown", "Dip"],
    "Gambe": ["Squat", "Leg press", "Affondi", "Leg curl", "Leg extension"],
    "Core": ["Crunch", "Plank", "Russian twist"]
}

SVG_ICONS = {
    "Petto": "<svg class='muscle-icon' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'><path d='M3 12c0-3.314 2.686-6 6-6 1.657 0 3 1.343 3 3 0-1.657 1.343-3 3-3 3.314 0 6 2.686 6 6v6H3v-6z' stroke='#ffccd9' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    "Dorso": "<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M12 2v4m0 12v4M4 8c4 4 8 4 16 0' stroke='#ffd9b3' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    "Spalle": "<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M12 3c2 0 3 1 4 3s2 3 4 3' stroke='#d9b3ff' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    "Bicipiti": "<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M4 20c2-4 6-6 10-6s8 2 10 6' stroke='#ffd1b3' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    "Tricipiti": "<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M3 12h18' stroke='#ffb3d9' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    "Gambe": "<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M6 3v18M18 3v18' stroke='#c6f0ff' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    "Core": "<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M12 2c3 0 6 4 6 10s-3 10-6 10-6-4-6-10 3-10 6-10z' stroke='#e6ffcc' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>"
}

# -------------------------
# Session init
# -------------------------
if "athlete" not in st.session_state:
    st.session_state.athlete = ATHLETES[0]
if "motiv_index" not in st.session_state:
    st.session_state.motiv_index = 0
if "last_motiv_time" not in st.session_state:
    st.session_state.last_motiv_time = time.time()
if "show_plan_editor" not in st.session_state:
    st.session_state.show_plan_editor = False

# -------------------------
# Motivational quotes rotation (session-based)
# -------------------------
MOTIVATIONS = [
    "Spingi oggi, vinci domani.",
    "Ogni rep ti avvicina al tuo obiettivo.",
    "Fai ciò che altri non vogliono fare.",
    "Tu costruisci la tua disciplina.",
    "Non fermarti quando sei stanco, fermati quando hai finito.",
    "Un giorno o il giorno 1. Decidi tu."
]
MOTIV_INTERVAL = 6  # seconds

# update index if enough time passed
now_t = time.time()
if now_t - st.session_state.last_motiv_time > MOTIV_INTERVAL:
    st.session_state.motiv_index = (st.session_state.motiv_index + 1) % len(MOTIVATIONS)
    st.session_state.last_motiv_time = now_t
    # rerun to update UI
    st.rerun()

# show motivational pill
st.markdown(f"<div class='motiv-container card'><span id='motiv-text' class='motiv-text'>{MOTIVATIONS[st.session_state.motiv_index]}</span></div>", unsafe_allow_html=True)

# -------------------------
# Athlete selector (avatars) in main area and sidebar
# -------------------------
st.write("## 👤 Atleti")
c1, c2 = st.columns(2)
for col, name in zip((c1, c2), ATHLETES):
    selected = (st.session_state.athlete == name)
    bg = "#7c52ff" if name == "Simone" else "#4db8ff"
    cls = "avatar avatar-selected" if selected else "avatar"
    with col:
        st.markdown(f"<div style='text-align:center;'><div class='{cls}' style='background:{bg};'>{name[0]}</div></div>", unsafe_allow_html=True)
        if st.button(f"Seleziona {name}", key=f"sel_{name}"):
            st.session_state.athlete = name
            st.rerun()

ath = st.session_state.athlete
ensure_files(ath)

# -------------------------
# Top controls: export/reset
# -------------------------
col1, col2, col3 = st.columns([3,2,2])
with col1:
    st.markdown(f"<div class='card'><b>{ath}</b> — <span class='small'>Ultimo salvataggio locale</span></div>", unsafe_allow_html=True)
with col2:
    if st.button("📥 Esporta storico (CSV)"):
        hist = load_history(ath)
        if hist:
            df = pd.DataFrame(hist)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, file_name=f"{ath.lower()}_history.csv")
        else:
            st.info("Nessuno storico disponibile.")
with col3:
    if st.button("🧹 Reset locale"):
        save_workouts(ath, [])
        save_history(ath, [])
        save_plan(ath, "")
        st.success("Dati locali resettati.")
        st.rerun()

st.markdown("---")

# -------------------------
# Load & normalize workouts (handle legacy structures)
# -------------------------
def normalize(e: Dict[str,Any]) -> Dict[str,Any]:
    out = {}
    out["id"] = e.get("id", str(uuid.uuid4()))
    out["group"] = e.get("group", e.get("muscle", "Generale"))
    out["exercise"] = e.get("exercise", e.get("esercizio", "Unnamed"))
    out["day"] = e.get("day", e.get("giorno", "Lun"))
    sets = e.get("sets") or e.get("serie") or e.get("series") or e.get("weights")
    if isinstance(sets, list):
        s = []
        for item in sets:
            if isinstance(item, dict):
                s.append({"peso": int(item.get("peso",0)), "reps": int(item.get("reps",0))})
            elif isinstance(item, (int,float)):
                s.append({"peso": int(item), "reps": 0})
            else:
                s.append({"peso":0,"reps":0})
    elif isinstance(sets, dict):
        s = []
        for k in sorted(sets.keys()):
            v = sets[k]
            if isinstance(v, dict):
                s.append({"peso": int(v.get("peso",0)), "reps": int(v.get("reps",0))})
            else:
                s.append({"peso": int(v if isinstance(v,(int,float)) else 0), "reps": 0})
    else:
        s = [{"peso":0,"reps":0} for _ in range(3)]
    out["sets"] = s
    out["timestamp"] = e.get("timestamp", datetime.now().isoformat())
    return out

workouts_raw = load_workouts(ath)
workouts = [normalize(e) for e in workouts_raw]
save_workouts(ath, workouts)

# -------------------------
# Add exercise form (with icons)
# -------------------------
st.subheader("➕ Aggiungi esercizio")
with st.expander("Aggiungi nuovo esercizio"):
    colA, colB, colC = st.columns([2,3,1])
    with colA:
        group = st.selectbox("Gruppo muscolare", list(PRELOADED.keys()))
        icon_html = SVG_ICONS.get(group, "")
        st.markdown(f"<div style='margin-top:6px'>{icon_html} <span class='small'>{group}</span></div>", unsafe_allow_html=True)
    with colB:
        exercise_choice = st.selectbox("Scegli esercizio", PRELOADED[group] + ["➕ Personalizzato"])
        if exercise_choice == "➕ Personalizzato":
            exercise = st.text_input("Nome esercizio personalizzato").strip()
        else:
            exercise = exercise_choice
    with colC:
        day = st.selectbox("Giorno", ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"])
    if exercise:
        sets_n = st.number_input("Numero serie", min_value=1, max_value=12, value=3)
        st.markdown("**Pesi per serie (opzionale)**")
        sw_cols = st.columns(min(4, sets_n))
        new_sets = []
        for i in range(sets_n):
            c = sw_cols[i % len(sw_cols)]
            w = c.number_input(f"S{i+1} kg", min_value=0, max_value=500, value=0, key=f"new_w_{i}")
            r = c.number_input(f"S{i+1} rep", min_value=0, max_value=200, value=0, key=f"new_r_{i}")
            new_sets.append({"peso": int(w), "reps": int(r)})
        if st.button("Aggiungi esercizio alla routine"):
            new_entry = {
                "id": str(uuid.uuid4()),
                "group": group,
                "exercise": exercise,
                "day": day,
                "sets": new_sets if any(s["peso"]>0 or s["reps"]>0 for s in new_sets) else [{"peso":0,"reps":0} for _ in range(sets_n)],
                "timestamp": datetime.now().isoformat()
            }
            workouts.append(new_entry)
            save_workouts(ath, workouts)
            st.success("Esercizio aggiunto!")
            st.rerun()

st.markdown("---")

# -------------------------
# Filters & display list
# -------------------------
st.subheader("📋 Routine & modifica per-set")
f1, f2 = st.columns([2,3])
with f1:
    filter_day = st.selectbox("Filtra giorno", ["Tutti","Lun","Mar","Mer","Gio","Ven","Sab","Dom"])
with f2:
    all_exs = sorted({w["exercise"] for w in workouts})
    filter_ex = st.selectbox("Filtra esercizio", ["Tutti"] + all_exs)

filtered = []
for w in workouts:
    if filter_day != "Tutti" and w["day"] != filter_day:
        continue
    if filter_ex != "Tutti" and w["exercise"] != filter_ex:
        continue
    filtered.append(w)

if not filtered:
    st.info("Nessun esercizio con questi filtri — aggiungine uno.")
else:
    for entry in filtered:
        st.markdown(f"<div class='exercise-card'><b style='font-size:15px'>{entry['exercise']}</b> <span class='small'> — {entry['group']} ({entry['day']})</span>", unsafe_allow_html=True)
        sets = entry["sets"]
        for i, s in enumerate(sets):
            cols = st.columns([2,1,1,1])
            cols[0].markdown(f"**Serie {i+1}**")
            p = cols[1].number_input(f"peso_{entry['id']}_{i}", min_value=0, max_value=1000, value=int(s.get("peso",0)), key=f"peso_{entry['id']}_{i}")
            r = cols[2].number_input(f"rep_{entry['id']}_{i}", min_value=0, max_value=200, value=int(s.get("reps",0)), key=f"rep_{entry['id']}_{i}")
            idx = next((ix for ix,w in enumerate(workouts) if w["id"]==entry["id"]), None)
            if idx is not None:
                workouts[idx]["sets"][i]["peso"] = int(p)
                workouts[idx]["sets"][i]["reps"] = int(r)
        b1, b2 = st.columns([1,1])
        if b1.button("💾 Salva entry", key=f"save_{entry['id']}"):
            save_workouts(ath, workouts)
            st.success("Salvato")
        if b2.button("🗑️ Elimina entry", key=f"del_{entry['id']}"):
            workouts = [w for w in workouts if w["id"] != entry["id"]]
            save_workouts(ath, workouts)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# Scheda palestra (hidden editor toggled by button)
# -------------------------
st.subheader("📒 Scheda palestra (opzionale)")
if st.button("🔽 Mostra / Nascondi scheda"):
    st.session_state.show_plan_editor = not st.session_state.show_plan_editor

if st.session_state.get("show_plan_editor", False):
    plan_text = load_plan(ath)
    txt = st.text_area("Modifica la tua scheda (Markdown / testo). Salva quando hai finito.", value=plan_text, height=280)
    colp, colq = st.columns([1,1])
    with colp:
        if st.button("💾 Salva scheda"):
            save_plan(ath, txt)
            st.success("Scheda salvata")
    with colq:
        if st.button("📄 Esporta scheda (TXT)"):
            st.download_button("Download TXT", txt.encode("utf-8"), file_name=f"{ath.lower()}_plan.txt")

st.markdown("---")

# -------------------------
# Register session to history (log) + note sessione
# -------------------------
st.subheader("📥 Registra sessione")
st.write("Aggiungi una nota (es. sensazioni, RPE, durata). Verrà salvata con ogni record di ogni serie.")
note = st.text_input("Nota sessione (opzionale)", value="")
if st.button("Registra sessione nello storico"):
    hist = load_history(ath)
    now = datetime.now().isoformat()
    for w in workouts:
        for s in w["sets"]:
            hist.append({
                "date": now,
                "exercise": w["exercise"],
                "group": w["group"],
                "day": w["day"],
                "peso": s.get("peso", 0),
                "reps": s.get("reps", 0),
                "note": note
            })
    save_history(ath, hist)
    st.success("Sessione registrata nello storico")

st.markdown("---")

# -------------------------
# Charts: progression & weekly volume
# -------------------------
st.subheader("📈 Analytics")

hist = load_history(ath)
if not hist:
    st.info("Nessuno storico: registra una sessione per popolare i grafici.")
else:
    dfh = pd.DataFrame(hist)
    # progression per exercise
    ex_list = sorted(dfh["exercise"].unique())
    sel_ex = st.selectbox("Scegli esercizio per progressione", ex_list)
    df_sel = dfh[dfh["exercise"]==sel_ex].copy()
    df_sel["date_dt"] = pd.to_datetime(df_sel["date"])
    df_plot = df_sel.groupby("date_dt", as_index=False).agg({"peso":"mean", "reps":"sum"})
    fig = px.line(df_plot, x="date_dt", y="peso", markers=True, title=f"Progressione peso — {sel_ex}")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    st.plotly_chart(fig, use_container_width=True)

    # weekly volume: sum(weight * reps) per week
    dfh["date_dt"] = pd.to_datetime(dfh["date"])
    dfh["year_week"] = dfh["date_dt"].dt.strftime("%Y-%U")
    dfh["volume"] = dfh["peso"] * dfh["reps"]
    vol = dfh.groupby("year_week", as_index=False).agg({"volume":"sum"})
    vol = vol.sort_values("year_week")
    if not vol.empty:
        fig2 = px.bar(vol.tail(12), x="year_week", y="volume", title="Volume settimanale (ultime 12 settimane)")
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("Workout Tracker PRO — Dark Purple Gradient — features: per-set editing, progression chart, weekly volume. Data saved locally in /data/*.json and plans in /data/*.txt")
