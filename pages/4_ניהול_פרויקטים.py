import streamlit as st
import pandas as pd
import re
import os
from pathlib import Path
from datetime import date

st.set_page_config(
    page_title="ניהול פרויקטים – משרד מודדים",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family:'Heebo',sans-serif; direction:rtl; }

.hero-pm {
    background:linear-gradient(135deg,#0d1f38 0%,#1a4a7a 60%,#0d3b6e 100%);
    border-radius:16px; padding:32px 36px; color:#fff;
    display:flex; align-items:center; justify-content:space-between;
    margin-bottom:16px;
}
.hero-pm h1 { margin:0; font-size:1.9rem; font-weight:800; }
.hero-pm p  { margin:6px 0 0; opacity:.7; font-size:.95rem; }

.chip {
    display:inline-flex; align-items:center; gap:8px;
    border-radius:22px; padding:10px 20px;
    font-size:.9rem; font-weight:700; color:#fff; margin-left:10px;
}
.c-new   { background:#2d6a9f; }
.c-prog  { background:#d68910; }
.c-stuck { background:#c0392b; }
.c-done  { background:#1e8449; }
.c-late  { background:#7b1a1a; }

.alert-warn {
    background:#fff8e1; border-right:4px solid #f39c12;
    border-radius:8px; padding:12px 16px; margin:8px 0;
    font-size:.9rem; color:#7d5a00; line-height:1.65;
}
.alert-err {
    background:#fdecea; border-right:4px solid #e53935;
    border-radius:8px; padding:12px 16px; margin:8px 0;
    font-size:.9rem; color:#7b1a1a; line-height:1.65;
}
.sec {
    font-size:1rem; font-weight:700; color:#1e3a5f;
    border-right:4px solid #2d6a9f; padding-right:10px;
    margin:14px 0 12px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PATHS & CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
SOURCE_CSV        = Path(__file__).parent.parent / "2025_cleaned.csv"
PROJECTS_CSV      = Path(__file__).parent.parent / "projects.csv"
MEASUREMENTS_ROOT = Path("D:/מדידות")

STATUS_OPTIONS = ["חדשה", "בתהליך", "תקוע", "הסתיים"]

EDITABLE_COLS = [
    "מטפל", "סטטוס",
    "הצעת מחיר", "זמן מדידה (שעות)",
    "תאריך התחלה", "יעד סיום",
    "תשלום שהתקבל",
]
BASE_COLS = ["מס עבודה", "שם לקוח", "גוש", "חלקה", "מקום"]
ALL_COLS  = BASE_COLS + EDITABLE_COLS


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _ensure_cols(df: pd.DataFrame) -> pd.DataFrame:
    defaults = {
        "מטפל":               "",
        "סטטוס":              "חדשה",
        "הצעת מחיר":          None,
        "זמן מדידה (שעות)":   None,
        "תאריך התחלה":        None,
        "יעד סיום":           None,
        "תשלום שהתקבל":       None,
    }
    for col, val in defaults.items():
        if col not in df.columns:
            df[col] = val
    # text columns must be str, never float/NaN
    for tcol in ("מטפל", "סטטוס"):
        df[tcol] = df[tcol].fillna("").astype(str)
    df["סטטוס"] = df["סטטוס"].replace("", "חדשה")
    # parse date columns
    for dcol in ("תאריך התחלה", "יעד סיום"):
        df[dcol] = pd.to_datetime(df[dcol], errors="coerce").dt.date
    # numeric
    for ncol in ("הצעת מחיר", "זמן מדידה (שעות)", "תשלום שהתקבל"):
        df[ncol] = pd.to_numeric(df[ncol], errors="coerce")
    return df


def load_projects() -> pd.DataFrame:
    if PROJECTS_CSV.exists():
        df = pd.read_csv(PROJECTS_CSV, encoding="utf-8-sig")
        return _ensure_cols(df)
    if SOURCE_CSV.exists():
        df = pd.read_csv(SOURCE_CSV, encoding="utf-8-sig")
        return _ensure_cols(df)
    return pd.DataFrame(columns=ALL_COLS)


def save_projects(df: pd.DataFrame) -> None:
    df.to_csv(PROJECTS_CSV, index=False, encoding="utf-8-sig")


def next_job_id(df: pd.DataFrame) -> str:
    nums = df["מס עבודה"].astype(str).str.extract(r"(\d+)")[0].dropna().astype(int)
    return str(nums.max() + 1) if len(nums) else "26069"


def extract_nums(val) -> set:
    return set(re.findall(r"\d+", str(val)))


def find_project_folder(job_id: str) -> Path | None:
    job_id = str(job_id).strip()
    if not MEASUREMENTS_ROOT.exists():
        return None
    for year_dir in sorted(MEASUREMENTS_ROOT.iterdir()):
        if not year_dir.is_dir():
            continue
        for folder in year_dir.iterdir():
            if folder.is_dir() and folder.name.startswith(job_id):
                return folder
    return None


def find_duplicates(df: pd.DataFrame, gush: str, chalka: str) -> pd.DataFrame:
    g = extract_nums(gush)
    c = extract_nums(chalka)
    if not g or not c:
        return pd.DataFrame()
    return df[df.apply(
        lambda r: bool(g & extract_nums(r["גוש"])) and bool(c & extract_nums(r["חלקה"])),
        axis=1,
    )]


def calc_balance_pct(row) -> str:
    try:
        quote   = float(row["הצעת מחיר"])
        payment = float(row["תשלום שהתקבל"])
        if quote <= 0:
            return ""
        pct = max(0.0, (quote - payment) / quote * 100)
        return f"{pct:.0f}%"
    except Exception:
        return ""


def is_overdue(row) -> bool:
    if str(row.get("סטטוס", "")) == "הסתיים":
        return False
    deadline = row.get("יעד סיום")
    if deadline is None or (isinstance(deadline, float) and pd.isna(deadline)):
        return False
    try:
        d = deadline if isinstance(deadline, date) else pd.to_datetime(deadline).date()
        return d < date.today()
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "pdf" not in st.session_state:
    st.session_state.pdf = load_projects()

pdf = st.session_state.pdf

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
overdue_count = sum(is_overdue(r) for _, r in pdf.iterrows())

st.markdown(f"""
<div class="hero-pm">
  <div>
    <h1>📋 ניהול פרויקטים</h1>
    <p>עריכת סטטוס · תאריכים · תשלומים · התרעות איחור</p>
  </div>
  <div style="text-align:left; font-size:1.8rem; font-weight:800; opacity:.85;">
    {len(pdf):,} עבודות
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# KPI STATUS CHIPS
# ══════════════════════════════════════════════════════════════════════════════
sc = pdf["סטטוס"].value_counts().to_dict() if "סטטוס" in pdf.columns else {}
late_chip = f'<span class="chip c-late">🔴 באיחור &nbsp; <strong>{overdue_count}</strong></span>' if overdue_count else ""
st.markdown(f"""
<div style="margin:4px 0 18px; display:flex; flex-wrap:wrap; gap:0;">
  <span class="chip c-new">🆕 חדשה &nbsp; <strong>{sc.get("חדשה", 0)}</strong></span>
  <span class="chip c-prog">⚙️ בתהליך &nbsp; <strong>{sc.get("בתהליך", 0)}</strong></span>
  <span class="chip c-stuck">🔴 תקוע &nbsp; <strong>{sc.get("תקוע", 0)}</strong></span>
  <span class="chip c-done">✅ הסתיים &nbsp; <strong>{sc.get("הסתיים", 0)}</strong></span>
  {late_chip}
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FILTERS
# ══════════════════════════════════════════════════════════════════════════════
f1, f2, f3, f4 = st.columns([1, 1, 1, 2])
with f1:
    flt_status = st.multiselect("סטטוס:", STATUS_OPTIONS, default=STATUS_OPTIONS)
with f2:
    handlers    = sorted(pdf["מטפל"].replace("", pd.NA).dropna().unique().tolist())
    flt_handler = st.selectbox("מטפל:", ["הכל"] + handlers)
with f3:
    flt_late = st.checkbox("⚠️ באיחור בלבד", value=False)
with f4:
    search = st.text_input("🔍 חיפוש (שם לקוח / מקום / גוש / חלקה):")

filtered = pdf.copy()
if flt_status:
    filtered = filtered[filtered["סטטוס"].isin(flt_status)]
if flt_handler != "הכל":
    filtered = filtered[filtered["מטפל"] == flt_handler]
if flt_late:
    filtered = filtered[filtered.apply(is_overdue, axis=1)]
if search.strip():
    mask = filtered.apply(
        lambda r: search.strip().lower() in " ".join(r.astype(str)).lower(), axis=1
    )
    filtered = filtered[mask]

st.caption(f"מציג **{len(filtered):,}** מתוך **{len(pdf):,}** עבודות")

# ══════════════════════════════════════════════════════════════════════════════
# DATA EDITOR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📋 רשימת עבודות – ערוך ישירות בטבלה</div>',
            unsafe_allow_html=True)

# add computed columns for display
display_df = filtered.copy().reset_index(drop=True)
display_df["יתרת תשלום %"] = display_df.apply(calc_balance_pct, axis=1)
display_df["⏰"] = display_df.apply(lambda r: "🔴" if is_overdue(r) else "", axis=1)

orig_indices = filtered.index.tolist()

edited = st.data_editor(
    display_df,
    column_config={
        "מס עבודה":          st.column_config.TextColumn("מס׳ עבודה",       disabled=True, width="small"),
        "שם לקוח":           st.column_config.TextColumn("שם לקוח",          disabled=True, width="large"),
        "גוש":               st.column_config.TextColumn("גוש",               disabled=True, width="small"),
        "חלקה":              st.column_config.TextColumn("חלקה",              disabled=True, width="small"),
        "מקום":              st.column_config.TextColumn("מקום",              disabled=True, width="medium"),
        "מטפל":              st.column_config.TextColumn("✏️ מטפל",           width="medium"),
        "סטטוס":             st.column_config.SelectboxColumn(
                                 "✏️ סטטוס", options=STATUS_OPTIONS,
                                 width="small", required=True),
        "הצעת מחיר":         st.column_config.NumberColumn(
                                 "💰 הצעת מחיר (₪)", min_value=0,
                                 format="₪ %d", width="medium"),
        "זמן מדידה (שעות)":  st.column_config.NumberColumn(
                                 "⏱ זמן מדידה (שעות)", min_value=0,
                                 format="%.1f ש׳", width="medium"),
        "תאריך התחלה":       st.column_config.DateColumn(
                                 "📅 תאריך התחלה", format="DD/MM/YYYY", width="medium"),
        "יעד סיום":          st.column_config.DateColumn(
                                 "🏁 יעד סיום", format="DD/MM/YYYY", width="medium"),
        "תשלום שהתקבל":      st.column_config.NumberColumn(
                                 "✅ תשלום שהתקבל (₪)", min_value=0,
                                 format="₪ %d", width="medium"),
        "יתרת תשלום %":      st.column_config.TextColumn(
                                 "📊 יתרת תשלום %", disabled=True, width="small"),
        "⏰":                 st.column_config.TextColumn(
                                 "⏰", disabled=True, width="small"),
    },
    hide_index=True,
    use_container_width=True,
    height=450,
    num_rows="fixed",
    key="editor",
)

# ── Save / Download ────────────────────────────────────────────────────────
s1, s2, _ = st.columns([1, 1, 3])
with s1:
    if st.button("💾 שמור שינויים", type="primary", use_container_width=True):
        updated = pdf.copy()
        for i, orig_idx in enumerate(orig_indices):
            if i >= len(edited):
                continue
            for col in EDITABLE_COLS:
                if col in edited.columns:
                    updated.at[orig_idx, col] = edited.at[i, col]
        st.session_state.pdf = updated
        save_projects(updated)
        st.success("✅ שינויים נשמרו!")
        st.rerun()
with s2:
    st.download_button(
        "⬇️ ייצא CSV",
        data=pdf.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name="projects_export.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ── Overdue warning table ──────────────────────────────────────────────────
overdue_df = pdf[pdf.apply(is_overdue, axis=1)]
if not overdue_df.empty:
    st.markdown(f"""
<div style="background:#fdecea;border-right:4px solid #e53935;border-radius:10px;
            padding:14px 18px;margin:14px 0;">
  🔴 <strong>{len(overdue_df)} עבודות באיחור</strong> — יעד הסיום עבר ללא סיום:
</div>""", unsafe_allow_html=True)

    def _style_overdue(row):
        return ["background-color:#fdecea; color:#7b1a1a"] * len(row)

    show_cols = ["מס עבודה", "שם לקוח", "מקום", "מטפל", "יעד סיום", "סטטוס"]
    show_cols = [c for c in show_cols if c in overdue_df.columns]
    styled = overdue_df[show_cols].style.apply(_style_overdue, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# ADD NEW PROJECT
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="sec">➕ הוספת עבודה חדשה</div>', unsafe_allow_html=True)

with st.form("add_form", clear_on_submit=True):
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        n_id      = st.text_input("מס׳ עבודה", value=next_job_id(pdf))
        n_client  = st.text_input("שם לקוח *")
        n_gush    = st.text_input("גוש *")
        n_chalka  = st.text_input("חלקה *")
    with r1c2:
        n_place   = st.text_input("מקום")
        n_handler = st.text_input("מטפל")
        n_status  = st.selectbox("סטטוס", STATUS_OPTIONS)
        n_hours   = st.number_input("זמן מדידה (שעות)", min_value=0.0, step=0.5)
    with r1c3:
        n_quote   = st.number_input("הצעת מחיר (₪)", min_value=0, step=500)
        n_payment = st.number_input("תשלום שהתקבל (₪)", min_value=0, step=500)
        n_start   = st.date_input("תאריך התחלה", value=None)
        n_end     = st.date_input("יעד סיום", value=None)

    submitted = st.form_submit_button("➕ הוסף עבודה", type="primary",
                                      use_container_width=True)

if submitted:
    if not n_client.strip() or not n_gush.strip() or not n_chalka.strip():
        st.markdown('<div class="alert-err">⚠️ שדות חובה: שם לקוח, גוש, חלקה</div>',
                    unsafe_allow_html=True)
    else:
        dups = find_duplicates(pdf, n_gush.strip(), n_chalka.strip())
        if not dups.empty:
            rows_html = "".join(
                f"<tr><td><b>{r['מס עבודה']}</b></td><td>{r['שם לקוח']}</td>"
                f"<td>{r.get('מקום','')}</td><td>{r.get('סטטוס','')}</td></tr>"
                for _, r in dups.iterrows()
            )
            st.markdown(f"""
<div class="alert-err">
  🔴 <strong>גוש {n_gush} + חלקה {n_chalka} כבר קיימים!</strong>
  <table style="margin-top:8px;width:100%;font-size:.85rem;border-collapse:collapse;">
    <thead><tr style="border-bottom:1px solid #e09090;">
      <th>מס׳</th><th>לקוח</th><th>מקום</th><th>סטטוס</th>
    </tr></thead><tbody>{rows_html}</tbody>
  </table>
  <div style="margin-top:10px;font-size:.82rem;opacity:.8;">העבודה לא נוספה.</div>
</div>""", unsafe_allow_html=True)
        else:
            new_row = {
                "מס עבודה":          n_id.strip(),
                "שם לקוח":           n_client.strip(),
                "גוש":               n_gush.strip(),
                "חלקה":              n_chalka.strip(),
                "מקום":              n_place.strip(),
                "מטפל":              n_handler.strip(),
                "סטטוס":             n_status,
                "הצעת מחיר":         n_quote or None,
                "זמן מדידה (שעות)":  n_hours or None,
                "תאריך התחלה":       n_start,
                "יעד סיום":          n_end,
                "תשלום שהתקבל":      n_payment or None,
            }
            updated = pd.concat([pdf, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.pdf = updated
            save_projects(updated)
            st.success(f"✅ עבודה {n_id} – {n_client} נוספה!")
            st.rerun()

# ── Upload saved CSV ────────────────────────────────────────────────────────
st.divider()
with st.expander("📂 טען קובץ פרויקטים שמור"):
    up = st.file_uploader("בחר projects.csv", type="csv", key="restore")
    if up:
        try:
            restored = _ensure_cols(pd.read_csv(up, encoding="utf-8-sig"))
            st.session_state.pdf = restored
            save_projects(restored)
            st.success(f"✅ שוחזר – {len(restored):,} עבודות")
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה בטעינה: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# OPEN PROJECT FOLDER
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="sec">📂 פתח תיקיית מדידות לעבודה</div>', unsafe_allow_html=True)

job_ids = sorted(pdf["מס עבודה"].astype(str).tolist())
col_sel, col_btn = st.columns([3, 1])
with col_sel:
    selected_job = st.selectbox("בחר מס׳ עבודה:", job_ids, key="folder_select")
with col_btn:
    st.write("")
    open_clicked = st.button("📂 פתח תיקייה", use_container_width=True)

if open_clicked:
    folder = find_project_folder(selected_job)
    if folder:
        os.startfile(str(folder))
        st.success(f"✅ פותח: {folder.name}")
    elif not MEASUREMENTS_ROOT.exists():
        st.error("❌ הנתיב D:\\מדידות לא נמצא")
    else:
        st.warning(f"⚠️ לא נמצאה תיקייה עבור עבודה {selected_job}")

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#e8edf4; margin:24px 0 14px">
<div style="text-align:center; color:#aaa; font-size:.8rem;">
    📋 ניהול פרויקטים · משרד מודדים · שינויים נשמרים ב-projects.csv
</div>
""", unsafe_allow_html=True)
