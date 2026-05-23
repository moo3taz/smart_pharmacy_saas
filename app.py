import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Smart Pharmacy SaaS", layout="wide")

# منطق تسجيل الدخول
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.sidebar.title("🔐 تسجيل الدخول")
    user = st.sidebar.text_input("اسم المستخدم")
    pw = st.sidebar.text_input("كلمة المرور", type="password")
    if st.sidebar.button("دخول"):
        if user == "admin" and pw == "123":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("بيانات الدخول غير صحيحة")
    st.stop()

st.title("💊 لوحة تحكم صيدليتك الذكية")

with st.sidebar:
    uploaded_file = st.file_uploader("ارفع ملف المخزون", type=["csv", "xlsx"])
    safety_factor = st.slider("مخزون الأمان (%)", 0, 100, 25)
    if st.button("تسجيل خروج"): st.session_state.logged_in = False; st.rerun()

if uploaded_file:
    # 1. قراءة الملف مع معالجة الأسماء المكررة
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df = df.loc[:, ~df.columns.duplicated()] # حل مشكلة التكرار
    
    cols = df.columns.tolist()
    with st.expander("🛠️ ضبط الأعمدة"):
        c1, c2, c3 = st.columns(3)
        col_name = c1.selectbox("اسم الدواء", cols)
        col_stock = c2.selectbox("المخزون", cols)
        col_sales = c3.selectbox("البيع اليومي", cols)
        col_lead = st.selectbox("مدة التوريد", cols)
        col_history = st.selectbox("مبيعات 3 شهور", cols)

    # 2. تحويل البيانات لأرقام (تنظيف آمن)
    for col in [col_stock, col_sales, col_lead, col_history]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3. حسابات
    df['نقطة_إعادة_الطلب'] = ((df[col_sales] * df[col_lead]) * (1 + safety_factor/100)).round(1)
    df['الحالة'] = np.where(df[col_stock] <= df['نقطة_إعادة_الطلب'], '⚠️ ناقص', '✅ متوفر')

    # 4. عرض البيانات
    k1, k2, k3 = st.columns(3)
    k1.metric("أصناف ناقصة", len(df[df['الحالة'] == '⚠️ ناقص']))
    k2.metric("إجمالي المخزون", int(df[col_stock].sum()))
    k3.metric("عدد الأصناف", len(df))

    st.subheader("📋 تقرير التفاصيل")
    st.dataframe(df, use_container_width=True)
else:
    st.info("👋 يرجى رفع ملف المخزون للبدء.")
