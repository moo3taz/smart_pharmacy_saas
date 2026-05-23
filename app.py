import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة
st.set_page_config(page_title="Smart Pharmacy SaaS", layout="wide")

# 2. منطق تسجيل الدخول
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

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

# --- بعد تسجيل الدخول ---
st.title("💊 لوحة تحكم صيدليتك الذكية")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    uploaded_file = st.file_uploader("ارفع ملف المخزون (xlsx/csv)", type=["csv", "xlsx"])
    safety_factor = st.slider("نسبة مخزون الأمان (%)", 0, 100, 25, 5)
    forecast_months = st.slider("فترة التنبؤ (شهور)", 1, 6, 3)
    if st.button("تسجيل خروج"):
        st.session_state.logged_in = False
        st.rerun()

# 3. معالجة البيانات
if uploaded_file is None:
    st.info("👋 يرجى رفع ملف المخزون للبدء.")
else:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        cols = df.columns.tolist()
        
        # اختيار الأعمدة بوضوح
        st.subheader("🛠️ تأكد من اختيار الأعمدة الصحيحة:")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        col_name = c1.selectbox("اسم الدواء", cols)
        col_stock = c2.selectbox("المخزون", cols)
        col_sales = c3.selectbox("البيع اليومي", cols)
        col_lead = c4.selectbox("مدة التوريد", cols)
        col_history = c5.selectbox("مبيعات 3 شهور", cols)
        col_active = c6.selectbox("المادة الفعالة", cols)

        # 4. الحسابات (بشكل آمن تماماً)
        for col in [col_stock, col_sales, col_lead, col_history]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df['نقطة_إعادة_الطلب'] = ((df[col_sales] * df[col_lead]) * (1 + safety_factor/100)).round(1)

        # 5. التبويبات
        tab1, tab2, tab3 = st.tabs(["📊 نظرة عامة", "🔮 التنبؤ الذكي", "🥀 الرواكد والبدائل"])

        with tab1:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("إجمالي الأصناف", len(df))
            k2.metric("أصناف حرجة", len(df[df[col_stock] <= df['نقطة_إعادة_الطلب']]))
            k3.metric("مخزون راكد", len(df[df[col_history] == 0]))
            k4.metric("مبيعات متوقعة", f"{(df[col_sales].sum()*30*forecast_months):,.0f} ج.م")
            
            st.markdown("---")
            fig1 = px.bar(df, x=col_name, y=col_sales, title="معدل المبيعات اليومي", template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)
            st.dataframe(df, use_container_width=True)

        with tab2:
            st.header("🔮 التنبؤ الذكي")
            df['متوقع'] = (df[col_sales] * 30 * forecast_months).round(0)
            st.dataframe(df[[col_name, 'متوقع']], use_container_width=True)

        with tab3:
            st.header("🔄 إدارة الرواكد والأصناف الحرجة")
            critical_df = df[df[col_stock] <= df['نقطة_إعادة_الطلب']]
            st.subheader("⚠️ الأصناف الحرجة")
            st.dataframe(critical_df[[col_name, col_stock, 'نقطة_إعادة_الطلب']], use_container_width=True)
            
            dead_df = df[df[col_history] == 0]
            st.subheader("🥀 الأصناف الراكدة")
            st.dataframe(dead_df[[col_name, col_stock]], use_container_width=True)
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {e}")
