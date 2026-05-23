import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة
st.set_page_config(page_title="Smart Pharmacy SaaS", layout="wide")

# 2. تسجيل الدخول
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

# 3. إعدادات النظام
st.title("💊 لوحة تحكم صيدليتك الذكية")
with st.sidebar:
    uploaded_file = st.file_uploader("ارفع ملف المخزون", type=["csv", "xlsx"])
    if st.button("تسجيل خروج"): st.session_state.logged_in = False; st.rerun()

# 4. المعالجة
if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    cols = df.columns.tolist()

    # اختيار الأعمدة
    with st.expander("🛠️ ضبط الأعمدة"):
        c1, c2, c3 = st.columns(3)
        col_name = c1.selectbox("اسم الدواء", cols)
        col_stock = c2.selectbox("المخزون", cols)
        col_sales = c3.selectbox("البيع اليومي", cols)
        col_lead = st.selectbox("مدة التوريد", cols)
        col_price = st.selectbox("السعر", cols)

    # تنظيف البيانات
    for c in [col_stock, col_sales, col_lead, col_price]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    
    # حسابات
    df['نقطة_إعادة_الطلب'] = (df[col_sales] * df[col_lead] * 1.25).round(0)
    df['الحالة'] = np.where(df[col_stock] <= df['نقطة_إعادة_الطلب'], 'نقص', 'آمن')

    # عرض KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric("إجمالي الأصناف", len(df))
    k2.metric("أصناف ناقصة", len(df[df['الحالة'] == 'نقص']))
    k3.metric("قيمة المخزون", f"{int((df[col_stock]*df[col_price]).sum()):,}")

    st.markdown("---")
    
    # الرسم البياني
    st.subheader("📊 مستويات المخزون")
    fig = px.bar(df, x=col_name, y=col_stock, color='الحالة', color_discrete_map={'نقص': 'red', 'آمن': 'green'})
    st.plotly_chart(fig, use_container_width=True)

    # الجدول
    st.subheader("📋 تقرير التفاصيل")
    st.dataframe(df, use_container_width=True)
else:
    st.info("👋 ارفع ملف المخزون للبدء.")
