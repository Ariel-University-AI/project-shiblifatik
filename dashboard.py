import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# הגדרת מבנה הדף
st.set_page_config(page_title="Data Analysis Dashboard", layout="wide")

# פונקציית הניקוי מהשלב הקודם
@st.cache_data # מסייע לביצועים מהירים ב-Streamlit
def clean_data(df):
    # הסרת כפילויות
    df = df.drop_duplicates(keep='first')
    
    # הסרת עמודות שרובן חסרות
    threshold = 0.5 * len(df)
    missing = df.isna().sum()
    cols_to_drop = missing[missing > threshold].index
    if len(cols_to_drop) > 0:
        df = df.drop(columns=cols_to_drop)
        
    # השלמת נתונים הנותרים
    for col in df.columns:
        if df[col].isna().sum() > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])
    return df

st.title("📊 מערכת ניתוח משרד מודדים")

# === תפריט צד (Sidebar) ===
st.sidebar.header("הגדרות והעלאת קבצים")
# "הוסף sidebar להעלאת CSV אחר"
uploaded_file = st.sidebar.file_uploader("העלה קובץ CSV כאן", type=['csv'])

if uploaded_file is not None:
    # קריאת הקובץ
    raw_df = pd.read_csv(uploaded_file, na_values=['/'])
    
    # הפעלת אלגוריתם הניקוי על הקובץ שהועלה!
    df = clean_data(raw_df)
    st.success("✅ הקובץ נטען החסרים טופלו והשכפולים הוסרו!")
    
    # --- סינון לפני ציור הגרפים ---
    # "הוסף סינון לפי [קטגוריה] שמסנן את כל הגרפים"
    cat_columns = df.select_dtypes(include=['object', 'string']).columns.tolist()
    
    if len(cat_columns) > 0:
        st.sidebar.subheader("🎯 סינון מותאם (Filters)")
        # מאפשר למשתמש לבחור לפי איזו עמודה לסנן
        filter_category = st.sidebar.selectbox("בחר עמודת קטגוריה לסינון:", cat_columns)
        
        unique_vals = df[filter_category].unique().tolist()
        # בוחרים אילו ערכים בדיוק לסנן
        selected_vals = st.sidebar.multiselect(f"בחר ערכים מתוך {filter_category}:", unique_vals, default=unique_vals)
        
        # עדכון המסד נתונים לפי הסינון. הגרפים למטה ישתמשו בקובץ המסונן, ולכן יתעדכנו אוטומטית!
        filtered_df = df[df[filter_category].isin(selected_vals)]
    else:
        filtered_df = df
        st.sidebar.info("לא נמצאו עמודות קטגוריאליות מתאימות לסינון.")

    # --- יצירת גרפים מתעדכנים ---
    st.markdown("---")
    
    if not filtered_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 התפלגות נתונים")
            if len(cat_columns) > 0:
                # גרף פשוט שמראה כמות לפי קטגוריה (לדוגמה לפי המקום שסונן)
                plot_col = cat_columns[-1] 
                fig1 = px.histogram(filtered_df, x=plot_col, title=f"כמות פרויקטים לפי: {plot_col}")
                st.plotly_chart(fig1, use_container_width=True)
                
        with col2:
            st.markdown("### 🔥 מפת חום (Correlation Heatmap)")
            # "heatmap קורלציה"
            # חילוץ עמודות מספריות בלבד בשביל קורלציה
            num_cols = filtered_df.select_dtypes(include=[np.number])
            if len(num_cols.columns) > 1:
                # מחשב קורלציה (קשרים בין הנתונים)
                corr_matrix = num_cols.corr()
                
                # ציור ההיטמאפ
                fig2 = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                                color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("אין מספיק עמודות מספריות טהורות בקובץ ליצירת מפתקורלציות.")
                
        with st.expander("👁️ הצג נתוני טבלה מלאים (לאחר הניקוי)"):
            st.dataframe(filtered_df)
    else:
        st.warning("כל הנתונים סוננו החוצה, אנא שנה את הסינון בתפריט השמאלי עקב חוסר בתוצאות.")
        
else:
    st.info("👈 אנא העלה קובץ באזור ה-Sidebar השמאלי להצגת ניתוח הנתונים.")
