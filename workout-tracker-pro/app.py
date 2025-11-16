# app.py — Workout Tracker PRO (Dark Purple Gradient, animated, full features)
import streamlit as st
import json, os, uuid, time, html
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
import plotly.express as px
from streamlit.components.v1 import html as st_html

# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="Workout Tracker PRO", page_icon="🏋️", layout="wide")

# -----------------------
# CSS + animations
# -----------------------
st.markdown("""
<style>
:root{
  --bg1:#0b0714; --card: rgba(255,255,255,0.02);
  --accent1:#9b4dff; --accent2:#6fc3ff; --muted:#9aa6b2;
}
.stApp { background: linear-gradient(135deg,#12001f,#04102a); color:#eaf0ff; font-family:Inter, sans-serif;}
.header { padding:18px; border-radius:12px; margin-bottom:12px;
  background: linear-gradient(90deg, rgba(27,6,47,0.6), rgba(6,16,42,0.6));
  box-shadow: 0 10px 30px rgba(0,0,0,0.6);
}
.title { font-size:20px; font-weight:800; color:#fff; }
.subtitle { color:var(--muted); font-size:13px; margin-top:6px; }

.avatar {
  width:86px; height:86px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center;
  font-weight:800; color:white; cursor:pointer; transition: transform .18s ease, box-shadow .18s ease, border .18s;
  border: 3px solid rgba(255,255,255,0.06); box-shadow: 0 6px 18px rgba(0,0,0,0.5); margin-bottom:6px;
}
.avatar:hover { transform:scale(1.06); }
.avatar-selected { box-shadow: 0 12px 36px rgba(155,77,255,0.28); border-color: rgba(155,77,255,0.9); transform:scale(1.08); }

.card { background: var(--card); padding:12px; border-radius:12px; border:1px solid rgba(155,77,255,0.06); transition: transform .12s, box-shadow .12s; }
.card:hover { transform: translateY(-6px); box-shadow: 0 18px 40px rgba(0,0,0,0.6); }

.exercise-card { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.008)); border-radius:12px; padding:10px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.03); }

.motiv-container { display:inline-block; padding:8px 14px; border-radius:999px; background: linear-gradient(90deg, rgba(155,77,255,0.12), rgba(111,195,255,0.06)); }
.motiv-text { font-weight:700; color:#fff; font-size:16px; }

@keyframes glow {
  0% { box-shadow: 0 0 0px rgba(155,77,255,0.0); }
  50% { box-shadow: 0 0 20px rgba(155,77,255,0.12); }
  100% { box-shadow: 0 0 0px rgba(155,77,255,0.0); }
}
.glow { animation: glow 2.6s infinite; }

.small { font-size:12px; color:var(--muted); }
.muscle-icon { width:24px; height:24px; vertical-align: middle; margin-right:6px; }

@media (max-width:600px) {
  .avatar { width:64px; height:64px; font-size:18px; }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><div class="title">🏋️ Workout Tracker PRO — PRO Animated</div>'
            '<div class="subtitle">Tema: Dark Purple Gradient · Per-set editing · Analytics · Scheda</div></div>',
            unsafe_allow_html=True)

# -----------------------
# Data paths + helpers
# -----------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

ATHLETES = ["Simone", "Antonio"]

def file_workouts(a: str) -> str:
    return os.path.join(DATA_DIR, f"{a.lower()}_workouts.json")

def file_history(a: str) -> str:
    return os.path.join(DATA_DIR, f"{a.lower()}_history.json")

def file_plan(a: str) -> str:
    return os.path.join(DATA_DIR, f"{a.lower()}_plan.txt")

def ensure_files(a: str):
    for p in (file_workouts(a), file_history(a)):
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    if not os.path.exists(file_plan(a)):
        with open(file_plan(a), "w", encoding="utf-8") as f:
            f.write("")

def load_workouts(a: str) -> List[Dict[str,Any]]:
    ensure_files(a)
    with open(file_workouts(a), "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return []

def save_workouts(a: str, data: List[Dict[str,Any]]):
    with open(file_workouts(a), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_history(a: str) -> List[Dict[str,Any]]:
    ensure_files(a)
    with open(file_history(a), "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return []

def save_history(a: str, data: List[Dict[str,Any]]):
    with open(file_history(a), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_plan(a: str) -> str:
    p = file_plan(a)
    if not os.path.exists(p):
        with open(p,"w",encoding="utf-8") as f: f.write("")
        return ""
    with open(p,"r",encoding="utf-8") as f:
        return f.read()

def save_plan(a: str, text: str):
    with open(file_plan(a),"w",encoding="utf-8") as f:
        f.write(text)

# -----------------------
# Preloaded exercises + inline SVG icons (bodybuilding style)
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
SVG = {
  "Petto":"<svg class='muscle-icon' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'><path d='M3 12c0-3.314 2.686-6 6-6 1.657 0 3 1.343 3 3 0-1.657 1.343-3 3-3 3.314 0 6 2.686 6 6v6H3v-6z' stroke='#ffccd9' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
  "Dorso":"<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M12 2v4m0 12v4M4 8c4 4 8 4 16 0' stroke='#ffd9b3' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
  "Spalle":"<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M12 3c2 0 3 1 4 3s2 3 4 3' stroke='#d9b3ff' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
  "Bicipiti":"<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M4 20c2-4 6-6 10-6s8 2 10 6' stroke='#ffd1b3' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
  "Tricipiti":"<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M3 12h18' stroke='#ffb3d9' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
  "Gambe":"<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M6 3v18M18 3v18' stroke='#c6f0ff' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>",
  "Core":"<svg class='muscle-icon' viewBox='0 0 24 24' fill='none'><path d='M12 2c3 0 6 4 6 10s-3 10-6 10-6-4-6-10 3-10 6-10z' stroke='#e6ffcc' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round'/></svg>"
}

# -----------------------
# Session state init
# -----------------------
if "athlete" not in st.session_state: st.session_state.athlete = ATHLETES[0]
if "show_plan_editor" not in st.session_state: st.session_state.show_plan_editor = False

# -----------------------
# Motivational rotating text (30s) — self-contained HTML/JS component
# -----------------------
MOTIVS = [
  "Non mollare ora.",
  "Ogni rep ti avvicina al tuo obiettivo.",
  "Il dolore è temporaneo, il risultato è per sempre.",
  "Diventa la versione più forte di te stesso.",
  "Disciplina > Motivazione.",
  "Un giorno o il giorno 1 — scegli oggi."
]
# JS inside component rotates the text locally every 30s; no rerun needed.
# Inject animation for motivational phrases (SAFE VERSION)
import json

motivs_json = json.dumps(MOTIVS)

js = f"""
<script>
const motivs = {motivs_json};
let idx = 0;
function rotateMotiv() {{
    const el = window.parent.document.querySelector('#motiv-box');
    if (el) {{
        el.innerText = motivs[idx];
        idx = (idx + 1) % motivs.length;
    }}
}}
setInterval(rotateMotiv, 30000);
</script>
"""

st.markdown("<div id='motiv-box' style='font-size:22px; padding:12px; color:#00eaff; font-weight:600;'>Caricamento...</div>", unsafe_allow_html=True)
st.markdown(js, unsafe_allow_html=True)

st_html(js, height=64)

# -----------------------
# Athlete picker main area (animated avatars)
# -----------------------
st.write("## 👤 Scegli atleta")
cols = st.columns(len(ATHLETES))
for i,a in enumerate(ATHLETES):
    with cols[i]:
        selected = (st.session_state.athlete == a)
        bg = "#7c52ff" if a == "Simone" else "#4db8ff"
        cls = "avatar avatar-selected" if selected else "avatar"
        st.markdown(f"<div style='text-align:center;'><div class='{cls}' style='background:{bg};'>{a[0]}</div></div>", unsafe_allow_html=True)
        if st.button(f"Seleziona {a}", key=f"sel_{a}"):
            st.session_state.athlete = a
            st.rerun()

ath = st.session_state.athlete
ensure_files(ath)

# -----------------------
# Top controls (export/reset)
# -----------------------
c1,c2,c3 = st.columns([3,2,2])
with c1:
    st.markdown(f"<div class='card'><b>{ath}</b> — <span class='small'>Salvataggi locali in data/</span></div>", unsafe_allow_html=True)
with c2:
    if st.button("📥 Esporta storico (CSV)"):
        hist = load_history(ath)
        if hist:
            df = pd.DataFrame(hist)
            st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"{ath.lower()}_history.csv")
        else:
            st.info("Nessuno storico disponibile.")
with c3:
    if st.button("🧹 Reset locale"):
        save_workouts(ath, []); save_history(ath, []); save_plan(ath, ""); st.success("Dati resettati"); st.rerun()

st.markdown("---")

# -----------------------
# Load & normalize workouts
# -----------------------
def normalize(e: Dict[str,Any]) -> Dict[str,Any]:
    out = {}
    out["id"] = e.get("id", str(uuid.uuid4()))
    out["group"] = e.get("group", e.get("muscle", "Generale"))
    out["exercise"] = e.get("exercise", e.get("esercizio", "Unnamed"))
    out["day"] = e.get("day", e.get("giorno", "Lun"))
    sets = e.get("sets") or e.get("serie") or e.get("series") or e.get("weights")
    if isinstance(sets, list):
        s=[]
        for item in sets:
            if isinstance(item, dict):
                s.append({"peso":int(item.get("peso",0)),"reps":int(item.get("reps",0))})
            elif isinstance(item,(int,float)):
                s.append({"peso":int(item),"reps":0})
            else:
                s.append({"peso":0,"reps":0})
    elif isinstance(sets, dict):
        s=[]
        for k in sorted(sets.keys()):
            v=sets[k]; 
            if isinstance(v,dict): s.append({"peso":int(v.get("peso",0)),"reps":int(v.get("reps",0))})
            else: s.append({"peso":int(v if isinstance(v,(int,float)) else 0),"reps":0})
    else:
        s=[{"peso":0,"reps":0} for _ in range(3)]
    out["sets"]=s; out["timestamp"]=e.get("timestamp", datetime.now().isoformat())
    return out

workouts_raw = load_workouts(ath)
workouts = [normalize(e) for e in workouts_raw]
save_workouts(ath, workouts)

# -----------------------
# Add exercise UI
# -----------------------
st.subheader("➕ Aggiungi esercizio")
with st.expander("Aggiungi nuovo esercizio"):
    g_col, e_col, d_col = st.columns([2,4,1])
    with g_col:
        group = st.selectbox("Gruppo muscolare", list(PRELOADED.keys()))
        st.markdown(SVG.get(group,""), unsafe_allow_html=True)
    with e_col:
        exercise_choice = st.selectbox("Scegli esercizio", PRELOADED[group] + ["➕ Personalizzato"])
        if exercise_choice == "➕ Personalizzato":
            exercise = st.text_input("Nome esercizio (personalizzato)").strip()
        else:
            exercise = exercise_choice
    with d_col:
        day = st.selectbox("Giorno", ["Lun","Mar","Mer","Gio","Ven","Sab","Dom"])
    if exercise:
        sets_n = st.number_input("Numero serie", min_value=1, max_value=12, value=3)
        st.markdown("**Pesi & reps per serie (opzionale)**")
        cols_weights = st.columns(min(4, sets_n))
        new_sets=[]
        for i in range(sets_n):
            c = cols_weights[i % len(cols_weights)]
            w = c.number_input(f"S{i+1} kg", min_value=0, max_value=600, value=0, key=f"new_w_{i}")
            r = c.number_input(f"S{i+1} rep", min_value=0, max_value=200, value=0, key=f"new_r_{i}")
            new_sets.append({"peso":int(w),"reps":int(r)})
        if st.button("Aggiungi alla routine"):
            new_entry = {"id":str(uuid.uuid4()), "group":group, "exercise":exercise, "day":day, "sets": new_sets if any(s["peso"]>0 or s["reps"]>0 for s in new_sets) else [{"peso":0,"reps":0} for _ in range(sets_n)], "timestamp": datetime.now().isoformat()}
            workouts.append(new_entry); save_workouts(ath, workouts); st.success("Aggiunto!"); st.rerun()

st.markdown("---")

# -----------------------
# Filters and per-set editing
# -----------------------
st.subheader("📋 Routine — modifica per-set")
f1,f2 = st.columns([2,3])
with f1: filter_day = st.selectbox("Filtra giorno", ["Tutti","Lun","Mar","Mer","Gio","Ven","Sab","Dom"])
with f2:
    all_ex = sorted({w["exercise"] for w in workouts})
    filter_ex = st.selectbox("Filtra esercizio", ["Tutti"] + all_ex)

display_list=[]
for w in workouts:
    if filter_day!="Tutti" and w["day"]!=filter_day: continue
    if filter_ex!="Tutti" and w["exercise"]!=filter_ex: continue
    display_list.append(w)

if not display_list:
    st.info("Nessun esercizio con i filtri selezionati.")
else:
    for entry in display_list:
        st.markdown(f"<div class='exercise-card'><b style='font-size:15px'>{entry['exercise']}</b> <span class='small'> — {entry['group']} ({entry['day']})</span>", unsafe_allow_html=True)
        for i,s in enumerate(entry["sets"]):
            cols = st.columns([2,1,1,1])
            cols[0].markdown(f"**Serie {i+1}**")
            p = cols[1].number_input(f"peso_{entry['id']}_{i}", min_value=0, max_value=2000, value=int(s.get("peso",0)), key=f"peso_{entry['id']}_{i}")
            r = cols[2].number_input(f"rep_{entry['id']}_{i}", min_value=0, max_value=500, value=int(s.get("reps",0)), key=f"rep_{entry['id']}_{i}")
            idx = next((ix for ix,w in enumerate(workouts) if w["id"]==entry["id"]), None)
            if idx is not None:
                workouts[idx]["sets"][i]["peso"] = int(p)
                workouts[idx]["sets"][i]["reps"] = int(r)
        b1,b2 = st.columns([1,1])
        if b1.button("💾 Salva entry", key=f"save_{entry['id']}"):
            save_workouts(ath, workouts); st.success("Salvato")
        if b2.button("🗑️ Elimina entry", key=f"del_{entry['id']}"):
            workouts = [w for w in workouts if w["id"]!=entry["id"]]; save_workouts(ath, workouts); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------
# Scheda palestra (hidden editor)
# -----------------------
st.subheader("📒 Scheda palestra")
if st.button("🔽 Mostra / Nascondi scheda"):
    st.session_state.show_plan_editor = not st.session_state.show_plan_editor

if st.session_state.show_plan_editor:
    plan = load_plan(ath)
    txt = st.text_area("Modifica la scheda (Markdown o testo)", value=plan, height=260)
    c1,c2 = st.columns([1,1])
    with c1:
        if st.button("💾 Salva scheda"):
            save_plan(ath, txt); st.success("Scheda salvata")
    with c2:
        st.download_button("📄 Esporta scheda (TXT)", txt.encode("utf-8"), file_name=f"{ath.lower()}_plan.txt")

st.markdown("---")

# -----------------------
# Register session -> history (with note)
# -----------------------
st.subheader("📥 Registra sessione")
st.write("La nota verrà salvata insieme a ciascuna serie registrata.")
note = st.text_input("Nota sessione (opzionale)", value="")
if st.button("Registra sessione nello storico"):
    hist = load_history(ath)
    now = datetime.now().isoformat()
    for w in workouts:
        for s in w["sets"]:
            hist.append({"date":now,"exercise":w["exercise"],"group":w["group"],"day":w["day"],"peso":s.get("peso",0),"reps":s.get("reps",0),"note":note})
    save_history(ath, hist); st.success("Sessione registrata"); st.rerun()

st.markdown("---")

# -----------------------
# Analytics: per-exercise or group
# -----------------------
st.subheader("📈 Analytics")
hist = load_history(ath)
if not hist:
    st.info("Nessuno storico: registra sessioni per popolare i grafici.")
else:
    df = pd.DataFrame(hist)
    df["date_dt"] = pd.to_datetime(df["date"])
    mode = st.radio("Visualizza per", ["Esercizio","Gruppo muscolare"], horizontal=True)
    if mode=="Esercizio":
        ex_list = sorted(df["exercise"].unique())
        sel = st.selectbox("Scegli esercizio", ex_list)
        df_sel = df[df["exercise"]==sel].sort_values("date_dt")
        df_plot = df_sel.groupby("date_dt", as_index=False).agg({"peso":"mean","reps":"sum"})
        fig = px.line(df_plot, x="date_dt", y="peso", markers=True, title=f"Progressione peso — {sel}")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        groups = sorted(df["group"].unique())
        selg = st.selectbox("Scegli gruppo", groups)
        df_g = df[df["group"]==selg].copy()
        df_g["week"] = df_g["date_dt"].dt.strftime("%Y-%U")
        df_g["volume"] = df_g["peso"]*df_g["reps"]
        vol = df_g.groupby("week", as_index=False).agg({"volume":"sum"}).sort_values("week")
        if vol.empty:
            st.info("Dati insufficienti per questo gruppo.")
        else:
            fig2 = px.bar(vol.tail(12), x="week", y="volume", title=f"Volume settimanale — {selg} (ultime 12 settimane)")
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("Workout Tracker PRO — animated version — data saved locally in /data")
