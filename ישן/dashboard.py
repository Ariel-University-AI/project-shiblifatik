import streamlit as st

st.set_page_config(
    page_title="משרד מודדים – EDA",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
html, body, [class*="css"] { direction:rtl; }
</style>
""", unsafe_allow_html=True)

st.title("📐 מערכת ניתוח נתונים – משרד מודדים")
st.markdown("בחר דף מהתפריט הצדדי:")
st.page_link("pages/4_ניהול_פרויקטים.py", label="📋 ניהול פרויקטים",       icon="📋")
st.page_link("pages/1_ניתוח_נתונים.py",  label="📊 ניתוח נתונים (EDA)",   icon="📊")
st.page_link("pages/3_הסברי_גרפים.py",   label="📖 הסברי גרפים ומדדים",  icon="📖")
st.page_link("pages/2_אודות.py",           label="ℹ️ אודות הפרויקט",       icon="ℹ️")
