import streamlit as st
import pandas as pd
import re
from pathlib import Path

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
SOURCE_CSV   = Path(__file__).parent.parent / "2025_cleaned.csv"
PROJECTS_CSV = Path(__file__).parent.parent / "projects.csv"

STATUS_OPTIONS = ["חדשה", "בתהליך", "תקוע", "הסתיים"]
COLS = ["מס עבודה", "שם לקוח", "גוש", "חלקה", "מקום", "מטפל", "סטטוס"]


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def load_projects() -> pd.DataFrame:
    if PROJECTS_CSV.exists():
        df = pd.read_csv(PROJECTS_CSV, encoding="utf-8-sig")
        for col in ["מטפל", "סטטוס"]:
            if col not in df.columns:
                df[col] = "" if col == "מטפל" else "חדשה"
        return df
    if SOURCE_CSV.exists():
        df = pd.read_csv(SOURCE_CSV, encoding="utf-8-sig")
        df["מטפל"]  = ""
        df["סטטוס"] = "חדשה"
        return df
    return pd.DataFrame(columns=COLS)


def save_projects(df: pd.DataFrame) -> None:
    df.to_csv(PROJECTS_CSV, index=False, encoding="utf-8-sig")


def next_job_id(df: pd.DataFrame) -> str:
    nums = df["מס עבודה"].astype(str).str.extract(r"(\d+)")[0].dropna().astype(int)
    return str(nums.max() + 1) if len(nums) else "26069"


def extract_nums(val) -> set:
    return set(re.findall(r"\d+", str(val)))


def find_duplicates(df: pd.DataFrame, gush: str, chalka: str) -> pd.DataFrame:
    g = extract_nums(gush)
    c = extract_nums(chalka)
    if not g or not c:
        return pd.DataFrame()
    return df[df.apply(
        lambda r: bool(g & extract_nums(r["גוש"])) and bool(c & extract_nums(r["חלקה"])),
        axis=1,
    )]


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "pdf" not in st.session_state:
    st.session_state.pdf = load_projects()

pdf = st.session_state.pdf

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero-pm">
  <div>
    <h1>📋 ניהול פרויקטים</h1>
    <p>עריכת סטטוס ומטפל · הוספת עבודות חדשות · התרעה על כפילויות</p>
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
st.markdown(f"""
<div style="margin:4px 0 18px; display:flex; flex-wrap:wrap; gap:0;">
  <span class="chip c-new">🆕 חדשה &nbsp; <strong>{sc.get("חדשה", 0)}</strong></span>
  <span class="chip c-prog">⚙️ בתהליך &nbsp; <strong>{sc.get("בתהליך", 0)}</strong></span>
  <span class="chip c-stuck">🔴 תקוע &nbsp; <strong>{sc.get("תקוע", 0)}</strong></span>
  <span class="chip c-done">✅ הסתיים &nbsp; <strong>{sc.get("הסתיים", 0)}</strong></span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FILTERS
# ══════════════════════════════════════════════════════════════════════════════
f1, f2, f3 = st.columns([1, 1, 2])
with f1:
    flt_status = st.multiselect("סטטוס:", STATUS_OPTIONS, default=STATUS_OPTIONS)
with f2:
    handlers    = sorted(pdf["מטפל"].replace("", pd.NA).dropna().unique().tolist())
    flt_handler = st.selectbox("מטפל:", ["הכל"] + handlers)
with f3:
    search = st.text_input("🔍 חיפוש (שם לקוח / מקום / גוש / חלקה):")

filtered = pdf.copy()
if flt_status:
    filtered = filtered[filtered["סטטוס"].isin(flt_status)]
if flt_handler != "הכל":
    filtered = filtered[filtered["מטפל"] == flt_handler]
if search.strip():
    mask = filtered.apply(
        lambda r: search.strip().lower() in " ".join(r.astype(str)).lower(), axis=1
    )
    filtered = filtered[mask]

st.caption(f"מציג **{len(filtered):,}** מתוך **{len(pdf):,}** עבודות")

# ══════════════════════════════════════════════════════════════════════════════
# DATA EDITOR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📋 רשימת עבודות – ערוך סטטוס ומטפל ישירות בטבלה</div>',
            unsafe_allow_html=True)

orig_indices = filtered.index.tolist()

edited = st.data_editor(
    filtered.reset_index(drop=True),
    column_config={
        "מס עבודה": st.column_config.TextColumn("מס׳ עבודה",  disabled=True, width="small"),
        "שם לקוח":  st.column_config.TextColumn("שם לקוח",    disabled=True, width="large"),
        "גוש":      st.column_config.TextColumn("גוש",         disabled=True, width="small"),
        "חלקה":     st.column_config.TextColumn("חלקה",        disabled=True, width="small"),
        "מקום":     st.column_config.TextColumn("מקום",        disabled=True, width="medium"),
        "מטפל": st.column_config.TextColumn(
            "✏️ מטפל",
            width="medium",
            help="הקלד שם המטפל בעבודה",
        ),
        "סטטוס": st.column_config.SelectboxColumn(
            "✏️ סטטוס",
            options=STATUS_OPTIONS,
            width="small",
            required=True,
            help="בחר סטטוס עבודה",
        ),
    },
    hide_index=True,
    use_container_width=True,
    height=430,
    num_rows="fixed",
    key="editor",
)

# ── Save / Download buttons ────────────────────────────────────────────────
s1, s2, s3 = st.columns([1, 1, 3])
with s1:
    if st.button("💾 שמור שינויים", type="primary", use_container_width=True):
        updated = pdf.copy()
        for i, orig_idx in enumerate(orig_indices):
            if i < len(edited):
                updated.at[orig_idx, "מטפל"]  = edited.at[i, "מטפל"]  or ""
                updated.at[orig_idx, "סטטוס"] = edited.at[i, "סטטוס"] or "חדשה"
        st.session_state.pdf = updated
        save_projects(updated)
        st.success("✅ שינויים נשמרו בהצלחה!")
        st.rerun()
with s2:
    st.download_button(
        "⬇️ ייצא CSV",
        data=pdf.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name="projects_export.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# ADD NEW PROJECT
# ══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown('<div class="sec">➕ הוספת עבודה חדשה</div>', unsafe_allow_html=True)

with st.form("add_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        n_id      = st.text_input("מס׳ עבודה", value=next_job_id(pdf),
                                   help="מספר ייחודי – ממולא אוטומטית")
        n_client  = st.text_input("שם לקוח *")
        n_gush    = st.text_input("גוש *", help="ניתן להזין מספרים מרובים מופרדים בפסיק")
        n_chalka  = st.text_input("חלקה *", help="ניתן להזין מספרים מרובים")
    with c2:
        n_place   = st.text_input("מקום")
        n_handler = st.text_input("מטפל")
        n_status  = st.selectbox("סטטוס", STATUS_OPTIONS)

    submitted = st.form_submit_button("➕ הוסף עבודה", type="primary",
                                      use_container_width=True)

if submitted:
    if not n_client.strip() or not n_gush.strip() or not n_chalka.strip():
        st.markdown('<div class="alert-err">⚠️ שדות חובה: שם לקוח, גוש, חלקה</div>',
                    unsafe_allow_html=True)
    else:
        dups = find_duplicates(pdf, n_gush.strip(), n_chalka.strip())
        if not dups.empty:
            rows_html = ""
            for _, row in dups.iterrows():
                rows_html += (
                    f"<tr><td><b>{row['מס עבודה']}</b></td>"
                    f"<td>{row['שם לקוח']}</td>"
                    f"<td>{row.get('מקום','')}</td>"
                    f"<td>{row.get('סטטוס','')}</td></tr>"
                )
            st.markdown(f"""
<div class="alert-err">
  🔴 <strong>התרעה: גוש {n_gush} + חלקה {n_chalka} כבר קיימים במערכת!</strong>
  <table style="margin-top:8px; width:100%; font-size:.85rem; border-collapse:collapse;">
    <thead><tr style="border-bottom:1px solid #e09090;">
      <th>מס׳ עבודה</th><th>לקוח</th><th>מקום</th><th>סטטוס</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
  <div style="margin-top:10px; font-size:.82rem; opacity:.8;">
    העבודה <u>לא נוספה</u>. בדוק שהגוש/חלקה נכונים לפני הוספה.
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            new_row = {
                "מס עבודה": n_id.strip(),
                "שם לקוח":  n_client.strip(),
                "גוש":      n_gush.strip(),
                "חלקה":     n_chalka.strip(),
                "מקום":     n_place.strip(),
                "מטפל":     n_handler.strip(),
                "סטטוס":    n_status,
            }
            updated = pd.concat(
                [pdf, pd.DataFrame([new_row])], ignore_index=True
            )
            st.session_state.pdf = updated
            save_projects(updated)
            st.success(f"✅ עבודה {n_id} – {n_client} נוספה בהצלחה!")
            st.rerun()

# ── Upload saved CSV ────────────────────────────────────────────────────────
st.divider()
with st.expander("📂 טען קובץ פרויקטים שמור"):
    st.caption("אם הורדת CSV קודם – העלה אותו כאן כדי לשחזר את הנתונים")
    up = st.file_uploader("בחר projects.csv", type="csv", key="restore")
    if up:
        try:
            restored = pd.read_csv(up, encoding="utf-8-sig")
            for col in ["מטפל", "סטטוס"]:
                if col not in restored.columns:
                    restored[col] = "" if col == "מטפל" else "חדשה"
            st.session_state.pdf = restored
            save_projects(restored)
            st.success(f"✅ שוחזר – {len(restored):,} עבודות")
            st.rerun()
        except Exception as e:
            st.error(f"שגיאה בטעינה: {e}")

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#e8edf4; margin:24px 0 14px">
<div style="text-align:center; color:#aaa; font-size:.8rem;">
    📋 ניהול פרויקטים · משרד מודדים · שינויים נשמרים ב-projects.csv
</div>
""", unsafe_allow_html=True)
