# app.py — Workout Tracker PRO (stable, multi-athlete fixed: Simone & Antonio)
import streamlit as st
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd
import plotly.express as px

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Workout Tracker PRO", page_icon="🏋️", layout="wide")
DATA_DIR = "dati"   # <- attenzione: la tua cartella è 'dati' come richiesto
os.makedirs(DATA_DIR, exist_ok=True)

# Fixed athletes list (A: editing manuale nel codice)
ATHLETES = ["Simone", "Antonio"]

# -----------------------
# File helpers (single JSON per atleta)
# Structure per file: {"workouts": [...], "history": [...], "plan": "text"}
# -----------------------
def athlete_file(a: str) -> str:
    safe = a.strip()
    return os.path.join(DATA_DIR, f"{safe}.json")

def ensure_athlete_file(a: str):
    p = athlete_file(a)
    if not os.path.exists(p):
        data = {"workouts": [], "history": [], "plan": ""}
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def load_athlete_data(a: str) -> Dict[str, Any]:
    ensure_athlete_file(a)
    p = athlete_file(a)
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"workouts": [], "history": [], "plan": ""}

def save_athlete_data(a: str, data: Dict[str, Any]):
    p = athlete_file(a)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_workouts(a: str) -> List[Dict[str, Any]]:
    return load_athlete_data(a).get("workouts", [])

def save_workouts(a: str, workouts: List[Dict[str, Any]]):
    d = load_athlete_data(a); d["workouts"] = workouts; save_athlete_data(a, d)

def load_history(a: str) -> List[Dict[str, Any]]:
    return load_athlete_data(a).get("history", [])

def save_history(a: str, hist: List[Dict[str, Any]]):
    d = load_athlete_data(a); d["history"] = hist; save_athlete_data(a, d)

def load_plan(a: str) -> str:
    return load_athlete_data(a).get("plan", "")

def save_plan(a: str, txt: str):
    d = load_athlete_data(a); d["plan"] = txt; save_athlete_data(a, d)

# -----------------------
# UI: style + header
# -----------------------
st.markdown(
    """
    <style>
    :root{ --bg:#05030a; --card: rgba(255,255,255,0.02); --muted:#9aa6b2; }
    .stApp { background: linear-gradient(135deg,#12001f,#04102a); color:#eaf0ff; font-family: Inter, sans-serif;}
    .header { padding:12px; border-radius:10px; margin-bottom:12px; background: linear-gradient(90deg, rgba(27,6,47,0.6), rgba(6,16,42,0.6)); }
    .card { background: var(--card); padding:10px; border-radius:10px; border:1px solid rgba(155,77,255,0.06); }
    .small { font-size:12px; color:var(--muted); }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header"><h2 style="margin:0">🏋️ Workout Tracker PRO</h2><div class="small">Multi-athlete (Simone & Antonio) · Routine migliorata · Analytics</div></div>', unsafe_allow_html=True)

# -----------------------
# Motivational ticker (safe, 30s)
# -----------------------
MOTIVS = [
    "Non mollare ora.",
    "Ogni rep ti avvicina al tuo obiettivo.",
    "Il dolore è temporaneo, il risultato è per sempre.",
   # Motivational ticker — JS inserito correttamente in una stringa multilinea
from streamlit.components.v1 import html as components_html
motivs_json = json.dumps(MOTIVS)

ticker_html = f"""<div id="motiv" class="motiv">Caricamento...</div>
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

selected_athlete = st.sidebar.radio("Scegli atleta", ATHLETES, index=0, key="sidebar_athlete")
ath = selected_athlete
ensure_athlete_file(ath)

if st.sidebar.button("🔄 Ricarica dati"):
    st.experimental_rerun()

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Reset dati atleta"):
    save_workouts(ath, [])
    save_history(ath, [])
    save_plan(ath, "")
    st.sidebar.success(f"Dati di {ath} resettati")
    st.sidebar.button(" ")  # useless button to force rerender on some clients
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Nota: per aggiungere altri atleti modifica ATHLETES in app.py")

st.markdown("---")

# -----------------------
# PRELOADED exercises (grouped)
# -----------------------
PRELOADED = {
  "Petto":["Panca piana","Panca inclinata","Chest press","Croci con manubri"],
  "Dorso":["Lat machine","Rematore con bilanciere","Pulldown","Trazioni"],
  "Spalle":["Military press","Alzate laterali","Arnold press"],
  "Bicipiti":["Curl bilanciere","Curl manubri","Hammer curl"],
  "Tricipiti":["French press","Pushdown","Dip"],
  "Gambe":["Squat","Leg press","Affondi","Leg extension"],
  "Core":["Crunch","Plank","Russian twist"]
}

# -----------------------
# Page layout: Routine | Progressione | Note | Analytics
# -----------------------
tab = st.tabs(["🏷️ Routine","📈 Progressione","📝 Note sessione","📊 Analytics"])[0]  # we'll control content manually

# Routine tab (improved layout)
st.header("📋 Routine — visuale e modifica")
workouts = load_workouts(ath)

# normalize: ensure id and sets
def normalize(e: Dict[str,Any]) -> Dict[str,Any]:
    out = dict(e)
    out.setdefault("id", str(uuid.uuid4()))
    out.setdefault("group", out.get("group","Generale"))
    out.setdefault("exercise", out.get("exercise","Unnamed"))
    out.setdefault("day", out.get("day","Lun"))
    s = out.get("sets")
    if not isinstance(s, list) or len(s) == 0:
        out["sets"] = [{"peso":0,"reps":0} for _ in range(3)]
    else:
        # ensure dict shape
        ns=[]
        for it in s:
            if isinstance(it, dict):
                ns.append({"peso": int(it.get("peso",0)), "reps": int(it.get("reps",0))})
            else:
                ns.append({"peso": int(it), "reps": 0})
        out["sets"]=ns
    out.setdefault("timestamp", out.get("timestamp", datetime.now().isoformat()))
    return out

workouts = [normalize(w) for w in workouts]
save_workouts(ath, workouts)

# Group workouts by day for compact cards
days = ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"]
cols = st.columns(3)
for idx_day, day in enumerate(days):
    # show three columns (grid)
    col = cols[idx_day % 3]
    with col:
        st.markdown(f"#### {day}")
        day_list = [w for w in workouts if w.get("day")==day]
        if not day_list:
            st.markdown("_Nessun esercizio_")
        else:
            for entry in day_list:
                st.markdown(f"<div style='padding:8px;border-radius:8px;background:rgba(255,255,255,0.02);margin-bottom:8px;'>"
                            f"<b>{entry['exercise']}</b> <span style='color:#9aa6b2'> — {entry.get('group')}</span><br>", unsafe_allow_html=True)
                # show per-set quick inline editing
                sets = entry["sets"]
                cols_sets = st.columns((len(sets)))
                for i, s in enumerate(sets):
                    with cols_sets[i]:
                        p = st.number_input(f"{entry['id']}_peso_{i}", min_value=0, max_value=2000, value=int(s.get("peso",0)), key=f"peso_{entry['id']}_{i}")
                        r = st.number_input(f"{entry['id']}_rep_{i}", min_value=0, max_value=500, value=int(s.get("reps",0)), key=f"rep_{entry['id']}_{i}")
                        # update in-memory
                        idx = next((ix for ix,w in enumerate(workouts) if w["id"]==entry["id"]), None)
                        if idx is not None:
                            workouts[idx]["sets"][i]["peso"] = int(p)
                            workouts[idx]["sets"][i]["reps"] = int(r)
                # actions
                a_col1, a_col2 = st.columns([1,1])
                with a_col1:
                    if st.button("💾 Salva", key=f"save_{entry['id']}"):
                        save_workouts(ath, workouts)
                        st.success("Salvato")
                with a_col2:
                    if st.button("🗑️ Elimina", key=f"del_{entry['id']}"):
                        workouts = [w for w in workouts if w["id"]!=entry["id"]]
                        save_workouts(ath, workouts)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# Add new exercise area (compact)
st.subheader("➕ Aggiungi esercizio")
with st.expander("Apri form aggiunta"):
    col_g, col_e, col_d = st.columns([2,5,1])
    with col_g:
        group = st.selectbox("Gruppo muscolare", sorted(PRELOADED.keys()))
    with col_e:
        options = PRELOADED[group][:]
        options.append("➕ Personalizzato")
        choice = st.selectbox("Esercizio", options)
        if choice == "➕ Personalizzato":
            exercise = st.text_input("Nome esercizio (personalizzato)").strip()
        else:
            exercise = choice
    with col_d:
        day = st.selectbox("Giorno", days)
    sets_n = st.number_input("Numero serie", min_value=1, max_value=12, value=3)
    st.markdown("**Pesi & rep per serie (opzionale)**")
    cols_weights = st.columns(min(4, sets_n))
    new_sets = []
    for i in range(sets_n):
        c = cols_weights[i % len(cols_weights)]
        w = c.number_input(f"S{i+1} kg", min_value=0, max_value=600, value=0, key=f"new_w_{i}")
        r = c.number_input(f"S{i+1} rep", min_value=0, max_value=200, value=0, key=f"new_r_{i}")
        new_sets.append({"peso": int(w), "reps": int(r)})
    if st.button("Aggiungi alla routine"):
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
        st.success("Esercizio aggiunto")
        st.rerun()

st.markdown("---")

# -----------------------
# Progressione tab (compact)
# -----------------------
st.header("📈 Progressione — scegli esercizio")
hist = load_history(ath)
if not hist:
    st.info("Nessuno storico: registra sessioni per popolare i grafici.")
else:
    df_hist = pd.DataFrame(hist)
    ex_list = sorted(df_hist["exercise"].unique())
    sel = st.selectbox("Scegli esercizio per progressione", ex_list)
    df_sel = df_hist[df_hist["exercise"]==sel].copy()
    df_sel["date_dt"] = pd.to_datetime(df_sel["date"])
    df_plot = df_sel.groupby("date_dt", as_index=False).agg({"peso":"mean","reps":"sum"})
    if not df_plot.empty:
        fig = px.line(df_plot, x="date_dt", y="peso", markers=True, title=f"Progressione peso — {sel}")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nessun dato per questo esercizio.")

st.markdown("---")

# -----------------------
# Note sessione
# -----------------------
st.header("📝 Note sessione")
st.write("Le note vengono salvate nello storico assieme alle serie quando registri la sessione.")
note = st.text_input("Nota sessione (opzionale)", value="")
if st.button("Registra sessione nello storico"):
    hist = load_history(ath)
    now = datetime.now().isoformat()
    for w in workouts:
        for s in w["sets"]:
            hist.append({
                "date": now,
                "exercise": w["exercise"],
                "group": w.get("group","Generale"),
                "day": w.get("day",""),
                "peso": s.get("peso",0),
                "reps": s.get("reps",0),
                "note": note
            })
    save_history(ath, hist)
    st.success("Sessione registrata")
    st.rerun()

st.markdown("---")

# -----------------------
# Analytics final
# -----------------------
st.header("📊 Analytics (gruppo o esercizio)")
hist = load_history(ath)
if not hist:
    st.info("Registra almeno una sessione per vedere le analytics.")
else:
    df = pd.DataFrame(hist)
    df["date_dt"] = pd.to_datetime(df["date"])
    mode = st.radio("Visualizza per", ["Esercizio","Gruppo muscolare"], horizontal=True)
    if mode == "Esercizio":
        ex_list = sorted(df["exercise"].unique())
        sel = st.selectbox("Scegli esercizio", ex_list)
        df_sel = df[df["exercise"]==sel].sort_values("date_dt")
        df_plot = df_sel.groupby("date_dt", as_index=False).agg({"peso":"mean","reps":"sum"})
        fig = px.line(df_plot, x="date_dt", y="peso", markers=True, title=f"Progressione peso — {sel}")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        groups = sorted(df["group"].unique())
        selg = st.selectbox("Scegli gruppo muscolare", groups)
        df_g = df[df["group"]==selg].copy()
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
st.caption("Workout Tracker PRO — stable multi-athlete — dati locali in /dati")
