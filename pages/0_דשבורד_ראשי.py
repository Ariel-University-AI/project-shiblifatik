import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date, timedelta

st.set_page_config(page_title="דשבורד ראשי", page_icon="🏠", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family:'Heebo',sans-serif; direction:rtl; }
[data-testid="stSidebar"] { background:#0d1f38; }
[data-testid="stSidebar"] * { color:#cfe2f7 !important; }
.kpi { flex:1; border-radius:14px; padding:22px 16px;
       background:linear-gradient(135deg,#1e3a5f,#2d6a9f);
       color:#fff; box-shadow:0 4px 18px rgba(0,0,0,.25); text-align:center; }
.kpi.ok   { background:linear-gradient(135deg,#0d3320,#1e8449); }
.kpi.warn { background:linear-gradient(135deg,#4a1010,#c0392b); }
.kpi.gold { background:linear-gradient(135deg,#4a3000,#d68910); }
.kpi-lbl  { font-size:.73rem; letter-spacing:1.2px; text-transform:uppercase;
            opacity:.75; margin-bottom:6px; }
.kpi-val  { font-size:2.4rem; font-weight:800; line-height:1; }
.kpi-sub  { font-size:.7rem; opacity:.6; margin-top:4px; }
.sec { font-size:1rem; font-weight:700; color:#1e3a5f;
       border-right:4px solid #2d6a9f; padding-right:10px; margin:18px 0 12px; }
.alert-deadline {
    background:#7b1a1a; border-radius:10px; padding:14px 18px;
    margin:10px 0; color:#fff; font-size:.9rem; line-height:1.8;
}
.search-result {
    background:#f0f5fc; border-right:4px solid #2d6a9f;
    border-radius:8px; padding:10px 14px; margin:6px 0;
    font-size:.88rem; color:#1e3a5f;
}
</style>
""", unsafe_allow_html=True)

ROOT = Path(__file__).parent.parent
PROJECTS_CSV = ROOT / "projects.csv"
TASKS_CSV    = ROOT / "tasks.csv"

@st.cache_data(ttl=30)
def load_projects():
    if not PROJECTS_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(PROJECTS_CSV, encoding="utf-8-sig")
    if "יעד סיום" in df.columns:
        df["יעד סיום"] = pd.to_datetime(df["יעד סיום"], errors="coerce").dt.date
    return df

@st.cache_data(ttl=30)
def load_tasks():
    if not TASKS_CSV.exists():
        return pd.DataFrame()
    df = pd.read_csv(TASKS_CSV, encoding="utf-8-sig")
    for col in ["דד ליין", "תאריך יצירה", "תאריך סגירה"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("").astype(str)
    return df

proj = load_projects()
tasks = load_tasks()
today = date.today()

st.markdown("""
<div style="background:linear-gradient(135deg,#0d1f38 0%,#1a4a7a 60%,#0d3b6e 100%);
     border-radius:18px;padding:40px;text-align:center;color:#fff;margin-bottom:20px;">
  <div style="font-size:2.6rem;font-weight:800;margin-bottom:8px;">🏠 דשבורד ראשי</div>
  <div style="opacity:.75;font-size:1rem;">סיכום כולל – פרויקטים, משימות ותזכורות</div>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">📌 מדדי מפתח</div>', unsafe_allow_html=True)

def is_overdue_proj(row):
    if str(row.get("סטטוס","")) == "הסתיים":
        return False
    d = row.get("יעד סיום")
    if d is None or (isinstance(d, float) and pd.isna(d)):
        return False
    try:
        return (d if isinstance(d, date) else pd.to_datetime(d).date()) < today
    except Exception:
        return False

proj_total   = len(proj) if not proj.empty else 0
proj_open    = int((proj["סטטוס"] != "הסתיים").sum()) if not proj.empty and "סטטוס" in proj.columns else 0
proj_overdue = int(proj.apply(is_overdue_proj, axis=1).sum()) if not proj.empty else 0

task_total   = len(tasks) if not tasks.empty else 0
task_open    = int((tasks["סטטוס"] != "הושלם").sum()) if not tasks.empty and "סטטוס" in tasks.columns else 0
task_stuck   = int((tasks["סטטוס"] == "תקועה").sum()) if not tasks.empty and "סטטוס" in tasks.columns else 0

def _days(d):
    try:
        return (d if isinstance(d, date) else pd.to_datetime(d).date())
    except Exception:
        return None

if not tasks.empty and "דד ליין" in tasks.columns:
    soon = tasks[tasks["סטטוס"] != "הושלם"].copy()
    deadline_dt = pd.to_datetime(soon["דד ליין"], errors="coerce")
    today_ts = pd.Timestamp(today)
    task_soon = int(((deadline_dt >= today_ts) & (deadline_dt <= today_ts + timedelta(days=7))).sum())
else:
    task_soon = 0

c1,c2,c3,c4,c5,c6 = st.columns(6)
cards = [
    (c1, "📁 פרויקטים", proj_total, "סה\"כ", ""),
    (c2, "🔓 פרויקטים פתוחים", proj_open, "פעילים", ""),
    (c3, "⏰ פרויקטים באיחור", proj_overdue, "עברו דדליין", "warn"),
    (c4, "✅ משימות", task_total, "סה\"כ", ""),
    (c5, "🟣 משימות תקועות", task_stuck, "דורשות טיפול", "warn" if task_stuck else "ok"),
    (c6, "⚡ דד-ליין השבוע", task_soon, "משימות קרובות", "gold" if task_soon else "ok"),
]
for col, lbl, val, sub, cls in cards:
    with col:
        st.markdown(f'<div class="kpi {cls}"><div class="kpi-lbl">{lbl}</div>'
                    f'<div class="kpi-val">{val}</div>'
                    f'<div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

# ── deadline alerts ───────────────────────────────────────────────────────────
if task_soon > 0:
    st.markdown('<div class="sec">⚡ תזכורות – דד-ליין השבוע</div>', unsafe_allow_html=True)
    soon_tasks = soon[soon["_d"].apply(lambda d: d is not None and today <= d <= today + timedelta(days=7))]
    items = "".join(
        f'<div>🔴 <strong>{r.get("שם המשימה","")}</strong> — {r.get("אחראי","")} | '
        f'דד-ליין: <strong>{r["_d"]}</strong></div>'
        for _, r in soon_tasks.iterrows()
    )
    st.markdown(f'<div class="alert-deadline">{items}</div>', unsafe_allow_html=True)

# ── global search ─────────────────────────────────────────────────────────────
st.markdown('<div class="sec">🔍 חיפוש גלובלי</div>', unsafe_allow_html=True)
gsearch = st.text_input("חפש בפרויקטים ובמשימות:", placeholder="שם לקוח, גוש, חלקה, אחראי...")

if gsearch.strip():
    q = gsearch.strip().lower()
    results = []
    if not proj.empty:
        for _, r in proj.iterrows():
            if q in " ".join(r.fillna("").astype(str).tolist()).lower():
                results.append(("📁 פרויקט", str(r.get("שם לקוח","")), str(r.get("מקום","")), str(r.get("סטטוס",""))))
    if not tasks.empty:
        for _, r in tasks.iterrows():
            if q in " ".join(r.fillna("").astype(str).tolist()).lower():
                results.append(("✅ משימה", str(r.get("שם המשימה","")), str(r.get("אחראי","")), str(r.get("סטטוס",""))))

    st.caption(f"נמצאו **{len(results)}** תוצאות")
    for kind, name, detail, status in results:
        st.markdown(f'<div class="search-result">{kind} &nbsp;|&nbsp; <strong>{name}</strong>'
                    f'&nbsp;·&nbsp; {detail} &nbsp;|&nbsp; {status}</div>',
                    unsafe_allow_html=True)

# ── charts row ────────────────────────────────────────────────────────────────
st.markdown('<div class="sec">📊 ניתוח</div>', unsafe_allow_html=True)
ch1, ch2, ch3 = st.columns(3)

with ch1:
    if not proj.empty and "סטטוס" in proj.columns:
        pc = proj["סטטוס"].value_counts().reset_index()
        pc.columns = ["סטטוס","כמות"]
        fig = px.pie(pc, names="סטטוס", values="כמות", title="פרויקטים לפי סטטוס",
                     hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r,
                     template="plotly_white")
        fig.update_layout(title_font_size=13, margin=dict(t=40,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

with ch2:
    if not tasks.empty and "סטטוס" in tasks.columns:
        tc = tasks["סטטוס"].value_counts().reset_index()
        tc.columns = ["סטטוס","כמות"]
        cmap = {"חדשה":"#1565c0","בתהליך":"#e65100","תקועה":"#6a1a6a","הושלם":"#1b5e20"}
        fig2 = px.bar(tc, x="סטטוס", y="כמות", color="סטטוס",
                      color_discrete_map=cmap, text_auto=True,
                      title="משימות לפי סטטוס", template="plotly_white")
        fig2.update_layout(showlegend=False, title_font_size=13,
                           margin=dict(t=40,b=10,l=10,r=10))
        st.plotly_chart(fig2, use_container_width=True)

with ch3:
    if not tasks.empty and "אחראי" in tasks.columns:
        wl = tasks[tasks["אחראי"].str.strip() != ""]["אחראי"].value_counts().head(8).reset_index()
        wl.columns = ["אחראי","משימות"]
        fig3 = px.bar(wl, x="משימות", y="אחראי", orientation="h",
                      title="עומס לפי אחראי", color="משימות",
                      color_continuous_scale="Blues", text_auto=True,
                      template="plotly_white")
        fig3.update_layout(coloraxis_showscale=False, title_font_size=13,
                           yaxis=dict(autorange="reversed"),
                           margin=dict(t=40,b=10,l=10,r=10))
        st.plotly_chart(fig3, use_container_width=True)

# ── recent tasks ──────────────────────────────────────────────────────────────
if not tasks.empty:
    st.markdown('<div class="sec">🕐 משימות אחרונות</div>', unsafe_allow_html=True)
    show = tasks.sort_values("תאריך יצירה", ascending=False).head(5)[
        ["שם המשימה","סטטוס","אחראי","דד ליין","הערות"]
    ]
    st.dataframe(show, use_container_width=True, hide_index=True)
