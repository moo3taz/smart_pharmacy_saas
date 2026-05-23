import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة
st.set_page_config(page_title="Smart Pharmacy Pro", layout="wide")

# 2. منطق تسجيل الدخول
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.sidebar.title("🔐 تسجيل الدخول")
    user = st.sidebar.text_input("اسم المستخدم")
    pw = st.sidebar.text_input("كلمة المرور", type="password")
    if st.sidebar.button("دخول"):
        if user == "admin" and pw == "123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")
    st.stop()

# 3. Sidebar
with st.sidebar:
    st.header("⚙️ إعدادات الإدارة")
    uploaded_file = st.file_uploader("ارفع ملف الإكسيل", type=["csv", "xlsx"])
    safety_factor = st.slider("مخزون الأمان (%)", 0, 100, 25)
    if st.button("تسجيل خروج"): st.session_state.logged_in = False; st.rerun()

# 4. معالجة البيانات
if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    cols = df.columns.tolist()
    
    # اختيار الأعمدة بمرونة (بدل ما نفتح 7 أعمدة غصب)
    st.subheader("حدد الأعمدة من ملفك:")
    c1, c2, c3 = st.columns(3)
    col_name = c1.selectbox("اسم الدواء", cols)
    col_stock = c2.selectbox("المخزون", cols)
    col_sales = c3.selectbox("البيع اليومي", cols)
    
    c4, c5, c6 = st.columns(3)
    col_lead = c4.selectbox("مدة التوريد", cols)
    col_history = c5.selectbox("مبيعات 3 شهور", cols)
    col_price = c6.selectbox("السعر", cols)
else:
    df = pd.DataFrame([{"name": "Panadol", "stock": 5, "sales": 8, "lead": 2, "last_3": 0, "price": 50}])
    col_name, col_stock, col_sales, col_lead, col_history, col_price = "name", "stock", "sales", "lead", "last_3", "price"

# 5. الحسابات
df[col_stock] = pd.to_numeric(df[col_stock], errors='coerce').fillna(0)
df[col_sales] = pd.to_numeric(df[col_sales], errors='coerce').fillna(0)
df['نقطة إعادة الطلب'] = ((df[col_sales] * df[col_lead]) * (1 + safety_factor/100)).round(1)
df['حالة القرار'] = np.where(df[col_stock] <= df['نقطة إعادة الطلب'], '⚠️ اطلب فوراً', '✅ آمن')
df['قيمة_النقص'] = np.where(df[col_stock] <= df['نقطة إعادة الطلب'], (df['نقطة إعادة الطلب'] - df[col_stock]) * df[col_price], 0)

# 6. العرض
st.subheader("تقرير المخزون")
def color_status(val):
    return 'background-color: #FF4B4B' if val == '⚠️ اطلب فوراً' else 'background-color: #008080'

st.dataframe(df.style.map(color_status, subset=['حالة القرار']), use_container_width=True)
