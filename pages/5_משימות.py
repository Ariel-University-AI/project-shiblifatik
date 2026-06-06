import streamlit as st
import pandas as pd
import plotly.express as px
import io
from pathlib import Path
from datetime import date, timedelta

st.set_page_config(page_title="משימות", page_icon="✅", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family:'Heebo',sans-serif; direction:rtl; }
[data-testid="stSidebar"] { background:#0d1f38; }
[data-testid="stSidebar"] * { color:#cfe2f7 !important; }
.hero-t { background:linear-gradient(135deg,#0d1f38 0%,#1a4a7a 60%,#0d3b6e 100%);
          border-radius:16px; padding:36px 40px; text-align:center;
          color:#fff; margin-bottom:18px; }
.hero-t h1 { font-size:2.2rem; font-weight:800; margin:0 0 8px; }
.hero-t p  { font-size:.95rem; opacity:.75; margin:0; }
.chip { display:inline-block; border-radius:20px; padding:5px 16px;
        font-size:.82rem; font-weight:700; margin:3px 4px; color:#fff; }
.c-new   { background:#1565c0; }
.c-prog  { background:#e65100; }
.c-stuck { background:#6a1a6a; }
.c-done  { background:#1b5e20; }
.sec { font-size:1rem; font-weight:700; color:#1e3a5f;
       border-right:4px solid #2d6a9f; padding-right:10px; margin:18px 0 12px; }
.kanban-col { background:#f0f5fc; border-radius:12px; padding:12px;
              min-height:200px; }
.kanban-card { background:#fff; border-radius:8px; padding:10px 12px;
               margin:8px 0; box-shadow:0 2px 8px rgba(0,0,0,.1);
               border-right:4px solid #2d6a9f; font-size:.88rem; }
.deadline-warn { background:#7b1a1a; border-radius:10px; padding:12px 18px;
                 color:#fff; margin:10px 0; font-size:.9rem; line-height:1.8; }
</style>
""", unsafe_allow_html=True)

ROOT       = Path(__file__).parent.parent
TASKS_CSV  = ROOT / "tasks.csv"
LOG_CSV    = ROOT / "tasks_log.csv"
PROJ_CSV   = ROOT / "projects.csv"

STATUSES   = ["חדשה", "בתהליך", "תקועה", "הושלם"]
ASSIGNEES  = ["גודאת", "מוסטפא", "נדים"]
STATUS_COL = "סטטוס"
COLUMNS    = ["שם המשימה","סטטוס","אחראי","פרויקט","חברה",
              "לקוח מקושר","דד ליין","שעות מדווחות","שעות שבוצעו",
              "תאריך יצירה","תאריך סגירה","הערות"]
TEXT_COLS  = ["שם המשימה","סטטוס","אחראי","פרויקט","חברה","לקוח מקושר","הערות"]
DATE_COLS  = ["דד ליין","תאריך יצירה","תאריך סגירה"]
NUM_COLS   = ["שעות מדווחות","שעות שבוצעו"]

def load_tasks() -> pd.DataFrame:
    if TASKS_CSV.exists():
        df = pd.read_csv(TASKS_CSV, encoding="utf-8-sig")
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        for col in TEXT_COLS:
            df[col] = df[col].fillna("").astype(str)
        for col in DATE_COLS:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
        for col in NUM_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)

def save_tasks(df: pd.DataFrame):
    df.to_csv(TASKS_CSV, index=False, encoding="utf-8-sig")

def log_change(action: str, name: str):
    entry = pd.DataFrame([{"תאריך": str(date.today()), "פעולה": action, "שם המשימה": name}])
    if LOG_CSV.exists():
        log = pd.read_csv(LOG_CSV, encoding="utf-8-sig")
        log = pd.concat([log, entry], ignore_index=True)
    else:
        log = entry
    log.to_csv(LOG_CSV, index=False, encoding="utf-8-sig")

def load_project_numbers():
    if PROJ_CSV.exists():
        df = pd.read_csv(PROJ_CSV, encoding="utf-8-sig")
        if "מס עבודה" in df.columns:
            return sorted(df["מס עבודה"].dropna().astype(str).unique().tolist())
    return []

def to_excel(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="משימות")
    return buf.getvalue()

today = date.today()

# ── load ──────────────────────────────────────────────────────────────────────
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

with st.sidebar:
    if st.button("🔄 רענן נתונים"):
        st.session_state.tasks = load_tasks()
        st.rerun()

pdf = st.session_state.tasks.copy()

# ── hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-t">
  <h1>✅ ניהול משימות</h1>
  <p>מעקב משימות לפי סטטוס, אחראי ופרויקט</p>
</div>
""", unsafe_allow_html=True)

# ── deadline alert ────────────────────────────────────────────────────────────
if not pdf.empty and "דד ליין" in pdf.columns:
    open_tasks = pdf[pdf["סטטוס"] != "הושלם"].copy()
    open_tasks["_d"] = open_tasks["דד ליין"].apply(
        lambda x: x if isinstance(x, date) else None)
    soon = open_tasks[open_tasks["_d"].apply(
        lambda d: pd.notna(d) and d is not None and today <= d <= today + timedelta(days=7))]
    if not soon.empty:
        items = "".join(
            f'<div>⚡ <strong>{r["שם המשימה"]}</strong>'
            f'{" — " + r["אחראי"] if r["אחראי"] else ""}'
            f' | דד-ליין: <strong>{r["_d"]}</strong></div>'
            for _, r in soon.iterrows()
        )
        st.markdown(f'<div class="deadline-warn">🔔 {len(soon)} משימות עם דד-ליין השבוע:<br>{items}</div>',
                    unsafe_allow_html=True)

# ── KPI chips ─────────────────────────────────────────────────────────────────
sc = pdf[STATUS_COL].value_counts().to_dict() if STATUS_COL in pdf.columns else {}
st.markdown(f"""
<div style="margin:0 0 18px; display:flex; flex-wrap:wrap; gap:0;">
  <span class="chip c-new">🆕 חדשה &nbsp;<strong>{sc.get("חדשה",0)}</strong></span>
  <span class="chip c-prog">⚙️ בתהליך &nbsp;<strong>{sc.get("בתהליך",0)}</strong></span>
  <span class="chip c-stuck">🟣 תקועה &nbsp;<strong>{sc.get("תקועה",0)}</strong></span>
  <span class="chip c-done">✅ הושלם &nbsp;<strong>{sc.get("הושלם",0)}</strong></span>
</div>
""", unsafe_allow_html=True)

# ── filters sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 סינון משימות")
    flt_status  = st.multiselect("סטטוס:", STATUSES, default=STATUSES)
    people      = sorted(pdf["אחראי"].replace("", pd.NA).dropna().unique().tolist())
    flt_person  = st.selectbox("אחראי:", ["הכל"] + people)
    projects_list = sorted(pdf["פרויקט"].replace("", pd.NA).dropna().unique().tolist())
    flt_project = st.selectbox("פרויקט:", ["הכל"] + projects_list)
    search      = st.text_input("🔍 חיפוש חופשי:")
    flt_soon    = st.checkbox("⚡ דד-ליין השבוע בלבד")

filtered = pdf.copy()
if flt_status:
    filtered = filtered[filtered[STATUS_COL].isin(flt_status)]
if flt_person != "הכל":
    filtered = filtered[filtered["אחראי"] == flt_person]
if flt_project != "הכל":
    filtered = filtered[filtered["פרויקט"] == flt_project]
if search.strip():
    mask = filtered.apply(
        lambda r: search.strip().lower() in " ".join(r.fillna("").astype(str).tolist()).lower(), axis=1)
    filtered = filtered[mask]
if flt_soon:
    filtered["_d"] = filtered["דד ליין"].apply(lambda x: x if isinstance(x, date) else None)
    filtered = filtered[filtered["_d"].apply(
        lambda d: pd.notna(d) and d is not None and today <= d <= today + timedelta(days=7))]
    filtered = filtered.drop(columns=["_d"], errors="ignore")

st.caption(f"מציג **{len(filtered):,}** מתוך **{len(pdf):,}** משימות")

# ── tabs ──────────────────────────────────────────────────────────────────────
tab_table, tab_kanban, tab_gantt, tab_analytics, tab_log = st.tabs([
    "📋 טבלה", "🗂 Kanban", "📅 גאנט", "📊 ניתוח", "🕐 היסטוריה"
])

# ── TAB: TABLE ────────────────────────────────────────────────────────────────
with tab_table:
    proj_names = load_project_numbers()

    edited = st.data_editor(
        filtered.reset_index(drop=True),
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "שם המשימה":     st.column_config.TextColumn("שם המשימה", width="large"),
            "סטטוס":         st.column_config.SelectboxColumn("סטטוס", options=STATUSES, width="small"),
            "אחראי":         st.column_config.SelectboxColumn("אחראי", options=ASSIGNEES, width="small"),
            "פרויקט":        st.column_config.SelectboxColumn("פרויקט",
                             options=(proj_names if proj_names else None), width="medium"),
            "חברה":          st.column_config.TextColumn("חברה", width="medium"),
            "לקוח מקושר":   st.column_config.TextColumn("לקוח מקושר", width="medium"),
            "דד ליין":       st.column_config.DateColumn("דד ליין", format="DD/MM/YYYY", width="small"),
            "שעות מדווחות": st.column_config.NumberColumn("שעות מדווחות", min_value=0, step=0.5, width="small"),
            "שעות שבוצעו":  st.column_config.NumberColumn("שעות שבוצעו", min_value=0, step=0.5, width="small"),
            "תאריך יצירה":  st.column_config.DateColumn("תאריך יצירה", format="DD/MM/YYYY", width="small"),
            "תאריך סגירה":  st.column_config.DateColumn("תאריך סגירה", format="DD/MM/YYYY", width="small"),
            "הערות":         st.column_config.TextColumn("הערות", width="large"),
        },
        hide_index=True,
        key="tasks_editor",
    )

    sv, dl_btn, _ = st.columns([1, 1, 4])
    with sv:
        if st.button("💾 שמור שינויים", type="primary", use_container_width=True):
            orig_indices = filtered.index.tolist()
            updated = pdf.copy()
            for i, orig_i in enumerate(orig_indices):
                if i < len(edited):
                    updated.loc[orig_i] = edited.iloc[i].values
            new_rows = edited.iloc[len(orig_indices):]
            if not new_rows.empty:
                for _, nr in new_rows.iterrows():
                    if str(nr.get("שם המשימה","")).strip():
                        log_change("נוספה", str(nr.get("שם המשימה","")))
                updated = pd.concat([updated, new_rows], ignore_index=True)
            updated = updated.dropna(subset=["שם המשימה"]).reset_index(drop=True)
            updated = updated[updated["שם המשימה"].astype(str).str.strip() != ""]
            save_tasks(updated)
            st.session_state.tasks = updated
            log_change("עודכנה", "שינויים כלליים")
            st.success("✅ המשימות נשמרו!")
            st.rerun()
    with dl_btn:
        st.download_button("⬇️ ייצוא Excel", data=to_excel(filtered),
                           file_name="משימות.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)

# ── TAB: KANBAN ───────────────────────────────────────────────────────────────
with tab_kanban:
    st.markdown('<div class="sec">🗂 תצוגת Kanban</div>', unsafe_allow_html=True)
    colors = {"חדשה":"#1565c0","בתהליך":"#e65100","תקועה":"#6a1a6a","הושלם":"#1b5e20"}
    cols = st.columns(4)
    for idx, status in enumerate(STATUSES):
        with cols[idx]:
            grp = filtered[filtered["סטטוס"] == status]
            st.markdown(
                f'<div style="background:{colors[status]};color:#fff;border-radius:10px;'
                f'padding:8px 14px;text-align:center;font-weight:700;margin-bottom:10px;">'
                f'{status} ({len(grp)})</div>', unsafe_allow_html=True)
            for _, row in grp.iterrows():
                deadline_str = f"<br>📅 {row['דד ליין']}" if pd.notna(row.get("דד ליין")) and row["דד ליין"] != "" else ""
                person_str   = f"<br>👤 {row['אחראי']}" if str(row.get("אחראי","")).strip() else ""
                notes_str    = f"<br>📝 {row['הערות']}" if str(row.get("הערות","")).strip() else ""
                st.markdown(
                    f'<div class="kanban-card" style="border-right-color:{colors[status]};">'
                    f'<strong>{row["שם המשימה"]}</strong>'
                    f'{person_str}{deadline_str}{notes_str}</div>',
                    unsafe_allow_html=True)

# ── TAB: GANTT ────────────────────────────────────────────────────────────────
with tab_gantt:
    st.markdown('<div class="sec">📅 גאנט – ציר זמן משימות</div>', unsafe_allow_html=True)
    gantt_df = filtered.copy()
    gantt_df["_start"] = gantt_df["תאריך יצירה"].apply(
        lambda x: x if isinstance(x, date) else today)
    gantt_df["_end"] = gantt_df.apply(
        lambda r: r["דד ליין"] if isinstance(r.get("דד ליין"), date)
        else (r["תאריך סגירה"] if isinstance(r.get("תאריך סגירה"), date)
              else today + timedelta(days=7)), axis=1)
    gantt_df = gantt_df[gantt_df["_start"] <= gantt_df["_end"]]

    if gantt_df.empty:
        st.info("אין משימות עם תאריכים להצגה בגאנט. הוסף תאריך יצירה ו/או דד-ליין.")
    else:
        fig_g = px.timeline(
            gantt_df,
            x_start="_start", x_end="_end",
            y="שם המשימה", color="סטטוס",
            color_discrete_map={"חדשה":"#1565c0","בתהליך":"#e65100",
                                "תקועה":"#6a1a6a","הושלם":"#1b5e20"},
            title="גאנט – משימות לפי זמן",
            template="plotly_white",
            hover_data=["אחראי","הערות"],
        )
        fig_g.update_yaxes(autorange="reversed")
        fig_g.update_layout(title_font_size=14, height=max(300, len(gantt_df)*40))
        fig_g.add_vline(x=str(today), line_dash="dash", line_color="#c0392b",
                        annotation_text="היום", annotation_position="top right")
        st.plotly_chart(fig_g, use_container_width=True)

# ── TAB: ANALYTICS ────────────────────────────────────────────────────────────
with tab_analytics:
    st.markdown('<div class="sec">📊 ניתוח משימות</div>', unsafe_allow_html=True)
    if pdf.empty:
        st.info("אין נתונים לניתוח.")
    else:
        a1, a2 = st.columns(2)

        with a1:
            # workload per person
            wl = pdf[pdf["אחראי"].str.strip() != ""]["אחראי"].value_counts().head(10).reset_index()
            wl.columns = ["אחראי","משימות"]
            fig_wl = px.bar(wl, x="משימות", y="אחראי", orientation="h",
                            title="עומס לפי אחראי", color="משימות",
                            color_continuous_scale="Blues", text_auto=True,
                            template="plotly_white")
            fig_wl.update_layout(coloraxis_showscale=False, title_font_size=13,
                                 yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_wl, use_container_width=True)

        with a2:
            # completion trend by month
            done = pdf[pdf["תאריך סגירה"].apply(lambda x: isinstance(x, date))].copy()
            if not done.empty:
                done["חודש"] = pd.to_datetime(done["תאריך סגירה"]).dt.strftime("%Y-%m")
                trend = done.groupby("חודש").size().reset_index(name="הושלמו")
                fig_tr = px.line(trend, x="חודש", y="הושלמו",
                                 title="מגמת השלמת משימות לפי חודש",
                                 markers=True, template="plotly_white",
                                 color_discrete_sequence=["#2d6a9f"])
                fig_tr.update_layout(title_font_size=13)
                st.plotly_chart(fig_tr, use_container_width=True)
            else:
                st.info("אין משימות עם תאריך סגירה להצגת מגמה.")

        a3, a4 = st.columns(2)
        with a3:
            # hours comparison
            hours = pdf[NUM_COLS].sum()
            if hours.sum() > 0:
                fig_h = px.bar(
                    x=["מדווחות","שבוצעו"],
                    y=[hours["שעות מדווחות"], hours["שעות שבוצעו"]],
                    title="שעות: מדווחות vs שבוצעו",
                    color=["מדווחות","שבוצעו"],
                    color_discrete_sequence=["#2d6a9f","#1e8449"],
                    template="plotly_white", text_auto=True,
                )
                fig_h.update_layout(showlegend=False, title_font_size=13)
                st.plotly_chart(fig_h, use_container_width=True)

        with a4:
            # status donut
            sc2 = pdf["סטטוס"].value_counts().reset_index()
            sc2.columns = ["סטטוס","כמות"]
            fig_d = px.pie(sc2, names="סטטוס", values="כמות",
                           title="התפלגות סטטוסים", hole=0.45,
                           color="סטטוס",
                           color_discrete_map={"חדשה":"#1565c0","בתהליך":"#e65100",
                                               "תקועה":"#6a1a6a","הושלם":"#1b5e20"},
                           template="plotly_white")
            fig_d.update_layout(title_font_size=13)
            st.plotly_chart(fig_d, use_container_width=True)

# ── TAB: LOG ──────────────────────────────────────────────────────────────────
with tab_log:
    st.markdown('<div class="sec">🕐 היסטוריית שינויים</div>', unsafe_allow_html=True)
    if LOG_CSV.exists():
        log_df = pd.read_csv(LOG_CSV, encoding="utf-8-sig")
        st.dataframe(log_df.sort_values("תאריך", ascending=False),
                     use_container_width=True, hide_index=True)
        st.download_button("⬇️ ייצוא לוג Excel", data=to_excel(log_df),
                           file_name="tasks_log.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("עדיין אין היסטוריית שינויים.")

# ── add quick task ─────────────────────────────────────────────────────────────
st.divider()
st.markdown('<div class="sec">➕ הוספת משימה מהירה</div>', unsafe_allow_html=True)
proj_names_form = load_project_numbers()

with st.form("add_task", clear_on_submit=True):
    c1,c2,c3,c4 = st.columns([3,1,2,2])
    with c1: n_name     = st.text_input("שם המשימה *")
    with c2: n_status   = st.selectbox("סטטוס", STATUSES)
    with c3: n_person   = st.selectbox("אחראי", [""] + ASSIGNEES)
    with c4: n_deadline = st.date_input("דד ליין", value=None)

    c5,c6,c7 = st.columns([2,2,3])
    with c5:
        n_project = (st.selectbox("פרויקט", [""] + proj_names_form)
                     if proj_names_form else st.text_input("פרויקט"))
    with c6: n_company = st.text_input("חברה")
    with c7: n_notes   = st.text_input("הערות")

    submitted = st.form_submit_button("➕ הוסף משימה", type="primary")

if submitted:
    if not n_name.strip():
        st.error("שם המשימה הוא שדה חובה.")
    else:
        new_row = {
            "שם המשימה": n_name.strip(), "סטטוס": n_status,
            "אחראי": n_person.strip(), "פרויקט": str(n_project).strip(),
            "חברה": n_company.strip(), "לקוח מקושר": "",
            "דד ליין": str(n_deadline) if n_deadline else "",
            "שעות מדווחות": "", "שעות שבוצעו": "",
            "תאריך יצירה": str(date.today()), "תאריך סגירה": "",
            "הערות": n_notes.strip(),
        }
        updated = pd.concat([st.session_state.tasks, pd.DataFrame([new_row])], ignore_index=True)
        save_tasks(updated)
        log_change("נוספה", n_name.strip())
        st.session_state.tasks = updated
        st.success(f"✅ המשימה '{n_name}' נוספה!")
        st.rerun()
